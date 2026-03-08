from fastapi import FastAPI, HTTPException, Form
from pydantic import BaseModel
from openai import OpenAI
from typing import Optional
from dotenv import load_dotenv
import json
import os

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

app = FastAPI(
    title="Sales Call Transcript Analyzer",
    description="Analyzes sales call transcripts and returns actionable insights.",
    version="1.0.0"
)

# ─── Models ───────────────────────────────────────────────────────────────────

class TranscriptRequest(BaseModel):
    transcript: str
    salesperson_name: Optional[str] = None

class SentimentTone(BaseModel):
    overall_sentiment: str
    salesperson_tone: str
    prospect_tone: str
    emotional_shifts: list[str]

class TopicsObjections(BaseModel):
    key_topics: list[str]
    objections_raised: list[str]
    how_objections_were_handled: list[str]
    unresolved_objections: list[str]

class ActionItems(BaseModel):
    salesperson_actions: list[str]
    prospect_commitments: list[str]
    suggested_next_steps: list[str]

class PerformanceScore(BaseModel):
    overall_score: int
    rapport_building: int
    discovery_questioning: int
    objection_handling: int
    closing_effectiveness: int
    coaching_tips: list[str]
    strengths: list[str]
    areas_for_improvement: list[str]

class TranscriptAnalysis(BaseModel):
    call_summary: str
    sentiment_tone: SentimentTone
    topics_and_objections: TopicsObjections
    action_items: ActionItems
    performance: PerformanceScore

# ─── Prompt ───────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are an expert sales coach and conversation analyst.
Analyze the provided sales call transcript and return a JSON object with exactly this structure:

{
  "call_summary": "2-3 sentence overview of the call",
  "sentiment_tone": {
    "overall_sentiment": "Positive | Neutral | Negative",
    "salesperson_tone": "description of salesperson tone",
    "prospect_tone": "description of prospect tone",
    "emotional_shifts": ["list of notable emotional changes during the call"]
  },
  "topics_and_objections": {
    "key_topics": ["list of main topics discussed"],
    "objections_raised": ["list of objections the prospect raised"],
    "how_objections_were_handled": ["how each objection was addressed"],
    "unresolved_objections": ["objections that were not properly handled"]
  },
  "action_items": {
    "salesperson_actions": ["tasks the salesperson committed to"],
    "prospect_commitments": ["things the prospect agreed to do"],
    "suggested_next_steps": ["recommended follow-up actions"]
  },
  "performance": {
    "overall_score": 0,
    "rapport_building": 0,
    "discovery_questioning": 0,
    "objection_handling": 0,
    "closing_effectiveness": 0,
    "coaching_tips": ["specific, actionable coaching tips"],
    "strengths": ["what the salesperson did well"],
    "areas_for_improvement": ["specific areas to work on"]
  }
}

All score fields must be integers between 0 and 100.
Return ONLY valid JSON. No markdown, no explanation, no extra text."""

# ─── Shared Logic ─────────────────────────────────────────────────────────────

def run_analysis(transcript: str, salesperson_name: Optional[str]) -> dict:
    if not OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY not set in .env file.")
    if not transcript.strip():
        raise HTTPException(status_code=400, detail="Transcript cannot be empty.")
    if len(transcript) < 50:
        raise HTTPException(status_code=400, detail="Transcript is too short to analyze.")
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        user_content = f"Salesperson: {salesperson_name or 'Unknown'}\n\nTranscript:\n{transcript}"
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_content}
            ],
            temperature=0.2,
            response_format={"type": "json_object"}
        )
        raw = response.choices[0].message.content
        return json.loads(raw)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Failed to parse AI response. Try again.")
    except Exception as e:
        error_msg = str(e)
        if "api_key" in error_msg.lower() or "authentication" in error_msg.lower() or "401" in error_msg:
            raise HTTPException(status_code=401, detail="Invalid OpenAI API key.")
        if "rate_limit" in error_msg.lower() or "429" in error_msg:
            raise HTTPException(status_code=429, detail="OpenAI rate limit reached. Please wait and retry.")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {error_msg}")

# ─── Endpoints ────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {
        "service": "Sales Transcript Analyzer",
        "status": "running",
        "endpoints": {
            "POST /analyze":      "Analyze transcript - raw JSON body",
            "POST /analyze-form": "Analyze transcript - form-data (recommended for Postman)",
            "GET  /health":       "Health check",
            "GET  /docs":         "Swagger UI"
        }
    }

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/analyze", response_model=TranscriptAnalysis)
def analyze_json(request: TranscriptRequest):
    """Analyze via raw JSON body. Use this when calling from code/apps."""
    return run_analysis(request.transcript, request.salesperson_name)

@app.post("/analyze-form", response_model=TranscriptAnalysis)
def analyze_form(
    transcript: str = Form(...),
    salesperson_name: Optional[str] = Form(None)
):
    """
    Analyze via form-data — RECOMMENDED FOR POSTMAN.
    Body > form-data, then add keys: transcript, salesperson_name
    Paste the transcript directly into the Value field — no escaping needed.
    """
    return run_analysis(transcript, salesperson_name)
