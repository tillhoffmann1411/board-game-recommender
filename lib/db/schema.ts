/**
 * MongoDB Schema Types for Board Game Recommender
 *
 * Collections:
 * - games: Board game catalog with metadata
 * - users: User profiles linked to Clerk auth
 * - ratings: User game ratings (separate for query efficiency)
 * - recommendations: Cached recommendation results
 * - gameSimilarities: Precomputed item-item similarity matrix
 * - onlineGames: Links to online versions (Tabletopia, Board Game Arena, etc.)
 */

import { ObjectId } from "mongodb";

// ============================================================================
// GAMES COLLECTION
// ============================================================================

export interface Game {
  _id: ObjectId;

  // Identifiers
  bggId: number | null; // Board Game Geek ID

  // Core info
  name: string;
  description: string | null;
  yearPublished: number | null;

  // Player info
  minPlayers: number | null;
  maxPlayers: number | null;

  // Time info
  minPlaytime: number | null; // minutes
  maxPlaytime: number | null; // minutes

  // Complexity
  minAge: number | null;
  complexity: number | null; // BGG weight, 1-5 scale

  // Images
  thumbnailUrl: string | null;
  imageUrl: string | null;

  // Denormalized arrays (embedded for query performance)
  categories: string[];
  mechanics: string[];
  designers: Designer[];
  publishers: Publisher[];

  // Ratings from external sources
  bggRating: ExternalRating | null;

  // Additional metadata
  officialUrl: string | null;
  priceUs: number | null;

  // Rankings
  bggRank: number | null;

  // Timestamps
  createdAt: Date;
  updatedAt: Date;
}

export interface Designer {
  id: string;
  name: string;
  url?: string;
  imageUrl?: string;
}

export interface Publisher {
  id: string;
  name: string;
  url?: string;
  imageUrl?: string;
}

export interface ExternalRating {
  average: number;
  count: number;
  stddev?: number;
  bayesAverage?: number;
}

// ============================================================================
// USERS COLLECTION
// ============================================================================

export interface User {
  _id: ObjectId;

  // Clerk integration
  clerkId: string; // Clerk user ID (unique)

  // Profile
  username: string | null;
  displayName: string | null;

  // Stats (denormalized for quick access)
  ratingCount: number;

  // Preferences (learned from ratings)
  preferences: UserPreferences | null;

  // Timestamps
  createdAt: Date;
  updatedAt: Date;
}

export interface UserPreferences {
  favoriteCategories: string[];
  favoriteMechanics: string[];
  averageComplexity: number | null;
  preferredPlayerCount: number | null;
}

// ============================================================================
// RATINGS COLLECTION
// ============================================================================

export interface Rating {
  _id: ObjectId;

  // References
  userId: ObjectId; // ref: users._id
  gameId: ObjectId; // ref: games._id

  // Rating data
  rating: number; // 1-10 scale

  // Origin tracking (for imported vs user-created)
  origin: "app" | "bgg";

  // Timestamps
  createdAt: Date;
  updatedAt: Date;
}

// ============================================================================
// RECOMMENDATIONS COLLECTION
// ============================================================================

export type RecommendationAlgorithm =
  | "collaborative"
  | "content-based"
  | "knn"
  | "popularity"
  | "hybrid";

export interface Recommendation {
  _id: ObjectId;

  // Reference
  userId: ObjectId; // ref: users._id

  // Algorithm used
  algorithm: RecommendationAlgorithm;

  // Results
  games: RecommendedGame[];

  // Cache control
  generatedAt: Date;
  expiresAt: Date;

  // Metadata
  inputRatingCount: number; // ratings used to generate
}

export interface RecommendedGame {
  gameId: ObjectId; // ref: games._id
  score: number; // algorithm-specific score
  rank: number; // position in recommendation list
}

// ============================================================================
// GAME SIMILARITIES COLLECTION
// ============================================================================

export interface GameSimilarity {
  _id: ObjectId;

  // Reference game
  gameId: ObjectId; // ref: games._id

  // Similar games (sorted by similarity descending)
  similarGames: SimilarGame[];

  // Metadata
  computedAt: Date;
}

export interface SimilarGame {
  gameId: ObjectId; // ref: games._id
  similarity: number; // 0-1 score
}

// ============================================================================
// ONLINE GAMES COLLECTION
// ============================================================================

export type OnlineGamePlatform =
  | "tabletopia"
  | "board-game-arena"
  | "yucata"
  | "other";

export interface OnlineGame {
  _id: ObjectId;

  // Reference to physical game
  gameId: ObjectId | null; // ref: games._id (null if unmatched)
  bggId: number | null;

  // Online game info
  name: string;
  url: string;
  platform: OnlineGamePlatform;

  // Timestamps
  createdAt: Date;
  updatedAt: Date;
}

// ============================================================================
// INDEX DEFINITIONS
// ============================================================================

/**
 * Recommended indexes for each collection.
 * These should be created during database initialization.
 */
export const INDEXES = {
  games: [
    { key: { bggId: 1 }, unique: true, sparse: true },
    { key: { name: "text", description: "text" } }, // text search
    { key: { categories: 1 } },
    { key: { mechanics: 1 } },
    { key: { "bggRating.average": -1 } },
    { key: { bggRank: 1 } },
    { key: { complexity: 1 } },
    { key: { minPlayers: 1, maxPlayers: 1 } },
    { key: { updatedAt: -1 } },
  ],

  users: [
    { key: { clerkId: 1 }, unique: true },
    { key: { username: 1 }, sparse: true },
  ],

  ratings: [
    { key: { userId: 1, gameId: 1 }, unique: true }, // one rating per user per game
    { key: { userId: 1 } },
    { key: { gameId: 1 } },
    { key: { userId: 1, createdAt: -1 } }, // user's recent ratings
    { key: { gameId: 1, rating: -1 } }, // game's top ratings
  ],

  recommendations: [
    { key: { userId: 1, algorithm: 1 }, unique: true },
    { key: { expiresAt: 1 }, expireAfterSeconds: 0 }, // TTL index
  ],

  gameSimilarities: [{ key: { gameId: 1 }, unique: true }],

  onlineGames: [
    { key: { gameId: 1 } },
    { key: { bggId: 1 } },
    { key: { platform: 1 } },
  ],
} as const;

// ============================================================================
// COLLECTION NAMES
// ============================================================================

export const COLLECTIONS = {
  GAMES: "games",
  USERS: "users",
  RATINGS: "ratings",
  RECOMMENDATIONS: "recommendations",
  GAME_SIMILARITIES: "gameSimilarities",
  ONLINE_GAMES: "onlineGames",
} as const;

// ============================================================================
// HELPER TYPES
// ============================================================================

/** Input type for creating a new game (without _id and timestamps) */
export type CreateGameInput = Omit<Game, "_id" | "createdAt" | "updatedAt">;

/** Input type for creating a new rating */
export type CreateRatingInput = Omit<
  Rating,
  "_id" | "createdAt" | "updatedAt"
>;

/** Input type for creating a new user */
export type CreateUserInput = Omit<User, "_id" | "createdAt" | "updatedAt">;

/** Game with computed popularity score */
export interface GameWithPopularity extends Game {
  popularityScore: number;
}

/** Partial game for list views (lighter payload) */
export type GameSummary = Pick<
  Game,
  | "_id"
  | "name"
  | "imageUrl"
  | "yearPublished"
  | "minPlayers"
  | "maxPlayers"
  | "minPlaytime"
  | "maxPlaytime"
  | "complexity"
  | "bggRating"
  | "categories"
>;
