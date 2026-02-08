"""
Analytics Service - Main Application
FastAPI microservice for AI-powered player analytics
"""

import logging
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
import httpx

from .ai_engine import AIAnalysisEngine
from .models import PlayerAnalysis, CareerPrediction, InjuryRisk, FullInsights, PlayerData

# Configure logging
logger = logging.getLogger("analytics-service")
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s [%(name)s] %(message)s"
)

# Initialize AI engine
ai_engine = AIAnalysisEngine()

# HTTP client for calling main API
http_client: Optional[httpx.AsyncClient] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    global http_client
    
    # Startup
    http_client = httpx.AsyncClient(timeout=10.0)
    logger.info("=" * 60)
    logger.info("🤖 Analytics Service v1.0.0")
    logger.info("=" * 60)
    logger.info("Features:")
    logger.info("  ✓ Mock AI Analysis (free, fast, deterministic)")
    logger.info("  ✓ Performance scoring")
    logger.info("  ✓ Career trajectory prediction")
    logger.info("  ✓ Injury risk assessment")
    logger.info("=" * 60)
    
    yield
    
    # Shutdown
    await http_client.aclose()
    logger.info("Analytics Service shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="Football Analytics Service",
    description="AI-powered analytics for football players",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "analytics",
        "version": "1.0.0"
    }


@app.post("/analyze/{player_id}", response_model=PlayerAnalysis)
async def analyze_player(player_id: int):
    """
    Analyze a player and return AI-generated insights.
    
    This endpoint fetches player data from the main API and generates
    intelligent analysis including performance scoring and recommendations.
    """
    player = await fetch_player_from_main_api(player_id)
    
    analysis = await ai_engine.analyze_player(player)
    logger.info(f"Generated analysis for player {player_id}: {player.full_name}")
    
    return analysis


@app.post("/predict-career/{player_id}", response_model=CareerPrediction)
async def predict_career(player_id: int):
    """
    Predict player's career trajectory.
    
    Returns expected years remaining, career phase, and strategic recommendations.
    """
    player = await fetch_player_from_main_api(player_id)
    
    prediction = await ai_engine.predict_career(player)
    logger.info(f"Generated career prediction for player {player_id}: {prediction.career_phase}")
    
    return prediction


@app.post("/injury-risk/{player_id}", response_model=InjuryRisk)
async def assess_injury_risk(player_id: int):
    """
    Assess injury risk based on player age, status, and historical patterns.
    
    Returns risk score, risk level, and preventive recommendations.
    """
    player = await fetch_player_from_main_api(player_id)
    
    risk_assessment = await ai_engine.assess_injury_risk(player)
    logger.info(f"Assessed injury risk for player {player_id}: {risk_assessment.risk_level}")
    
    return risk_assessment


@app.get("/insights/{player_id}", response_model=FullInsights)
async def get_full_insights(player_id: int):
    """
    Get comprehensive insights for a player.
    
    Returns all analysis types: performance analysis, career prediction, and injury risk.
    This is the recommended endpoint for full player analytics.
    """
    player = await fetch_player_from_main_api(player_id)
    
    # Generate all insights concurrently
    analysis = await ai_engine.analyze_player(player)
    prediction = await ai_engine.predict_career(player)
    risk = await ai_engine.assess_injury_risk(player)
    
    logger.info(f"Generated full insights for player {player_id}: {player.full_name}")
    
    return FullInsights(
        player_id=player_id,
        analysis=analysis,
        career_prediction=prediction,
        injury_risk=risk,
    )


async def fetch_player_from_main_api(player_id: int) -> PlayerData:
    """
    Fetch player data from the main FastAPI backend.
    
    Raises:
        HTTPException: If player not found or API unavailable
    """
    main_api_url = "http://backend:8000"  # Docker Compose service name
    
    try:
        response = await http_client.get(f"{main_api_url}/players/{player_id}")
        response.raise_for_status()
        
        player_data = response.json()
        return PlayerData(**player_data)
        
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Player {player_id} not found"
            )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Main API unavailable"
        )
    except Exception as e:
        logger.error(f"Error fetching player {player_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Failed to fetch player data from main API"
        )
