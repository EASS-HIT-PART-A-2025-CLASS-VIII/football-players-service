from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel
import os

try:
    import google.generativeai as genai
except ImportError:
    genai = None

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
    if not api_key or api_key == "your_gemini_api_key_here" or genai is None:
        # Fallback for demo/testing without key
        return {"report": f"⚠️ Simulated Report for {request.player_name}: This player shows great promise and excellent technical skills for their age ({request.age}). Based on their position ({request.position}), they demonstrate strong fundamentals. (No valid GEMINI_API_KEY provided - using fallback mode)"}

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        prompt = (
            f"Write a short, professional football scouting report for a player named {request.player_name}. "
            f"Position: {request.position}. Age: {request.age}. "
            f"Stats: {request.stats}. "
            "Focus on strengths and potential. Keep it under 100 words."
        )
        
        response = model.generate_content(prompt)
        return {"report": response.text}
    except Exception as e:
        # Log the error and return fallback instead of crashing
        print(f"ERROR: Gemini API failed: {str(e)}")
        return {"report": f"⚠️ Fallback Report for {request.player_name}: Excellent player with strong fundamentals. Position: {request.position}, Age: {request.age}. Shows promise for development. (API Error: {str(e)[:100]})"}

@app.get("/health")
def health():
    return {"status": "ok"}
