"use client";

import { useState } from "react";
import Image from "next/image";
import Link from "next/link";
import { Star, Users, Clock } from "lucide-react";
import { Card, CardContent, CardFooter, CardHeader } from "@/src/components/ui/card";
import { Badge } from "@/src/components/ui/badge";
import { Skeleton } from "@/src/components/ui/skeleton";

/** Serialized game summary for client components */
interface SerializedGameSummary {
  _id: string;
  name: string;
  imageUrl: string | null;
  thumbnailUrl: string | null;
  yearPublished: number | null;
  minPlayers: number | null;
  maxPlayers: number | null;
  minPlaytime: number | null;
  maxPlaytime: number | null;
  complexity: number | null;
  bggRating: { average: number; count: number } | null;
  categories: string[];
}

/** Recommended game with details */
interface RecommendedGameWithDetails {
  gameId: string;
  name: string;
  imageUrl?: string;
  thumbnailUrl?: string;
  score?: number;
  rank?: number;
  bggRating?: number;
  categories: string[];
  complexity?: number;
  minPlayers?: number;
  maxPlayers?: number;
  minPlaytime?: number;
  maxPlaytime?: number;
  yearPublished?: number;
}

type GameCardData = SerializedGameSummary | RecommendedGameWithDetails;

interface GameCardProps {
  game: GameCardData;
}

// Category colors for visual variety
const categoryColors: Record<string, string> = {
  "Strategy Games": "bg-purple-100 text-purple-700 border-purple-200",
  "Family Games": "bg-pink-100 text-pink-700 border-pink-200",
  "Thematic Games": "bg-orange-100 text-orange-700 border-orange-200",
  "War Games": "bg-red-100 text-red-700 border-red-200",
  "Party Games": "bg-yellow-100 text-yellow-700 border-yellow-200",
  "Abstract Games": "bg-blue-100 text-blue-700 border-blue-200",
  "Customizable Games": "bg-green-100 text-green-700 border-green-200",
  "Children's Games": "bg-teal-100 text-teal-700 border-teal-200",
};

function getCategoryColor(category: string): string {
  return categoryColors[category] || "bg-gray-100 text-gray-700 border-gray-200";
}

// Helper function to validate URL
function validateUrl(url: string | null | undefined): string | null {
  if (
    !url ||
    typeof url !== "string" ||
    url === "nan" ||
    url === "null" ||
    url.trim() === ""
  ) {
    return null;
  }
  if (
    url.startsWith("http://") ||
    url.startsWith("https://") ||
    url.startsWith("/")
  ) {
    return url;
  }
  return null;
}

