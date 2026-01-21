/**
 * Database Initialization Script
 *
 * Creates all collections and indexes for the board game recommender database.
 * Run this script once when setting up a new database.
 */

import dotenv from "dotenv";
import { initializeDatabase } from "../lib/db/init";

// Load environment variables from .env.local (fallback to .env)
dotenv.config({ path: ".env.local" });
dotenv.config(); // Fallback to .env

async function main() {
  console.log("🚀 Initializing database...\n");

  try {
    await initializeDatabase();
    console.log("\n✅ Database initialization completed successfully!");
    process.exit(0);
  } catch (error) {
    console.error("\n❌ Error initializing database:", error);
    process.exit(1);
  }
}

main();
