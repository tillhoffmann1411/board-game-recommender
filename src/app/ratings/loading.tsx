import { Header } from "@/src/components/header";
import { Skeleton } from "@/src/components/ui/skeleton";
import { Card, CardContent } from "@/src/components/ui/card";

export default function RatingsLoading() {
  return (
    <div className="flex min-h-screen flex-col">
      <Header />

      <main className="container flex-1 py-8">
        {/* Page Header Skeleton */}
        <Skeleton className="h-9 w-40 mb-6" />

        {/* Ratings Grid Skeleton */}
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <Card key={i} className="overflow-hidden">
              <CardContent className="flex items-center gap-4 p-4">
                <Skeleton className="h-16 w-16 rounded-md shrink-0" />
                <div className="flex-1">
                  <Skeleton className="h-5 w-3/4 mb-2" />
                  <Skeleton className="h-4 w-20" />
                </div>
                <Skeleton className="h-8 w-8 rounded" />
              </CardContent>
            </Card>
          ))}
        </div>
      </main>
    </div>
  );
}
