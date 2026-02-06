import { Suspense } from "react";
import Link from "next/link";
import { Search, Sparkles, ChevronLeft, ChevronRight, X } from "lucide-react";
import { Header } from "@/src/components/header";
import { GameCard, GameCardSkeleton } from "@/src/components/game-card";
import { Input } from "@/src/components/ui/input";
import { Button } from "@/src/components/ui/button";
import { Badge } from "@/src/components/ui/badge";
import { GamesSortDropdown } from "@/src/components/games-sort-dropdown";
import { GamesFilters } from "@/src/components/games-filters";
import { Filter, Sort } from "mongodb";
import { getDb } from "@/lib/db/client";
import { COLLECTIONS } from "@/lib/db/schema";
import type { Game, GameSummary } from "@/lib/db/schema";

// Force dynamic rendering (uses database)
export const dynamic = "force-dynamic";

const SORT_OPTIONS = [
  { value: "popular", label: "Most popular", sort: { "bggRating.count": -1 } as Sort },
  { value: "rating", label: "Top rated", sort: { "bggRating.average": -1 } as Sort },
  { value: "name-asc", label: "Name A–Z", sort: { name: 1 } as Sort },
  { value: "name-desc", label: "Name Z–A", sort: { name: -1 } as Sort },
  { value: "newest", label: "Newest", sort: { yearPublished: -1 } as Sort },
  { value: "oldest", label: "Oldest", sort: { yearPublished: 1 } as Sort },
  { value: "complexity", label: "Complexity", sort: { complexity: -1 } as Sort },
] as const;

function getSortForKey(value: string): Sort | null {
  const option = SORT_OPTIONS.find((o) => o.value === value);
  return option ? option.sort : null;
}

/** Time presets for filter (minutes). "Any" has no min/max so no time filter is applied. */
const TIME_PRESETS: Array<
  { value: string; label: string; min?: number; max?: number }
> = [
  { value: "", label: "Any" },
  { value: "under30", label: "Under 30 min", min: 0, max: 30 },
  { value: "30-60", label: "30–60 min", min: 30, max: 60 },
  { value: "60-120", label: "1–2 hours", min: 60, max: 120 },
  { value: "120+", label: "2+ hours", min: 120, max: 9999 },
];

interface GamesPageProps {
  searchParams: Promise<{
    q?: string;
    page?: string;
    sort?: string;
    players?: string;
    time?: string;
    categories?: string;
    mechanics?: string;
  }>;
}

/** Serialized game for client components (ObjectId -> string) */
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

interface GamesFilters {
  players?: number;
  time?: string;
  categories?: string[];
  mechanics?: string[];
}

function applyFilters(base: Filter<Game>, filters: GamesFilters): Filter<Game> {
  const conditions: Filter<Game>[] = [base];
  if (filters.players != null) {
    const n = filters.players;
    conditions.push({
      $and: [
        { $or: [{ minPlayers: null }, { minPlayers: { $lte: n } }] },
        { $or: [{ maxPlayers: null }, { maxPlayers: { $gte: n } }] },
      ],
    } as Filter<Game>);
  }
  const timePreset = TIME_PRESETS.find((p) => p.value === filters.time);
  if (timePreset && timePreset.min != null) {
    conditions.push({
      $and: [
        { $or: [{ minPlaytime: null }, { minPlaytime: { $lte: timePreset.max } }] },
        { $or: [{ maxPlaytime: null }, { maxPlaytime: { $gte: timePreset.min } }] },
      ],
    } as Filter<Game>);
  }
  if (filters.categories?.length) {
    conditions.push({ categories: { $in: filters.categories } });
  }
  if (filters.mechanics?.length) {
    conditions.push({ mechanics: { $in: filters.mechanics } });
  }
  if (conditions.length === 1) return base;
  return { $and: conditions };
}

async function getFilterOptions(): Promise<{
  categories: string[];
  mechanics: string[];
}> {
  const db = await getDb();
  const collection = db.collection<Game>(COLLECTIONS.GAMES);
  const [categories, mechanics] = await Promise.all([
    collection.distinct("categories").then((arr) => arr.filter(Boolean).sort()),
    collection.distinct("mechanics").then((arr) => arr.filter(Boolean).sort()),
  ]);
  return { categories, mechanics };
}

