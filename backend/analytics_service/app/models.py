"""
Analytics Service Models
Pydantic models for AI analysis responses
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class PlayerAnalysis(BaseModel):
    """AI-generated player analysis."""

    player_id: int
    player_name: str
    insights: List[str] = Field(
        description="List of AI-generated insights about the player"
    )
    performance_score: float = Field(
        ge=0, le=100, description="Overall performance score (0-100)"
    )
    generated_at: str


class CareerPrediction(BaseModel):
    """Career trajectory prediction."""

    player_id: int
    player_name: str
    career_phase: str = Field(
        description="Current career phase (early_development, peak_performance, decline, end_of_career)"
    )
    expected_years_remaining: int = Field(ge=0, description="Estimated years left")
    peak_age_reached: bool = Field(description="Whether player has reached peak age")
    recommendation: str
    predicted_at: str


class InjuryRisk(BaseModel):
    """Injury risk assessment."""

    player_id: int
    player_name: str
    risk_score: float = Field(ge=0, le=1, description="Risk score from 0 (low) to 1 (high)")
    risk_level: str = Field(description="Risk level: low, medium, high")
    risk_factors: List[str]
    recommendation: str
    assessed_at: str


class FullInsights(BaseModel):
    """Complete insights for a player."""

    player_id: int
    analysis: PlayerAnalysis
    career_prediction: CareerPrediction
    injury_risk: InjuryRisk


class PlayerData(BaseModel):
    """Player data structure from main API."""

    id: int
    full_name: str
    age: int
    status: str
    country: str
    current_team: Optional[str] = None
    league: Optional[str] = None
    market_value: Optional[int] = None
