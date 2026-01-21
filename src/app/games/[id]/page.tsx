import { notFound } from "next/navigation";
import Image from "next/image";
import { ObjectId } from "mongodb";
import { Star, Users, Clock, Brain, Calendar } from "lucide-react";
import { Header } from "@/src/components/header";
import { Badge } from "@/src/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/src/components/ui/card";
import { RatingForm } from "@/src/components/rating-form";
import { getDb } from "@/lib/db/client";
import { COLLECTIONS } from "@/lib/db/schema";
import type { Game } from "@/lib/db/schema";

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
    <div className="flex min-h-screen flex-col">
      <Header />

      <main className="container flex-1 py-8">
        <div className="grid gap-8 lg:grid-cols-3">
          {/* Game Image */}
          <div className="lg:col-span-1">
            <div className="relative aspect-square overflow-hidden rounded-lg bg-muted">
              {imageUrl ? (
                <Image
                  src={imageUrl}
                  alt={game.name}
                  fill
                  className="object-cover"
                  priority
                />
              ) : (
                <div className="flex h-full w-full items-center justify-center">
                  <span className="text-8xl">🎲</span>
                </div>
              )}
            </div>

            {/* Quick Stats */}
            <Card className="mt-4">
              <CardContent className="grid grid-cols-2 gap-4 p-4">
                <div className="flex items-center gap-2">
                  <Users className="h-5 w-5 text-muted-foreground" />
                  <div>
                    <p className="text-sm text-muted-foreground">Players</p>
                    <p className="font-medium">
                      {game.minPlayers === game.maxPlayers
                        ? game.minPlayers
                        : `${game.minPlayers}-${game.maxPlayers}`}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Clock className="h-5 w-5 text-muted-foreground" />
                  <div>
                    <p className="text-sm text-muted-foreground">Playtime</p>
                    <p className="font-medium">
                      {game.minPlaytime === game.maxPlaytime
                        ? `${game.minPlaytime} min`
                        : `${game.minPlaytime}-${game.maxPlaytime} min`}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Brain className="h-5 w-5 text-muted-foreground" />
                  <div>
                    <p className="text-sm text-muted-foreground">Complexity</p>
                    <p className="font-medium">
                      {game.complexity?.toFixed(2) || "N/A"} / 5
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Calendar className="h-5 w-5 text-muted-foreground" />
                  <div>
                    <p className="text-sm text-muted-foreground">Year</p>
                    <p className="font-medium">{game.yearPublished || "N/A"}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Game Details */}
          <div className="lg:col-span-2">
            <h1 className="mb-2 text-3xl font-bold">{game.name}</h1>

            {/* Rating */}
            <div className="mb-4 flex items-center gap-4">
              <div className="flex items-center gap-1">
                <Star className="h-6 w-6 fill-yellow-400 text-yellow-400" />
                <span className="text-2xl font-bold">{rating}</span>
                <span className="text-muted-foreground">/ 10</span>
              </div>
              <span className="text-muted-foreground">
                ({ratingCount} ratings)
              </span>
            </div>

            {/* Categories & Mechanics */}
            {game.categories && game.categories.length > 0 && (
              <div className="mb-4">
                <h3 className="mb-2 font-semibold">Categories</h3>
                <div className="flex flex-wrap gap-2">
                  {game.categories.map((cat) => (
                    <Badge key={cat} variant="secondary">
                      {cat}
                    </Badge>
                  ))}
                </div>
              </div>
            )}

            {game.mechanics && game.mechanics.length > 0 && (
              <div className="mb-4">
                <h3 className="mb-2 font-semibold">Mechanics</h3>
                <div className="flex flex-wrap gap-2">
                  {game.mechanics.map((mech) => (
                    <Badge key={mech} variant="outline">
                      {mech}
                    </Badge>
                  ))}
                </div>
              </div>
            )}

            {/* Description */}
            {game.description && (
              <div className="mb-6">
                <h3 className="mb-2 font-semibold">Description</h3>
                <p className="whitespace-pre-wrap text-muted-foreground">
                  {game.description}
                </p>
              </div>
            )}

            {/* Designers & Publishers */}
            {game.designers && game.designers.length > 0 && (
              <div className="mb-4">
                <h3 className="mb-2 font-semibold">Designers</h3>
                <p className="text-muted-foreground">
                  {game.designers.map((d) => d.name).join(", ")}
                </p>
              </div>
            )}

            {game.publishers && game.publishers.length > 0 && (
              <div className="mb-4">
                <h3 className="mb-2 font-semibold">Publishers</h3>
                <p className="text-muted-foreground">
                  {game.publishers.map((p) => p.name).join(", ")}
                </p>
              </div>
            )}

            {/* Rate This Game */}
            <Card className="mt-6">
              <CardHeader>
                <CardTitle>Rate This Game</CardTitle>
              </CardHeader>
              <CardContent>
                <RatingForm gameId={game._id.toString()} gameName={game.name} />
              </CardContent>
            </Card>
          </div>
        </div>
      </main>
    </div>
  );
}
