# Board Game Recommender - System Overview

## Project Vision

A modern board game recommendation platform where users can:
- Sign in and create accounts
- Rate board games they've played
- Get personalized recommendations based on their preferences
- Browse the game catalog

## Architecture Decision Log

### Phase 1 Cleanup (Completed)

**Date:** 2026-01-15

**Legacy Components Archived:**
| Component | Location | Reason for Archive |
|-----------|----------|-------------------|
| Django Backend | `_archive/backend/` | Replaced by Next.js API routes |
| Angular Frontend | `_archive/frontend/` | Replaced by Next.js App Router |
| Deployment Scripts | `_archive/scripts/` | New Docker setup created |
| PostgreSQL Data | Deleted | Migrating to MongoDB |
| Docker Compose Files | `_archive/` | New compose for Next.js stack |

**Preserved for Reference:**
- `_archive/recommendation-algorithms/` - 4 recommendation algorithm implementations
- `_archive/django-models/` - Database schema reference for MongoDB design

**Kept Active:**
- `/import/ETL/` - Data pipeline (to be modernized)
- `/import/recommender/` - Algorithm R&D scripts

### Phase 2 Schema Design (Completed)

**Date:** 2026-01-15

**Key Decisions:**

1. **Separate ratings collection** - Ratings stored separately from users for:
   - Better query performance (high write frequency)
   - Easier aggregation queries
   - Flexible origin tracking (app vs imported)

2. **Denormalized game attributes** - Categories, mechanics, designers, publishers embedded in games:
   - Avoids JOINs for common queries
   - Acceptable trade-off since these rarely change

3. **User preferences computed** - Not stored with ratings, derived from analysis:
   - Prevents stale data
   - Can be recalculated when algorithms improve

4. **TTL on recommendations** - Auto-expire cached recommendations:
   - Ensures freshness without manual cleanup
   - `expiresAt` field with TTL index

5. **Clerk for auth** - Only store `clerkId` reference:
   - Clerk manages auth, sessions, profile
   - We only store app-specific data

**Files Created:**
- `lib/db/schema.ts` - TypeScript types and index definitions

### Phase 3 Data Migration (Completed)

**Date:** 2026-01-15

**Key Decisions:**

1. **Dual-language database access:**
   - TypeScript client (`lib/db/`) for Next.js application
   - Python client (`etl/lib/mongodb.py`) for ETL pipeline

2. **Migration strategy:**
   - ETL generates CSV files from APIs/scrapers
   - Migration script transforms CSV to MongoDB documents
   - Denormalization happens during migration (relations → embedded arrays)

3. **ID mapping:**
   - Legacy integer IDs mapped to MongoDB ObjectIds during migration
   - Imported users get synthetic `clerkId` (e.g., `imported_bgg_12345`)

**Files Created:**
- `lib/db/client.ts` - MongoDB client singleton for Next.js
- `lib/db/init.ts` - Database initialization with indexes
- `lib/db/queries.ts` - Type-safe query functions
- `lib/db/index.ts` - Module exports
- `etl/lib/mongodb.py` - Python MongoDB helper
- `etl/migrate.py` - Data migration script
- `etl/requirements.txt` - Python dependencies
- `.env.example` - Environment variable template

**Data Flow:**
```
ETL Pipeline (Python)     Migration Script        MongoDB
┌─────────────────┐       ┌──────────────┐       ┌──────────────┐
│ BGG Scrapers    │──────>│ CSV Files    │──────>│ Collections  │
│                 │       │ (Data/*.csv) │       │ (denormalized)│
└─────────────────┘       └──────────────┘       └──────────────┘
```

### Phase 4 ETL Modernization (Completed)

**Date:** 2026-01-15

**Key Improvements:**

1. **Environment-based configuration:**
   - All settings via environment variables
   - Centralized `config.py` with dataclasses
   - `.env.example` template provided

