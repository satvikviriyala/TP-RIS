from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import FeedbackInput, AnalysisResult
from pipeline import analyze_with_llm

app = FastAPI(title="TP-RIS Offline Backend")

# Setup CORS for local React frontend - allow all origins for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/analyze-feedback", response_model=AnalysisResult)
async def analyze_feedback_endpoint(input_data: FeedbackInput):
    """
    Analyzes feedback text using the local TP-RIS pipeline.
    """
    if not input_data.review_text.strip():
        raise HTTPException(status_code=400, detail="Review text cannot be empty.")
    
    result = analyze_with_llm(input_data)
    return result

@app.get("/health")
async def health_check():
    return {"status": "ok", "system": "TP-RIS-Offline"}
