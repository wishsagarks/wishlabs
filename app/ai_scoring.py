# app/ai_scoring.py

import os
import google.generativeai as genai
# from dotenv import load_dotenv

# load_dotenv()
GEMINI_API_KEY = os.getenv("GOOGLE_GEMINI_API_KEY")

if GEMINI_API_KEY is None:
    raise ValueError("GOOGLE_GEMINI_API_KEY is not set in the .env file!")

# Configure Gemini once per process
genai.configure(api_key=GEMINI_API_KEY)

# Prompt template for ATS scoring with/without JD
BASIC_PROMPT = """
You are an advanced ATS resume analyzer.
Given the following resume text{jd_part}, analyze the quality, completeness, formatting, relevant skills, and match to the role. 
Score the resume on a scale of 0-100, and provide actionable improvement suggestions.
Respond in strict JSON with keys: score (int), feedback (str).
Resume text:
===
{resume_text}
===
{jd_block}
"""

def ai_ats_score(file_bytes, filename, jd, level):
    # Extract text from resume using same parsers as before
    from app.parsers import extract_text_from_pdf, extract_text_from_docx

    if filename.lower().endswith(".pdf"):
        resume_text = extract_text_from_pdf(file_bytes)
    elif filename.lower().endswith(".docx"):
        resume_text = extract_text_from_docx(file_bytes)
    else:
        return 0, "Unsupported file type for AI scoring."

    jd_part = ""
    jd_block = ""
    if jd:
        jd_part = " (for the job description provided below)"
        jd_block = f"Job Description:\n{jd}\n==="

    prompt = BASIC_PROMPT.format(
        resume_text=resume_text[:15000],  # Keep within Gemini input limits
        jd_part=jd_part,
        jd_block=jd_block
    )

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")  # Use flash or pro model as needed
        response = model.generate_content(prompt)
        # Parse JSON from Gemini response
        import json
        data = {}
        # The LLM might return extra text; look for JSON
        try:
            start = response.text.index('{')
            end = response.text.rindex('}') + 1
            data = json.loads(response.text[start:end])
        except Exception:
            # Fallback: treat all as feedback
            data = {"score": 0, "feedback": response.text.strip()}
        return data.get("score", 0), data.get("feedback", "")
    except Exception as e:
        return 0, f"AI scoring error: {str(e)}"
