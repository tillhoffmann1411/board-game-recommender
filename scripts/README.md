# Scripts

Utility scripts for database management and deployment.

## init-db.ts

Initializes the database by creating all required collections and indexes.

### What it does:

1. **Creates all collections** if they don't exist (games, users, ratings, recommendations, gameSimilarities, onlineGames)
2. **Creates all indexes** for optimal query performance

### Usage:

```bash
# Set environment variables
export MONGODB_URI="mongodb://localhost:27017"  # or your MongoDB Atlas connection string
export MONGODB_DB="board-game-recommender"  # Optional, defaults to this

# Run the script
npm run db:init
```

Or directly with tsx:

```bash
MONGODB_URI="your-connection-string" MONGODB_DB="board-game-recommender" npx tsx scripts/init-db.ts
```

### When to use:

- When setting up a new database (local or production)
- After importing data to ensure all indexes are created
- When you need to recreate indexes after schema changes

---

## sync-games-to-prod.ts

Syncs games from local MongoDB to production MongoDB (Atlas).

### What it does:

1. **Exports games** from local MongoDB (Docker container)
2. **Ensures all collections exist** in production database
3. **Initializes indexes** in production database
4. **Imports/updates games** in production (upsert based on `bggId`)

### Prerequisites:

- Local MongoDB running in Docker: `docker compose up -d mongodb`
- Production MongoDB connection string (MongoDB Atlas)

### Usage:

```bash
# Set environment variables
export LOCAL_MONGODB_URI="mongodb://localhost:27017"  # Optional, defaults to this
export MONGODB_URI="mongodb+srv://user:password@cluster.mongodb.net/board-game-recommender?retryWrites=true&w=majority"
export MONGODB_DB="board-game-recommender"  # Optional, defaults to this

# Run the script
npm run sync:games
```

Or directly with tsx:

```bash
LOCAL_MONGODB_URI="mongodb://localhost:27017" \
MONGODB_URI="your-atlas-connection-string" \
MONGODB_DB="board-game-recommender" \
npx tsx scripts/sync-games-to-prod.ts
```

### Environment Variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `LOCAL_MONGODB_URI` | Local MongoDB connection string | `mongodb://localhost:27017` |
| `MONGODB_URI` | Production MongoDB connection string (required) | - |
| `MONGODB_DB` | Database name | `board-game-recommender` |

### How it works:

- **Upsert logic**: Games are matched by `bggId`. If a game with the same `bggId` exists, it's updated. Otherwise, it's inserted.
- **Batch processing**: Games are processed in batches of 1000 for efficiency.
- **Index creation**: All required indexes are created automatically if they don't exist.
- **Collection creation**: All collections are created if they don't exist.

### Output:

The script provides detailed progress information:
- Number of games exported from local
- Collection creation status
- Index creation status
- Batch processing progress
- Final summary with inserted/updated counts

### Example Output:

```
🚀 Starting game sync to production...

📤 Exporting games from local MongoDB...
   URI: mongodb://localhost:27017
   Database: board-game-recommender
   ✅ Exported 15234 games

🔌 Connecting to production MongoDB...
   URI: mongodb+srv://***:***@cluster.mongodb.net/...
   Database: board-game-recommender

📋 Ensuring all collections exist in production...
   ✓ Collection exists: games
   ✓ Collection exists: users
   ✓ Collection exists: ratings
   ...

🔧 Initializing indexes in production database...
   ✅ Created index on games: bggId_1
   ...

📥 Importing/updating games in production database...
   Total games: 15234
   Processed batch 1/16: 1000 inserted, 0 updated
   ...

============================================================
✅ Sync completed successfully!
============================================================
   Total games processed: 15234
   Games inserted: 15234
   Games updated: 0
============================================================
```
