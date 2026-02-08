"""
Mock AI Analysis Engine
Provides intelligent player insights without external API calls.
Completely free, fast, and deterministic.
"""

from datetime import datetime
from typing import List
import random

from .models import PlayerData, PlayerAnalysis, CareerPrediction, InjuryRisk


class AIAnalysisEngine:
    """
    Mock AI engine for player analysis.
    - Uses pattern-based insights (completely FREE)
    - Deterministic results based on player attributes
    - Can be upgraded to real LLM later (Groq, Claude, etc.)
    """

    async def analyze_player(self, player: PlayerData) -> PlayerAnalysis:
        """Generate player analysis insights."""

        insights = []

        # Age-based insights
        if player.age < 20:
            insights.append(
                f"🌟 Young talent: {player.full_name} has significant growth potential"
            )
            insights.append("Early career stage - focus on skill development")
        elif 20 <= player.age < 25:
            insights.append(
                f"⭐ Rising star: {player.full_name} is in development years"
            )
            insights.append("Building experience and refining playstyle")
        elif 25 <= player.age < 30:
            insights.append(
                f"💪 Prime years: {player.full_name} is in peak performance years"
            )
            insights.append("Maximum physical and technical capabilities")
        elif 30 <= player.age < 33:
            insights.append(
                f"🏆 Experienced: {player.full_name} brings valuable experience"
            )
            insights.append("Leadership qualities and tactical maturity")
        else:
            insights.append(
                f"🔄 Veteran: {player.full_name} is approaching career twilight"
            )
            insights.append("Consider transition planning and mentoring roles")

        # Status-based insights
        if player.status == "active":
            insights.append("✅ Actively playing - available for selection")
        elif player.status == "retired":
            insights.append("🏁 Retired from professional football")
        elif player.status == "free_agent":
            insights.append("🎯 Free agent - available for team transfer")
            insights.append("No current contract obligations")

        # Market value insights
        if player.market_value:
            if player.market_value > 50_000_000:
                insights.append(
                    f"💎 Elite tier: Market value ${player.market_value:,} (world-class)"
                )
                insights.append("Among the most valuable players globally")
            elif player.market_value > 20_000_000:
                insights.append(
                    f"💰 High value: Market value ${player.market_value:,} (established star)"
                )
                insights.append("Strong market position with proven track record")
            elif player.market_value > 5_000_000:
                insights.append(
                    f"📈 Growing value: Market value ${player.market_value:,} (solid performer)"
                )
                insights.append("Consistent performance driving market interest")
            else:
                insights.append(
                    f"💵 Development value: Market value ${player.market_value:,}"
                )
                insights.append("Building reputation and market presence")

        # League/Team insights
        if player.league:
            insights.append(f"🏟️ Competing in {player.league}")
            if player.current_team:
                insights.append(f"Current club: {player.current_team}")

        # Country-based insights
        insights.append(f"🌍 International representation: {player.country}")

        # Performance score (mock calculation)
        performance_score = self._calculate_performance_score(player)

        return PlayerAnalysis(
            player_id=player.id,
            player_name=player.full_name,
            insights=insights,
            performance_score=performance_score,
            generated_at=datetime.utcnow().isoformat(),
        )

    async def predict_career(self, player: PlayerData) -> CareerPrediction:
        """Predict player's career trajectory."""

        # Set random seed based on player ID for deterministic results
        random.seed(player.id * 12345)

        # Career length estimation based on age
        if player.age < 20:
            expected_years = random.randint(12, 18)
            career_phase = "early_development"
            peak_reached = False
        elif 20 <= player.age < 25:
            expected_years = random.randint(8, 14)
            career_phase = "development"
            peak_reached = False
        elif 25 <= player.age < 30:
            expected_years = random.randint(6, 10)
            career_phase = "peak_performance"
            peak_reached = True
        elif 30 <= player.age < 33:
            expected_years = random.randint(3, 6)
            career_phase = "decline"
            peak_reached = True
        else:
            expected_years = random.randint(1, 3)
            career_phase = "end_of_career"
            peak_reached = True

        # Adjust for player status
        if player.status == "retired":
            expected_years = 0
            career_phase = "retired"
        elif player.status == "free_agent":
            expected_years = max(1, expected_years - 2)

        # Reset random seed
        random.seed()

        return CareerPrediction(
            player_id=player.id,
            player_name=player.full_name,
            career_phase=career_phase,
            expected_years_remaining=expected_years,
            peak_age_reached=peak_reached,
            recommendation=self._get_career_recommendation(career_phase, player.status),
            predicted_at=datetime.utcnow().isoformat(),
        )

    async def assess_injury_risk(self, player: PlayerData) -> InjuryRisk:
        """Assess injury risk based on age, status, and other factors."""

        risk_score = 0.0
        risk_factors = []

        # Age-based risk
        if player.age > 32:
            risk_score += 0.35
            risk_factors.append("Age 32+ significantly increases injury risk")
        elif player.age > 30:
            risk_score += 0.25
            risk_factors.append("Age 30+ increases recovery time and injury risk")
        elif player.age < 20:
            risk_score += 0.15
            risk_factors.append("Young players prone to growth-related injuries")

        # Status-based risk
        if player.status == "retired":
            risk_score = 0.0
            risk_factors = ["Player is retired - no active injury risk"]
        elif player.status == "free_agent":
            risk_score += 0.20
            risk_factors.append("Free agent status may indicate prior injury history")

        # Market value correlation (inverse)
        if player.market_value and player.market_value > 30_000_000:
            # High-value players typically have better medical care
            risk_score -= 0.10
        elif player.market_value and player.market_value < 2_000_000:
            risk_score += 0.10
            risk_factors.append("Limited access to premium medical facilities")

        # Add deterministic variation based on player ID
        random.seed(player.id * 54321)
        variation = random.uniform(-0.05, 0.05)
        risk_score += variation
        random.seed()

        # Clamp between 0 and 1
        risk_score = max(0.0, min(1.0, risk_score))

        # Determine risk level
        if risk_score > 0.7:
            risk_level = "high"
            recommendation = "⚠️ High risk: Recommend comprehensive medical monitoring and modified training"
        elif risk_score > 0.4:
            risk_level = "medium"
            recommendation = "⚠️ Moderate risk: Regular fitness assessments and injury prevention protocols recommended"
        else:
            risk_level = "low"
            recommendation = "✅ Low risk: Continue standard training and match schedule"

        if not risk_factors:
            risk_factors.append("No significant risk factors identified")

        return InjuryRisk(
            player_id=player.id,
            player_name=player.full_name,
            risk_score=round(risk_score, 2),
            risk_level=risk_level,
            risk_factors=risk_factors,
            recommendation=recommendation,
            assessed_at=datetime.utcnow().isoformat(),
        )

    def _calculate_performance_score(self, player: PlayerData) -> float:
        """Mock performance calculation based on player attributes."""
        score = 50.0  # Base score

        # Age bonus (peak performance years)
        if 25 <= player.age <= 29:
            score += 25
        elif 22 <= player.age <= 24 or 30 <= player.age <= 31:
            score += 15
        elif 20 <= player.age <= 21 or 32 <= player.age <= 33:
            score += 5

        # Market value bonus
        if player.market_value:
            if player.market_value > 50_000_000:
                score += 20
            elif player.market_value > 20_000_000:
                score += 15
            elif player.market_value > 10_000_000:
                score += 10
            elif player.market_value > 5_000_000:
                score += 5

        # Status bonus
        if player.status == "active":
            score += 10
        elif player.status == "free_agent":
            score -= 5
        elif player.status == "retired":
            score -= 30

        # Clamp to 0-100
        return max(0.0, min(100.0, score))

    def _get_career_recommendation(self, phase: str, status: str) -> str:
        """Get career recommendation based on phase."""
        if status == "retired":
            return "Explore coaching, punditry, or business opportunities in football"

        recommendations = {
            "early_development": "Focus on skill development, gain first-team experience, and build physical conditioning",
            "development": "Maximize playing time and seek opportunities in competitive leagues",
            "peak_performance": "Capitalize on peak years - seek optimal contracts and trophy opportunities",
            "decline": "Consider leadership roles, mentoring younger players, and career transition planning",
            "end_of_career": "Plan retirement transition - coaching badges, business ventures, or media roles",
        }
        return recommendations.get(phase, "Continue current trajectory and maintain fitness")