async function getGames(
  query?: string,
  page: number = 1,
  limit: number = 24,
  sortValue?: string,
  filters: GamesFilters = {}
): Promise<{ games: SerializedGameSummary[]; total: number }> {
  const db = await getDb();
  const collection = db.collection<Game>(COLLECTIONS.GAMES);

  const skip = (page - 1) * limit;

  let baseFilter: Filter<Game> = {};
  if (query) {
    baseFilter = { name: { $regex: query, $options: "i" } };
  }
  const filter = applyFilters(baseFilter, filters);

  const explicitSort = getSortForKey(sortValue || "");
  const sort: Sort = explicitSort ?? { "bggRating.count": -1 };

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
          thumbnailUrl: 1,
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
    <div className="grid grid-cols-2 gap-3 sm:gap-4 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-5">
      {games.map((game) => (
        <GameCard key={game._id} game={game} />
      ))}
    </div>
  );
}

function GamesGridSkeleton() {
  return (
    <div className="grid grid-cols-2 gap-3 sm:gap-4 lg:grid-cols-3 xl:grid-cols-4">
      {Array.from({ length: 12 }).map((_, i) => (
        <GameCardSkeleton key={i} />
      ))}
    </div>
  );
}

function buildGamesUrl({
  q,
  page,
  sort,
  players,
  time,
  categories,
  mechanics,
}: {
  q?: string;
  page?: number;
  sort?: string;
  players?: number;
  time?: string;
  categories?: string[];
  mechanics?: string[];
}) {
  const params = new URLSearchParams();
  if (q) params.set("q", q);
  if (page && page > 1) params.set("page", String(page));
  if (sort && sort !== "popular") params.set("sort", sort);
  if (players != null) params.set("players", String(players));
  if (time) params.set("time", time);
  if (categories?.length) params.set("categories", categories.join(","));
  if (mechanics?.length) params.set("mechanics", mechanics.join(","));
  const s = params.toString();
  return s ? `/games?${s}` : "/games";
}

async function GamesContent({
  query,
  page,
  sort: sortValue,
  filters,
}: {
  query?: string;
  page: number;
  sort?: string;
  filters: GamesFilters;
}) {
  const { games, total } = await getGames(query, page, 24, sortValue, filters);
  const totalPages = Math.ceil(total / 24);
  const urlOpts = {
    q: query,
    sort: sortValue,
    players: filters.players,
    time: filters.time,
    categories: filters.categories,
    mechanics: filters.mechanics,
  };

  return (
    <>
      <div className="mb-4 sm:mb-6 flex items-center justify-between">
        <p className="text-sm sm:text-base text-gray-600">
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
        <div className="mt-8 sm:mt-12 flex flex-wrap items-center justify-center gap-2">
          {page > 1 ? (
            <Link href={buildGamesUrl({ ...urlOpts, page: page - 1 })}>
              <Button variant="outline" size="sm" className="gap-1 text-xs sm:text-sm">
                <ChevronLeft className="h-3 w-3 sm:h-4 sm:w-4" />
                Previous
              </Button>
            </Link>
          ) : (
            <Button variant="outline" size="sm" className="gap-1 text-xs sm:text-sm" disabled>
              <ChevronLeft className="h-3 w-3 sm:h-4 sm:w-4" />
              Previous
            </Button>
          )}

          <div className="flex items-center gap-1 px-2 sm:px-4">
            <span className="text-xs sm:text-sm text-gray-500">Page</span>
            <span className="text-sm sm:text-base font-semibold text-purple-600">{page}</span>
            <span className="text-xs sm:text-sm text-gray-500">of</span>
            <span className="text-sm sm:text-base font-semibold text-purple-600">{totalPages}</span>
          </div>

          {page < totalPages ? (
            <Link href={buildGamesUrl({ ...urlOpts, page: page + 1 })}>
              <Button variant="outline" size="sm" className="gap-1 text-xs sm:text-sm">
                Next
                <ChevronRight className="h-3 w-3 sm:h-4 sm:w-4" />
              </Button>
            </Link>
          ) : (
            <Button variant="outline" size="sm" className="gap-1 text-xs sm:text-sm" disabled>
              Next
              <ChevronRight className="h-3 w-3 sm:h-4 sm:w-4" />
            </Button>
          )}
        </div>
      )}
    </>
  );
}

