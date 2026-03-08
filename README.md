# 📞 Sales Call Transcript Analyzer

A FastAPI service that analyzes sales call transcripts using GPT-4o and returns structured, actionable insights — including sentiment analysis, objection tracking, action items, and salesperson performance scores.

---

## Features

- **Call Summary** — concise overview of the conversation
- **Sentiment & Tone Analysis** — overall mood, salesperson/prospect tone, and emotional shifts
- **Topics & Objections** — key topics discussed, objections raised, how they were handled, and any unresolved issues
- **Action Items** — commitments from both sides and suggested next steps
- **Performance Scoring** — 0–100 scores across rapport building, discovery questioning, objection handling, and closing effectiveness, plus coaching tips

---

## Requirements

- Python 3.10+
- An [OpenAI API key](https://platform.openai.com/api-keys) with access to `gpt-4o`

---

## Setup

**1. Clone the repo and install dependencies:**

```bash
pip install -r requirements.txt
```

**2. Run the server:**

```bash
uvicorn main:app --reload --port 8000 
```

The API will be available at `http://localhost:8000`.

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Service info and endpoint listing |
| `GET` | `/health` | Health check |
| `GET` | `/docs` | Interactive Swagger UI |
| `POST` | `/analyze` | Analyze transcript via JSON body |
| `POST` | `/analyze-form` | Analyze transcript via form-data |

---

## Usage

In Postman, set the request to `POST /analyze-form` with **Body → form-data** and add these keys:

| Key | Value |
|-----|-------|
| `transcript` | *(paste transcript text directly)* |
| `api_key` | `sk-...` |
| `salesperson_name` | *(optional)* |

---

## Response Structure

```json
{
  "call_summary": "...",
  "sentiment_tone": {
    "overall_sentiment": "Positive | Neutral | Negative",
    "salesperson_tone": "...",
    "prospect_tone": "...",
    "emotional_shifts": ["..."]
  },
  "topics_and_objections": {
    "key_topics": ["..."],
    "objections_raised": ["..."],
    "how_objections_were_handled": ["..."],
    "unresolved_objections": ["..."]
  },
  "action_items": {
    "salesperson_actions": ["..."],
    "prospect_commitments": ["..."],
    "suggested_next_steps": ["..."]
  },
  "performance": {
    "overall_score": 82,
    "rapport_building": 90,
    "discovery_questioning": 75,
    "objection_handling": 80,
    "closing_effectiveness": 70,
    "coaching_tips": ["..."],
    "strengths": ["..."],
    "areas_for_improvement": ["..."]
  }
}
```

---

## Error Handling

| Status | Meaning |
|--------|---------|
| `400` | Transcript is empty or too short (minimum 50 characters) |
| `401` | Invalid OpenAI API key |
| `429` | OpenAI rate limit reached — wait and retry |
| `500` | AI response parsing failure or unexpected error |

---

## Interactive Docs

Once the server is running, visit **`http://localhost:8000/docs`** for the full Swagger UI where you can test all endpoints directly in your browser.
