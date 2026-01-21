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
  // Default to local MongoDB for development if not specified
  const uri = process.env.MONGODB_URI || "mongodb://localhost:27017";

  // Mask password in logs for security
  const maskedUri = uri.replace(/:([^:@]+)@/, ":****@");
  console.log("Connecting to MongoDB:", maskedUri);

  if (clientPromise) {
    return clientPromise;
  }

  // Connection options for better reliability, especially for Atlas
  const options = {
    serverSelectionTimeoutMS: 30000, // 30 seconds
    connectTimeoutMS: 30000, // 30 seconds
    socketTimeoutMS: 30000, // 30 seconds
    retryWrites: true,
    retryReads: true,
    // For Atlas connections, ensure TLS is used
    ...(uri.includes("mongodb+srv://") && {
      tls: true,
      tlsAllowInvalidCertificates: false,
    }),
  };

  if (process.env.NODE_ENV === "development") {
    // In development, use a global variable to preserve the client across HMR
    if (!global._mongoClientPromise) {
      const client = new MongoClient(uri, options);
      global._mongoClientPromise = client.connect();
    }
    clientPromise = global._mongoClientPromise;
  } else {
    // In production, create a new client for each instance
    const client = new MongoClient(uri, options);
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
