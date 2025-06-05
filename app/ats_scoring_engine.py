# app/ats_scoring_engine.py
import re

def extract_metadata(text):
    """
    Extract key fields from resume text for demo purposes.
    Expand this with robust NLP in production!
    """
    metadata = {}
    metadata["name"] = re.search(r"Name[:\-]?\s*(.*)", text, re.IGNORECASE)
    metadata["email"] = re.search(r"[\w\.-]+@[\w\.-]+", text)
    metadata["phone"] = re.search(r"\b\d{10,12}\b", text)
    # Demo section splits:
    metadata["sections"] = {
        "skills": "\n".join([l for l in text.splitlines() if "skill" in l.lower()]),
        "education": "\n".join([l for l in text.splitlines() if "educat" in l.lower()]),
        "experience": "\n".join([l for l in text.splitlines() if "experienc" in l.lower()]),
        "projects": "\n".join([l for l in text.splitlines() if "project" in l.lower()]),
        "summary": "\n".join([l for l in text.splitlines() if "summary" in l.lower()]),
    }
    metadata["section_texts"] = metadata["sections"]
    return metadata

def compute_ats_score(metadata, level, jd=None):
    """
    Score based on which sections/fields are present. 
    More sophisticated logic can be implemented.
    """
    details = {"sections": [], "section_texts": metadata.get("sections", {}), "warnings": [], "skills_bonus": 0}
    total = 0
    max_score = 100
    section_weights = {"name": 10, "email": 10, "phone": 5, "skills": 25, "education": 10, "experience": 20, "projects": 10, "summary": 10}

    for section, weight in section_weights.items():
        val = 0
        present = False
        if section == "name" and metadata.get("name"):
            val, present = weight, True
        elif section == "email" and metadata.get("email"):
            val, present = weight, True
        elif section == "phone" and metadata.get("phone"):
            val, present = weight, True
        elif section in metadata.get("sections", {}) and metadata["sections"][section].strip():
            val, present = weight, True
        details["sections"].append({
            "section": section,
            "score": val,
            "weight": weight,
            "present": present
        })
        total += val
    # Add bonus for 5+ skills
    skills_text = metadata.get("sections", {}).get("skills", "")
    if skills_text and len(skills_text.split(",")) >= 5:
        details["skills_bonus"] = 5
        total += 5
    details["warnings"] = [f"{k.capitalize()} missing!" for k, v in section_weights.items() if not any(s["section"] == k and s["present"] for s in details["sections"])]
    return {"score": min(total, max_score), "details": details}

def compute_basic_ats_score(resume_text):
    # Just a wrapper for extracting metadata
    return extract_metadata(resume_text)
