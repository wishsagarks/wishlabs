import pytest
from app.scoring import traditional_ats_score


def test_traditional_ats_score_basic():
    metadata = {
        "name": "John Doe",
        "email": "john@example.com",
        "phone": "1234567890",
        "skills": ["python", "aws", "docker"],
        "education": "BS CS",
        "experience_years": 2,
        "projects": ["proj"],
        "summary": "good"
    }
    result = traditional_ats_score(metadata, "entry")
    assert isinstance(result["score"], int)
    assert 0 <= result["score"] <= 100
    assert "details" in result