function parseFiltersFromParams(params: Awaited<GamesPageProps["searchParams"]>): GamesFilters {
  const playersParam = params.players;
  const players =
    playersParam != null && playersParam !== ""
      ? parseInt(playersParam, 10)
      : undefined;
  const time = params.time && params.time !== "" ? params.time : undefined;
  const categories = params.categories
    ? params.categories.split(",").map((s) => s.trim()).filter(Boolean)
    : undefined;
  const mechanics = params.mechanics
    ? params.mechanics.split(",").map((s) => s.trim()).filter(Boolean)
    : undefined;
  return {
    ...(players != null && !Number.isNaN(players) && players >= 1 && players <= 8
      ? { players }
      : {}),
    ...(time ? { time } : {}),
    ...(categories?.length ? { categories } : {}),
    ...(mechanics?.length ? { mechanics } : {}),
  };
}

export default async function GamesPage({ searchParams }: GamesPageProps) {
  const params = await searchParams;
  const query = params.q;
  const page = parseInt(params.page || "1", 10);
  const sort = params.sort || "popular";
  const filters = parseFiltersFromParams(params);

  const filterOptions = await getFilterOptions();

  return (
    <div className="flex min-h-screen flex-col bg-gradient-to-b from-purple-50/30 via-white to-white">
      <Header />

      <main className="flex-1 py-4 px-4 sm:py-8 sm:px-6">
        <div className="container">
          {/* Page Header */}
          <div className="mb-6 sm:mb-8">
            <div className="flex items-center gap-2 sm:gap-3 mb-2">
              <div className="p-1.5 sm:p-2 rounded-xl bg-gradient-to-br from-purple-500 to-pink-500">
                <Sparkles className="h-4 w-4 sm:h-6 sm:w-6 text-white" />
              </div>
              <h1 className="text-2xl sm:text-3xl font-bold text-gray-900">Browse Games</h1>
            </div>
            <p className="text-sm sm:text-base text-gray-600">
              Explore our collection of board games and find your next favorite
            </p>
          </div>

          {/* Search Form */}
          <form action="/games" method="GET" className="mb-4 sm:mb-6">
            <div className="relative max-w-xl">
              <Search className="absolute left-3 sm:left-4 top-1/2 h-4 w-4 sm:h-5 sm:w-5 -translate-y-1/2 text-gray-400" />
              <Input
                name="q"
                placeholder="Search for board games..."
                defaultValue={query}
                className="pl-10 sm:pl-12 h-12 sm:h-14 text-base sm:text-lg border-2 border-gray-200 focus:border-purple-400 rounded-xl shadow-sm"
              />
              <Button
                type="submit"
                size="sm"
                className="absolute right-1.5 sm:right-2 top-1/2 -translate-y-1/2 rounded-lg bg-gradient-to-r from-purple-600 to-pink-500 hover:from-purple-700 hover:to-pink-600 text-xs sm:text-sm"
              >
                Search
              </Button>
            </div>
            {query && (
              <div className="mt-2 flex items-center gap-1">
                <Badge variant="secondary" className="gap-1.5 py-1 pr-1 pl-2.5 text-sm font-medium">
                  <span>{query}</span>
                  <Link
                    href={buildGamesUrl({
                      sort: sort !== "popular" ? sort : undefined,
                      players: filters.players,
                      time: filters.time,
                      categories: filters.categories,
                      mechanics: filters.mechanics,
                    })}
                    className="inline-flex rounded-full p-0.5 hover:bg-muted focus:outline-none focus:ring-2 focus:ring-ring"
                    aria-label={`Clear search "${query}"`}
                  >
                    <X className="h-3.5 w-3.5" />
                  </Link>
                </Badge>
              </div>
            )}
            {sort !== "popular" && <input type="hidden" name="sort" value={sort} />}
            {filters.players != null && (
              <input type="hidden" name="players" value={String(filters.players)} />
            )}
            {filters.time && <input type="hidden" name="time" value={filters.time} />}
            {filters.categories?.length && (
              <input type="hidden" name="categories" value={filters.categories.join(",")} />
            )}
            {filters.mechanics?.length && (
              <input type="hidden" name="mechanics" value={filters.mechanics.join(",")} />
            )}
          </form>

          {/* Active filter badges */}
          {(filters.players != null ||
            filters.time ||
            (filters.categories?.length ?? 0) > 0 ||
            (filters.mechanics?.length ?? 0) > 0) && (
            <div className="mt-2 flex flex-wrap items-center gap-1.5">
              {filters.players != null && (
                <Badge variant="secondary" className="gap-1.5 py-1 pr-1 pl-2.5 text-sm font-medium">
                  <span>Players: {filters.players}</span>
                  <Link
                    href={buildGamesUrl({
                      q: query,
                      sort: sort !== "popular" ? sort : undefined,
                      time: filters.time,
                      categories: filters.categories,
                      mechanics: filters.mechanics,
                    })}
                    className="inline-flex rounded-full p-0.5 hover:bg-muted focus:outline-none focus:ring-2 focus:ring-ring"
                    aria-label={`Remove players filter`}
                  >
                    <X className="h-3.5 w-3.5" />
                  </Link>
                </Badge>
              )}
              {filters.time && (
                <Badge variant="secondary" className="gap-1.5 py-1 pr-1 pl-2.5 text-sm font-medium">
                  <span>
                    Time: {TIME_PRESETS.find((p) => p.value === filters.time)?.label ?? filters.time}
                  </span>
                  <Link
                    href={buildGamesUrl({
                      q: query,
                      sort: sort !== "popular" ? sort : undefined,
                      players: filters.players,
                      categories: filters.categories,
                      mechanics: filters.mechanics,
                    })}
                    className="inline-flex rounded-full p-0.5 hover:bg-muted focus:outline-none focus:ring-2 focus:ring-ring"
                    aria-label={`Remove time filter`}
                  >
                    <X className="h-3.5 w-3.5" />
                  </Link>
                </Badge>
              )}
              {filters.categories?.map((cat) => {
                const next = filters.categories!.filter((c) => c !== cat);
                return (
                  <Badge
                    key={cat}
                    variant="secondary"
                    className="gap-1.5 py-1 pr-1 pl-2.5 text-sm font-medium"
                  >
                    <span>{cat}</span>
                    <Link
                      href={buildGamesUrl({
                        q: query,
                        sort: sort !== "popular" ? sort : undefined,
                        players: filters.players,
                        time: filters.time,
                        categories: next.length ? next : undefined,
                        mechanics: filters.mechanics,
                      })}
                      className="inline-flex rounded-full p-0.5 hover:bg-muted focus:outline-none focus:ring-2 focus:ring-ring"
                      aria-label={`Remove category ${cat}`}
                    >
                      <X className="h-3.5 w-3.5" />
                    </Link>
                  </Badge>
                );
              })}
              {filters.mechanics?.map((mech) => {
                const next = filters.mechanics!.filter((m) => m !== mech);
                return (
                  <Badge
                    key={mech}
                    variant="secondary"
                    className="gap-1.5 py-1 pr-1 pl-2.5 text-sm font-medium"
                  >
                    <span>{mech}</span>
                    <Link
                      href={buildGamesUrl({
                        q: query,
                        sort: sort !== "popular" ? sort : undefined,
                        players: filters.players,
                        time: filters.time,
                        categories: filters.categories,
                        mechanics: next.length ? next : undefined,
                      })}
                      className="inline-flex rounded-full p-0.5 hover:bg-muted focus:outline-none focus:ring-2 focus:ring-ring"
                      aria-label={`Remove mechanic ${mech}`}
                    >
                      <X className="h-3.5 w-3.5" />
                    </Link>
                  </Badge>
                );
              })}
            </div>
          )}

          {/* Filters + Sort */}
          <div className="mb-6 sm:mb-8 space-y-3">
            <div>
              <p className="text-xs sm:text-sm text-gray-500 mb-2">Filters</p>
              <GamesFilters
                query={query}
                sort={sort}
                players={filters.players}
                time={filters.time}
                categories={filters.categories}
                mechanics={filters.mechanics}
                categoryOptions={filterOptions.categories}
                mechanicsOptions={filterOptions.mechanics}
              />
            </div>
            <div>
              <p className="text-xs sm:text-sm text-gray-500 mb-2">Sort by</p>
              <GamesSortDropdown
                options={SORT_OPTIONS.map((o) => ({ value: o.value, label: o.label }))}
                currentSort={sort || "popular"}
                query={query}
                filters={{
                  players: filters.players,
                  time: filters.time,
                  categories: filters.categories,
                  mechanics: filters.mechanics,
                }}
              />
            </div>
          </div>

          <Suspense fallback={<GamesGridSkeleton />}>
            <GamesContent query={query} page={page} sort={sort} filters={filters} />
          </Suspense>
        </div>
      </main>
    </div>
  );
}
