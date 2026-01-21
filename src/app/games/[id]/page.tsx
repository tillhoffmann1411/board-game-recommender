import { notFound } from "next/navigation";
import Image from "next/image";
import { ObjectId } from "mongodb";
import { Star, Users, Clock, Brain, Calendar } from "lucide-react";
import { Header } from "@/src/components/header";
import { Badge } from "@/src/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/src/components/ui/card";
import { RatingForm } from "@/src/components/rating-form";
import { ExternalLinkButton } from "@/src/components/external-link-button";
import { getDb } from "@/lib/db/client";
import { COLLECTIONS } from "@/lib/db/schema";
import type { Game } from "@/lib/db/schema";
import { getGameRating } from "@/src/app/actions/ratings";

// Force dynamic rendering (uses database)
export const dynamic = "force-dynamic";

interface GamePageProps {
  params: Promise<{ id: string }>;
}

async function getGame(id: string): Promise<Game | null> {
  if (!ObjectId.isValid(id)) {
    return null;
  }

  const db = await getDb();
  const game = await db
    .collection<Game>(COLLECTIONS.GAMES)
    .findOne({ _id: new ObjectId(id) });

  return game;
}

export default async function GamePage({ params }: GamePageProps) {
  const { id } = await params;
  const game = await getGame(id);

  if (!game) {
    notFound();
  }

  const rating = game.bggRating?.average?.toFixed(1) || "N/A";
  const ratingCount = game.bggRating?.count?.toLocaleString() || "0";
  const userRating = await getGameRating(game._id.toString());

  // Validate image URL - must be a valid URL string
  const rawImageUrl = game.imageUrl;
  const imageUrl =
    rawImageUrl &&
      typeof rawImageUrl === "string" &&
      rawImageUrl !== "nan" &&
      rawImageUrl !== "null" &&
      rawImageUrl.trim() !== "" &&
      (rawImageUrl.startsWith("http://") || rawImageUrl.startsWith("https://") || rawImageUrl.startsWith("/"))
      ? rawImageUrl
      : null;

  return (
    <div className="flex w-full flex-col">
      <Header />

      <main className="flex-1 py-4 px-4 sm:py-8 sm:px-6">
        <div className="mx-auto max-w-6xl">
          <div className="grid gap-6 lg:grid-cols-3 lg:gap-8">
            {/* Game Image */}
            <div className="lg:col-span-1">
              <div className="relative w-full overflow-hidden rounded-lg bg-muted">
                {imageUrl ? (
                  <Image
                    src={imageUrl}
                    alt={game.name}
                    width={600}
                    height={800}
                    className="w-full h-auto object-contain"
                    priority
                    sizes="(max-width: 1024px) 100vw, 33vw"
                  />
                ) : (
                  <div className="flex aspect-square w-full items-center justify-center">
                    <span className="text-6xl sm:text-8xl">🎲</span>
                  </div>
                )}
              </div>

              {/* Quick Stats */}
              <Card className="mt-4">
                <CardContent className="grid grid-cols-2 gap-3 p-3 sm:gap-4 sm:p-4">
                  <div className="flex items-center gap-2">
                    <Users className="h-4 w-4 sm:h-5 sm:w-5 text-muted-foreground" />
                    <div>
                      <p className="text-xs sm:text-sm text-muted-foreground">Players</p>
                      <p className="text-sm sm:text-base font-medium">
                        {game.minPlayers === game.maxPlayers
                          ? game.minPlayers
                          : `${game.minPlayers}-${game.maxPlayers}`}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Clock className="h-4 w-4 sm:h-5 sm:w-5 text-muted-foreground" />
                    <div>
                      <p className="text-xs sm:text-sm text-muted-foreground">Playtime</p>
                      <p className="text-sm sm:text-base font-medium">
                        {game.minPlaytime === game.maxPlaytime
                          ? `${game.minPlaytime} min`
                          : `${game.minPlaytime}-${game.maxPlaytime} min`}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Brain className="h-4 w-4 sm:h-5 sm:w-5 text-muted-foreground" />
                    <div>
                      <p className="text-xs sm:text-sm text-muted-foreground">Complexity</p>
                      <p className="text-sm sm:text-base font-medium">
                        {game.complexity?.toFixed(2) || "N/A"} / 5
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Calendar className="h-4 w-4 sm:h-5 sm:w-5 text-muted-foreground" />
                    <div>
                      <p className="text-xs sm:text-sm text-muted-foreground">Year</p>
                      <p className="text-sm sm:text-base font-medium">{game.yearPublished || "N/A"}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Game Details */}
            <div className="lg:col-span-2 space-y-4">
              <h1 className="mb-2 text-2xl sm:text-3xl font-bold">{game.name}</h1>

              {/* Rating */}
              <div className="flex flex-wrap items-center gap-2 sm:gap-4">
                <div className="flex items-center gap-1">
                  <Star className="h-5 w-5 sm:h-6 sm:w-6 fill-yellow-400 text-yellow-400" />
                  <span className="text-xl sm:text-2xl font-bold">{rating}</span>
                  <span className="text-sm sm:text-base text-muted-foreground">/ 10</span>
                </div>
                <span className="text-sm sm:text-base text-muted-foreground">
                  ({ratingCount} ratings)
                </span>
              </div>

              {/* Official URL Button */}
              {game.officialUrl && (
                <div>
                  <ExternalLinkButton
                    url={game.officialUrl}
                    label="View on Board Game Geek"
                  />
                </div>
              )}

              {/* Categories & Mechanics */}
              {game.categories && game.categories.length > 0 && (
                <div>
                  <h3 className="mb-2 text-sm sm:text-base font-semibold">Categories</h3>
                  <div className="flex flex-wrap gap-2">
                    {game.categories.map((cat) => (
                      <Badge key={cat} variant="secondary" className="text-xs sm:text-sm">
                        {cat}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}

              {game.mechanics && game.mechanics.length > 0 && (
                <div>
                  <h3 className="mb-2 text-sm sm:text-base font-semibold">Mechanics</h3>
                  <div className="flex flex-wrap gap-2">
                    {game.mechanics.map((mech) => (
                      <Badge key={mech} variant="outline" className="text-xs sm:text-sm">
                        {mech}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}

              {/* Description */}
              {game.description && (
                <div className="mb-6">
                  <h3 className="mb-2 text-sm sm:text-base font-semibold">Description</h3>
                  <p className="text-sm sm:text-base whitespace-pre-wrap text-muted-foreground">
                    {game.description}
                  </p>
                </div>
              )}

              {/* Designers & Publishers */}
              {game.designers && game.designers.length > 0 && (
                <div>
                  <h3 className="mb-2 text-sm sm:text-base font-semibold">Designers</h3>
                  <p className="text-sm sm:text-base text-muted-foreground">
                    {game.designers.map((d) => d.name).join(", ")}
                  </p>
                </div>
              )}

              {game.publishers && game.publishers.length > 0 && (
                <div>
                  <h3 className="mb-2 text-sm sm:text-base font-semibold">Publishers</h3>
                  <p className="text-sm sm:text-base text-muted-foreground">
                    {game.publishers.map((p) => p.name).join(", ")}
                  </p>
                </div>
              )}

              {/* Rate This Game */}
              <Card className="sm:mt-6">
                <CardHeader className="pb-3">
                  <CardTitle className="text-lg sm:text-xl">Rate This Game</CardTitle>
                </CardHeader>
                <CardContent>
                  <RatingForm
                    gameId={game._id.toString()}
                    gameName={game.name}
                    initialRating={userRating || undefined}
                  />
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
