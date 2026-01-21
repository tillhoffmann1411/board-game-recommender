/**
 * Sync Games to Production Database
 *
 * This script:
 * 1. Exports games from local MongoDB (Docker)
 * 2. Ensures all collections exist in production database
 * 3. Imports/updates games in production (upsert based on bggId)
 */

import dotenv from "dotenv";
import { MongoClient, Db, AnyBulkWriteOperation, CreateIndexesOptions } from "mongodb";
import { COLLECTIONS, INDEXES } from "../lib/db/schema";

// Load environment variables from .env.local (fallback to .env)
dotenv.config({ path: ".env.local" });
dotenv.config(); // Fallback to .env

// Configuration
const LOCAL_MONGODB_URI = process.env.MONGODB_URI || "mongodb://localhost:27017";
const PROD_MONGODB_URI = process.env.MONGODB_URI_ATLAS;
const DATABASE_NAME = process.env.MONGODB_DB || "board-game-recommender";
const BATCH_SIZE = 1000;

if (!PROD_MONGODB_URI) {
  throw new Error(
    "MONGODB_URI environment variable is required for production database"
  );
}

/**
 * Get MongoDB client and database
 */
async function getDatabase(uri: string, dbName: string): Promise<{ client: MongoClient; db: Db }> {
  const client = new MongoClient(uri);
  await client.connect();
  const db = client.db(dbName);
  return { client, db };
}

/**
 * Export games from local MongoDB
 */
async function exportGamesFromLocal(): Promise<any[]> {
  console.log("📤 Exporting games from local MongoDB...");
  console.log(`   URI: ${LOCAL_MONGODB_URI}`);
  console.log(`   Database: ${DATABASE_NAME}`);

  const { client, db } = await getDatabase(LOCAL_MONGODB_URI, DATABASE_NAME);

  try {
    // Test connection
    await client.db("admin").command({ ping: 1 });

    const gamesCollection = db.collection(COLLECTIONS.GAMES);
    const games = await gamesCollection.find({}).toArray();

    // Warn about games without bggId
    const gamesWithoutBggId = games.filter((g) => !g.bggId);
    if (gamesWithoutBggId.length > 0) {
      console.warn(
        `   ⚠️  Warning: ${gamesWithoutBggId.length} games without bggId found`
      );
    }

    console.log(`   ✅ Exported ${games.length} games`);
    return games;
  } finally {
    await client.close();
  }
}

/**
 * Ensure all collections exist in production database
 */
async function ensureCollectionsExist(prodDb: Db): Promise<void> {
  console.log("\n📋 Ensuring all collections exist in production...");

  const existingCollections = await prodDb.listCollections().toArray();
  const existingNames = new Set(existingCollections.map((c) => c.name));

  for (const collectionName of Object.values(COLLECTIONS)) {
    if (!existingNames.has(collectionName)) {
      await prodDb.createCollection(collectionName);
      console.log(`   ✅ Created collection: ${collectionName}`);
    } else {
      console.log(`   ✓ Collection exists: ${collectionName}`);
    }
  }
}

/**
 * Import/update games in production database (upsert based on bggId)
 */
async function importGamesToProd(
  prodDb: Db,
  games: any[]
): Promise<{ inserted: number; updated: number; invalidCount: number }> {
  console.log("\n📥 Importing/updating games in production database...");
  console.log(`   Total games: ${games.length}`);

  const gamesCollection = prodDb.collection(COLLECTIONS.GAMES);
  let inserted = 0;
  let updated = 0;

  // Filter out games without bggId or _id (shouldn't happen, but be safe)
  const validGames = games.filter((game) => game.bggId || game._id);
  const invalidCount = games.length - validGames.length;

  if (invalidCount > 0) {
    console.warn(`   ⚠️  Skipping ${invalidCount} games without bggId or _id`);
  }

  // Process in batches
  for (let i = 0; i < validGames.length; i += BATCH_SIZE) {
    const batch = validGames.slice(i, i + BATCH_SIZE);
    const operations: AnyBulkWriteOperation<any>[] = [];

    for (const game of batch) {
      // Remove _id to avoid conflicts, MongoDB will generate a new one if needed
      const { _id, createdAt, updatedAt, ...gameData } = game;

      // Use bggId as the unique identifier for upsert
      // If bggId is null, use _id as fallback (though this shouldn't happen for games)
      const filter = game.bggId
        ? { bggId: game.bggId }
        : { _id: game._id };

      // Prepare update operation
      // $set: always update these fields
      // $setOnInsert: only set these when inserting (not updating)
      operations.push({
        updateOne: {
          filter,
          update: {
            $set: {
              ...gameData,
              updatedAt: new Date(),
            },
            $setOnInsert: {
              createdAt: createdAt || new Date(),
            },
          },
          upsert: true,
        },
      });
    }

    const result = await gamesCollection.bulkWrite(operations, {
      ordered: false, // Continue on errors
    });

    inserted += result.upsertedCount;
    updated += result.modifiedCount;

    console.log(
      `   Processed batch ${Math.floor(i / BATCH_SIZE) + 1}/${Math.ceil(validGames.length / BATCH_SIZE)}: ` +
      `${result.upsertedCount} inserted, ${result.modifiedCount} updated`
    );
  }

  return { inserted, updated, invalidCount };
}

