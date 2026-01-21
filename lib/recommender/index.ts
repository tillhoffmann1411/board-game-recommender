/**
 * Recommendation Engine Module
 *
 * Main entry point for generating and caching recommendations.
 * Provides a unified interface to all recommendation algorithms.
 */

import { ObjectId } from "mongodb";
import { getDb } from "@/lib/db/client";
import { COLLECTIONS } from "@/lib/db/schema";
import type { Rating, Recommendation, Game } from "@/lib/db/schema";
import type {
  AlgorithmType,
  RecommendationEngine,
  ScoredGame,
  UserRating,
  RecommendationResult,
} from "./types";

import { PopularityEngine } from "./popularity";
import { ContentBasedEngine } from "./content-based";
import { CollaborativeEngine } from "./collaborative";
import { KnnEngine } from "./knn";

// Engine instances
const engines: Record<AlgorithmType, RecommendationEngine> = {
  popularity: new PopularityEngine(),
  "content-based": new ContentBasedEngine(),
  collaborative: new CollaborativeEngine(),
  knn: new KnnEngine(),
};

// Cache TTL in hours
const CACHE_TTL = 24;

/**
 * Get recommendations for a user using the specified algorithm.
 * Results are cached in MongoDB with automatic TTL expiration.
 */
export async function getRecommendations(
  userId: ObjectId,
  algorithm: AlgorithmType,
  limit: number = 50,
  forceRefresh: boolean = false
): Promise<RecommendationResult> {
  const db = await getDb();

  // Check cache first (unless force refresh)
  if (!forceRefresh) {
    const cached = await db
      .collection<Recommendation>(COLLECTIONS.RECOMMENDATIONS)
      .findOne({
        userId,
        algorithm,
        expiresAt: { $gt: new Date() },
      });

    if (cached) {
      return {
        algorithm,
        recommendations: cached.games.slice(0, limit).map((g) => ({
          gameId: g.gameId,
          score: g.score,
        })),
        generatedAt: cached.generatedAt,
        inputRatingCount: cached.inputRatingCount,
      };
    }
  }

  // Get user's ratings
  const ratings = await db
    .collection<Rating>(COLLECTIONS.RATINGS)
    .find({ userId })
    .toArray();

  const userRatings: UserRating[] = ratings.map((r) => ({
    gameId: r.gameId,
    rating: r.rating,
  }));

  // Build exclusion set (games already rated)
  const excludeGameIds = new Set(ratings.map((r) => r.gameId.toString()));

  // Get recommendations from engine
  const engine = engines[algorithm];
  const recommendations = await engine.recommend(
    userId,
    userRatings,
    excludeGameIds,
    Math.max(limit, 100) // Cache more than requested
  );

  const now = new Date();
  const expiresAt = new Date(now.getTime() + CACHE_TTL * 60 * 60 * 1000);

  // Cache results with rank
  const cachedGames = recommendations.map((r, index) => ({
    gameId: r.gameId,
    score: r.score,
    rank: index + 1,
  }));

  // Upsert cache entry
  await db.collection<Recommendation>(COLLECTIONS.RECOMMENDATIONS).updateOne(
    { userId, algorithm },
    {
      $set: {
        games: cachedGames,
        generatedAt: now,
        expiresAt,
        inputRatingCount: userRatings.length,
      },
    },
    { upsert: true }
  );

  return {
    algorithm,
    recommendations: recommendations.slice(0, limit),
    generatedAt: now,
    inputRatingCount: userRatings.length,
  };
}

/**
 * Get recommendations with full game details.
 */
export async function getRecommendationsWithDetails(
  userId: ObjectId,
  algorithm: AlgorithmType,
  limit: number = 20
): Promise<{
  algorithm: AlgorithmType;
  games: Array<Game & { score: number; rank: number }>;
  generatedAt: Date;
  inputRatingCount: number;
}> {
  const result = await getRecommendations(userId, algorithm, limit);

  if (result.recommendations.length === 0) {
    return {
      algorithm,
      games: [],
      generatedAt: result.generatedAt,
      inputRatingCount: result.inputRatingCount,
    };
  }

  const db = await getDb();
  const gameIds = result.recommendations.map((r) => r.gameId);

  const games = await db
    .collection<Game>(COLLECTIONS.GAMES)
    .find({ _id: { $in: gameIds } })
    .toArray();

  // Create lookup for quick access
  const gameMap = new Map<string, Game>();
  for (const game of games) {
    gameMap.set(game._id.toString(), game);
  }

  // Merge scores and ranks with game details
  const gamesWithScores = result.recommendations
    .map((r, index) => {
      const game = gameMap.get(r.gameId.toString());
      if (!game) return null;
      return {
        ...game,
        score: r.score,
        rank: index + 1,
      };
    })
    .filter((g): g is Game & { score: number; rank: number } => g !== null);

  return {
    algorithm,
    games: gamesWithScores,
    generatedAt: result.generatedAt,
    inputRatingCount: result.inputRatingCount,
  };
}

/**
 * Invalidate cached recommendations for a user.
 * Call this when the user's ratings change.
 */
export async function invalidateCache(userId: ObjectId): Promise<void> {
  const db = await getDb();
  await db
    .collection<Recommendation>(COLLECTIONS.RECOMMENDATIONS)
    .deleteMany({ userId });
}

/**
 * Pre-compute recommendations for a user across all relevant algorithms.
 * Call this after rating changes to ensure fresh recommendations are ready.
 * Runs in background - does not block the caller.
 */
export async function precomputeRecommendations(userId: ObjectId): Promise<void> {
  // Get user's rating count to determine which algorithms to run
  const db = await getDb();
  const ratingCount = await db
    .collection<Rating>(COLLECTIONS.RATINGS)
    .countDocuments({ userId });

  // Determine which algorithms to pre-compute based on rating count
  const algorithmsToRun: AlgorithmType[] = ["popularity"];

  if (ratingCount >= 1) {
    algorithmsToRun.push("content-based");
  }
  if (ratingCount >= 3) {
    algorithmsToRun.push("collaborative", "knn");
  }

  // Run all algorithms in parallel (fire and forget style, but we await to ensure completion)
  await Promise.all(
    algorithmsToRun.map((algorithm) =>
      getRecommendations(userId, algorithm, 50, true).catch((err) => {
        console.error(`Failed to precompute ${algorithm} recommendations:`, err);
      })
    )
  );
}

/**
 * Get available algorithms with descriptions.
 */
export function getAvailableAlgorithms(): Array<{
  id: AlgorithmType;
  name: string;
  description: string;
  minRatings: number;
}> {
  return [
    {
      id: "popularity",
      name: "Popular Games",
      description: "Top-rated games by the community. Great for new users.",
      minRatings: 0,
    },
    {
      id: "content-based",
      name: "Content Match",
      description:
        "Games similar to ones you rated highly (categories, mechanics).",
      minRatings: 1,
    },
    {
      id: "collaborative",
      name: "Similar Users",
      description: "Games liked by users with similar taste.",
      minRatings: 3,
    },
    {
      id: "knn",
      name: "Item Similarity",
      description: "Predictions based on similar games you've rated.",
      minRatings: 3,
    },
  ];
}

// Re-export types
export type { AlgorithmType, ScoredGame, UserRating, RecommendationResult };