2. **Structured logging:**
   - Console + file output
   - Progress tracking with rates
   - Timestamped log files

3. **Retry handling:**
   - Decorator-based retry with exponential backoff
   - Configurable attempts and delays
   - Exception-specific retry logic

4. **Docker support:**
   - `Dockerfile` for ETL container
   - `docker-compose.yml` with MongoDB + ETL services
   - Health checks and proper orchestration

5. **Modular architecture:**
   - Separate modules for config, logging, utils, transform, load
   - Clean pipeline orchestration
   - Type hints throughout

**Files Created:**
- `etl/config.py` - Configuration management
- `etl/logger.py` - Logging setup
- `etl/utils.py` - Utilities with retry handling
- `etl/transform.py` - Data transformers
- `etl/load.py` - MongoDB loader
- `etl/pipeline.py` - Main orchestrator
- `etl/Dockerfile` - Container image
- `etl/README.md` - Documentation
- `docker-compose.yml` - Service orchestration

**Running the ETL:**
```bash
# Using Docker
docker compose up -d mongodb
docker compose --profile etl up etl

# Using Python directly
cd etl
pip install -r requirements.txt
python -m etl.pipeline --data-dir ../data
```

### Phase 5 Next.js Application (Completed)

**Date:** 2026-01-15

**Stack:**
- Next.js 15 with App Router
- TypeScript
- Tailwind CSS + shadcn/ui components
- Clerk for authentication
- Server Actions for mutations

**Pages Created:**
- `/` - Landing page with feature overview
- `/games` - Game browsing with search and pagination
- `/games/[id]` - Game detail page with rating form
- `/ratings` - User's ratings management
- `/recommendations` - Personalized recommendations with algorithm selector
- `/sign-in`, `/sign-up` - Clerk authentication pages

**Components:**
- `Header` - Navigation with auth state
- `GameCard` - Game preview card
- `RatingForm` - Interactive rating widget (1-10 stars)
- UI components (Button, Card, Input, Badge, Skeleton)

**Server Actions:**
- `rateGame` - Create/update game rating
- `deleteRating` - Remove a rating
- `getUserRatings` - Fetch user's ratings with game details
- `getRecommendations` - Get recommendations by algorithm

**Recommendation Algorithms (client-side):**
- Popularity - Top-rated games by BGG score
- Content-Based - Category/mechanic matching
- KNN - Item similarity based predictions
- Collaborative - (placeholder, uses popularity)

**Files Structure:**
```
src/
├── app/
│   ├── (auth)/sign-in, sign-up
│   ├── actions/ratings.ts, recommendations.ts
│   ├── games/page.tsx, [id]/page.tsx
│   ├── ratings/page.tsx
│   ├── recommendations/page.tsx
│   ├── page.tsx (home)
│   ├── layout.tsx
│   └── globals.css
├── components/
│   ├── ui/ (button, card, input, badge, skeleton)
│   ├── header.tsx
│   ├── game-card.tsx
│   └── rating-form.tsx
├── lib/utils.ts
└── middleware.ts
```

### Phase 6 Recommendation Engine Integration (Completed)

**Date:** 2026-01-15

**Key Decisions:**

1. **Modular engine architecture:**
   - Common `RecommendationEngine` interface for all algorithms
   - Each algorithm is a separate class implementing the interface
   - Central module (`lib/recommender/index.ts`) orchestrates engines

2. **Four recommendation algorithms:**
   - **Popularity** - Top-rated games by community score
   - **Content-Based** - Matches user profile to game features
   - **Collaborative** - User-based collaborative filtering with centered cosine similarity
   - **KNN** - Item-item similarity with weighted predictions

3. **MongoDB caching:**
   - Recommendations cached per user per algorithm
   - 24-hour TTL with automatic expiration
   - Cache invalidated when user ratings change

4. **Server Actions pattern:**
   - Uses Next.js Server Actions instead of API routes
   - Cleaner integration with React Server Components
   - Type-safe end-to-end

