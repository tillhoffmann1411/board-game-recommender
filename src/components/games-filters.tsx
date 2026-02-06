"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { Check, ChevronDown, Users, Clock, Tags, Cog } from "lucide-react";
import { Button } from "@/src/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/src/components/ui/dropdown-menu";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/src/components/ui/popover";
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from "@/src/components/ui/command";

const TIME_OPTIONS = [
  { value: "", label: "Any" },
  { value: "under30", label: "Under 30 min" },
  { value: "30-60", label: "30–60 min" },
  { value: "60-120", label: "1–2 hours" },
  { value: "120+", label: "2+ hours" },
] as const;

const PLAYER_COUNTS = [1, 2, 3, 4, 5, 6, 7, 8] as const;

function buildUrl(params: {
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

export interface GamesFiltersProps {
  query?: string;
  sort?: string;
  players?: number;
  time?: string;
  categories?: string[];
  mechanics?: string[];
  categoryOptions: string[];
  mechanicsOptions: string[];
}

const COMBOBOX_THRESHOLD = 15;

export function GamesFilters({
  query,
  sort,
  players,
  time,
  categories = [],
  mechanics = [],
  categoryOptions,
  mechanicsOptions,
}: GamesFiltersProps) {
  const router = useRouter();
  const base = { q: query, sort };

  const playersLabel = players != null ? `${players} player${players === 1 ? "" : "s"}` : "Players";
  const timeLabel = TIME_OPTIONS.find((t) => t.value === time)?.label ?? "Playtime";
  const categoriesLabel =
    categories.length === 0 ? "Categories" : `Categories (${categories.length})`;
  const mechanicsLabel =
    mechanics.length === 0 ? "Mechanics" : `Mechanics (${mechanics.length})`;

  const useCategoriesCombobox = categoryOptions.length > COMBOBOX_THRESHOLD;
  const useMechanicsCombobox = mechanicsOptions.length > COMBOBOX_THRESHOLD;

  const navigateCategories = (nextCategories: string[]) => {
    router.push(
      buildUrl({
        ...base,
        players,
        time,
        categories: nextCategories.length ? nextCategories : undefined,
        mechanics,
      })
    );
  };

  const navigateMechanics = (nextMechanics: string[]) => {
    router.push(
      buildUrl({
        ...base,
        players,
        time,
        categories,
        mechanics: nextMechanics.length ? nextMechanics : undefined,
      })
    );
  };

  return (
    <div className="flex flex-wrap items-center gap-2">
      {/* Players */}
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button
            variant="outline"
            size="sm"
            className="h-8 gap-1.5 text-xs sm:text-sm rounded-lg"
          >
            <Users className="h-3.5 w-3.5" />
            <span>{playersLabel}</span>
            <ChevronDown className="h-3.5 w-3.5 opacity-50" />
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="start" className="max-h-[min(20rem,70vh)] overflow-y-auto">
          <DropdownMenuItem asChild>
            <Link
              href={buildUrl({ ...base, players: undefined, time, categories, mechanics })}
              className="flex items-center gap-2"
            >
              {players == null ? <Check className="h-4 w-4" /> : <span className="w-4" />}
              Any
            </Link>
          </DropdownMenuItem>
          {PLAYER_COUNTS.map((n) => {
            const isActive = players === n;
            return (
              <DropdownMenuItem key={n} asChild>
                <Link
                  href={buildUrl({ ...base, players: n, time, categories, mechanics })}
                  className="flex items-center gap-2"
                >
                  {isActive ? <Check className="h-4 w-4" /> : <span className="w-4" />}
                  {n} player{n === 1 ? "" : "s"}
                </Link>
              </DropdownMenuItem>
            );
          })}
        </DropdownMenuContent>
      </DropdownMenu>

      {/* Time */}
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button
            variant="outline"
            size="sm"
            className="h-8 gap-1.5 text-xs sm:text-sm rounded-lg"
          >
            <Clock className="h-3.5 w-3.5" />
            <span>{timeLabel}</span>
            <ChevronDown className="h-3.5 w-3.5 opacity-50" />
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="start">
          {TIME_OPTIONS.map((opt) => {
            const isActive = (time || "") === opt.value;
            return (
              <DropdownMenuItem key={opt.value || "any"} asChild>
                <Link
                  href={buildUrl({
                    ...base,
                    players,
                    time: opt.value || undefined,
                    categories,
                    mechanics,
                  })}
                  className="flex items-center gap-2"
                >
                  {isActive ? <Check className="h-4 w-4" /> : <span className="w-4" />}
                  {opt.label}
                </Link>
              </DropdownMenuItem>
            );
          })}
        </DropdownMenuContent>
      </DropdownMenu>

      {/* Categories: combobox when many options, else dropdown */}
      {useCategoriesCombobox ? (
        <Popover>
          <PopoverTrigger asChild>
            <Button
              variant="outline"
              size="sm"
              className="h-8 gap-1.5 text-xs sm:text-sm rounded-lg min-w-[8rem] justify-between"
            >
              <Tags className="h-3.5 w-3.5 shrink-0" />
              <span className="truncate">{categoriesLabel}</span>
              <ChevronDown className="h-3.5 w-3.5 opacity-50 shrink-0" />
            </Button>
          </PopoverTrigger>
          <PopoverContent className="w-[min(20rem,90vw)] p-0" align="start">
            <Command className="rounded-lg border-0">
              <CommandInput placeholder="Search categories..." className="h-9" />
              <CommandList className="max-h-[min(20rem,70vh)]">
                <CommandEmpty>No category found.</CommandEmpty>
                <CommandGroup>
                  {categoryOptions.map((cat) => {
                    const isSelected = categories.includes(cat);
                    const next = isSelected
                      ? categories.filter((c) => c !== cat)
                      : [...categories, cat];
                    return (
                      <CommandItem
                        key={cat}
                        value={cat}
                        onSelect={() => navigateCategories(next)}
                        className="gap-2"
                      >
                        {isSelected ? <Check className="h-4 w-4" /> : <span className="w-4" />}
                        <span className="truncate">{cat}</span>
                      </CommandItem>
                    );
                  })}
                </CommandGroup>
              </CommandList>
            </Command>
          </PopoverContent>
        </Popover>
      ) : (
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button
              variant="outline"
              size="sm"
              className="h-8 gap-1.5 text-xs sm:text-sm rounded-lg"
            >
              <Tags className="h-3.5 w-3.5" />
              <span>{categoriesLabel}</span>
              <ChevronDown className="h-3.5 w-3.5 opacity-50" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="start" className="max-h-[min(20rem,70vh)] overflow-y-auto min-w-[10rem]">
            {categoryOptions.map((cat) => {
              const isSelected = categories.includes(cat);
              const nextCategories = isSelected
                ? categories.filter((c) => c !== cat)
                : [...categories, cat];
              return (
                <DropdownMenuItem key={cat} asChild>
                  <Link
                    href={buildUrl({
                      ...base,
                      players,
                      time,
                      categories: nextCategories.length ? nextCategories : undefined,
                      mechanics,
                    })}
                    className="flex items-center gap-2"
                  >
                    {isSelected ? <Check className="h-4 w-4" /> : <span className="w-4" />}
                    <span className="truncate">{cat}</span>
                  </Link>
                </DropdownMenuItem>
              );
            })}
          </DropdownMenuContent>
        </DropdownMenu>
      )}

      {/* Mechanics: combobox when many options, else dropdown */}
      {useMechanicsCombobox ? (
        <Popover>
          <PopoverTrigger asChild>
            <Button
              variant="outline"
              size="sm"
              className="h-8 gap-1.5 text-xs sm:text-sm rounded-lg min-w-[8rem] justify-between"
            >
              <Cog className="h-3.5 w-3.5 shrink-0" />
              <span className="truncate">{mechanicsLabel}</span>
              <ChevronDown className="h-3.5 w-3.5 opacity-50 shrink-0" />
            </Button>
          </PopoverTrigger>
          <PopoverContent className="w-[min(20rem,90vw)] p-0" align="start">
            <Command className="rounded-lg border-0">
              <CommandInput placeholder="Search mechanics..." className="h-9" />
              <CommandList className="max-h-[min(20rem,70vh)]">
                <CommandEmpty>No mechanic found.</CommandEmpty>
                <CommandGroup>
                  {mechanicsOptions.map((mech) => {
                    const isSelected = mechanics.includes(mech);
                    const next = isSelected
                      ? mechanics.filter((m) => m !== mech)
                      : [...mechanics, mech];
                    return (
                      <CommandItem
                        key={mech}
                        value={mech}
                        onSelect={() => navigateMechanics(next)}
                        className="gap-2"
                      >
                        {isSelected ? <Check className="h-4 w-4" /> : <span className="w-4" />}
                        <span className="truncate">{mech}</span>
                      </CommandItem>
                    );
                  })}
                </CommandGroup>
              </CommandList>
            </Command>
          </PopoverContent>
        </Popover>
      ) : (
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button
              variant="outline"
              size="sm"
              className="h-8 gap-1.5 text-xs sm:text-sm rounded-lg"
            >
              <Cog className="h-3.5 w-3.5" />
              <span>{mechanicsLabel}</span>
              <ChevronDown className="h-3.5 w-3.5 opacity-50" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="start" className="max-h-[min(20rem,70vh)] overflow-y-auto min-w-[10rem]">
            {mechanicsOptions.map((mech) => {
              const isSelected = mechanics.includes(mech);
              const nextMechanics = isSelected
                ? mechanics.filter((m) => m !== mech)
                : [...mechanics, mech];
              return (
                <DropdownMenuItem key={mech} asChild>
                  <Link
                    href={buildUrl({
                      ...base,
                      players,
                      time,
                      categories,
                      mechanics: nextMechanics.length ? nextMechanics : undefined,
                    })}
                    className="flex items-center gap-2"
                  >
                    {isSelected ? <Check className="h-4 w-4" /> : <span className="w-4" />}
                    <span className="truncate">{mech}</span>
                  </Link>
                </DropdownMenuItem>
              );
            })}
          </DropdownMenuContent>
        </DropdownMenu>
      )}
    </div>
  );
}
