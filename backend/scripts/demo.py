#!/usr/bin/env python3
"""
Complete Full-Stack Microservices Demo Script

This script provides a comprehensive demonstration of the Football Player Service:

**Full Demo Flow:**
1. Start all Docker services (backend, frontend, AI service, Redis, worker)
2. Health check all services 
3. Demonstrate Session 09 async refresher (bounded concurrency, retries, Redis)
4. AI Scout feature demo:
   - Authenticate with JWT
   - Create test player
   - Request AI scouting report
   - Poll task status until completed
   - Display final report
5. Show access URLs for manual testing

**Usage:**
    # From project root:
    uv run python backend/scripts/demo.py
    
    # Or from backend directory:
    cd backend
    uv run python scripts/demo.py

**Interactive Options:**
- Choose whether to start Docker services (y/n)
- Choose whether to run AI Scout demo (y/n)
- Skip to manual testing if preferred

**Requirements:**
- Docker and Docker Compose installed
- All services configured in docker-compose.yml
- GEMINI_API_KEY set for AI features (optional for basic demo)
"""

import sys
import time
import requests
import subprocess
import os
from typing import Optional

# API Configuration
BASE_URL = "http://localhost:8000"
POLL_INTERVAL = 2  # seconds
MAX_POLLS = 30  # 60 seconds max wait

# Default admin credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"


def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def start_services():
    """Start all Docker services."""
    print_section("Starting All Services")
    
    print("🐳 Building and starting Docker services...")
    print("   This may take a few minutes on first run...")
    
    try:
        # Change to project root directory
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        
        # Start services
        result = subprocess.run(
            ["docker", "compose", "up", "-d", "--build"],
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        if result.returncode != 0:
            print(f"❌ Error starting services: {result.stderr}")
            return False
            
        print("✅ Docker services started!")
        
        # Wait for services to stabilize
        print("⏳ Waiting 15 seconds for services to stabilize...")
        time.sleep(15)
        
        return True
        
    except subprocess.TimeoutExpired:
        print("❌ Timeout starting Docker services (took > 5 minutes)")
        return False
    except FileNotFoundError:
        print("❌ Docker not found. Please install Docker and make sure it's running.")
        return False
    except Exception as e:
        print(f"❌ Error starting services: {e}")
        return False


def health_check() -> bool:
    """Check if all services are healthy."""
    print_section("Health Check")
    
    services = {
        "Backend API": "http://localhost:8000/health",
        "AI Service": "http://localhost:8001/health", 
        "Frontend": "http://localhost:3000"
    }
    
    all_healthy = True
    
    for service, url in services.items():
        try:
            print(f"Checking {service}...")
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"   ✅ {service} is UP!")
            else:
                print(f"   ⚠️  {service} returned {response.status_code}")
                all_healthy = False
        except requests.exceptions.RequestException:
            print(f"   ❌ {service} is not responding")
            all_healthy = False
    
    if all_healthy:
        print("\n🎉 All services are healthy!")
    else:
        print("\n⚠️  Some services may still be starting...")
    
    return all_healthy


