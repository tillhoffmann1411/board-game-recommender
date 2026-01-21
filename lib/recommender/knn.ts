/**
 * KNN with Item Similarity Recommendation Engine
 *
 * Uses precomputed game-to-game similarity matrix to predict ratings.
 * For each unrated game, finds the k most similar games the user has
 * rated and calculates a weighted average prediction.
 *
 * Ported from: _archive/recommendation-algorithms/knn_selfmade.py
 */

import { ObjectId } from "mongodb";
import { getDb } from "@/lib/db/client";
import { COLLECTIONS } from "@/lib/db/schema";
import type { Game, GameSimilarity } from "@/lib/db/schema";
import type { RecommendationEngine, ScoredGame, UserRating } from "./types";

// Algorithm parameters
const K = 40; // Maximum neighbors to consider
const MIN_K = 5; // Minimum neighbors needed for valid prediction

export class KnnEngine implements RecommendationEngine {
  name = "knn" as const;

  async recommend(
    _userId: ObjectId,
    userRatings: UserRating[],
    excludeGameIds: Set<string>,
    limit: number
  ): Promise<ScoredGame[]> {
    // Need at least a few ratings
    if (userRatings.length < 3) {
      return [];
    }

    const db = await getDb();

    // Get the rated game IDs
    const ratedGameIds = userRatings.map((r) => r.gameId);

    // Fetch similarities for all rated games
    const similarities = await db
      .collection<GameSimilarity>(COLLECTIONS.GAME_SIMILARITIES)
      .find({ gameId: { $in: ratedGameIds } })
      .toArray();

    if (similarities.length === 0) {
      return [];
    }

    // Build similarity lookup: Map<ratedGameId, Map<candidateGameId, similarity>>
    const simLookup = new Map<string, Map<string, number>>();
    const candidateGameIds = new Set<string>();

    for (const sim of similarities) {
      const ratedId = sim.gameId.toString();
      if (!simLookup.has(ratedId)) {
        simLookup.set(ratedId, new Map());
      }
      const simMap = simLookup.get(ratedId)!;

      for (const { gameId, similarity } of sim.similarGames) {
        const candId = gameId.toString();
        simMap.set(candId, similarity);
        candidateGameIds.add(candId);
      }
    }

    // Get average ratings for all candidate games (for baseline)
    const candidateIds = Array.from(candidateGameIds).map(
      (id) => new ObjectId(id)
    );
    const games = await db
      .collection<Game>(COLLECTIONS.GAMES)
      .find(
        { _id: { $in: candidateIds } },
        { projection: { _id: 1, "bggRating.average": 1 } }
      )
      .toArray();

    const gameMeans = new Map<string, number>();
    for (const game of games) {
      const avg = game.bggRating?.average ?? 6.5; // Default to middle rating
      gameMeans.set(game._id.toString(), avg);
    }

    // Also get means for rated games
    const ratedGames = await db
      .collection<Game>(COLLECTIONS.GAMES)
      .find(
        { _id: { $in: ratedGameIds } },
        { projection: { _id: 1, "bggRating.average": 1 } }
      )
      .toArray();

    for (const game of ratedGames) {
      const avg = game.bggRating?.average ?? 6.5;
      gameMeans.set(game._id.toString(), avg);
    }

    // Create rating lookup for user's ratings
    const userRatingMap = new Map<string, number>();
    for (const r of userRatings) {
      userRatingMap.set(r.gameId.toString(), r.rating);
    }

    // For each candidate game, predict rating
    const predictions: ScoredGame[] = [];

    for (const candId of candidateGameIds) {
      // Skip already rated games
      if (userRatingMap.has(candId)) continue;
      // Skip excluded games
      if (excludeGameIds.has(candId)) continue;

      const prediction = this.predictRating(
        candId,
        userRatings,
        simLookup,
        gameMeans
      );

      if (prediction !== null) {
        // Normalize to 0-1 for consistency
        const score = prediction / 10;
        predictions.push({ gameId: new ObjectId(candId), score });
      }
    }

    // Sort by predicted score descending
    predictions.sort((a, b) => b.score - a.score);

    return predictions.slice(0, limit);
  }

  private predictRating(
    targetGameId: string,
    userRatings: UserRating[],
    simLookup: Map<string, Map<string, number>>,
    gameMeans: Map<string, number>
  ): number | null {
    // Get similarities from rated games to target game
    const neighbors: Array<{
      ratedGameId: string;
      similarity: number;
      rating: number;
    }> = [];

    for (const r of userRatings) {
      const ratedId = r.gameId.toString();
      const simMap = simLookup.get(ratedId);
      if (!simMap) continue;

      const similarity = simMap.get(targetGameId);
      if (similarity !== undefined && similarity > 0) {
        neighbors.push({
          ratedGameId: ratedId,
          similarity,
          rating: r.rating,
        });
      }
    }

    // Sort by similarity and take top k
    neighbors.sort((a, b) => b.similarity - a.similarity);
    const kNeighbors = neighbors.slice(0, K);

    // Start with baseline (average rating for target game)
    const baseline = gameMeans.get(targetGameId) ?? 6.5;

    // Calculate weighted average adjustment
    let sumSim = 0;
    let sumWeightedDiff = 0;
    let actualK = 0;

    for (const { ratedGameId, similarity, rating } of kNeighbors) {
      if (similarity > 0) {
        const ratedMean = gameMeans.get(ratedGameId) ?? 6.5;
        sumSim += similarity;
        sumWeightedDiff += similarity * (rating - ratedMean);
        actualK++;
      }
    }

    // If not enough neighbors, return null (skip this game)
    if (actualK < MIN_K) {
      return null;
    }

    // Compute prediction
    let prediction = baseline;
    if (sumSim > 0) {
      prediction += sumWeightedDiff / sumSim;
    }

    // Clamp to valid range
    return Math.max(1, Math.min(10, prediction));
  }
}
