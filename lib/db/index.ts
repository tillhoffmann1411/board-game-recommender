/**
 * Database Module Exports
 *
 * Central export point for all database utilities.
 */

// Client
export { getClient, getDb, default as clientPromise } from "./client";

// Schema types
export * from "./schema";

// Query functions
export * from "./queries";

// Initialization
export { initializeDatabase, dropAllCollections, getDatabaseStats } from "./init";
