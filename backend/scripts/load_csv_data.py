#!/usr/bin/env python3
"""
CSV Data Loader for Football Player Service

This script loads additional players from CSV files to supplement the basic
sample data that's automatically seeded during Docker startup.

Usage:
    # Load 100 additional random players from CSV
    docker compose exec backend python scripts/load_csv_data.py

    # Load 500 players and reset existing data
    docker compose exec backend python scripts/load_csv_data.py --limit 500 --reset

    # Load all available players from CSV
    docker compose exec backend python scripts/load_csv_data.py --limit 0

Requirements:
    - CSV files in data_scraper/rawData/ (players.csv, competitions.csv)
    - Container must be running (for docker exec)

This is separate from the automatic seeding that happens during startup.
"""

import os
import sys
from pathlib import Path

# Add backend to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import the existing load_data functionality
from data_scraper.load_data import load_players


def main():
    """Main entry point for CSV data loading."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Load additional player data from CSV files"
    )
    parser.add_argument(
        "--reset", 
        action="store_true", 
        help="Clear all existing players before loading (DESTRUCTIVE)"
    )
    parser.add_argument(
        "--limit", 
        type=int, 
        default=100,
        help="Number of random players to load (default: 100, use 0 for all)"
    )
    
    args = parser.parse_args()
    
    print("🚀 Football Player Service - CSV Data Loader")
    print("=" * 60)
    
    if args.reset:
        print("⚠️  WARNING: This will DELETE all existing players!")
        confirm = input("Type 'yes' to continue: ")
        if confirm.lower() != 'yes':
            print("❌ Cancelled")
            return
    
    # Use existing load_data function
    load_players(limit=args.limit if args.limit > 0 else 999999, reset=args.reset)
    
    print("\n✅ CSV loading complete!")
    print("   💡 Tip: Visit http://localhost:3000 to see the loaded players")


if __name__ == "__main__":
    main()