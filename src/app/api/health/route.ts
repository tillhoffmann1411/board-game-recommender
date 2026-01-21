import { NextResponse } from "next/server";
import { getDb } from "@/lib/db/client";

// Force dynamic rendering (not static)
export const dynamic = "force-dynamic";

export async function GET() {
  try {
    // Check MongoDB connection
    const db = await getDb();
    await db.command({ ping: 1 });

    return NextResponse.json(
      {
        status: "healthy",
        timestamp: new Date().toISOString(),
        services: {
          database: "connected",
        },
      },
      { status: 200 }
    );
  } catch (error) {
    return NextResponse.json(
      {
        status: "unhealthy",
        timestamp: new Date().toISOString(),
        services: {
          database: "disconnected",
        },
        error: error instanceof Error ? error.message : "Unknown error",
      },
      { status: 503 }
    );
  }
}
