/**
 * Popularity-Based Recommendation Engine
 *
 * Recommends games based on a popularity score combining:
 * - Average BGG rating (normalized)
 * - Number of ratings (normalized)
 *
 * Good for cold-start users with few or no ratings.
 */

import { ObjectId } from "mongodb";
import { getDb } from "@/lib/db/client";
import { COLLECTIONS } from "@/lib/db/schema";
import type { Game } from "@/lib/db/schema";
import type { RecommendationEngine, ScoredGame, UserRating } from "./types";

export class PopularityEngine implements RecommendationEngine {
  name = "popularity" as const;

  async recommend(
    _userId: ObjectId,
    _userRatings: UserRating[],
    excludeGameIds: Set<string>,
    limit: number
  ): Promise<ScoredGame[]> {
    const db = await getDb();

    // Get games with sufficient ratings
    const games = await db
      .collection<Game>(COLLECTIONS.GAMES)
      .find({
        "bggRating.average": { $exists: true, $ne: null },
        "bggRating.count": { $gte: 100 },
      })
      .project({
        _id: 1,
        "bggRating.average": 1,
        "bggRating.count": 1,
      })
      .toArray();

    // Calculate min/max for normalization
    let minAvg = Infinity,
      maxAvg = -Infinity;
    let minCount = Infinity,
      maxCount = -Infinity;

    for (const game of games) {
      if (!game.bggRating) continue;
      const avg = game.bggRating.average || 0;
      const count = game.bggRating.count || 0;

      if (avg < minAvg) minAvg = avg;
      if (avg > maxAvg) maxAvg = avg;
      if (count < minCount) minCount = count;
      if (count > maxCount) maxCount = count;
    }

    const avgRange = maxAvg - minAvg || 1;
    const countRange = maxCount - minCount || 1;

    // Calculate popularity scores
    const scored: ScoredGame[] = [];

    for (const game of games) {
      const id = game._id.toString();
      if (excludeGameIds.has(id)) continue;
      if (!game.bggRating) continue;

      const avg = game.bggRating.average || 0;
      const count = game.bggRating.count || 0;

      // Normalize to 0-1 range
      const normalizedAvg = (avg - minAvg) / avgRange;
      const normalizedCount = (count - minCount) / countRange;

      // Combined score: 70% rating, 30% popularity
      const score = normalizedAvg * 0.7 + normalizedCount * 0.3;

      scored.push({ gameId: game._id, score });
    }

    // Sort by score descending and take top N
    scored.sort((a, b) => b.score - a.score);

    return scored.slice(0, limit);
  }
}