**Files Created:**
- `lib/recommender/types.ts` - Core types and interfaces
- `lib/recommender/popularity.ts` - Popularity-based engine
- `lib/recommender/content-based.ts` - Content-based filtering engine
- `lib/recommender/collaborative.ts` - User-based collaborative filtering
- `lib/recommender/knn.ts` - KNN with item similarity
- `lib/recommender/index.ts` - Main module with caching

**Algorithm Details:**

| Algorithm | Min Ratings | Description |
|-----------|-------------|-------------|
| Popularity | 0 | 70% average rating + 30% rating count |
| Content-Based | 1 | 50% categories + 30% mechanics + 20% numeric features |
| Collaborative | 3 | Top 20% similar users, centered cosine similarity |
| KNN | 3 | k=40 neighbors, min_k=5, weighted mean adjustment |

### Phase 7 Docker & Deployment (Completed)

**Date:** 2026-01-15

**Key Decisions:**

1. **Multi-stage Docker build:**
   - Separate stages for deps, build, and runtime
   - Standalone output mode for minimal image size
   - Non-root user for security

2. **Docker Compose services:**
   - `mongodb` - MongoDB 7 with health checks
   - `app` - Next.js application
   - `etl` - On-demand ETL pipeline (profile: etl)
   - `mongo-express` - Admin UI (profile: admin)

3. **Environment configuration:**
   - Runtime environment variables via docker-compose
   - Clerk keys passed from host `.env` file
   - MongoDB connection via Docker network

4. **Dynamic rendering:**
   - All pages use `force-dynamic` for Clerk compatibility
   - No static generation at build time
   - Health check API at `/api/health`

**Files Created:**
- `Dockerfile` - Production multi-stage build
- `Dockerfile.dev` - Development with hot-reload
- `docker-compose.yml` - Updated with app service
- `docker-compose.dev.yml` - Development override
- `.dockerignore` - Build exclusions
- `src/app/api/health/route.ts` - Health check endpoint

**Running Locally:**
```bash
# Start all services (requires .env with Clerk keys)
docker compose up -d

# Run ETL pipeline
docker compose --profile etl up etl

# Access admin UI
docker compose --profile admin up mongo-express
```

**Vercel Deployment:**
1. Connect repository to Vercel
2. Set environment variables:
   - `MONGODB_URI` - MongoDB Atlas connection string
   - `MONGODB_DB` - Database name
   - `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` - Clerk public key
   - `CLERK_SECRET_KEY` - Clerk secret key
3. Deploy automatically on push to main

### Phase 8 Documentation & Cleanup (Completed)

**Date:** 2026-01-15

**Completed Tasks:**

1. **README.md overhaul:**
   - Complete rewrite for new tech stack
   - Quick start guide with Docker and local options
   - Project structure documentation
   - Environment variables reference

2. **ESLint cleanup:**
   - Fixed all linting warnings
   - Configured underscore prefix convention for unused params
   - Updated eslint.config.mjs with proper rules

3. **Code cleanup:**
   - Removed unused imports
   - Fixed anonymous default exports
   - Removed unnecessary eslint-disable comments

4. **Environment template:**
   - Updated .env.example with all required variables
   - Added documentation comments for each section
   - Included Docker-specific configuration notes

**Final State:**
- All 8 development phases complete
- Zero ESLint warnings on build
- Comprehensive documentation in place
- Project ready for production deployment

---

## Target Architecture

### Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Frontend | Next.js 14+ (App Router) | React-based UI with SSR |
| Styling | Tailwind CSS + shadcn/ui | Modern, accessible components |
| Auth | Clerk | User authentication |
| Database | MongoDB Atlas | Document storage |
| ETL | Python (standalone) | Data pipeline |
| Deployment | Docker + Vercel | Containerized local, serverless production |

### Project Structure (Target)

