import Link from "next/link";
import Image from "next/image";
import { Star, Trash2 } from "lucide-react";
import { Header } from "@/src/components/header";
import { Card, CardContent } from "@/src/components/ui/card";
import { Button } from "@/src/components/ui/button";
import { getUserRatings, deleteRating } from "@/src/app/actions/ratings";

// Force dynamic rendering (uses auth and database)
export const dynamic = "force-dynamic";

async function DeleteRatingButton({ gameId }: { gameId: string }) {
  const handleDelete = async () => {
    "use server";
    await deleteRating(gameId);
  };

  return (
    <form action={handleDelete}>
      <Button variant="ghost" size="icon" className="text-destructive">
        <Trash2 className="h-4 w-4" />
      </Button>
    </form>
  );
}

export default async function RatingsPage() {
  const ratings = await getUserRatings();

  return (
    <div className="flex min-h-screen flex-col">
      <Header />

      <main className="container flex-1 py-8">
        <h1 className="mb-6 text-3xl font-bold">My Ratings</h1>

        {ratings.length === 0 ? (
          <div className="py-12 text-center">
            <p className="mb-4 text-lg text-muted-foreground">
              You haven&apos;t rated any games yet.
            </p>
            <Link href="/games">
              <Button>Browse Games</Button>
            </Link>
          </div>
        ) : (
          <>
            <p className="mb-6 text-muted-foreground">
              You&apos;ve rated {ratings.length} games
            </p>

            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {ratings.map((item) => {
                // Validate image URL - must be a valid URL string
                const rawImageUrl = item.imageUrl;
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
                  <Card key={item.gameId} className="overflow-hidden">
                    <CardContent className="flex items-center gap-4 p-4">
                      <Link href={`/games/${item.gameId}`} className="shrink-0">
                        <div className="relative h-16 w-16 overflow-hidden rounded-md bg-muted">
                          {imageUrl ? (
                            <Image
                              src={imageUrl}
                              alt={item.gameName}
                              fill
                              className="object-cover"
                            />
                          ) : (
                            <div className="flex h-full w-full items-center justify-center">
                              <span className="text-2xl">🎲</span>
                            </div>
                          )}
                        </div>
                      </Link>

                    <div className="flex-1 overflow-hidden">
                      <Link href={`/games/${item.gameId}`}>
                        <h3 className="truncate font-medium hover:underline">
                          {item.gameName}
                        </h3>
                      </Link>
                      <div className="flex items-center gap-1 text-sm">
                        <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                        <span className="font-medium">{item.rating}</span>
                        <span className="text-muted-foreground">/ 10</span>
                      </div>
                    </div>

                    <DeleteRatingButton gameId={item.gameId} />
                  </CardContent>
                </Card>
                );
              })}
            </div>

            <div className="mt-8 text-center">
              <p className="mb-4 text-sm text-muted-foreground">
                Rate at least 5 games to get personalized recommendations
              </p>
              {ratings.length >= 5 ? (
                <Link href="/recommendations">
                  <Button>View Recommendations</Button>
                </Link>
              ) : (
                <Link href="/games">
                  <Button variant="outline">
                    Rate {5 - ratings.length} more games
                  </Button>
                </Link>
              )}
            </div>
          </>
        )}
      </main>
    </div>
  );
}
