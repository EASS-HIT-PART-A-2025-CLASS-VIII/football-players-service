# Data Loading Strategy

## Overview

The `load_data.py` script provides a **universal data loading solution** that works with both:

- **SQLite** (local development)
- **PostgreSQL** (production/Render)

It reads from CSV files and transforms the data to match your `Player` model schema.

---

## How It Works

### 1. **Automatic Database Detection**

```python
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./football_players.db")
```

- **No DATABASE_URL set?** → Uses SQLite locally
- **DATABASE_URL set?** → Uses PostgreSQL on Render

### 2. **Data Flow**

```
players.csv (32,601 records)
    ↓
Random Sample (200 records for testing)
    ↓
Data Transformation (map CSV → Player model)
    ↓
Database Insert (SQLite or PostgreSQL)
    ↓
Database Persist
```

### 3. **Data Mapping**

| CSV                                    | Model          | Transformation                            |
| -------------------------------------- | -------------- | ----------------------------------------- |
| `first_name`, `last_name`              | `full_name`    | `"{first_name} {last_name}".title()`      |
| `country_of_citizenship`               | `country`      | Title case, max 50 chars                  |
| `date_of_birth`                        | `age`          | Calculated from DOB to today              |
| `current_club_name`                    | `current_team` | Title case                                |
| `current_club_domestic_competition_id` | `league`       | Mapped from competitions.csv              |
| `market_value_in_eur`                  | `market_value` | Parsed as integer                         |
| `last_season`                          | `status`       | If >5 years old: "retired", else "active" |

---

## Local Development (SQLite)

### Step 1: Run the loader

```bash
cd backend
python data_scraper/load_data.py --limit 200
```

### Step 2: Start your app

```bash
# Terminal 1: Backend
uv run python -m uvicorn football_player_service.app.main:app --reload --port 8000

# Terminal 2: Frontend
cd frontend && npm run dev
```

### Step 3: Verify data

Open **http://localhost:5173** → You should see 200+ players!

---

## Production (PostgreSQL on Render)

### Step 1: Get your DATABASE_URL

From your Render dashboard:

1. Go to your PostgreSQL instance
2. Copy the **External Database URL**
3. It looks like: `postgresql://user:password@host:5432/database`

### Step 2: Load data into Render PostgreSQL

```bash
export DATABASE_URL="postgresql+psycopg2://user:password@host:5432/football"
cd backend
python data_scraper/load_data.py --limit 200
```

Or on Windows PowerShell:

```powershell
$env:DATABASE_URL = "postgresql+psycopg2://user:password@host:5432/football"
python data_scraper/load_data.py --limit 200
```

### Step 3: Verify on Render

- Redeploy your backend service (Render will use the data)
- Or call the API: `curl https://your-service.onrender.com/players`

---

## Docker Compose

Both databases (SQLite in volume + PostgreSQL on Render) work with Docker Compose:

```bash
# Start everything locally
docker-compose up

# Load data into the containerized SQLite
docker-compose exec backend python data_scraper/load_data.py --limit 200

# Check the data
docker-compose logs -f backend
```

---

## Comparison: SQLite vs PostgreSQL

| Feature         | SQLite                | PostgreSQL                             |
| --------------- | --------------------- | -------------------------------------- |
| **Best for**    | Local dev             | Production                             |
| **Setup**       | Zero config           | Requires connection string             |
| **Persistence** | File on disk          | Remote database                        |
| **Scalability** | Single file           | Distributed                            |
| **Command**     | `python load_data.py` | `DATABASE_URL=... python load_data.py` |

---

## Options & Examples

### Load different amounts

```bash
# 200 players (default)
python data_scraper/load_data.py

# 500 players
python data_scraper/load_data.py --limit 500

# All 32,601 players
python data_scraper/load_data.py --limit 32601
```

### Clear and reload

```bash
# Reset: delete existing players, load 200 fresh ones
python data_scraper/load_data.py --reset --limit 200
```

### Use with environment variables

```bash
# Use Render PostgreSQL
export DATABASE_URL="postgresql+psycopg2://user:password@render.host:5432/football"
python data_scraper/load_data.py --limit 200

# Use local SQLite (default)
python data_scraper/load_data.py --limit 200
```

---

## What Gets Loaded?

Example output after running the script:

```
🚀 Football Player Data Loader
==================================================
📚 Loading competition mappings...
   ✓ Loaded 44 competitions

🗄️  Database: sqlite:///./football_players.db...

📖 Reading players.csv...
   Total players in CSV: 32,601
   📊 Sampling 200 random players

💾 Inserting players into database...
   50 players processed...
   100 players processed...
   150 players processed...
   200 players processed...

✅ Data loading complete!
   ✓ Inserted: 200 players
   ⚠️  Skipped: 0 players
   📊 Total players in database: 201
```

---

## Sample Data

After running the script with 200 players:

```
✅ Total Players: 201

Sample Players:
ID: 1 | Name: Lionel Messi
  Country: Argentina | Age: 37 | Status: ACTIVE
  Team: Inter Miami | League: Mls
  Market Value: $16,000,000

ID: 2 | Name: Christian Jakobsen
  Country: Denmark | Age: 32 | Status: ACTIVE
  Team: Hvidovre If | League: Superligaen
  Market Value: $350,000

ID: 3 | Name: Rubén Alcaraz
  Country: Spain | Age: 34 | Status: ACTIVE
  Team: Cádiz Cf | League: Laliga
  Market Value: $1,500,000
```

---

## Troubleshooting

**Q: I get "ModuleNotFoundError: No module named 'sqlmodel'"**

A: Install dependencies:

```bash
cd backend
uv sync --no-dev
```

**Q: "players.csv not found"**

A: Make sure you're in the `backend/` directory and the file exists at `data_scraper/rawData/players.csv`

**Q: PostgreSQL connection fails**

A: Check your DATABASE_URL format:

```
postgresql+psycopg2://user:password@host:5432/database
```

**Q: Want to reload data without losing existing records?**

A: Don't use `--reset`, just run it again (will add more players):

```bash
python data_scraper/load_data.py --limit 100
```

---

## Next Steps

1. ✅ Load 200 players locally: `python data_scraper/load_data.py`
2. ✅ Test locally: `npm run dev` & `uv run python -m uvicorn ...`
3. 📋 When ready for production: Load into Render PostgreSQL
4. 🚀 Deploy: Render automatically picks up the data

Done! Your database is now populated and ready. 🎉
