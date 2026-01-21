# Local Development Setup

Guide for setting up and running the BGG scraper locally (outside Docker).

## Prerequisites

1. **Python 3.11+** - Check with `python3 --version`
2. **Chrome or Chromium browser** - Required for Selenium
   - macOS: `brew install --cask google-chrome` or `brew install chromium`
   - Linux: `sudo apt-get install chromium chromium-driver` (or use Chrome)
   - Windows: Download from [Google Chrome](https://www.google.com/chrome/)

## Quick Setup

### Option 1: Using the Setup Script (Recommended)

```bash
cd etl
./setup_venv.sh
```

### Option 2: Manual Setup

```bash
# Navigate to ETL directory
cd etl

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate  # On Windows

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

## Running the Scraper

### Activate the Virtual Environment

```bash
cd etl
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows
```

### Run the Scraper

**Basic usage (scrape 5 pages):**
```bash
python -m etl.extraction.bgg_scraper --max-pages 5 --output data/bgg_games.csv
```

**Scrape all pages (takes a long time!):**
```bash
python -m etl.extraction.bgg_scraper --output data/bgg_games.csv
```

**With options:**
```bash
# Scrape 10 pages, save as JSON, show browser window
python -m etl.extraction.bgg_scraper \
  --max-pages 10 \
  --output data/bgg_games.json \
  --format json \
  --no-headless \
  --delay 3.0
```

### Command Line Options

- `--max-pages N` - Maximum number of pages to scrape (default: all pages)
- `--start-page N` - Page number to start from (default: 1)
- `--output PATH` - Output file path (default: None, no file saved)
- `--format {csv,json}` - Output format (default: csv)
- `--headless` - Run browser in headless mode (default: True)
- `--no-headless` - Run browser with GUI (useful for debugging)
- `--delay SECONDS` - Delay between page requests (default: 2.0)
- `--log-level {DEBUG,INFO,WARNING,ERROR}` - Logging level (default: INFO)

## Troubleshooting

### "ModuleNotFoundError: No module named 'selenium'"

Make sure you've activated the virtual environment:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### "selenium.common.exceptions.WebDriverException"

**On macOS:**
- Make sure Chrome/Chromium is installed
- If using Chrome, Selenium will auto-download ChromeDriver
- If issues persist, install ChromeDriver manually:
  ```bash
  brew install chromedriver
  ```

**On Linux:**
- Install Chromium and ChromeDriver:
  ```bash
  sudo apt-get install chromium chromium-driver
  ```

**On Windows:**
- Chrome should work automatically
- If not, download ChromeDriver from [ChromeDriver Downloads](https://chromedriver.chromium.org/downloads)

### Browser doesn't start

Try running with `--no-headless` to see what's happening:
```bash
python -m etl.extraction.bgg_scraper --max-pages 1 --no-headless
```

### Permission denied on setup script

Make the script executable:
```bash
chmod +x setup_venv.sh
```

## Output

The scraper will save data to:
- `etl/data/bgg_games.csv` (if using default path)
- Or the path specified with `--output`

The CSV contains columns:
- `rank` - Board game rank
- `name` - Game name
- `detailUrl` - Link to game detail page
- `bggId` - BoardGameGeek ID
- `yearPublished` - Year published
- `geekRating` - Geek rating
- `avgRating` - Average rating
- `numVoters` - Number of voters
- `thumbnailUrl` - Thumbnail image URL
- `description` - Game description
- `page` - Page number where game was found

## Deactivating the Virtual Environment

When you're done:
```bash
deactivate
```
