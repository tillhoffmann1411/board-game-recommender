/**
 * Content-Based Recommendation Engine
 *
 * Recommends games based on similarity to user's highly-rated games.
 * Uses weighted cosine similarity across:
 * - Categories (50%)
 * - Mechanics (30%)
 * - Numeric features: players, playtime, complexity (20%)
 *
 * Ported from: _archive/recommendation-algorithms/content_based_filtering.py
 */

import { ObjectId } from "mongodb";
import { getDb } from "@/lib/db/client";
import { COLLECTIONS } from "@/lib/db/schema";
import type { Game } from "@/lib/db/schema";
import type { RecommendationEngine, ScoredGame, UserRating } from "./types";

// Weight configuration
const WEIGHTS = {
  categories: 0.5,
  mechanics: 0.3,
  players: 0.07,
  playtime: 0.07,
  complexity: 0.06,
};

interface UserProfile {
  categories: Map<string, number>; // category -> weight
  mechanics: Map<string, number>; // mechanic -> weight
  avgMinPlayers: number;
  avgMaxPlayers: number;
  avgMinPlaytime: number;
  avgMaxPlaytime: number;
  avgComplexity: number;
}

export class ContentBasedEngine implements RecommendationEngine {
  name = "content-based" as const;

  async recommend(
    _userId: ObjectId,
    userRatings: UserRating[],
    excludeGameIds: Set<string>,
    limit: number
  ): Promise<ScoredGame[]> {
    // Need at least one rating
    if (userRatings.length === 0) {
      return [];
    }

    const db = await getDb();

    // Get highly-rated games (7+)
    const highRatings = userRatings.filter((r) => r.rating >= 7);
    if (highRatings.length === 0) {
      // Fall back to all ratings
      highRatings.push(...userRatings);
    }

    // Fetch game details for rated games
    const ratedGameIds = highRatings.map((r) => r.gameId);
    const ratedGames = await db
      .collection<Game>(COLLECTIONS.GAMES)
      .find({ _id: { $in: ratedGameIds } })
      .toArray();

    // Build user profile from rated games
    const profile = this.buildUserProfile(ratedGames, highRatings);

    // Get candidate games that share categories or mechanics
    const allCategories = Array.from(profile.categories.keys());
    const allMechanics = Array.from(profile.mechanics.keys());

    const candidates = await db
      .collection<Game>(COLLECTIONS.GAMES)
      .find({
        $or: [
          { categories: { $in: allCategories } },
          { mechanics: { $in: allMechanics } },
        ],
      })
      .limit(1000)
      .toArray();

    // Calculate similarity scores
    const scored: ScoredGame[] = [];

    for (const game of candidates) {
      const id = game._id.toString();
      if (excludeGameIds.has(id)) continue;

      const score = this.calculateSimilarity(profile, game);
      if (score > 0) {
        scored.push({ gameId: game._id, score });
      }
    }

    // Sort by score descending
    scored.sort((a, b) => b.score - a.score);

    return scored.slice(0, limit);
  }

  private buildUserProfile(
    games: Game[],
    ratings: UserRating[]
  ): UserProfile {
    // Create rating lookup
    const ratingMap = new Map<string, number>();
    for (const r of ratings) {
      ratingMap.set(r.gameId.toString(), r.rating);
    }

    const categories = new Map<string, number>();
    const mechanics = new Map<string, number>();

    let totalWeight = 0;
    let sumMinPlayers = 0,
      sumMaxPlayers = 0;
    let sumMinPlaytime = 0,
      sumMaxPlaytime = 0;
    let sumComplexity = 0;
    let countPlayers = 0,
      countPlaytime = 0,
      countComplexity = 0;

    for (const game of games) {
      const rating = ratingMap.get(game._id.toString()) || 5;
      const weight = rating / 10; // Normalize to 0-1

      // Accumulate category weights
      for (const cat of game.categories || []) {
        categories.set(cat, (categories.get(cat) || 0) + weight);
      }

      // Accumulate mechanic weights
      for (const mech of game.mechanics || []) {
        mechanics.set(mech, (mechanics.get(mech) || 0) + weight);
      }

      // Accumulate numeric features
      if (game.minPlayers != null && game.maxPlayers != null) {
        sumMinPlayers += game.minPlayers * weight;
        sumMaxPlayers += game.maxPlayers * weight;
        countPlayers += weight;
      }

      if (game.minPlaytime != null && game.maxPlaytime != null) {
        sumMinPlaytime += game.minPlaytime * weight;
        sumMaxPlaytime += game.maxPlaytime * weight;
        countPlaytime += weight;
      }

      if (game.complexity != null) {
        sumComplexity += game.complexity * weight;
        countComplexity += weight;
      }

      totalWeight += weight;
    }

    // Normalize weights
    for (const [key, value] of categories) {
      categories.set(key, value / totalWeight);
    }
    for (const [key, value] of mechanics) {
      mechanics.set(key, value / totalWeight);
    }

    return {
      categories,
      mechanics,
      avgMinPlayers: countPlayers > 0 ? sumMinPlayers / countPlayers : 2,
      avgMaxPlayers: countPlayers > 0 ? sumMaxPlayers / countPlayers : 4,
      avgMinPlaytime: countPlaytime > 0 ? sumMinPlaytime / countPlaytime : 60,
      avgMaxPlaytime: countPlaytime > 0 ? sumMaxPlaytime / countPlaytime : 90,
      avgComplexity: countComplexity > 0 ? sumComplexity / countComplexity : 2.5,
    };
  }

  private calculateSimilarity(profile: UserProfile, game: Game): number {
    let score = 0;

    // Category similarity (Jaccard-weighted)
    let catScore = 0;
    for (const cat of game.categories || []) {
      if (profile.categories.has(cat)) {
        catScore += profile.categories.get(cat)!;
      }
    }
    score += catScore * WEIGHTS.categories;

    // Mechanic similarity
    let mechScore = 0;
    for (const mech of game.mechanics || []) {
      if (profile.mechanics.has(mech)) {
        mechScore += profile.mechanics.get(mech)!;
      }
    }
    score += mechScore * WEIGHTS.mechanics;

    // Player count similarity (inverse distance)
    if (game.minPlayers != null && game.maxPlayers != null) {
      const playerDist =
        Math.abs(game.minPlayers - profile.avgMinPlayers) +
        Math.abs(game.maxPlayers - profile.avgMaxPlayers);
      const playerSim = Math.max(0, 1 - playerDist / 10);
      score += playerSim * WEIGHTS.players;
    }

    // Playtime similarity
    if (game.minPlaytime != null && game.maxPlaytime != null) {
      const timeDist =
        Math.abs(game.minPlaytime - profile.avgMinPlaytime) +
        Math.abs(game.maxPlaytime - profile.avgMaxPlaytime);
      const timeSim = Math.max(0, 1 - timeDist / 200);
      score += timeSim * WEIGHTS.playtime;
    }

    // Complexity similarity
    if (game.complexity != null) {
      const complexityDist = Math.abs(game.complexity - profile.avgComplexity);
      const complexitySim = Math.max(0, 1 - complexityDist / 2.5);
      score += complexitySim * WEIGHTS.complexity;
    }

    return score;
  }
}
