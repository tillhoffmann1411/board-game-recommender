"use client";

import Link from "next/link";
import { Check, ChevronDown } from "lucide-react";
import { Button } from "@/src/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/src/components/ui/dropdown-menu";

export interface SortOption {
  value: string;
  label: string;
}

export interface GamesSortDropdownFilters {
  players?: number;
  time?: string;
  categories?: string[];
  mechanics?: string[];
}

function buildGamesUrl(params: {
  q?: string;
  sort?: string;
  players?: number;
  time?: string;
  categories?: string[];
  mechanics?: string[];
}) {
  const search = new URLSearchParams();
  if (params.q) search.set("q", params.q);
  if (params.sort && params.sort !== "popular") search.set("sort", params.sort);
  if (params.players != null) search.set("players", String(params.players));
  if (params.time) search.set("time", params.time);
  if (params.categories?.length) search.set("categories", params.categories.join(","));
  if (params.mechanics?.length) search.set("mechanics", params.mechanics.join(","));
  const s = search.toString();
  return s ? `/games?${s}` : "/games";
}

export function GamesSortDropdown({
  options,
  currentSort,
  query,
  filters,
}: {
  options: SortOption[];
  currentSort: string;
  query?: string;
  filters?: GamesSortDropdownFilters;
}) {
  const currentLabel = options.find((o) => o.value === currentSort)?.label ?? options[0]!.label;

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button
          variant="outline"
          size="sm"
          className="min-w-[10rem] justify-between text-xs sm:text-sm rounded-lg h-8"
        >
          <span>{currentLabel}</span>
          <ChevronDown className="h-3.5 w-3.5 opacity-50" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="start" className="min-w-[10rem]">
        {options.map((option) => {
          const href = buildGamesUrl({
            q: query,
            sort: option.value === "popular" ? undefined : option.value,
            ...filters,
          });
          const isActive = option.value === currentSort;
          return (
            <DropdownMenuItem key={option.value} asChild>
              <Link href={href} className="flex items-center gap-2">
                {isActive ? <Check className="h-4 w-4" /> : <span className="w-4" />}
                {option.label}
              </Link>
            </DropdownMenuItem>
          );
        })}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
