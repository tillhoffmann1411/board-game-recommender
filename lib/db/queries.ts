/**
 * Database Query Functions
 *
 * Type-safe query functions for all collections.
 */

import { ObjectId, Filter, Sort, UpdateFilter } from "mongodb";
import { getDb } from "./client";
import {
  COLLECTIONS,
  Game,
  User,
  Rating,
  Recommendation,
  GameSimilarity,
  OnlineGame,
  CreateGameInput,
  CreateRatingInput,
  CreateUserInput,
  GameSummary,
  RecommendationAlgorithm,
} from "./schema";

// ============================================================================
// GAMES
// ============================================================================

export async function findGameById(id: ObjectId): Promise<Game | null> {
  const db = await getDb();
  return db.collection<Game>(COLLECTIONS.GAMES).findOne({ _id: id });
}

export async function findGameByBggId(bggId: number): Promise<Game | null> {
  const db = await getDb();
  return db.collection<Game>(COLLECTIONS.GAMES).findOne({ bggId });
}

export async function searchGames(
  query: string,
  limit = 20
): Promise<GameSummary[]> {
  const db = await getDb();
  return db
    .collection<Game>(COLLECTIONS.GAMES)
    .find(
      { $text: { $search: query } },
      {
        projection: {
          _id: 1,
          name: 1,
          imageUrl: 1,
          yearPublished: 1,
          minPlayers: 1,
          maxPlayers: 1,
          minPlaytime: 1,
          maxPlaytime: 1,
          complexity: 1,
          bggRating: 1,
          categories: 1,
        },
      }
    )
    .sort({ score: { $meta: "textScore" } })
    .limit(limit)
    .toArray() as Promise<GameSummary[]>;
}

export async function findGames(options: {
  filter?: Filter<Game>;
  sort?: Sort;
  skip?: number;
  limit?: number;
}): Promise<Game[]> {
  const db = await getDb();
  const { filter = {}, sort = { "bggRating.average": -1 }, skip = 0, limit = 50 } = options;

  return db
    .collection<Game>(COLLECTIONS.GAMES)
    .find(filter)
    .sort(sort)
    .skip(skip)
    .limit(limit)
    .toArray();
}

export async function countGames(filter: Filter<Game> = {}): Promise<number> {
  const db = await getDb();
  return db.collection<Game>(COLLECTIONS.GAMES).countDocuments(filter);
}

export async function insertGame(game: CreateGameInput): Promise<ObjectId> {
  const db = await getDb();
  const now = new Date();
  const result = await db.collection<Game>(COLLECTIONS.GAMES).insertOne({
    ...game,
    _id: new ObjectId(),
    createdAt: now,
    updatedAt: now,
  } as Game);
  return result.insertedId;
}

export async function insertManyGames(
  games: CreateGameInput[]
): Promise<ObjectId[]> {
  const db = await getDb();
  const now = new Date();
  const docs = games.map((game) => ({
    ...game,
    _id: new ObjectId(),
    createdAt: now,
    updatedAt: now,
  })) as Game[];

  const result = await db.collection<Game>(COLLECTIONS.GAMES).insertMany(docs);
  return Object.values(result.insertedIds);
}

export async function updateGame(
  id: ObjectId,
  update: UpdateFilter<Game>
): Promise<boolean> {
  const db = await getDb();
  const result = await db.collection<Game>(COLLECTIONS.GAMES).updateOne(
    { _id: id },
    {
      ...update,
      $set: { ...(update.$set || {}), updatedAt: new Date() },
    }
  );
  return result.modifiedCount > 0;
}

// ============================================================================
// USERS
// ============================================================================

export async function findUserById(id: ObjectId): Promise<User | null> {
  const db = await getDb();
  return db.collection<User>(COLLECTIONS.USERS).findOne({ _id: id });
}

export async function findUserByClerkId(clerkId: string): Promise<User | null> {
  const db = await getDb();
  return db.collection<User>(COLLECTIONS.USERS).findOne({ clerkId });
}

export async function createUser(user: CreateUserInput): Promise<ObjectId> {
  const db = await getDb();
  const now = new Date();
  const result = await db.collection<User>(COLLECTIONS.USERS).insertOne({
    ...user,
    _id: new ObjectId(),
    createdAt: now,
    updatedAt: now,
  } as User);
  return result.insertedId;
}

export async function upsertUserByClerkId(
  clerkId: string,
  data: Partial<Omit<User, "_id" | "clerkId" | "createdAt">>
): Promise<ObjectId> {
  const db = await getDb();
  const now = new Date();

  const result = await db.collection<User>(COLLECTIONS.USERS).findOneAndUpdate(
    { clerkId },
    {
      $set: { ...data, updatedAt: now },
      $setOnInsert: { clerkId, createdAt: now },
    },
    { upsert: true, returnDocument: "after" }
  );

  return result!._id;
}

export async function incrementUserRatingCount(
  userId: ObjectId,
  delta: number
): Promise<void> {
  const db = await getDb();
  await db.collection<User>(COLLECTIONS.USERS).updateOne(
    { _id: userId },
    {
      $inc: { ratingCount: delta },
      $set: { updatedAt: new Date() },
    }
  );
}

