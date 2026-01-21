# Board Game Recommender

A modern board game recommendation platform where users can rate games and receive personalized recommendations powered by multiple algorithms.

## Features

- **Browse Games** - Explore thousands of board games with detailed information
- **Rate Games** - Rate games on a 1-10 scale to build your preference profile
- **Get Recommendations** - Receive personalized suggestions from 4 different algorithms:
  - **Popularity** - Top-rated games by the community
  - **Content-Based** - Games matching your preferred categories and mechanics
  - **Collaborative Filtering** - Games liked by users with similar taste
  - **KNN Item Similarity** - Predictions based on similar games you've rated
- **Authentication** - Secure sign-in via Clerk

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Next.js 15 (App Router) |
| Styling | Tailwind CSS + shadcn/ui |
| Auth | Clerk |
| Database | MongoDB |
| ETL | Python |
| Deployment | Docker / Vercel |

## Quick Start

### Prerequisites

- Node.js 20+
- Docker & Docker Compose
- Clerk account (for authentication)

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/tillhoffmann1411/board-game-recommender.git
   cd board-game-recommender
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```

   Fill in your Clerk keys (get from https://dashboard.clerk.com):
   ```
   NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
   CLERK_SECRET_KEY=sk_test_...
   ```

3. **Start with Docker** (recommended)
   ```bash
   docker compose up -d
   ```

   The app will be available at http://localhost:3000

4. **Or run locally without Docker**
   ```bash
   # Start MongoDB
   docker compose up -d mongodb

   # Install dependencies
   npm install

   # Run development server
   npm run dev
   ```

### Loading Sample Data

Run the ETL pipeline to load board game data:

```bash
# With Docker
docker compose --profile etl up etl

# Or with Python directly
cd etl
pip install -r requirements.txt
python -m etl.pipeline --data-dir ../data
```

## Project Structure

```
board-game-recommender/
├── src/
│   ├── app/                 # Next.js App Router pages
│   │   ├── (auth)/          # Sign-in/sign-up pages
│   │   ├── actions/         # Server Actions
│   │   ├── api/             # API routes
│   │   ├── games/           # Game browsing
│   │   ├── ratings/         # User ratings
│   │   └── recommendations/ # Recommendations
│   └── components/          # React components
├── lib/
│   ├── db/                  # MongoDB client & schema
│   └── recommender/         # Recommendation engines
├── etl/                     # Python ETL pipeline
└── docker-compose.yml       # Docker services
```

## Docker Services

| Service | Port | Description |
|---------|------|-------------|
| app | 3000 | Next.js application |
| mongodb | 27017 | MongoDB database |
| mongo-express | 8081 | Database admin UI (profile: admin) |
| etl | - | ETL pipeline (profile: etl) |

```bash
# Start main services
docker compose up -d

# Run ETL pipeline
docker compose --profile etl up etl

# Start admin UI
docker compose --profile admin up -d mongo-express
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `MONGODB_URI` | MongoDB connection string |
| `MONGODB_DB` | Database name |
| `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` | Clerk public key |
| `CLERK_SECRET_KEY` | Clerk secret key |

See `.env.example` for all available options.

## Deployment

### Vercel

1. Connect your repository to Vercel
2. Set environment variables in Vercel dashboard
3. Deploy automatically on push to main

### Docker (Self-hosted)

```bash
# Build and run
docker compose up -d --build

# Check health
curl http://localhost:3000/api/health
```

## Documentation

- **[SYSTEM_OVERVIEW.md](./SYSTEM_OVERVIEW.md)** - Architecture decisions and detailed documentation
- **[etl/README.md](./etl/README.md)** - ETL pipeline documentation

## License

MIT
