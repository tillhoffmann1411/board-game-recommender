import { Header } from "@/src/components/header";
import { Skeleton } from "@/src/components/ui/skeleton";
import { Card, CardContent, CardHeader } from "@/src/components/ui/card";

export default function GameDetailLoading() {
  return (
    <div className="flex min-h-screen flex-col">
      <Header />

      <main className="container flex-1 py-8">
        <div className="grid gap-8 lg:grid-cols-3">
          {/* Game Image Skeleton */}
          <div className="lg:col-span-1">
            <Skeleton className="aspect-square w-full rounded-lg" />

            {/* Quick Stats Skeleton */}
            <Card className="mt-4">
              <CardContent className="grid grid-cols-2 gap-4 p-4">
                {Array.from({ length: 4 }).map((_, i) => (
                  <div key={i} className="flex items-center gap-2">
                    <Skeleton className="h-5 w-5 rounded" />
                    <div className="flex-1">
                      <Skeleton className="h-3 w-16 mb-2" />
                      <Skeleton className="h-4 w-12" />
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>
          </div>

          {/* Game Details Skeleton */}
          <div className="lg:col-span-2">
            <Skeleton className="h-9 w-3/4 mb-4" />

            {/* Rating Skeleton */}
            <div className="mb-4 flex items-center gap-4">
              <Skeleton className="h-8 w-24" />
              <Skeleton className="h-5 w-32" />
            </div>

            {/* Categories Skeleton */}
            <div className="mb-4">
              <Skeleton className="h-5 w-24 mb-2" />
              <div className="flex flex-wrap gap-2">
                {Array.from({ length: 5 }).map((_, i) => (
                  <Skeleton key={i} className="h-6 w-20 rounded-full" />
                ))}
              </div>
            </div>

            {/* Description Skeleton */}
            <div className="mb-6">
              <Skeleton className="h-5 w-32 mb-2" />
              <Skeleton className="h-4 w-full mb-2" />
              <Skeleton className="h-4 w-full mb-2" />
              <Skeleton className="h-4 w-3/4" />
            </div>

            {/* Rate This Game Skeleton */}
            <Card className="mt-6">
              <CardHeader>
                <Skeleton className="h-6 w-40" />
              </CardHeader>
              <CardContent>
                <Skeleton className="h-10 w-full" />
              </CardContent>
            </Card>
          </div>
        </div>
      </main>
    </div>
  );
}
