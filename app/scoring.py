# app/scoring.py

import re
from collections import Counter
from app.parsers import COMMON_SKILLS
# app/scoring.py

from collections import defaultdict

# Dynamic section weights for each resume level
SECTION_WEIGHTS_BY_LEVEL = {
    "entry": {
        "name": 8, "email": 8, "phone": 6,
        "skills": 25, "education": 25,
        "experience_years": 10, "projects": 10, "summary": 8
    },
    "mid": {
        "name": 6, "email": 6, "phone": 6,
        "skills": 20, "education": 12,
        "experience_years": 25, "projects": 12, "summary": 5
    },
    "senior": {
        "name": 5, "email": 5, "phone": 5,
        "skills": 15, "education": 5,
        "experience_years": 35, "projects": 15, "summary": 5
    }
}

def traditional_ats_score(metadata, level):
    weights = SECTION_WEIGHTS_BY_LEVEL.get(level, SECTION_WEIGHTS_BY_LEVEL["entry"])
    score = 0
    section_breakdown = []
    warnings = []

    # Section-wise scoring, with dynamic weights
    for field, weight in weights.items():
        present = bool(metadata.get(field)) and metadata.get(field) not in ["", [], None]
        field_score = weight if present else 0
        score += field_score
        section_breakdown.append({
            "section": field,
            "present": present,
            "weight": weight,
            "score": field_score
        })
        # Warn if missing a high-weight section (>15%)
        if not present and weight >= 15:
            warnings.append(f"Your '{field.capitalize()}' section is critical for this level. Please add or improve it.")

    # Skills bonus (optional, based on detected skills)
    num_skills = len(metadata.get("skills", []))
    skills_bonus = 0
    if num_skills >= 10:
        skills_bonus = 10
        score += 10
    elif num_skills >= 5:
        skills_bonus = 5
        score += 5

    # Experience check for minimum thresholds (optional)
    exp = metadata.get("experience_years")
    if exp is None:
        exp = 0  # Safest default for ATS

    exp_match = False  # <-- Always initialize!

    if level == "entry" and exp >= 0:
        exp_match = True
    elif level == "mid" and exp >= 3:
        exp_match = True
    elif level == "senior" and exp >= 7:
        exp_match = True
    # (Can add bonus points here if wanted)

    # Final normalize and cap at 100
    final_score = min(int(score), 100)

    # Return all breakdown for UI/analysis
    return {
        "score": final_score,
        "details": {
            "sections": section_breakdown,
            "skills_bonus": skills_bonus,
            "exp_match": exp_match,
            "level": level,
            "warnings": warnings
        }
    }

def clean_and_tokenize(text):
    return set(re.sub(r"[^A-Za-z0-9]", " ", text).lower().split())

def jd_based_score(metadata, jd, level):
    if not jd:
        return None

    # Extract JD keywords
    jd_tokens = clean_and_tokenize(jd)
    jd_skills = [skill for skill in COMMON_SKILLS if skill in jd.lower()]

    # Resume skills
    resume_skills = set(metadata.get("skills", []))
    resume_tokens = clean_and_tokenize(metadata.get("raw_text", ""))

    # Skill overlap
    skills_matched = resume_skills & set(jd_skills)
    skill_match_pct = round((len(skills_matched) / max(len(jd_skills), 1)) * 100, 1)

    # JD keyword overlap (not just skills)
    word_overlap = jd_tokens & resume_tokens
    word_match_pct = round((len(word_overlap) / max(len(jd_tokens), 1)) * 100, 1)

    # Experience
    required_exp = None
    exp_match = False
    for s in jd_tokens:
        if s.isdigit():
            required_exp = int(s)
            break
    candidate_exp = metadata.get("experience_years", 0)
    if required_exp is not None:
        exp_match = candidate_exp >= required_exp

    score = int(skill_match_pct * 0.5 + word_match_pct * 0.3 + (20 if exp_match else 0))
    score = min(score, 100)

    return {
        "score": score,
        "details": {
            "skills_matched": list(skills_matched),
            "skill_match_pct": skill_match_pct,
            "word_match_pct": word_match_pct,
            "exp_match": exp_match,
            "required_exp": required_exp,
            "candidate_exp": candidate_exp
        }
    }
