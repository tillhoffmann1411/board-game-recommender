import { Suspense } from "react";
import { Search, Sparkles, ChevronLeft, ChevronRight } from "lucide-react";
import { Header } from "@/src/components/header";
import { GameCard, GameCardSkeleton } from "@/src/components/game-card";
import { Input } from "@/src/components/ui/input";
import { Button } from "@/src/components/ui/button";
import { Filter, Sort } from "mongodb";
import { getDb } from "@/lib/db/client";
import { COLLECTIONS } from "@/lib/db/schema";
import type { Game, GameSummary } from "@/lib/db/schema";

// Force dynamic rendering (uses database)
export const dynamic = "force-dynamic";

interface GamesPageProps {
  searchParams: Promise<{ q?: string; page?: string }>;
}

/** Serialized game for client components (ObjectId -> string) */
interface SerializedGameSummary {
  _id: string;
  name: string;
  imageUrl: string | null;
  yearPublished: number | null;
  minPlayers: number | null;
  maxPlayers: number | null;
  minPlaytime: number | null;
  maxPlaytime: number | null;
  complexity: number | null;
  bggRating: { average: number; count: number } | null;
  categories: string[];
}

async function getGames(
  query?: string,
  page: number = 1,
  limit: number = 24
): Promise<{ games: SerializedGameSummary[]; total: number }> {
  const db = await getDb();
  const collection = db.collection<Game>(COLLECTIONS.GAMES);

  const skip = (page - 1) * limit;

  let filter: Filter<Game> = {};
  let sort: Sort = { "bggRating.average": -1 };

  if (query) {
    // Use case-insensitive regex search instead of $text (no index required)
    filter = {
      name: { $regex: query, $options: "i" }
    };
    // Sort by name for search results to show most relevant matches first
    sort = { name: 1 };
  }

  const [rawGames, total] = await Promise.all([
    collection
      .find(filter, {
        projection: {
          _id: 1,
          name: 1,
          imageUrl: 1,
          yearPublished: 1,
          minPlayers: 1,
          maxPlayers: 1,
          minPlaytime: 1,
          maxPlaytime: 1,
          complexity: 1,
          bggRating: 1,
          categories: 1,
        },
      })
      .sort(sort)
      .skip(skip)
      .limit(limit)
      .toArray() as Promise<GameSummary[]>,
    collection.countDocuments(filter),
  ]);

  // Serialize ObjectIds for client components
  const games: SerializedGameSummary[] = rawGames.map((game) => ({
    ...game,
    _id: game._id.toString(),
  }));

  return { games, total };
}

function GamesGrid({ games }: { games: SerializedGameSummary[] }) {
  if (games.length === 0) {
    return (
      <div className="py-16 text-center">
        <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-purple-100 mb-4">
          <Search className="h-8 w-8 text-purple-500" />
        </div>
        <p className="text-lg font-medium text-gray-900">No games found</p>
        <p className="text-gray-500 mt-1">
          Try a different search term or browse all games.
        </p>
      </div>
    );
  }

  return (
    <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
      {games.map((game) => (
        <GameCard key={game._id} game={game} />
      ))}
    </div>
  );
}

function GamesGridSkeleton() {
  return (
    <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
      {Array.from({ length: 12 }).map((_, i) => (
        <GameCardSkeleton key={i} />
      ))}
    </div>
  );
}

async function GamesContent({ query, page }: { query?: string; page: number }) {
  const { games, total } = await getGames(query, page);
  const totalPages = Math.ceil(total / 24);

  return (
    <>
      <div className="mb-6 flex items-center justify-between">
        <p className="text-gray-600">
          <span className="font-semibold text-purple-600">{total.toLocaleString()}</span> games
          {query && (
            <span>
              {" "}matching <span className="font-medium">&quot;{query}&quot;</span>
            </span>
          )}
        </p>
      </div>

      <GamesGrid games={games} />

      {totalPages > 1 && (
        <div className="mt-12 flex items-center justify-center gap-2">
          {page > 1 ? (
            <a
              href={`/games?${query ? `q=${query}&` : ""}page=${page - 1}`}
            >
              <Button variant="outline" className="gap-1">
                <ChevronLeft className="h-4 w-4" />
                Previous
              </Button>
            </a>
          ) : (
            <Button variant="outline" className="gap-1" disabled>
              <ChevronLeft className="h-4 w-4" />
              Previous
            </Button>
          )}

          <div className="flex items-center gap-1 px-4">
            <span className="text-sm text-gray-500">Page</span>
            <span className="font-semibold text-purple-600">{page}</span>
            <span className="text-sm text-gray-500">of</span>
            <span className="font-semibold text-purple-600">{totalPages}</span>
          </div>

          {page < totalPages ? (
            <a
              href={`/games?${query ? `q=${query}&` : ""}page=${page + 1}`}
            >
              <Button variant="outline" className="gap-1">
                Next
                <ChevronRight className="h-4 w-4" />
              </Button>
            </a>
          ) : (
            <Button variant="outline" className="gap-1" disabled>
              Next
              <ChevronRight className="h-4 w-4" />
            </Button>
          )}
        </div>
      )}
    </>
  );
}

export default async function GamesPage({ searchParams }: GamesPageProps) {
  const params = await searchParams;
  const query = params.q;
  const page = parseInt(params.page || "1", 10);

  return (
    <div className="flex min-h-screen flex-col bg-gradient-to-b from-purple-50/30 via-white to-white">
      <Header />

      <main className="flex-1 py-8">
        <div className="container">
          {/* Page Header */}
          <div className="mb-8">
            <div className="flex items-center gap-3 mb-2">
              <div className="p-2 rounded-xl bg-gradient-to-br from-purple-500 to-pink-500">
                <Sparkles className="h-6 w-6 text-white" />
              </div>
              <h1 className="text-3xl font-bold text-gray-900">Browse Games</h1>
            </div>
            <p className="text-gray-600">
              Explore our collection of board games and find your next favorite
            </p>
          </div>

          {/* Search Form */}
          <form action="/games" method="GET" className="mb-8">
            <div className="relative max-w-xl">
              <Search className="absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-gray-400" />
              <Input
                name="q"
                placeholder="Search for board games..."
                defaultValue={query}
                className="pl-12 h-12 text-base border-2 border-gray-200 focus:border-purple-400 rounded-xl shadow-sm"
              />
              <Button
                type="submit"
                className="absolute right-2 top-1/2 -translate-y-1/2 rounded-lg bg-gradient-to-r from-purple-600 to-pink-500 hover:from-purple-700 hover:to-pink-600"
              >
                Search
              </Button>
            </div>
          </form>

          <Suspense fallback={<GamesGridSkeleton />}>
            <GamesContent query={query} page={page} />
          </Suspense>
        </div>
      </main>
    </div>
  );
}