// ============================================================================
// RATINGS
// ============================================================================

export async function findRatingsByUser(
  userId: ObjectId,
  options: { skip?: number; limit?: number } = {}
): Promise<Rating[]> {
  const db = await getDb();
  const { skip = 0, limit = 100 } = options;

  return db
    .collection<Rating>(COLLECTIONS.RATINGS)
    .find({ userId })
    .sort({ createdAt: -1 })
    .skip(skip)
    .limit(limit)
    .toArray();
}

export async function findRatingByUserAndGame(
  userId: ObjectId,
  gameId: ObjectId
): Promise<Rating | null> {
  const db = await getDb();
  return db.collection<Rating>(COLLECTIONS.RATINGS).findOne({ userId, gameId });
}

export async function countRatingsByUser(userId: ObjectId): Promise<number> {
  const db = await getDb();
  return db.collection<Rating>(COLLECTIONS.RATINGS).countDocuments({ userId });
}

export async function upsertRating(
  rating: CreateRatingInput
): Promise<ObjectId> {
  const db = await getDb();
  const now = new Date();

  const result = await db
    .collection<Rating>(COLLECTIONS.RATINGS)
    .findOneAndUpdate(
      { userId: rating.userId, gameId: rating.gameId },
      {
        $set: { rating: rating.rating, origin: rating.origin, updatedAt: now },
        $setOnInsert: { createdAt: now },
      },
      { upsert: true, returnDocument: "after" }
    );

  return result!._id;
}

export async function deleteRating(
  userId: ObjectId,
  gameId: ObjectId
): Promise<boolean> {
  const db = await getDb();
  const result = await db
    .collection<Rating>(COLLECTIONS.RATINGS)
    .deleteOne({ userId, gameId });
  return result.deletedCount > 0;
}

export async function findAllRatingsForAlgorithm(
  minRatingsPerUser = 5
): Promise<Rating[]> {
  const db = await getDb();

  // Get users with enough ratings
  const userCounts = await db
    .collection<Rating>(COLLECTIONS.RATINGS)
    .aggregate<{ _id: ObjectId; count: number }>([
      { $group: { _id: "$userId", count: { $sum: 1 } } },
      { $match: { count: { $gte: minRatingsPerUser } } },
    ])
    .toArray();

  const validUserIds = userCounts.map((u) => u._id);

  return db
    .collection<Rating>(COLLECTIONS.RATINGS)
    .find({ userId: { $in: validUserIds } })
    .toArray();
}

// ============================================================================
// RECOMMENDATIONS
// ============================================================================

export async function findRecommendation(
  userId: ObjectId,
  algorithm: RecommendationAlgorithm
): Promise<Recommendation | null> {
  const db = await getDb();
  return db
    .collection<Recommendation>(COLLECTIONS.RECOMMENDATIONS)
    .findOne({ userId, algorithm, expiresAt: { $gt: new Date() } });
}

export async function saveRecommendation(
  recommendation: Omit<Recommendation, "_id">
): Promise<ObjectId> {
  const db = await getDb();

  const result = await db
    .collection<Recommendation>(COLLECTIONS.RECOMMENDATIONS)
    .findOneAndUpdate(
      { userId: recommendation.userId, algorithm: recommendation.algorithm },
      { $set: recommendation },
      { upsert: true, returnDocument: "after" }
    );

  return result!._id;
}

export async function deleteExpiredRecommendations(): Promise<number> {
  const db = await getDb();
  const result = await db
    .collection<Recommendation>(COLLECTIONS.RECOMMENDATIONS)
    .deleteMany({ expiresAt: { $lt: new Date() } });
  return result.deletedCount;
}

// ============================================================================
// GAME SIMILARITIES
// ============================================================================

export async function findSimilarGames(
  gameId: ObjectId,
  limit = 20
): Promise<GameSimilarity | null> {
  const db = await getDb();
  const similarity = await db
    .collection<GameSimilarity>(COLLECTIONS.GAME_SIMILARITIES)
    .findOne({ gameId });

  if (similarity) {
    similarity.similarGames = similarity.similarGames.slice(0, limit);
  }

  return similarity;
}

export async function upsertGameSimilarity(
  gameId: ObjectId,
  similarGames: { gameId: ObjectId; similarity: number }[]
): Promise<void> {
  const db = await getDb();
  await db
    .collection<GameSimilarity>(COLLECTIONS.GAME_SIMILARITIES)
    .updateOne(
      { gameId },
      { $set: { similarGames, computedAt: new Date() } },
      { upsert: true }
    );
}

// ============================================================================
// ONLINE GAMES
// ============================================================================

export async function findOnlineGamesByGameId(
  gameId: ObjectId
): Promise<OnlineGame[]> {
  const db = await getDb();
  return db
    .collection<OnlineGame>(COLLECTIONS.ONLINE_GAMES)
    .find({ gameId })
    .toArray();
}

export async function findOnlineGamesByBggId(
  bggId: number
): Promise<OnlineGame[]> {
  const db = await getDb();
  return db
    .collection<OnlineGame>(COLLECTIONS.ONLINE_GAMES)
    .find({ bggId })
    .toArray();
}
