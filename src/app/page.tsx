import Link from "next/link";
import { SignedIn, SignedOut } from "@clerk/nextjs";
import { Dice1, Dice2, Dice3, Dice4, Dice5, Dice6, Search, Star, Sparkles, ArrowRight, Users, Brain, Zap } from "lucide-react";
import { Header } from "@/src/components/header";
import { Button } from "@/src/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/src/components/ui/card";

// Force dynamic rendering (uses Clerk auth)
export const dynamic = "force-dynamic";

export default function HomePage() {
  return (
    <div className="flex min-h-screen flex-col bg-gradient-to-b from-purple-50/50 via-white to-pink-50/30">
      <Header />

      <main className="flex-1">
        {/* Hero Section */}
        <section className="relative overflow-hidden">
          {/* Background decoration */}
          <div className="absolute inset-0 -z-10">
            <div className="absolute top-20 left-10 w-72 h-72 bg-purple-300 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-pulse" />
            <div className="absolute top-40 right-10 w-72 h-72 bg-pink-300 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-pulse delay-1000" />
            <div className="absolute bottom-20 left-1/3 w-72 h-72 bg-orange-300 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-pulse delay-500" />
          </div>

          <div className="container flex flex-col items-center justify-center gap-8 py-20 md:py-32 text-center">
            {/* Floating dice decoration */}
            <div className="flex items-center gap-2 text-purple-400/60">
              <Dice1 className="h-6 w-6 animate-bounce delay-100" />
              <Dice3 className="h-8 w-8 animate-bounce delay-200" />
              <Dice5 className="h-6 w-6 animate-bounce delay-300" />
            </div>

            <div className="space-y-4">
              <h1 className="text-4xl font-extrabold tracking-tight sm:text-5xl md:text-6xl lg:text-7xl">
                <span className="bg-gradient-to-r from-purple-600 via-pink-500 to-orange-400 bg-clip-text text-transparent">
                  Board Game
                </span>
                <br />
                <span className="text-gray-900">Recommender</span>
              </h1>

              <p className="mx-auto max-w-[600px] text-lg text-gray-600 sm:text-xl">
                Discover your next favorite board game. Rate games you&apos;ve played and
                get <span className="font-semibold text-purple-600">personalized recommendations</span> powered by smart algorithms.
              </p>
            </div>

            <div className="flex flex-col sm:flex-row gap-4 mt-4">
              <SignedOut>
                <Link href="/sign-up">
                  <Button size="lg" className="rounded-full bg-gradient-to-r from-purple-600 to-pink-500 hover:from-purple-700 hover:to-pink-600 text-white px-8 shadow-lg shadow-purple-500/25 transition-all hover:shadow-xl hover:shadow-purple-500/30 hover:-translate-y-0.5">
                    Get Started Free
                    <ArrowRight className="ml-2 h-4 w-4" />
                  </Button>
                </Link>
                <Link href="/games">
                  <Button variant="outline" size="lg" className="rounded-full px-8 border-2 hover:bg-purple-50">
                    Browse Games
                  </Button>
                </Link>
              </SignedOut>
              <SignedIn>
                <Link href="/recommendations">
                  <Button size="lg" className="rounded-full bg-gradient-to-r from-purple-600 to-pink-500 hover:from-purple-700 hover:to-pink-600 text-white px-8 shadow-lg shadow-purple-500/25 transition-all hover:shadow-xl hover:shadow-purple-500/30 hover:-translate-y-0.5">
                    View Recommendations
                    <Sparkles className="ml-2 h-4 w-4" />
                  </Button>
                </Link>
                <Link href="/ratings">
                  <Button variant="outline" size="lg" className="rounded-full px-8 border-2 hover:bg-purple-50">
                    My Ratings
                  </Button>
                </Link>
              </SignedIn>
            </div>

            {/* Stats */}
            <div className="flex flex-wrap justify-center gap-8 mt-8 pt-8 border-t border-purple-100">
              <div className="text-center">
                <div className="text-3xl font-bold text-purple-600">20,000+</div>
                <div className="text-sm text-gray-500">Board Games</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-pink-500">4</div>
                <div className="text-sm text-gray-500">Algorithms</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-orange-500">100%</div>
                <div className="text-sm text-gray-500">Free</div>
              </div>
            </div>
          </div>
        </section>

        {/* Features Section */}
        <section className="container py-20">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">How It Works</h2>
            <p className="text-gray-600 max-w-2xl mx-auto">
              Get personalized board game recommendations in three simple steps
            </p>
          </div>

          <div className="grid gap-8 md:grid-cols-3">
            <Card className="relative overflow-hidden border-2 border-purple-100 bg-white shadow-lg hover:shadow-xl transition-all hover:-translate-y-1 group">
              <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-purple-500/10 to-transparent rounded-bl-full" />
              <CardHeader>
                <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-purple-500 to-purple-600 flex items-center justify-center mb-4 shadow-lg shadow-purple-500/25 group-hover:scale-110 transition-transform">
                  <Search className="h-7 w-7 text-white" />
                </div>
                <CardTitle className="text-xl">Browse Games</CardTitle>
                <CardDescription className="text-base">
                  Explore our catalog of 20,000+ board games with detailed information,
                  ratings, and categories.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Link href="/games">
                  <Button variant="ghost" className="p-0 h-auto text-purple-600 hover:text-purple-700 group/btn">
                    Browse catalog
                    <ArrowRight className="ml-2 h-4 w-4 transition-transform group-hover/btn:translate-x-1" />
                  </Button>
                </Link>
              </CardContent>
            </Card>

            <Card className="relative overflow-hidden border-2 border-pink-100 bg-white shadow-lg hover:shadow-xl transition-all hover:-translate-y-1 group">
              <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-pink-500/10 to-transparent rounded-bl-full" />
              <CardHeader>
                <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-pink-500 to-pink-600 flex items-center justify-center mb-4 shadow-lg shadow-pink-500/25 group-hover:scale-110 transition-transform">
                  <Star className="h-7 w-7 text-white" />
                </div>
                <CardTitle className="text-xl">Rate Your Games</CardTitle>
                <CardDescription className="text-base">
                  Rate board games you&apos;ve played on a scale of 1-10 to build
                  your personal preference profile.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <SignedIn>
                  <Link href="/ratings">
                    <Button variant="ghost" className="p-0 h-auto text-pink-600 hover:text-pink-700 group/btn">
                      Start rating
                      <ArrowRight className="ml-2 h-4 w-4 transition-transform group-hover/btn:translate-x-1" />
                    </Button>
                  </Link>
                </SignedIn>
                <SignedOut>
                  <Link href="/sign-up">
                    <Button variant="ghost" className="p-0 h-auto text-pink-600 hover:text-pink-700 group/btn">
                      Sign up to rate
                      <ArrowRight className="ml-2 h-4 w-4 transition-transform group-hover/btn:translate-x-1" />
                    </Button>
                  </Link>
                </SignedOut>
              </CardContent>
            </Card>

            <Card className="relative overflow-hidden border-2 border-orange-100 bg-white shadow-lg hover:shadow-xl transition-all hover:-translate-y-1 group">
              <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-orange-500/10 to-transparent rounded-bl-full" />
              <CardHeader>
                <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-orange-500 to-orange-600 flex items-center justify-center mb-4 shadow-lg shadow-orange-500/25 group-hover:scale-110 transition-transform">
                  <Sparkles className="h-7 w-7 text-white" />
                </div>
                <CardTitle className="text-xl">Get Recommendations</CardTitle>
                <CardDescription className="text-base">
                  Receive personalized game suggestions based on your ratings
                  using multiple smart algorithms.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <SignedIn>
                  <Link href="/recommendations">
                    <Button variant="ghost" className="p-0 h-auto text-orange-600 hover:text-orange-700 group/btn">
                      View recommendations
                      <ArrowRight className="ml-2 h-4 w-4 transition-transform group-hover/btn:translate-x-1" />
                    </Button>
                  </Link>
                </SignedIn>
                <SignedOut>
                  <Link href="/sign-up">
                    <Button variant="ghost" className="p-0 h-auto text-orange-600 hover:text-orange-700 group/btn">
                      Get recommendations
                      <ArrowRight className="ml-2 h-4 w-4 transition-transform group-hover/btn:translate-x-1" />
                    </Button>
                  </Link>
                </SignedOut>
              </CardContent>
            </Card>
          </div>
        </section>

        {/* Algorithms Section */}
        <section className="bg-gradient-to-br from-purple-900 via-purple-800 to-pink-900 py-20">
          <div className="container">
            <div className="text-center mb-12">
              <h2 className="text-3xl font-bold text-white mb-4">
                Powered by Smart Algorithms
              </h2>
              <p className="text-purple-200 max-w-2xl mx-auto">
                Our recommendation engine uses multiple algorithms to find the perfect games for you
              </p>
            </div>

            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
              {[
                {
                  name: "Collaborative",
                  description: "Finds users with similar tastes and recommends games they loved.",
                  icon: Users,
                  color: "from-blue-400 to-blue-500",
                },
                {
                  name: "Content-Based",
                  description: "Analyzes game categories and mechanics you prefer.",
                  icon: Brain,
                  color: "from-green-400 to-green-500",
                },
                {
                  name: "KNN Similarity",
                  description: "Uses item-to-item similarity to predict your ratings.",
                  icon: Zap,
                  color: "from-yellow-400 to-orange-500",
                },
                {
                  name: "Popularity",
                  description: "Shows trending games loved by the community.",
                  icon: Star,
                  color: "from-pink-400 to-pink-500",
                },
              ].map((algo) => {
                const Icon = algo.icon;
                return (
                  <Card key={algo.name} className="bg-white/10 backdrop-blur-sm border-white/20 hover:bg-white/15 transition-all hover:-translate-y-1">
                    <CardHeader className="pb-2">
                      <div className={`w-10 h-10 rounded-xl bg-gradient-to-br ${algo.color} flex items-center justify-center mb-3`}>
                        <Icon className="h-5 w-5 text-white" />
                      </div>
                      <CardTitle className="text-lg text-white">{algo.name}</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="text-sm text-purple-200">
                        {algo.description}
                      </p>
                    </CardContent>
                  </Card>
                );
              })}
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="container py-20">
          <div className="relative overflow-hidden rounded-3xl bg-gradient-to-r from-purple-600 via-pink-500 to-orange-400 p-12 text-center text-white shadow-2xl">
            <div className="absolute inset-0 bg-black/10" />
            <div className="relative">
              <div className="flex justify-center gap-2 mb-6">
                <Dice2 className="h-8 w-8 animate-bounce delay-100" />
                <Dice4 className="h-10 w-10 animate-bounce delay-200" />
                <Dice6 className="h-8 w-8 animate-bounce delay-300" />
              </div>
              <h2 className="text-3xl md:text-4xl font-bold mb-4">
                Ready to find your next favorite game?
              </h2>
              <p className="text-lg text-white/90 mb-8 max-w-xl mx-auto">
                Join thousands of board game enthusiasts and get personalized recommendations today.
              </p>
              <SignedOut>
                <Link href="/sign-up">
                  <Button size="lg" className="rounded-full bg-white text-purple-600 hover:bg-gray-100 px-8 font-semibold shadow-lg">
                    Get Started Free
                    <ArrowRight className="ml-2 h-4 w-4" />
                  </Button>
                </Link>
              </SignedOut>
              <SignedIn>
                <Link href="/recommendations">
                  <Button size="lg" className="rounded-full bg-white text-purple-600 hover:bg-gray-100 px-8 font-semibold shadow-lg">
                    View My Recommendations
                    <Sparkles className="ml-2 h-4 w-4" />
                  </Button>
                </Link>
              </SignedIn>
            </div>
          </div>
        </section>
      </main>

      <footer className="border-t bg-gray-50 py-8">
        <div className="container text-center">
          <div className="flex items-center justify-center gap-2 mb-2">
            <div className="rounded-lg bg-gradient-to-br from-purple-600 to-pink-500 p-1.5">
              <Dice6 className="h-4 w-4 text-white" />
            </div>
            <span className="font-semibold text-gray-900">Board Game Recommender</span>
          </div>
          <p className="text-sm text-gray-500">
            Discover your next adventure in board gaming
          </p>
        </div>
      </footer>
    </div>
  );
}
