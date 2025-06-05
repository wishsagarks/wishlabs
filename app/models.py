# app/models.py
from pydantic import BaseModel
from typing import Optional, Dict, Any

class ScoreResponse(BaseModel):
    ats_score: Dict[str, Any]
    jd_score: Optional[Dict[str, Any]] = None
    ai_score: Any
    ai_feedback: str
    comparison: Dict[str, Any]