export function GameCard({ game }: GameCardProps) {
  // Handle both data structures
  const gameId = "_id" in game ? game._id : game.gameId;

  // Get image URLs from both data structures
  const rawImageUrl = game.imageUrl;
  const rawThumbnailUrl = "thumbnailUrl" in game ? game.thumbnailUrl : undefined;

  // Validate URLs
  const imageUrl = validateUrl(rawImageUrl);
  const thumbnailUrl = validateUrl(rawThumbnailUrl);

  // Progressive image loading: start with thumbnail, then load full image
  const [fullImageLoaded, setFullImageLoaded] = useState(false);
  
  // Determine if we should show thumbnail first (only if both exist and are different)
  const showThumbnailFirst = thumbnailUrl && imageUrl && thumbnailUrl !== imageUrl;

  const bggRatingValue =
    "bggRating" in game && typeof game.bggRating === "object" && game.bggRating !== null
      ? game.bggRating.average
      : "bggRating" in game && typeof game.bggRating === "number"
        ? game.bggRating
        : null;

  const rating = bggRatingValue?.toFixed(1) || "N/A";
  const ratingNum = bggRatingValue || 0;
  const playerRange =
    game.minPlayers && game.maxPlayers
      ? game.minPlayers === game.maxPlayers
        ? `${game.minPlayers}`
        : `${game.minPlayers}-${game.maxPlayers}`
      : "?";
  const playtime =
    game.minPlaytime && game.maxPlaytime
      ? game.minPlaytime === game.maxPlaytime
        ? `${game.minPlaytime}`
        : `${game.minPlaytime}-${game.maxPlaytime}`
      : "?";
  const yearPublished = "yearPublished" in game ? game.yearPublished : null;
  const rank = "rank" in game ? game.rank : null;
  const score = "score" in game ? game.score : null;

  // Rating color based on score
  const getRatingColor = () => {
    if (ratingNum >= 8) return "text-green-600 bg-green-50";
    if (ratingNum >= 7) return "text-purple-600 bg-purple-50";
    if (ratingNum >= 6) return "text-blue-600 bg-blue-50";
    return "text-gray-600 bg-gray-50";
  };

  return (
    <Link href={`/games/${gameId}`}>
      <Card className="h-full overflow-hidden border border-transparent bg-white shadow-sm transition-all duration-300 hover:shadow hover:border-purple-200 group">
        <CardHeader className="p-0">
          <div className="relative aspect-[3/4] w-full overflow-hidden bg-gradient-to-br from-purple-100 to-pink-50">
            {thumbnailUrl || imageUrl ? (
              <>
                {/* Thumbnail (shown first if available, fades out when full image loads) */}
                {showThumbnailFirst && thumbnailUrl && (
                  <Image
                    src={thumbnailUrl}
                    alt={game.name}
                    fill
                    className={`object-cover transition-opacity duration-500 ${
                      fullImageLoaded ? "opacity-0" : "opacity-100"
                    }`}
                    sizes="(max-width: 640px) 50vw, (max-width: 1024px) 33vw, (max-width: 1280px) 25vw, 20vw"
                    loading="lazy"
                    quality={70}
                  />
                )}
                {/* Full image (preloaded in background, fades in when ready) */}
                {imageUrl && (
                  <Image
                    src={imageUrl}
                    alt={game.name}
                    fill
                    className={`object-cover transition-opacity duration-500 ${
                      showThumbnailFirst
                        ? fullImageLoaded
                          ? "opacity-100"
                          : "opacity-0"
                        : "opacity-100"
                    }`}
                    sizes="(max-width: 640px) 50vw, (max-width: 1024px) 33vw, (max-width: 1280px) 25vw, 20vw"
                    loading="lazy"
                    quality={85}
                    onLoad={() => {
                      setFullImageLoaded(true);
                    }}
                  />
                )}
              </>
            ) : (
              <div className="flex h-full w-full items-center justify-center">
                <span className="text-2xl">🎲</span>
              </div>
            )}
            {/* Rank badge (for recommendations) */}
            {typeof rank === 'number' && (
              <Badge className="absolute left-1 top-1 text-[10px] px-1 py-0">#{rank}</Badge>
            )}
            {/* Rating badge overlay */}
            {bggRatingValue !== null && (
              <div className={`absolute top-1 right-1 flex items-center gap-0.5 px-1 py-0.5 rounded-full ${getRatingColor()} shadow-sm backdrop-blur-sm`}>
                <Star className="h-2.5 w-2.5 fill-current" />
                <span className="text-[10px] font-bold">{rating}</span>
              </div>
            )}
          </div>
        </CardHeader>
        <CardContent className="p-2">
          <h3 className="line-clamp-2 text-xs font-semibold text-gray-900 group-hover:text-purple-700 transition-colors leading-tight">
            {game.name}
          </h3>
          {yearPublished && (
            <p className="text-[10px] text-gray-500 mt-0.5">
              {yearPublished}
            </p>
          )}
          {typeof score === 'number' && (
            <p className="text-[10px] text-muted-foreground mt-0.5">
              Match: {(score * 100).toFixed(0)}%
            </p>
          )}
          <div className="mt-1.5 flex flex-wrap gap-0.5">
            {game.categories?.slice(0, 2).map((cat) => (
              <Badge
                key={cat}
                variant="outline"
                className={`text-[10px] font-medium border px-1 py-0 ${getCategoryColor(cat)}`}
              >
                {cat.replace(" Games", "")}
              </Badge>
            ))}
          </div>
        </CardContent>
        {(playerRange !== "?" || playtime !== "?") && (
          <CardFooter className="flex items-center justify-between border-t border-gray-100 bg-gray-50/50 px-2 py-1.5 text-[10px]">
            <div className="flex items-center gap-0.5 text-gray-600">
              <Users className="h-3 w-3 text-purple-500" />
              <span className="font-medium">{playerRange}</span>
            </div>
            <div className="flex items-center gap-0.5 text-gray-600">
              <Clock className="h-3 w-3 text-pink-500" />
              <span className="font-medium">{playtime}m</span>
            </div>
          </CardFooter>
        )}
      </Card>
    </Link>
  );
}

export function GameCardSkeleton() {
  return (
    <Card className="h-full overflow-hidden border border-gray-100">
      <CardHeader className="p-0">
        <Skeleton className="aspect-[3/4] w-full" />
      </CardHeader>
      <CardContent className="p-2">
        <Skeleton className="mb-1.5 h-3 w-3/4" />
        <Skeleton className="h-2.5 w-1/4" />
        <div className="mt-1.5 flex gap-0.5">
          <Skeleton className="h-3 w-12 rounded-full" />
          <Skeleton className="h-3 w-12 rounded-full" />
        </div>
      </CardContent>
      <CardFooter className="flex items-center justify-between border-t px-2 py-1.5">
        <Skeleton className="h-2.5 w-8" />
        <Skeleton className="h-2.5 w-8" />
      </CardFooter>
    </Card>
  );
}