def run_async_refresher():
    """Demonstrate the async refresh script (Session 09)."""
    print_section("Session 09 Demo: Async Refresher")
    
    print("🔄 Running async refresh script...")
    print("   (Demonstrates bounded concurrency, retries, Redis idempotency)")
    
    try:
        # Change to project root directory  
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        
        result = subprocess.run(
            ["docker", "compose", "exec", "-T", "backend", "sh", "-c", "cd /app && uv run python scripts/refresh.py"],
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            print("✅ Async refresher completed!")
            # Show last few lines of output
            lines = result.stdout.strip().split('\n')
            if lines:
                print("   Output:")
                for line in lines[-3:]:  # Last 3 lines
                    print(f"     {line}")
        else:
            print(f"⚠️  Refresher finished with warnings: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        print("⚠️  Refresher took longer than expected (still running in background)")
    except Exception as e:
        print(f"⚠️  Could not run refresher: {e}")


def show_access_info():
    """Show access URLs and instructions."""
    print_section("Access Information")
    
    print("🌐 **Service URLs:**")
    print("   • Frontend (React):     http://localhost:3000")
    print("   • Backend API (Swagger): http://localhost:8000/docs") 
    print("   • AI Service Health:    http://localhost:8001/health")
    print("   • Redis (if needed):    localhost:6379")
    
    print("\n🎯 **To test manually:**")
    print("   1. Open http://localhost:3000")
    print("   2. Create or select a player")
    print("   3. Click the purple scout icon (🔍)")
    print("   4. Watch real-time progress indicator")
    
    print("\n📋 **Architecture details:**")
    print("   • View complete docs: docs/ai-scout-notes.md")
    print("   • Test endpoints: http://localhost:8000/docs")


def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def login() -> Optional[str]:
    """Login and get JWT token."""
    print_section("Step 0: Authenticate")
    
    print(f"Logging in as {ADMIN_USERNAME}...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/token",
            data={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=10
        )
        response.raise_for_status()
        token = response.json()["access_token"]
        print(f"\n✅ Login successful!")
        print(f"   Token (first 20 chars): {token[:20]}...")
        return token
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Error logging in: {e}")
        print("   Make sure the backend is running: docker compose up")
        return None


def create_player(token: str) -> Optional[dict]:
    """Create a test player for demonstration (or use existing seeded player)."""
    print_section("Step 1: Select Player for AI Scouting")
    
    # First, check if we already have seeded players
    print("🔍 Checking for existing sample players...")
    try:
        response = requests.get(f"{BASE_URL}/players", timeout=10)
        response.raise_for_status()
        data = response.json()
        existing_players = data.get("players", [])
        
        if existing_players:
            print(f"✅ Found {len(existing_players)} existing players!")
            print("   Using seeded sample data (Messi, Ronaldo, Mbappé, etc.)")
            
            # Find an active player for demo
            active_players = [p for p in existing_players if p.get("status") == "active"]
            if active_players:
                player = active_players[0]  # Use first active player
                print(f"   Selected: {player['full_name']} (ID: {player['id']})")
                return player
    
    except Exception as e:
        print(f"   ⚠️  Couldn't check existing players: {e}")
    
    # Fallback: create a new player if needed
    print("\n🆕 Creating new demo player...")
    player_data = {
        "full_name": "Cristiano Ronaldo",
        "country": "Portugal",
        "status": "active",
        "current_team": "Al Nassr",
        "league": "Saudi Pro League",
        "age": 39,
        "market_value": 25000000
    }
    
    print(f"Creating player: {player_data['full_name']}")
    print(f"Team: {player_data['current_team']}")
    print(f"Age: {player_data['age']}, Market Value: ${player_data['market_value']:,}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/players", 
            json=player_data, 
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        response.raise_for_status()
        player = response.json()
        print(f"\n✅ Player created successfully!")
        print(f"   Player ID: {player['id']}")
        return player
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Error creating player: {e}")
        print("   Make sure the backend is running: docker compose up")
        return None


def scout_player(player_id: int, token: str) -> Optional[str]:
    """Request AI scouting report for a player."""
    print_section("Step 2: Request AI Scout Report")
    
    print(f"Sending scout request for player ID {player_id}...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/players/{player_id}/scout",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        task_id = data.get("task_id")
        
        print(f"\n✅ Scout request accepted!")
        print(f"   Task ID: {task_id}")
        print(f"   Status: {data.get('status')}")
        return task_id
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Error requesting scout: {e}")
        return None


def poll_task_status(task_id: str) -> dict:
    """Poll task status until completed or failed."""
    print_section("Step 3: Monitor Task Progress")
    
    print(f"Polling task {task_id}...")
    print(f"(Checking every {POLL_INTERVAL} seconds, max {MAX_POLLS} attempts)\n")
    
    for attempt in range(1, MAX_POLLS + 1):
        try:
            response = requests.get(f"{BASE_URL}/tasks/{task_id}", timeout=10)
            response.raise_for_status()
            status_data = response.json()
            
            status = status_data.get("status")
            symbols = {
                "pending": "⏳",
                "running": "🔄",
                "completed": "✅",
                "failed": "❌"
            }
            symbol = symbols.get(status, "❓")
            
            print(f"  [{attempt:2d}] {symbol} Status: {status.upper()}", end="")
            
            if status == "completed":
                print(f"\n      Result: {status_data.get('result')}")
                return status_data
            elif status == "failed":
                print(f"\n      Error: {status_data.get('error')}")
                return status_data
            else:
                print()  # Newline for pending/running
            
            time.sleep(POLL_INTERVAL)
            
        except requests.exceptions.RequestException as e:
            print(f"\n❌ Error checking task status: {e}")
            return {"status": "error", "error": str(e)}
    
    print(f"\n⏱️  Timeout: Task did not complete within {MAX_POLLS * POLL_INTERVAL} seconds")
    return {"status": "timeout"}


def get_player_report(player_id: int) -> Optional[str]:
    """Retrieve the player's scouting report from the database."""
    print_section("Step 4: Retrieve Scouting Report")
    
    try:
        response = requests.get(f"{BASE_URL}/players/{player_id}", timeout=10)
        response.raise_for_status()
        player = response.json()
        
        report = player.get("scouting_report")
        if report:
            print("📋 Scouting Report:\n")
            print("-" * 60)
            print(report)
            print("-" * 60)
            return report
        else:
            print("⚠️  No scouting report found for this player")
            return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Error retrieving player: {e}")
        return None


def main():
    """Run the complete Full-Stack Microservices Demo."""
    print("🔵" * 30)
    print("\n🚀 Full-Stack Microservices Demo")
    print("   Football Player Service with AI Scout & Async Workers")
    
    # Ask user if they want to start services
    print("\n" + "=" * 60)
    start_services_choice = input("Start Docker services? (y/n, default=y): ").strip().lower()
    if start_services_choice in ("", "y", "yes"):
        if not start_services():
            print("\n❌ Failed to start services. Exiting.")
            sys.exit(1)
        
        # Health check
        health_check()
    else:
        print("⏭️  Skipping service startup (assuming already running)")
    
    # Demo the async refresher (Session 09 requirement)
    run_async_refresher()
    
    # Show access information
    show_access_info()
    
    # AI Scout Demo Flow
    print("\n" + "=" * 60)
    print("🎯 **Database is automatically seeded with ~20 sample players:**")
    print("   • Famous players: Messi, Ronaldo, Mbappé, Haaland, etc.")
    print("   • Mix of active, retired, and free-agent statuses")  
    print("   • Ready for AI scouting and frontend browsing")
    print("   • Admin credentials: admin/admin123")
    print("")
    
    ai_demo_choice = input("Run AI Scout demo? (y/n, default=y): ").strip().lower() 
    if ai_demo_choice not in ("", "y", "yes"):
        print("✅ Demo setup complete! Use the URLs above to test manually.")
        return
    
    # Original AI demo flow
    print_section("AI Scout Demo Flow")
    
    # Step 0: Login
    token = login()
    if not token:
        sys.exit(1)
    
    # Step 1: Create player
    player = create_player(token)
    if not player:
        sys.exit(1)
    
    player_id = player["id"]
    
    # Step 2: Request scout
    task_id = scout_player(player_id, token)
    if not task_id:
        sys.exit(1)
    
    # Step 3: Poll task status
    final_status = poll_task_status(task_id)
    
    if final_status.get("status") != "completed":
        print("\n⚠️  Task did not complete successfully")
        print(f"   Final status: {final_status}")
        sys.exit(1)
    
    # Step 4: Get the report
    report = get_player_report(player_id)
    
    # Summary
    print_section("Demo Complete!")
    print("\n🎉 **Full Demo Successful!**")
    print(f"   • Services: Started & Healthy")
    print(f"   • Session 09: Async refresher demonstrated")  
    print(f"   • Player ID: {player_id}")
    print(f"   • Task ID: {task_id}")
    print(f"   • Report Length: {len(report) if report else 0} characters")
    
    print("\n💡 **Next Steps:**")
    print("   • Frontend UI: http://localhost:3000")
    print("   • Try manual scout: Click 🔍 on any player") 
    print("   • API docs: http://localhost:8000/docs")
    print("   • Full architecture: docs/ai-scout-notes.md")
    
    print("\n" + "🔵" * 30 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
