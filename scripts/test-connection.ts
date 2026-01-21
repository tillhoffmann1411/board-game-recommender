/**
 * Test MongoDB Connection
 *
 * Simple script to test MongoDB connection and diagnose issues.
 */

import dotenv from "dotenv";
import { MongoClient } from "mongodb";

// Load environment variables
dotenv.config({ path: ".env.local" });
dotenv.config(); // Fallback to .env

async function testConnection() {
  const uri = process.env.MONGODB_URI || "mongodb://localhost:27017";
  
  // Mask password in logs
  const maskedUri = uri.replace(/:([^:@]+)@/, ":****@");
  console.log("Testing connection to:", maskedUri);
  console.log("");

  const options = {
    serverSelectionTimeoutMS: 10000, // 10 seconds for quick test
    connectTimeoutMS: 10000,
    socketTimeoutMS: 10000,
    retryWrites: true,
    retryReads: true,
    ...(uri.includes("mongodb+srv://") && {
      tls: true,
      tlsAllowInvalidCertificates: false,
    }),
  };

  const client = new MongoClient(uri, options);

  try {
    console.log("Attempting to connect...");
    await client.connect();
    console.log("✅ Successfully connected!");

    // Test ping
    console.log("Testing ping...");
    const result = await client.db("admin").command({ ping: 1 });
    console.log("✅ Ping successful:", result);

    // List databases
    console.log("Listing databases...");
    const databases = await client.db().admin().listDatabases();
    console.log("✅ Available databases:", databases.databases.map((db) => db.name));

    console.log("\n✅ Connection test passed!");
  } catch (error: any) {
    console.error("\n❌ Connection test failed!");
    console.error("Error type:", error.constructor.name);
    console.error("Error message:", error.message);
    
    if (error.cause) {
      console.error("Cause:", error.cause.message);
      console.error("Error code:", error.cause.code);
    }

    if (error.reason) {
      console.error("\nTopology info:");
      console.error("Type:", error.reason.type);
      console.error("Servers:", Array.from(error.reason.servers.keys()));
    }

    console.error("\nTroubleshooting tips:");
    console.error("1. Check if your IP is whitelisted in MongoDB Atlas");
    console.error("2. Verify your connection string is correct");
    console.error("3. Check if you're behind a VPN or firewall");
    console.error("4. Try using mongosh to test: mongosh '<your-connection-string>'");
    console.error("5. Check if your Atlas cluster is running (not paused)");
    
    process.exit(1);
  } finally {
    await client.close();
    console.log("\nConnection closed.");
  }
}

testConnection();
