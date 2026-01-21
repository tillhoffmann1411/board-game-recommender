"use server";

import { auth } from "@clerk/nextjs/server";
import { ObjectId } from "mongodb";
import { revalidatePath } from "next/cache";
import { getDb } from "@/lib/db/client";
import { COLLECTIONS } from "@/lib/db/schema";
import type { Rating, User } from "@/lib/db/schema";
import { invalidateCache, precomputeRecommendations } from "@/lib/recommender";

export async function rateGame(
  gameId: string,
  rating: number
): Promise<{ success: boolean; error?: string }> {
  try {
    const { userId: clerkId } = await auth();

    if (!clerkId) {
      return { success: false, error: "Not authenticated" };
    }

    if (!ObjectId.isValid(gameId)) {
      return { success: false, error: "Invalid game ID" };
    }

    if (rating < 1 || rating > 10) {
      return { success: false, error: "Rating must be between 1 and 10" };
    }

    const db = await getDb();

    // Get or create user
    let user = await db
      .collection<User>(COLLECTIONS.USERS)
      .findOne({ clerkId });

    if (!user) {
      const now = new Date();
      const result = await db.collection<User>(COLLECTIONS.USERS).insertOne({
        _id: new ObjectId(),
        clerkId,
        username: null,
        displayName: null,
        ratingCount: 0,
        preferences: null,
        createdAt: now,
        updatedAt: now,
      });
      user = { _id: result.insertedId } as User;
    }

    const gameObjectId = new ObjectId(gameId);
    const now = new Date();

    // Check if rating exists
    const existingRating = await db
      .collection<Rating>(COLLECTIONS.RATINGS)
      .findOne({ userId: user._id, gameId: gameObjectId });

    if (existingRating) {
      // Update existing rating
      await db.collection<Rating>(COLLECTIONS.RATINGS).updateOne(
        { _id: existingRating._id },
        { $set: { rating, updatedAt: now } }
      );
    } else {
      // Insert new rating
      await db.collection<Rating>(COLLECTIONS.RATINGS).insertOne({
        _id: new ObjectId(),
        userId: user._id,
        gameId: gameObjectId,
        rating,
        origin: "app",
        createdAt: now,
        updatedAt: now,
      });

      // Increment user rating count
      await db.collection<User>(COLLECTIONS.USERS).updateOne(
        { _id: user._id },
        { $inc: { ratingCount: 1 }, $set: { updatedAt: now } }
      );
    }

    // Invalidate recommendation cache and precompute new recommendations
    await invalidateCache(user._id);

    // Precompute recommendations in background (don't block response)
    precomputeRecommendations(user._id).catch((err) => {
      console.error("Failed to precompute recommendations:", err);
    });

    revalidatePath(`/games/${gameId}`);
    revalidatePath("/ratings");
    revalidatePath("/recommendations");

    return { success: true };
  } catch (error) {
    console.error("Error rating game:", error);
    return { success: false, error: "Failed to save rating" };
  }
}

export async function deleteRating(
  gameId: string
): Promise<{ success: boolean; error?: string }> {
  try {
    const { userId: clerkId } = await auth();

    if (!clerkId) {
      return { success: false, error: "Not authenticated" };
    }

    if (!ObjectId.isValid(gameId)) {
      return { success: false, error: "Invalid game ID" };
    }

    const db = await getDb();

    const user = await db
      .collection<User>(COLLECTIONS.USERS)
      .findOne({ clerkId });

    if (!user) {
      return { success: false, error: "User not found" };
    }

    const gameObjectId = new ObjectId(gameId);

    const result = await db.collection<Rating>(COLLECTIONS.RATINGS).deleteOne({
      userId: user._id,
      gameId: gameObjectId,
    });

    if (result.deletedCount > 0) {
      // Decrement user rating count
      await db.collection<User>(COLLECTIONS.USERS).updateOne(
        { _id: user._id },
        { $inc: { ratingCount: -1 }, $set: { updatedAt: new Date() } }
      );

      // Invalidate recommendation cache and precompute new recommendations
      await invalidateCache(user._id);

      // Precompute recommendations in background (don't block response)
      precomputeRecommendations(user._id).catch((err) => {
        console.error("Failed to precompute recommendations:", err);
      });
    }

    revalidatePath(`/games/${gameId}`);
    revalidatePath("/ratings");
    revalidatePath("/recommendations");

    return { success: true };
  } catch (error) {
    console.error("Error deleting rating:", error);
    return { success: false, error: "Failed to delete rating" };
  }
}

export async function getUserRatings(): Promise<
  Array<{ gameId: string; gameName: string; rating: number; imageUrl?: string }>
> {
  try {
    const { userId: clerkId } = await auth();

    if (!clerkId) {
      return [];
    }

    const db = await getDb();

    const user = await db
      .collection<User>(COLLECTIONS.USERS)
      .findOne({ clerkId });

    if (!user) {
      return [];
    }

    // Get ratings with game info via aggregation
    const ratings = await db
      .collection<Rating>(COLLECTIONS.RATINGS)
      .aggregate([
        { $match: { userId: user._id } },
        {
          $lookup: {
            from: COLLECTIONS.GAMES,
            localField: "gameId",
            foreignField: "_id",
            as: "game",
          },
        },
        { $unwind: "$game" },
        {
          $project: {
            gameId: { $toString: "$gameId" },
            gameName: "$game.name",
            rating: 1,
            imageUrl: "$game.imageUrl",
            createdAt: 1,
          },
        },
        { $sort: { createdAt: -1 } },
      ])
      .toArray();

    return ratings as Array<{
      gameId: string;
      gameName: string;
      rating: number;
      imageUrl?: string;
    }>;
  } catch (error) {
    console.error("Error getting user ratings:", error);
    return [];
  }
}

export async function getGameRating(
  gameId: string
): Promise<number | null> {
  try {
    const { userId: clerkId } = await auth();

    if (!clerkId) {
      return null;
    }

    if (!ObjectId.isValid(gameId)) {
      return null;
    }

    const db = await getDb();

    const user = await db
      .collection<User>(COLLECTIONS.USERS)
      .findOne({ clerkId });

    if (!user) {
      return null;
    }

    const gameObjectId = new ObjectId(gameId);
    const rating = await db
      .collection<Rating>(COLLECTIONS.RATINGS)
      .findOne({ userId: user._id, gameId: gameObjectId });

    return rating ? rating.rating : null;
  } catch (error) {
    console.error("Error getting game rating:", error);
    return null;
  }
}
