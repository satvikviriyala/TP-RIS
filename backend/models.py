from typing import List, Optional, Dict
from pydantic import BaseModel, Field

# --- Input Contract ---

class UnmetNeed(BaseModel):
    domain: str = "university"
    metadata: Dict[str, Optional[str]] = Field(default_factory=lambda: {"course_policy": None})

class FeedbackInput(BaseModel):
    review_text: str
    rating: Optional[int] = None
    context: UnmetNeed = Field(default_factory=UnmetNeed)
    previous_decision: Optional[str] = None

# --- Output Components ---

class ConfidenceScores(BaseModel):
    observation: float
    feeling: float
    need: float
    request: float

class OFNRDComponents(BaseModel):
    observation: Optional[str] = None
    feeling: Optional[str] = None
    need: Optional[str] = None
    request: Optional[str] = None
    confidence: ConfidenceScores

class TrustAssessment(BaseModel):
    trust_score: float
    flags: List[str]

class Decision(BaseModel):
    action: str  # NO_OP, SUGGEST_CLARIFICATION, PARTIAL_REWRITE, FULL_REWRITE, FLAG
    rationale: str

class Rewrite(BaseModel):
    text: Optional[str] = None
    explanation: Optional[str] = None

# --- Main Output Contract ---

class AnalysisResult(BaseModel):
    ofnr_d: OFNRDComponents
    trust_assessment: TrustAssessment
    decision: Decision
    rewrite: Rewrite
