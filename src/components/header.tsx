"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { SignInButton, SignedIn, SignedOut, UserButton } from "@clerk/nextjs";
import { Dice6, Search, Star, Sparkles } from "lucide-react";
import { Button } from "@/src/components/ui/button";
import { cn } from "@/src/lib/utils";

const navItems = [
  { href: "/games", label: "Browse Games", icon: Search },
  { href: "/ratings", label: "My Ratings", icon: Star, authRequired: true },
  { href: "/recommendations", label: "For You", icon: Sparkles, authRequired: true },
];

export function Header() {
  const pathname = usePathname();

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-white/80 backdrop-blur-lg supports-[backdrop-filter]:bg-white/60">
      <div className="container flex h-16 items-center justify-between">
        <div className="flex items-center gap-8">
          <Link href="/" className="flex items-center gap-2 group">
            <div className="rounded-xl bg-gradient-to-br from-purple-600 to-pink-500 p-2 transition-transform group-hover:scale-110">
              <Dice6 className="h-5 w-5 text-white" />
            </div>
            <span className="hidden font-bold text-lg sm:inline-block bg-gradient-to-r from-purple-600 to-pink-500 bg-clip-text text-transparent">
              BoardGame Rec
            </span>
          </Link>

          <nav className="hidden md:flex items-center gap-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = pathname.startsWith(item.href);

              const linkContent = (
                <Link
                  key={item.href}
                  href={item.href}
                  className={cn(
                    "flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium transition-all",
                    isActive
                      ? "bg-purple-100 text-purple-700"
                      : "text-gray-600 hover:bg-gray-100 hover:text-gray-900"
                  )}
                >
                  <Icon className={cn("h-4 w-4", isActive && "text-purple-600")} />
                  <span>{item.label}</span>
                </Link>
              );

              if (item.authRequired) {
                return <SignedIn key={item.href}>{linkContent}</SignedIn>;
              }

              return linkContent;
            })}
          </nav>
        </div>

        {/* Mobile nav */}
        <nav className="flex md:hidden items-center gap-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = pathname.startsWith(item.href);

            const linkContent = (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "flex items-center justify-center p-2 rounded-full transition-all",
                  isActive
                    ? "bg-purple-100 text-purple-700"
                    : "text-gray-600 hover:bg-gray-100"
                )}
              >
                <Icon className="h-5 w-5" />
              </Link>
            );

            if (item.authRequired) {
              return <SignedIn key={item.href}>{linkContent}</SignedIn>;
            }

            return linkContent;
          })}
        </nav>

        <div className="flex items-center gap-3">
          <SignedOut>
            <SignInButton mode="modal">
              <Button
                size="sm"
                className="rounded-full bg-gradient-to-r from-purple-600 to-pink-500 hover:from-purple-700 hover:to-pink-600 text-white border-0"
              >
                Sign In
              </Button>
            </SignInButton>
          </SignedOut>
          <SignedIn>
            <UserButton
              afterSignOutUrl="/"
              appearance={{
                elements: {
                  avatarBox: "h-9 w-9 ring-2 ring-purple-200 ring-offset-2",
                },
              }}
            />
          </SignedIn>
        </div>
      </div>
    </header>
  );
}
