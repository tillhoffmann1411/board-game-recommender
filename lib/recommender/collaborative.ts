/**
 * Collaborative Filtering Recommendation Engine (User-Based)
 *
 * Finds users with similar rating patterns and recommends games
 * they liked. Uses centered cosine similarity to compare users.
 *
 * Ported from: _archive/recommendation-algorithms/collaborative_filtering_user_based.py
 */

import { ObjectId } from "mongodb";
import { getDb } from "@/lib/db/client";
import { COLLECTIONS } from "@/lib/db/schema";
import type { Rating } from "@/lib/db/schema";
import type { RecommendationEngine, ScoredGame, UserRating } from "./types";

// Algorithm parameters
const MIN_RATINGS_PER_GAME = 50; // Games need at least this many ratings
const SIMILAR_USER_PERCENTAGE = 0.2; // Take top 20% similar users
const MIN_RATINGS_IN_GROUP = 5; // Minimum ratings per game in similar user group

export class CollaborativeEngine implements RecommendationEngine {
  name = "collaborative" as const;

  async recommend(
    userId: ObjectId,
    userRatings: UserRating[],
    excludeGameIds: Set<string>,
    limit: number
  ): Promise<ScoredGame[]> {
    // Need at least a few ratings for collaborative filtering
    if (userRatings.length < 3) {
      return [];
    }

    const db = await getDb();

    // Get all ratings for games with sufficient rating count
    // This builds the utility matrix data
    const allRatings = await db
      .collection<Rating>(COLLECTIONS.RATINGS)
      .aggregate<{ userId: ObjectId; gameId: ObjectId; rating: number }>([
        {
          $group: {
            _id: "$gameId",
            count: { $sum: 1 },
            ratings: { $push: { userId: "$userId", rating: "$rating" } },
          },
        },
        { $match: { count: { $gte: MIN_RATINGS_PER_GAME } } },
        { $unwind: "$ratings" },
        {
          $project: {
            _id: 0,
            gameId: "$_id",
            userId: "$ratings.userId",
            rating: "$ratings.rating",
          },
        },
      ])
      .toArray();

    if (allRatings.length === 0) {
      return [];
    }

    // Build utility matrix: Map<userId, Map<gameId, rating>>
    const userRatingsMap = new Map<string, Map<string, number>>();
    const gameIds = new Set<string>();

    for (const r of allRatings) {
      const uid = r.userId.toString();
      const gid = r.gameId.toString();
      gameIds.add(gid);

      if (!userRatingsMap.has(uid)) {
        userRatingsMap.set(uid, new Map());
      }
      userRatingsMap.get(uid)!.set(gid, r.rating);
    }

    // Calculate mean rating for each user (for centered cosine)
    const userMeans = new Map<string, number>();
    for (const [uid, ratings] of userRatingsMap) {
      const values = Array.from(ratings.values());
      userMeans.set(uid, values.reduce((a, b) => a + b, 0) / values.length);
    }

    // Get target user's ratings vector
    const targetUserId = userId.toString();
    const targetRatings = new Map<string, number>();
    for (const r of userRatings) {
      const gid = r.gameId.toString();
      if (gameIds.has(gid)) {
        targetRatings.set(gid, r.rating);
      }
    }

    if (targetRatings.size === 0) {
      return [];
    }

    const targetMean =
      Array.from(targetRatings.values()).reduce((a, b) => a + b, 0) /
      targetRatings.size;

    // Calculate similarity with all other users
    const similarities: Array<{ userId: string; similarity: number }> = [];

    for (const [uid, ratings] of userRatingsMap) {
      if (uid === targetUserId) continue;

      const similarity = this.calculateCenteredCosineSimilarity(
        targetRatings,
        targetMean,
        ratings,
        userMeans.get(uid) || 0
      );

      if (similarity > 0) {
        similarities.push({ userId: uid, similarity });
      }
    }

    if (similarities.length === 0) {
      return [];
    }

    // Sort by similarity and take top percentage
    similarities.sort((a, b) => b.similarity - a.similarity);
    const numSimilarUsers = Math.max(
      1,
      Math.round(similarities.length * SIMILAR_USER_PERCENTAGE)
    );
    const similarUsers = similarities.slice(0, numSimilarUsers);

    // Get games rated by similar users but not by target user
    const gamePredictions = new Map<
      string,
      { sumRatings: number; count: number }
    >();

    for (const { userId: uid } of similarUsers) {
      const ratings = userRatingsMap.get(uid)!;
      for (const [gid, rating] of ratings) {
        if (targetRatings.has(gid)) continue; // Skip already rated
        if (excludeGameIds.has(gid)) continue; // Skip excluded

        if (!gamePredictions.has(gid)) {
          gamePredictions.set(gid, { sumRatings: 0, count: 0 });
        }
        const pred = gamePredictions.get(gid)!;
        pred.sumRatings += rating;
        pred.count += 1;
      }
    }

    // Calculate average rating per game (only if enough ratings)
    const scored: ScoredGame[] = [];

    for (const [gid, { sumRatings, count }] of gamePredictions) {
      if (count < MIN_RATINGS_IN_GROUP) continue;

      const avgRating = sumRatings / count;
      // Normalize to 0-1 range for consistency with other engines
      const score = avgRating / 10;

      scored.push({ gameId: new ObjectId(gid), score });
    }

    // Sort by score descending
    scored.sort((a, b) => b.score - a.score);

    return scored.slice(0, limit);
  }

  private calculateCenteredCosineSimilarity(
    ratingsA: Map<string, number>,
    meanA: number,
    ratingsB: Map<string, number>,
    meanB: number
  ): number {
    // Find common games
    const commonGames: string[] = [];
    for (const gid of ratingsA.keys()) {
      if (ratingsB.has(gid)) {
        commonGames.push(gid);
      }
    }

    if (commonGames.length < 2) {
      return 0;
    }

    // Calculate centered cosine similarity
    let dotProduct = 0;
    let normA = 0;
    let normB = 0;

    for (const gid of commonGames) {
      const a = ratingsA.get(gid)! - meanA;
      const b = ratingsB.get(gid)! - meanB;

      dotProduct += a * b;
      normA += a * a;
      normB += b * b;
    }

    const denominator = Math.sqrt(normA) * Math.sqrt(normB);
    if (denominator === 0) {
      return 0;
    }

    return dotProduct / denominator;
  }
}