```
board-game-recommender/
├── app/                    # Next.js App Router
│   ├── (auth)/            # Auth routes (sign-in, sign-up)
│   ├── (dashboard)/       # Protected routes
│   │   ├── games/         # Game browsing
│   │   ├── ratings/       # User ratings
│   │   └── recommendations/# Recommendation pages
│   ├── api/               # API routes
│   └── layout.tsx         # Root layout
├── components/            # React components
│   ├── ui/               # shadcn/ui components
│   └── ...               # Feature components
├── lib/                   # Utilities
│   ├── db/               # MongoDB client & queries
│   ├── recommender/      # Recommendation algorithms
│   └── ...
├── etl/                   # Python ETL pipeline (renamed from import/)
│   ├── extract/          # Data fetching
│   ├── transform/        # Data cleaning
│   └── load/             # MongoDB loading
├── _archive/             # Legacy code reference
└── docker/               # Docker configurations
```

---

## Database Schema (MongoDB)

**TypeScript types:** `lib/db/schema.ts`

### Collections Overview

| Collection | Purpose | Key Fields |
|------------|---------|------------|
| `games` | Board game catalog | bggId, name, categories, mechanics |
| `users` | User profiles (linked to Clerk) | clerkId, ratingCount, preferences |
| `ratings` | User game ratings | userId, gameId, rating (1-10) |
| `recommendations` | Cached recommendations | userId, algorithm, games[], expiresAt |
| `gameSimilarities` | Precomputed item-item similarity | gameId, similarGames[] |
| `onlineGames` | Online platform links | gameId, url, platform |

### games Collection

```typescript
{
  _id: ObjectId,
  bggId: number | null,        // Board Game Geek ID
  bgaId: string | null,        // deprecated - BGA service discontinued
  name: string,
  description: string | null,
  yearPublished: number | null,
  minPlayers: number | null,
  maxPlayers: number | null,
  minPlaytime: number | null,
  maxPlaytime: number | null,
  minAge: number | null,
  complexity: number | null,   // BGG weight, 1-5 scale
  thumbnailUrl: string | null,
  imageUrl: string | null,
  categories: string[],        // Denormalized
  mechanics: string[],         // Denormalized
  designers: [{ id, name, url?, imageUrl? }],
  publishers: [{ id, name, url?, imageUrl? }],
  bggRating: { average, count, stddev?, bayesAverage? } | null,
  bgaRating: { average, count } | null,  // deprecated - BGA service discontinued
  officialUrl: string | null,
  bgaUrl: string | null,       // deprecated - BGA service discontinued
  priceUs: number | null,
  bggRank: number | null,
  bgaRank: number | null,      // deprecated - BGA service discontinued
  createdAt: Date,
  updatedAt: Date
}
```

### users Collection

```typescript
{
  _id: ObjectId,
  clerkId: string,             // Clerk user ID (unique)
  username: string | null,
  displayName: string | null,
  ratingCount: number,         // Denormalized for quick access
  preferences: {
    favoriteCategories: string[],
    favoriteMechanics: string[],
    averageComplexity: number | null,
    preferredPlayerCount: number | null
  } | null,
  createdAt: Date,
  updatedAt: Date
}
```

### ratings Collection

```typescript
{
  _id: ObjectId,
  userId: ObjectId,            // ref: users._id
  gameId: ObjectId,            // ref: games._id
  rating: number,              // 1-10 scale
  origin: 'app' | 'bgg',
  createdAt: Date,
  updatedAt: Date
}
```

### recommendations Collection

```typescript
{
  _id: ObjectId,
  userId: ObjectId,
  algorithm: 'collaborative' | 'content-based' | 'knn' | 'popularity' | 'hybrid',
  games: [{
    gameId: ObjectId,
    score: number,
    rank: number
  }],
  generatedAt: Date,
  expiresAt: Date,             // TTL index auto-deletes expired
  inputRatingCount: number
}
```

### gameSimilarities Collection

