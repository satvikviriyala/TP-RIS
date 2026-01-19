from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from .models import FeedbackInput, AnalysisResult
from .pipeline import analyze_with_llm
import csv
import os
from datetime import datetime

app = FastAPI(title="TP-RIS Offline Backend")

# CSV file path for storing submitted feedback
FEEDBACK_CSV_PATH = os.path.join(os.path.dirname(__file__), "..", "submitted_feedback.csv")

# Setup CORS for local React frontend - allow all localhost ports for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for local development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class FeedbackSubmission(BaseModel):
    feedback_text: str
    observation: str | None = None
    feeling: str | None = None
    need: str | None = None
    request: str | None = None
    trust_score: float | None = None

@app.post("/analyze-feedback", response_model=AnalysisResult)
async def analyze_feedback_endpoint(input_data: FeedbackInput):
    """
    Analyzes feedback text using the local TP-RIS pipeline.
    """
    if not input_data.review_text.strip():
        raise HTTPException(status_code=400, detail="Review text cannot be empty.")
    
    # Call the logic layer
    result = analyze_with_llm(input_data)
    
    return result

@app.post("/submit-feedback")
async def submit_feedback_endpoint(submission: FeedbackSubmission):
    """
    Stores submitted feedback in a CSV file.
    """
    if not submission.feedback_text.strip():
        raise HTTPException(status_code=400, detail="Feedback text cannot be empty.")
    
    # Check if file exists to determine if we need to write headers
    file_exists = os.path.isfile(FEEDBACK_CSV_PATH)
    
    try:
        with open(FEEDBACK_CSV_PATH, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            
            # Write header if file is new
            if not file_exists:
                writer.writerow([
                    'timestamp',
                    'feedback_text',
                    'observation',
                    'feeling',
                    'need',
                    'request',
                    'trust_score'
                ])
            
            # Write the feedback data
            writer.writerow([
                datetime.now().isoformat(),
                submission.feedback_text,
                submission.observation or '',
                submission.feeling or '',
                submission.need or '',
                submission.request or '',
                submission.trust_score or ''
            ])
        
        return {"status": "success", "message": "Feedback submitted successfully"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save feedback: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "ok", "system": "TP-RIS-Offline"}
