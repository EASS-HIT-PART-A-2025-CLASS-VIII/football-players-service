from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel
import os
import google.generativeai as genai

app = FastAPI(title="AI Scout Service")

class ScoutRequest(BaseModel):
    player_name: str
    position: str
    age: int
    stats: dict

class ScoutResponse(BaseModel):
    report: str

@app.post("/generate", response_model=ScoutResponse)
def generate_report(request: ScoutRequest):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        # Fallback for demo/testing without key
        return {"report": "Simulated Report: This player shows great promise. (No API Key provided)"}
        # Alternatively raise error:
        # raise HTTPException(status_code=500, detail="GEMINI_API_KEY not set")

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = (
            f"Write a short, professional football scouting report for a player named {request.player_name}. "
            f"Position: {request.position}. Age: {request.age}. "
            f"Stats: {request.stats}. "
            "Focus on strengths and potential. Keep it under 100 words."
        )
        
        response = model.generate_content(prompt)
        return {"report": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health():
    return {"status": "ok"}
