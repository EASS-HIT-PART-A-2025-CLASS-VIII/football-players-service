# 📊 Data Loading Script

This script loads football player data from CSV files into your database (SQLite or PostgreSQL).

## Features

✅ **Automatic database detection** - Works with both SQLite (local dev) and PostgreSQL (production)  
✅ **Smart data mapping** - Converts CSV data to match your `Player` model schema  
✅ **Random sampling** - Load only 200 random players for testing (avoids large data loads)  
✅ **Competition mapping** - Links players to competitions/leagues from `competitions.csv`  
✅ **Age calculation** - Automatically calculates age from date of birth  
✅ **Data validation** - Validates all fields against model constraints  
✅ **Graceful error handling** - Skips invalid records and continues

## Data Source

The CSV files are downloaded from the **Kaggle Dataset**: [Player Scores](https://www.kaggle.com/datasets/davidcariboo/player-scores)

Download the dataset and extract:

- `competitions.csv`
- `players.csv`
- `clubs.csv`

Place them in the `backend/data_scraper/rawData/` directory.

## CSV Files

The script expects these files in `rawData/`:

- **players.csv** - Player data (32,601 records)

  - Columns: `player_id`, `first_name`, `last_name`, `date_of_birth`, `country_of_citizenship`, `current_club_name`, `current_club_domestic_competition_id`, `market_value_in_eur`, `last_season`, etc.
  - Source: [Kaggle - Player Scores Dataset](https://www.kaggle.com/datasets/davidcariboo/player-scores)

- **competitions.csv** - Competition/league data (44 records)
  - Columns: `competition_id`, `name`, etc.
  - Used to map league IDs to league names
  - Source: [Kaggle - Player Scores Dataset](https://www.kaggle.com/datasets/davidcariboo/player-scores)

## Data Mapping

| CSV Field                              | Model Field    | Transform                                |
| -------------------------------------- | -------------- | ---------------------------------------- |
| `first_name` + `last_name`             | `full_name`    | Concatenate & title case                 |
| `country_of_citizenship`               | `country`      | Title case                               |
| `date_of_birth`                        | `age`          | Calculate from current date              |
| `current_club_name`                    | `current_team` | Title case                               |
| `current_club_domestic_competition_id` | `league`       | Map from competitions.csv                |
| `market_value_in_eur`                  | `market_value` | Parse number                             |
| `last_season`                          | `status`       | "retired" if >5 years old, else "active" |

## Usage

### Local SQLite Database

```bash
cd backend

# Load 200 random players (default)
python data_scraper/load_data.py

# Load all players
python data_scraper/load_data.py --limit 32601

# Clear existing data and reload
python data_scraper/load_data.py --reset --limit 200
```

### Production PostgreSQL Database

```bash
# Set DATABASE_URL environment variable
export DATABASE_URL="postgresql+psycopg2://user:password@host:5432/football"

# Run the loader
python data_scraper/load_data.py --limit 200
```

### Windows PowerShell

```powershell
$env:DATABASE_URL = "postgresql+psycopg2://user:password@host:5432/football"
python data_scraper/load_data.py --limit 200
```

## Options

```
--limit N     : Number of random players to load (default: 200)
--reset       : Clear existing players before loading
```

## Examples

```bash
# Load 200 random players into SQLite
python data_scraper/load_data.py

# Load 500 random players
python data_scraper/load_data.py --limit 500

# Reset database and load 200 fresh players
python data_scraper/load_data.py --reset

# Load all players (be patient!)
python data_scraper/load_data.py --limit 32601
```

## Docker Compose

If using Docker, you can still run the loader:

```bash
# From project root
docker-compose exec backend python data_scraper/load_data.py --limit 200
```

The database volume will persist the data between container restarts.

## Output Example

```
🚀 Football Player Data Loader
==================================================
📚 Loading competition mappings...
   ✓ Loaded 44 competitions

🗄️  Database: sqlite:///./football_players.db...

📖 Reading players.csv...
   Total players in CSV: 32601
   📊 Sampling 200 random players

💾 Inserting players into database...
   50 players processed...
   100 players processed...
   150 players processed...
   200 players processed...

✅ Data loading complete!
   ✓ Inserted: 200 players
   ⚠️  Skipped: 0 players
   📊 Total players in database: 200
```

## Troubleshooting

**ModuleNotFoundError: No module named 'sqlmodel'**

```bash
cd backend
uv sync --no-dev
```

**Database connection error**

- Ensure `DATABASE_URL` environment variable is set correctly
- For PostgreSQL, verify host/port/credentials
- For SQLite, ensure `backend/` directory is writable

**Players not loading**

- Check that `rawData/players.csv` and `rawData/competitions.csv` exist
- Verify CSV files are not corrupted
- Check file encoding (should be UTF-8)

## Notes

- The script uses **random sampling** to avoid loading all 32k players at once during development
- **Status determination**: Players with `last_season` > 5 years ago are marked as "retired"
- **Age calculation**: From `date_of_birth`; defaults to 25 if missing
- **Market value**: Converted from EUR to integer; clamped to 0-10 billion
- **Validation**: Fields that don't meet model constraints are skipped