```typescript
{
  _id: ObjectId,
  gameId: ObjectId,            // ref: games._id
  similarGames: [{
    gameId: ObjectId,
    similarity: number         // 0-1 score
  }],
  computedAt: Date
}
```

### onlineGames Collection

```typescript
{
  _id: ObjectId,
  gameId: ObjectId | null,     // ref: games._id
  bggId: number | null,
  name: string,
  url: string,
  platform: 'tabletopia' | 'board-game-arena' | 'yucata' | 'other',
  createdAt: Date,
  updatedAt: Date
}
```

### Indexes

**games:**
- `{ bggId: 1 }` unique, sparse
- `{ bgaId: 1 }` unique, sparse (deprecated - BGA discontinued)
- `{ name: "text", description: "text" }` text search
- `{ categories: 1 }`, `{ mechanics: 1 }`
- `{ "bggRating.average": -1 }`, `{ bggRank: 1 }`
- `{ minPlayers: 1, maxPlayers: 1 }`

**users:**
- `{ clerkId: 1 }` unique

**ratings:**
- `{ userId: 1, gameId: 1 }` unique (one rating per user per game)
- `{ userId: 1 }`, `{ gameId: 1 }`
- `{ userId: 1, createdAt: -1 }`

**recommendations:**
- `{ userId: 1, algorithm: 1 }` unique
- `{ expiresAt: 1 }` TTL index

**gameSimilarities:**
- `{ gameId: 1 }` unique

---

## Recommendation Algorithms

Four algorithms ported from legacy system:

### 1. Collaborative Filtering (User-Based)
- Finds users with similar rating patterns
- Recommends games liked by similar users
- Source: `_archive/recommendation-algorithms/collaborative_filtering_user_based.py`

### 2. Content-Based Filtering
- Creates user profile from highly-rated games
- Matches against game features (categories, mechanics, etc.)
- Weighted similarity: 50% categories, 20% mechanics, 30% numeric features
- Source: `_archive/recommendation-algorithms/content_based_filtering.py`

### 3. KNN with Item Similarity
- Uses precomputed game-to-game similarity matrix
- Predicts ratings based on k=40 most similar rated games
- Source: `_archive/recommendation-algorithms/knn_selfmade.py`

### 4. Popularity Score
- Simple popularity-based recommendations
- Combines average rating + number of ratings
- Good for new users (cold start)
- Source: `_archive/recommendation-algorithms/popularity_score.py`

---

## ETL Pipeline

### Data Sources
1. **Board Game Geek** - Game metadata and ratings
2. **Online Platforms** - Tabletopia, Board Game Arena links

### Pipeline Stages
1. **Extract** - Fetch from APIs, scrape websites
2. **Transform** - Clean, normalize, deduplicate
3. **Integrate** - Match games across sources
4. **Load** - Insert into MongoDB

### Running ETL
```bash
cd etl
docker-compose up etl
# Or standalone:
python main.py
```

---

## Development Phases

- [x] **Phase 1** - Codebase Audit & Cleanup
- [x] **Phase 2** - MongoDB Schema Design
- [x] **Phase 3** - Data Migration
- [x] **Phase 4** - ETL Modernization
- [x] **Phase 5** - Next.js Application
- [x] **Phase 6** - Recommendation Engine Integration
- [x] **Phase 7** - Docker & Deployment
- [x] **Phase 8** - Documentation & Cleanup

---

## Constraints & Rules

- Prefer clarity over cleverness
- Delete unused code aggressively
- No business logic in React components
- Python only for ETL/data science
- Every major decision documented here
- Environment-based configuration (no hardcoded secrets)

---

## Definition of Done

The project is complete when:
- [x] App runs locally via Docker
- [x] App is deployable to Vercel
- [x] MongoDB Atlas works
- [x] Users can sign in
- [x] Users can rate games
- [x] Users can get recommendations
- [x] ETL pipeline runs independently
- [x] Architecture is documented
