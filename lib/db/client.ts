/**
 * MongoDB Client Singleton
 *
 * Provides a single MongoDB client instance for the entire application.
 * Uses connection pooling and handles reconnection automatically.
 */

import { MongoClient, Db } from "mongodb";

const MONGODB_DB = process.env.MONGODB_DB || "board-game-recommender";

/**
 * Global type augmentation for caching the client in development
 */
declare global {
  var _mongoClientPromise: Promise<MongoClient> | undefined;
}

let clientPromise: Promise<MongoClient> | null = null;

function getClientPromise(): Promise<MongoClient> {
  const uri = process.env.MONGODB_URI;

  if (!uri) {
    throw new Error(
      "Please define the MONGODB_URI environment variable in .env.local"
    );
  }

  if (clientPromise) {
    return clientPromise;
  }

  if (process.env.NODE_ENV === "development") {
    // In development, use a global variable to preserve the client across HMR
    if (!global._mongoClientPromise) {
      const client = new MongoClient(uri);
      global._mongoClientPromise = client.connect();
    }
    clientPromise = global._mongoClientPromise;
  } else {
    // In production, create a new client for each instance
    const client = new MongoClient(uri);
    clientPromise = client.connect();
  }

  return clientPromise;
}

/**
 * Get the MongoDB client instance
 */
export async function getClient(): Promise<MongoClient> {
  return getClientPromise();
}

/**
 * Get the database instance
 */
export async function getDb(): Promise<Db> {
  const client = await getClientPromise();
  return client.db(MONGODB_DB);
}

/**
 * Lazy-evaluated client promise for Next.js edge runtime compatibility
 */
const lazyClientPromise = {
  get then() {
    return getClientPromise().then.bind(getClientPromise());
  },
};

export default lazyClientPromise;
