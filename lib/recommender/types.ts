/**
 * Recommendation Engine Types
 */

import { ObjectId } from "mongodb";

export type AlgorithmType =
  | "popularity"
  | "content-based"
  | "collaborative"
  | "knn";

export interface UserRating {
  gameId: ObjectId;
  rating: number;
}

export interface GameFeatures {
  gameId: ObjectId;
  name: string;
  categories: string[];
  mechanics: string[];
  minPlayers: number | null;
  maxPlayers: number | null;
  minPlaytime: number | null;
  maxPlaytime: number | null;
  complexity: number | null;
  bggRating: number | null;
  bggRatingCount: number | null;
}

export interface ScoredGame {
  gameId: ObjectId;
  score: number;
}

export interface RecommendationResult {
  algorithm: AlgorithmType;
  recommendations: ScoredGame[];
  generatedAt: Date;
  inputRatingCount: number;
}

export interface RecommendationEngine {
  name: AlgorithmType;
  recommend(
    userId: ObjectId,
    userRatings: UserRating[],
    excludeGameIds: Set<string>,
    limit: number
  ): Promise<ScoredGame[]>;
}

export const CACHE_TTL_HOURS = 24;
