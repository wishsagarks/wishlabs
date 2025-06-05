# app/parsers.py

import io
import fitz  # PyMuPDF
import docx
import re
import spacy

# Load spaCy model at module import for speed
nlp = spacy.load("en_core_web_sm")

# Simple skill list (should use a richer taxonomy in prod)
COMMON_SKILLS = [
    "python", "java", "c++", "sql", "aws", "azure", "docker", "kubernetes",
    "javascript", "typescript", "node.js", "react", "django", "flask",
    "git", "linux", "html", "css", "nlp", "machine learning", "data analysis"
]


def format_gemini_feedback(feedback_text):
    """Convert markdown-like AI feedback to clean, pretty HTML for Streamlit."""
    # Replace double stars for bold (for section headers or strong phrases)
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', feedback_text)
    # Remove single star bullets, use Streamlit's default bullets or dash
    text = re.sub(r'^\s*[\*•]\s?', '• ', text, flags=re.MULTILINE)
    # Optionally, make headers larger
    text = re.sub(r'<b>(Strengths|Weaknesses and Improvement Suggestions|Specific Examples of Improvement):</b>',
                  r'<b><span style="font-size:1.1em">\1:</span></b>', text)
    # Remove stray backticks (if any)
    text = text.replace('`', '')
    return text

def extract_text_from_pdf(pdf_bytes):
    text = ""
    with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    return text

def extract_text_from_docx(docx_bytes):
    doc = docx.Document(io.BytesIO(docx_bytes))
    text = "\n".join([para.text for para in doc.paragraphs])
    return text

def extract_email(text):
    match = re.search(r"[\w\.-]+@[\w\.-]+", text)
    return match.group(0) if match else ""

def extract_phone(text):
    match = re.search(r"\+?\d[\d\- ]{8,}\d", text)
    return match.group(0) if match else ""

def extract_name(text):
    # Heuristic: name likely in first 5 lines and contains 2-3 words
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    for line in lines[:5]:
        if 1 < len(line.split()) < 5 and not re.search(r"\d", line):
            return line
    # fallback: first line
    return lines[0] if lines else ""

def extract_skills(text):
    tokens = set([token.text.lower() for token in nlp(text)])
    found = [skill for skill in COMMON_SKILLS if skill in tokens]
    # NLP noun chunk based skills
    for chunk in nlp(text).noun_chunks:
        if chunk.text.lower() not in found and chunk.text.lower() in COMMON_SKILLS:
            found.append(chunk.text.lower())
    return list(set(found))

def extract_experience_years(text):
    # Looks for patterns like "X years", "X+ years"
    exp_matches = re.findall(r"(\d{1,2})\s?\+?\s?years?", text, re.IGNORECASE)
    if exp_matches:
        return max([int(x) for x in exp_matches])
    return None

def extract_metadata(file_bytes, filename):
    # 1. Get text
    if filename.lower().endswith(".pdf"):
        text = extract_text_from_pdf(file_bytes)
    elif filename.lower().endswith(".docx"):
        text = extract_text_from_docx(file_bytes)
    else:
        raise ValueError("Unsupported file type.")

    # 2. Extract fields
    metadata = {
        "name": extract_name(text),
        "email": extract_email(text),
        "phone": extract_phone(text),
        "skills": extract_skills(text),
        "experience_years": extract_experience_years(text),
        "raw_text": text,
    }
    return metadata
