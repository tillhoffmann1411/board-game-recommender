"use server";

import { auth } from "@clerk/nextjs/server";
import { getDb } from "@/lib/db/client";
import { COLLECTIONS } from "@/lib/db/schema";
import type { User } from "@/lib/db/schema";
import {
  getRecommendationsWithDetails,
  invalidateCache,
  getAvailableAlgorithms,
  type AlgorithmType,
} from "@/lib/recommender";

interface RecommendedGameWithDetails {
  gameId: string;
  name: string;
  imageUrl?: string;
  score: number;
  rank: number;
  bggRating?: number;
  categories: string[];
  complexity?: number;
  minPlayers?: number;
  maxPlayers?: number;
}

export async function getRecommendations(
  algorithm: AlgorithmType = "popularity"
): Promise<{
  recommendations: RecommendedGameWithDetails[];
  algorithm: AlgorithmType;
  generatedAt?: Date;
  inputRatingCount?: number;
  error?: string;
}> {
  try {
    const { userId: clerkId } = await auth();

    if (!clerkId) {
      return { recommendations: [], algorithm, error: "Not authenticated" };
    }

    const db = await getDb();

    // Get or create user
    let user = await db
      .collection<User>(COLLECTIONS.USERS)
      .findOne({ clerkId });

    if (!user) {
      // Create user on first recommendation request
      const now = new Date();
      const newUser: Omit<User, "_id"> = {
        clerkId,
        username: null,
        displayName: null,
        ratingCount: 0,
        preferences: null,
        createdAt: now,
        updatedAt: now,
      };
      const result = await db
        .collection(COLLECTIONS.USERS)
        .insertOne(newUser);
      user = {
        _id: result.insertedId,
        ...newUser,
      };
    }

    // Get recommendations with details
    const result = await getRecommendationsWithDetails(user._id, algorithm, 20);

    const recommendations: RecommendedGameWithDetails[] = result.games.map(
      (game) => ({
        gameId: game._id.toString(),
        name: game.name,
        imageUrl: game.imageUrl || undefined,
        score: game.score,
        rank: game.rank,
        bggRating: game.bggRating?.average,
        categories: game.categories || [],
        complexity: game.complexity || undefined,
        minPlayers: game.minPlayers || undefined,
        maxPlayers: game.maxPlayers || undefined,
      })
    );

    return {
      recommendations,
      algorithm,
      generatedAt: result.generatedAt,
      inputRatingCount: result.inputRatingCount,
    };
  } catch (error) {
    console.error("Error getting recommendations:", error);
    return {
      recommendations: [],
      algorithm,
      error: "Failed to get recommendations",
    };
  }
}

export async function refreshRecommendations(
  _algorithm: AlgorithmType
): Promise<{
  success: boolean;
  error?: string;
}> {
  try {
    const { userId: clerkId } = await auth();

    if (!clerkId) {
      return { success: false, error: "Not authenticated" };
    }

    const db = await getDb();
    const user = await db
      .collection<User>(COLLECTIONS.USERS)
      .findOne({ clerkId });

    if (!user) {
      return { success: false, error: "User not found" };
    }

    // Invalidate cache to force refresh
    await invalidateCache(user._id);

    return { success: true };
  } catch (error) {
    console.error("Error refreshing recommendations:", error);
    return { success: false, error: "Failed to refresh recommendations" };
  }
}

export async function getAlgorithms(): Promise<
  Array<{
    id: AlgorithmType;
    name: string;
    description: string;
    minRatings: number;
  }>
> {
  return getAvailableAlgorithms();
}
