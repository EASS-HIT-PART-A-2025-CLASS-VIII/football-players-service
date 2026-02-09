#!/bin/bash
set -e

echo "🚀 Starting Football Player Service..."

# Wait for database to be ready (if using external DB)
echo "📋 Checking database connection..."

# Run database migrations and seeding
echo "🗄️  Initializing database..."
python -c "
from football_player_service.app.database import init_db
init_db()
print('✅ Database tables created')
"

# Seed sample data (idempotent - only if empty)
echo "🌱 Seeding sample data..."
python scripts/seed_data.py

echo "✅ Database initialization complete!"
echo ""

# Start the main application
echo "🌟 Starting FastAPI server..."
exec "$@"