/**
 * Initialize indexes in production database
 */
async function initializeIndexes(prodDb: Db): Promise<void> {
  console.log("\n🔧 Initializing indexes in production database...");

  interface IndexDefinition {
    key: Record<string, 1 | -1 | "text">;
    unique?: boolean;
    sparse?: boolean;
    expireAfterSeconds?: number;
  }

  // Create indexes for all collections
  const indexMappings: Record<string, IndexDefinition[]> = {
    [COLLECTIONS.GAMES]: INDEXES.games as unknown as IndexDefinition[],
    [COLLECTIONS.USERS]: INDEXES.users as unknown as IndexDefinition[],
    [COLLECTIONS.RATINGS]: INDEXES.ratings as unknown as IndexDefinition[],
    [COLLECTIONS.RECOMMENDATIONS]: INDEXES.recommendations as unknown as IndexDefinition[],
    [COLLECTIONS.GAME_SIMILARITIES]: INDEXES.gameSimilarities as unknown as IndexDefinition[],
    [COLLECTIONS.ONLINE_GAMES]: INDEXES.onlineGames as unknown as IndexDefinition[],
  };

  for (const [collectionName, indexes] of Object.entries(indexMappings)) {
    const collection = prodDb.collection(collectionName);

    for (const indexDef of indexes) {
      const options: CreateIndexesOptions = {};

      if (indexDef.unique) options.unique = true;
      if (indexDef.sparse) options.sparse = true;
      if (indexDef.expireAfterSeconds !== undefined) {
        options.expireAfterSeconds = indexDef.expireAfterSeconds;
      }

      try {
        const indexName = await collection.createIndex(indexDef.key, options);
        console.log(`   ✅ Created index on ${collectionName}: ${indexName}`);
      } catch (error) {
        // Index might already exist
        if ((error as Error).message?.includes("already exists")) {
          console.log(
            `   ✓ Index already exists on ${collectionName}: ${JSON.stringify(indexDef.key)}`
          );
        } else {
          console.warn(`   ⚠️  Failed to create index on ${collectionName}: ${error}`);
        }
      }
    }
  }
}

/**
 * Main execution
 */
async function main() {
  console.log("🚀 Starting game sync to production...\n");

  let prodClient: MongoClient | null = null;

  try {
    // Step 1: Export games from local MongoDB
    const games = await exportGamesFromLocal();

    if (games.length === 0) {
      console.log("\n⚠️  No games found in local database. Exiting.");
      return;
    }

    // Step 2: Connect to production database
    console.log("\n🔌 Connecting to production MongoDB...");
    console.log(`   URI: ${PROD_MONGODB_URI?.replace(/\/\/[^:]+:[^@]+@/, "//***:***@")}`); // Hide credentials
    console.log(`   Database: ${DATABASE_NAME}`);

    const prodConnection = await getDatabase(PROD_MONGODB_URI!, DATABASE_NAME);
    prodClient = prodConnection.client;
    const prodDb = prodConnection.db;

    // Step 3: Ensure all collections exist
    await ensureCollectionsExist(prodDb);

    // Step 4: Initialize indexes
    await initializeIndexes(prodDb);

    // Step 5: Import/update games
    const stats = await importGamesToProd(prodDb, games);

    // Summary
    console.log("\n" + "=".repeat(60));
    console.log("✅ Sync completed successfully!");
    console.log("=".repeat(60));
    console.log(`   Total games exported: ${games.length}`);
    console.log(`   Valid games processed: ${games.length - stats.invalidCount}`);
    if (stats.invalidCount > 0) {
      console.log(`   Invalid games skipped: ${stats.invalidCount}`);
    }
    console.log(`   Games inserted: ${stats.inserted}`);
    console.log(`   Games updated: ${stats.updated}`);
    console.log("=".repeat(60) + "\n");
  } catch (error) {
    console.error("\n❌ Error during sync:", error);
    process.exit(1);
  } finally {
    // Cleanup
    if (prodClient) {
      await prodClient.close();
    }
  }
}

// Run the script
main().catch((error) => {
  console.error("Fatal error:", error);
  process.exit(1);
});
