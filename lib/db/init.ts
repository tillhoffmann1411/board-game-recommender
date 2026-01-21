/**
 * Database Initialization
 *
 * Creates collections and indexes for the board game recommender.
 * Run this script once when setting up a new database.
 */

import { Db, CreateIndexesOptions } from "mongodb";
import { getDb } from "./client";
import { COLLECTIONS, INDEXES } from "./schema";

interface IndexDefinition {
  key: Record<string, 1 | -1 | "text">;
  unique?: boolean;
  sparse?: boolean;
  expireAfterSeconds?: number;
}

/**
 * Initialize all collections and indexes
 */
export async function initializeDatabase(): Promise<void> {
  const db = await getDb();

  console.log("Initializing database...");

  // Create collections (MongoDB creates them automatically, but we want to be explicit)
  await createCollections(db);

  // Create indexes
  await createAllIndexes(db);

  console.log("Database initialization complete.");
}

/**
 * Create all collections if they don't exist
 */
async function createCollections(db: Db): Promise<void> {
  const existingCollections = await db.listCollections().toArray();
  const existingNames = new Set(existingCollections.map((c) => c.name));

  for (const collectionName of Object.values(COLLECTIONS)) {
    if (!existingNames.has(collectionName)) {
      await db.createCollection(collectionName);
      console.log(`Created collection: ${collectionName}`);
    } else {
      console.log(`Collection exists: ${collectionName}`);
    }
  }
}

/**
 * Create indexes for all collections
 */
async function createAllIndexes(db: Db): Promise<void> {
  // Games indexes
  await createIndexesForCollection(
    db,
    COLLECTIONS.GAMES,
    INDEXES.games as unknown as IndexDefinition[]
  );

  // Users indexes
  await createIndexesForCollection(
    db,
    COLLECTIONS.USERS,
    INDEXES.users as unknown as IndexDefinition[]
  );

  // Ratings indexes
  await createIndexesForCollection(
    db,
    COLLECTIONS.RATINGS,
    INDEXES.ratings as unknown as IndexDefinition[]
  );

  // Recommendations indexes
  await createIndexesForCollection(
    db,
    COLLECTIONS.RECOMMENDATIONS,
    INDEXES.recommendations as unknown as IndexDefinition[]
  );

  // Game similarities indexes
  await createIndexesForCollection(
    db,
    COLLECTIONS.GAME_SIMILARITIES,
    INDEXES.gameSimilarities as unknown as IndexDefinition[]
  );

  // Online games indexes
  await createIndexesForCollection(
    db,
    COLLECTIONS.ONLINE_GAMES,
    INDEXES.onlineGames as unknown as IndexDefinition[]
  );
}

/**
 * Create indexes for a specific collection
 */
async function createIndexesForCollection(
  db: Db,
  collectionName: string,
  indexes: IndexDefinition[]
): Promise<void> {
  const collection = db.collection(collectionName);

  for (const indexDef of indexes) {
    const options: CreateIndexesOptions = {};

    if (indexDef.unique) options.unique = true;
    if (indexDef.sparse) options.sparse = true;
    if (indexDef.expireAfterSeconds !== undefined) {
      options.expireAfterSeconds = indexDef.expireAfterSeconds;
    }

    try {
      const indexName = await collection.createIndex(indexDef.key, options);
      console.log(`Created index on ${collectionName}: ${indexName}`);
    } catch (error) {
      // Index might already exist
      if ((error as Error).message?.includes("already exists")) {
        console.log(
          `Index already exists on ${collectionName}: ${JSON.stringify(indexDef.key)}`
        );
      } else {
        throw error;
      }
    }
  }
}

/**
 * Drop all collections (use with caution!)
 */
export async function dropAllCollections(): Promise<void> {
  const db = await getDb();

  console.log("Dropping all collections...");

  for (const collectionName of Object.values(COLLECTIONS)) {
    try {
      await db.dropCollection(collectionName);
      console.log(`Dropped collection: ${collectionName}`);
    } catch {
      // Collection might not exist
      console.log(`Collection does not exist: ${collectionName}`);
    }
  }

  console.log("All collections dropped.");
}

/**
 * Get database statistics
 */
export async function getDatabaseStats(): Promise<Record<string, number>> {
  const db = await getDb();
  const stats: Record<string, number> = {};

  for (const collectionName of Object.values(COLLECTIONS)) {
    const count = await db.collection(collectionName).countDocuments();
    stats[collectionName] = count;
  }

  return stats;
}
