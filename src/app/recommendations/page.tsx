import Link from "next/link";
import { Sparkles, Star, TrendingUp, Brain, Users } from "lucide-react";
import { Header } from "@/src/components/header";
import { Card, CardContent, CardHeader, CardTitle } from "@/src/components/ui/card";
import { Button } from "@/src/components/ui/button";
import { GameCard } from "@/src/components/game-card";
import { getRecommendations } from "@/src/app/actions/recommendations";
import { getUserRatings } from "@/src/app/actions/ratings";
import type { AlgorithmType } from "@/lib/recommender";

// Force dynamic rendering (uses auth and database)
export const dynamic = "force-dynamic";

interface RecommendationsPageProps {
  searchParams: Promise<{ algo?: AlgorithmType }>;
}

const algorithms: { id: AlgorithmType; name: string; icon: typeof Sparkles; description: string }[] = [
  {
    id: "popularity",
    name: "Popular",
    icon: TrendingUp,
    description: "Top-rated games loved by the community",
  },
  {
    id: "content-based",
    name: "Content",
    icon: Brain,
    description: "Based on categories and mechanics you like",
  },
  {
    id: "knn",
    name: "Similar",
    icon: Sparkles,
    description: "Games similar to ones you rated highly",
  },
  {
    id: "collaborative",
    name: "Users",
    icon: Users,
    description: "What users like you also enjoyed",
  },
];

export default async function RecommendationsPage({ searchParams }: RecommendationsPageProps) {
  const params = await searchParams;
  const selectedAlgo = params.algo || "popularity";
  const ratings = await getUserRatings();
  const { recommendations, error } = await getRecommendations(selectedAlgo);

  const needsMoreRatings = ratings.length < 5;

  return (
    <div className="flex min-h-screen flex-col">
      <Header />

      <main className="container flex-1 py-4 px-4 sm:py-8 sm:px-6">
        <h1 className="mb-2 text-2xl sm:text-3xl font-bold">Recommendations</h1>
        <p className="mb-4 sm:mb-6 text-sm sm:text-base text-muted-foreground">
          Games you might enjoy based on your preferences
        </p>

        {needsMoreRatings && (
          <Card className="mb-4 sm:mb-6 border-yellow-200 bg-yellow-50">
            <CardContent className="flex flex-col sm:flex-row items-start sm:items-center gap-3 sm:gap-4 p-3 sm:p-4">
              <Star className="h-6 w-6 sm:h-8 sm:w-8 text-yellow-600 flex-shrink-0" />
              <div className="flex-1">
                <p className="text-sm sm:text-base font-medium">Rate more games for better recommendations</p>
                <p className="text-xs sm:text-sm text-muted-foreground">
                  You&apos;ve rated {ratings.length} games. Rate at least 5 to unlock personalized recommendations.
                </p>
              </div>
              <Link href="/games" className="w-full sm:w-auto sm:ml-auto">
                <Button variant="outline" size="sm" className="w-full sm:w-auto text-xs sm:text-sm">
                  Browse Games
                </Button>
              </Link>
            </CardContent>
          </Card>
        )}

        {/* Algorithm Selector */}
        <div className="mb-6 sm:mb-8 grid grid-cols-2 sm:grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
          {algorithms.map((algo) => {
            const Icon = algo.icon;
            const isSelected = selectedAlgo === algo.id;
            return (
              <Link key={algo.id} href={`/recommendations?algo=${algo.id}`}>
                <Card
                  className={`cursor-pointer transition-colors ${
                    isSelected ? "border-primary bg-primary/5" : "hover:bg-muted/50"
                  }`}
                >
                  <CardHeader className="pb-2 p-3 sm:p-6">
                    <div className="flex items-center gap-2">
                      <Icon className={`h-4 w-4 sm:h-5 sm:w-5 ${isSelected ? "text-primary" : ""}`} />
                      <CardTitle className="text-sm sm:text-base">{algo.name}</CardTitle>
                    </div>
                  </CardHeader>
                  <CardContent className="p-3 pt-0 sm:p-6 sm:pt-0">
                    <p className="text-[10px] sm:text-xs text-muted-foreground">{algo.description}</p>
                  </CardContent>
                </Card>
              </Link>
            );
          })}
        </div>

        {error ? (
          <div className="py-8 sm:py-12 text-center">
            <p className="text-sm sm:text-lg text-muted-foreground">{error}</p>
          </div>
        ) : recommendations.length === 0 ? (
          <div className="py-8 sm:py-12 text-center">
            <p className="mb-4 text-sm sm:text-lg text-muted-foreground">
              No recommendations available yet.
            </p>
            <Link href="/games">
              <Button size="sm" className="text-xs sm:text-sm">Browse Games</Button>
            </Link>
          </div>
        ) : (
          <div className="grid grid-cols-2 gap-3 sm:gap-4 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-5">
            {recommendations.map((rec) => (
              <GameCard
                key={rec.gameId}
                game={{
                  ...rec,
                  rank: rec.rank || undefined,
                }}
              />
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
