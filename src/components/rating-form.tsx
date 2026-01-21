"use client";

import { useState, useTransition } from "react";
import { useAuth } from "@clerk/nextjs";
import { Star } from "lucide-react";
import { Button } from "@/src/components/ui/button";
import { cn } from "@/src/lib/utils";
import { rateGame } from "@/src/app/actions/ratings";

interface RatingFormProps {
  gameId: string;
  gameName: string;
  initialRating?: number;
}

export function RatingForm({ gameId, gameName, initialRating }: RatingFormProps) {
  const { isSignedIn } = useAuth();
  const [rating, setRating] = useState(initialRating || 0);
  const [hoveredRating, setHoveredRating] = useState(0);
  const [isPending, startTransition] = useTransition();
  const [message, setMessage] = useState<{ type: "success" | "error"; text: string } | null>(null);

  if (!isSignedIn) {
    return (
      <p className="text-muted-foreground">
        Please sign in to rate this game.
      </p>
    );
  }

  const handleSubmit = () => {
    if (rating === 0) return;

    startTransition(async () => {
      const result = await rateGame(gameId, rating);
      if (result.success) {
        setMessage({ type: "success", text: "Rating saved!" });
      } else {
        setMessage({ type: "error", text: result.error || "Failed to save rating" });
      }
      setTimeout(() => setMessage(null), 3000);
    });
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2">
        <div className="flex">
          {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((value) => (
            <button
              key={value}
              type="button"
              onClick={() => setRating(value)}
              onMouseEnter={() => setHoveredRating(value)}
              onMouseLeave={() => setHoveredRating(0)}
              className="p-1 transition-transform hover:scale-110"
              disabled={isPending}
            >
              <Star
                className={cn(
                  "h-6 w-6 transition-colors",
                  (hoveredRating || rating) >= value
                    ? "fill-yellow-400 text-yellow-400"
                    : "text-muted-foreground"
                )}
              />
            </button>
          ))}
        </div>
        <span className="ml-2 text-lg font-medium">
          {hoveredRating || rating || "?"} / 10
        </span>
      </div>

      <div className="flex items-center gap-4">
        <Button
          onClick={handleSubmit}
          disabled={rating === 0 || isPending}
        >
          {isPending ? "Saving..." : initialRating ? "Update Rating" : "Submit Rating"}
        </Button>

        {message && (
          <span
            className={cn(
              "text-sm",
              message.type === "success" ? "text-green-600" : "text-red-600"
            )}
          >
            {message.text}
          </span>
        )}
      </div>

      <p className="text-sm text-muted-foreground">
        Rate {gameName} on a scale of 1 to 10
      </p>
    </div>
  );
}
