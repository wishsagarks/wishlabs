from fastapi import FastAPI, File, UploadFile, Form # type: ignore
from fastapi.middleware.cors import CORSMiddleware # type: ignore
from typing import Optional
#from app.ai_scoring import sectionwise_gemini_feedback
from app.models import ScoreResponse
from app.scoring import traditional_ats_score, jd_based_score
from app.ai_scoring import ai_ats_score
from app.comparator import compare_scores
from app.parsers import extract_metadata

app = FastAPI(
    title="ATS Resume Checker API",
    description="Backend API for resume scoring and comparison using rule-based and AI-based engines.",
    version="2.0.0",
)

# CORS settings (update allow_origins for production!)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload_resume/", response_model=ScoreResponse)
async def upload_resume(
    resume: UploadFile = File(...),
    level: str = Form(...),  # entry, mid, senior
    jd: Optional[str] = Form(None)
):
    """
    Upload a resume and receive ATS scores from rule-based, JD-based, and AI-based engines.
    """
    # 1. Read file
    content = await resume.read()
    filename = resume.filename

    # 2. Parse resume to structured metadata
    metadata = extract_metadata(content, filename)

    # 3. Score resume by traditional/dynamic section weights
    ats_score = traditional_ats_score(metadata, level)

    # 4. JD-based scoring if JD is provided
    jd_score = None
    if jd:
        jd_score = jd_based_score(metadata, jd, level)

    # 5. Gemini AI scoring & suggestions
    ai_score, ai_feedback = ai_ats_score(content, filename, jd, level)

    # 6. Comparison/consistency analysis
    score_comparison = compare_scores(ats_score, ai_score, jd_score)

    # 7. Structured, detailed response
    return ScoreResponse(
        ats_score=ats_score,
        jd_score=jd_score,
        ai_score=ai_score,
        ai_feedback=ai_feedback,
        comparison=score_comparison
    )

@app.get("/health")
def health():
    return {"status": "ok"}
