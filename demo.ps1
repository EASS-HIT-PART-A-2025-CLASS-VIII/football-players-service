Write-Host "Starting EX3 Full Stack Microservices Demo..." -ForegroundColor Green

# 1. Start Services
Write-Host "Building and starting Docker services..."
docker-compose up -d --build

# 2. Waiting for Initial Startup
Write-Host "Waiting 10s for services to stabilize..."
Start-Sleep -Seconds 10

# 3. Health Check
$response = Invoke-WebRequest -Uri "http://localhost:8000/health" -Method Get -ErrorAction SilentlyContinue
if ($response.StatusCode -eq 200) {
    Write-Host "Backend is UP!" -ForegroundColor Green
} else {
    Write-Host "Backend might be initializing..." -ForegroundColor Yellow
}

# 4. Instructions
Write-Host "`n=================================================="
Write-Host "DEMO READY" -ForegroundColor Cyan
Write-Host "=================================================="
Write-Host "1. Frontend: http://localhost:3000 (React)"
Write-Host "2. Backend Docs: http://localhost:8000/docs (Swagger)"
Write-Host "3. AI Service (Internal): http://localhost:8001/health"
Write-Host "4. Worker: logs available via 'docker-compose logs -f worker'"
Write-Host "`nTo generate a scouting report:"
Write-Host "   - Go to Frontend."
Write-Host "   - Create a Player."
Write-Host "   - Click 'Scout' (Ensure backend has GEMINI_API_KEY in docker-compose or .env)"
Write-Host "=================================================="

# 5. Run Async Refresher
Write-Host "Running Async Refresher Script (Step 09 Demo)..."
docker-compose exec backend uv run python backend/scripts/refresh.py

Write-Host "`nDemo script completed."
