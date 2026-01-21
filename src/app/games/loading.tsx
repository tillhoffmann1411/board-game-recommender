import { Header } from "@/src/components/header";
import { GameCardSkeleton } from "@/src/components/game-card";
import { Skeleton } from "@/src/components/ui/skeleton";

export default function GamesLoading() {
  return (
    <div className="flex min-h-screen flex-col bg-gradient-to-b from-purple-50/30 via-white to-white">
      <Header />

      <main className="flex-1 py-8">
        <div className="container">
          {/* Page Header Skeleton */}
          <div className="mb-8">
            <div className="flex items-center gap-3 mb-2">
              <Skeleton className="h-10 w-10 rounded-xl" />
              <Skeleton className="h-9 w-48" />
            </div>
            <Skeleton className="h-5 w-96" />
          </div>

          {/* Search Form Skeleton */}
          <div className="mb-8">
            <Skeleton className="h-12 w-full max-w-xl rounded-xl" />
          </div>

          {/* Games Grid Skeleton */}
          <div className="mb-6">
            <Skeleton className="h-6 w-32 mb-6" />
          </div>

          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-5">
            {Array.from({ length: 12 }).map((_, i) => (
              <GameCardSkeleton key={i} />
            ))}
          </div>
        </div>
      </main>
    </div>
  );
}
