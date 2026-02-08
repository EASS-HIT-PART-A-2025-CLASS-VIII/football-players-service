#!/bin/bash
# Quick setup script to load data and start the app

echo "🚀 Football Player Service - Quick Setup"
echo "=========================================="
echo ""

# Check if we're in the right directory
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ Please run this script from the project root directory"
    exit 1
fi

# Load the data
echo "📊 Loading 200 random players into SQLite..."
cd backend
python data_scraper/load_data.py --limit 200

echo ""
echo "✅ Data loaded successfully!"
echo ""
echo "🎯 Next steps:"
echo ""
echo "  Option 1: Local Development"
echo "  Terminal 1: cd backend && uv run python -m uvicorn football_player_service.app.main:app --reload --port 8000"
echo "  Terminal 2: cd frontend && npm run dev"
echo "  Open: http://localhost:5173"
echo ""
echo "  Option 2: Docker Compose"
echo "  Run: docker-compose up"
echo "  Open: http://localhost:3000"
echo "  API Docs: http://localhost:8000/docs"
echo ""
