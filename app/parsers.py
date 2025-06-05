# app/parsers.py

import io
import fitz  # PyMuPDF
import docx
import re
import spacy
from datetime import datetime
from dateutil import parser as dateparser
    
# Load spaCy model at module import for speed
nlp = spacy.load("en_core_web_sm")

COMMON_SKILLS = [
    "python", "java", "c++", "sql", "aws", "azure", "docker", "kubernetes",
    "javascript", "typescript", "node.js", "react", "django", "flask",
    "git", "linux", "html", "css", "nlp", "machine learning", "data analysis"
]

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
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    for line in lines[:5]:
        if 1 < len(line.split()) < 5 and not re.search(r"\d", line):
            return line
    return lines[0] if lines else ""

def extract_skills(text):
    tokens = set([token.text.lower() for token in nlp(text)])
    found = [skill for skill in COMMON_SKILLS if skill in tokens]
    for chunk in nlp(text).noun_chunks:
        c = chunk.text.lower()
        if c not in found and c in COMMON_SKILLS:
            found.append(c)
    return list(set(found))

# --- Improved robust experience year extraction ---
def parse_date_safe(date_str):
    try:
        return dateparser.parse(date_str, default=datetime(1900, 1, 1), fuzzy=True)
    except Exception:
        return None

def extract_experience_years(text):
    """
    Finds all date ranges in the text, sums up non-overlapping durations (in years).
    Supports 'YYYY–YYYY', 'MMM YYYY–MMM YYYY', 'Month YYYY–Present', etc.
    """
    text = text.replace('–', '-').replace('—', '-').replace('to', '-').lower()
    date_range_pattern = re.compile(
        r'([a-z]{3,9}[\s/.,-]*)?(\d{4})\s*[-–—to]{1,3}\s*([a-z]{3,9}[\s/.,-]*)?(\d{4}|present)',
        re.IGNORECASE
    )
    intervals = []
    for match in date_range_pattern.finditer(text):
        start_month = match.group(1) or ""
        start_year = match.group(2)
        end_month = match.group(3) or ""
        end_year = match.group(4)
        start_text = f"{start_month} {start_year}".strip()
        end_text = f"{end_month} {end_year}".strip()
        start_dt = parse_date_safe(start_text)
        end_dt = parse_date_safe(end_text) if 'present' not in end_year.lower() else datetime.now()
        if start_dt and end_dt and end_dt > start_dt:
            intervals.append((start_dt, end_dt))
    intervals.sort()
    merged = []
    for start, end in intervals:
        if not merged or start > merged[-1][1]:
            merged.append([start, end])
        else:
            merged[-1][1] = max(merged[-1][1], end)
    total_months = 0
    for start, end in merged:
        months = (end.year - start.year) * 12 + (end.month - start.month)
        total_months += months
    years = round(total_months / 12.0, 1)
    return int(round(years)) if years > 0 else None

# ----------- Enhanced Section Extraction -------------

def extract_section(text, section_names, next_section_names):
    lines = text.splitlines()
    section_start, section_end = -1, -1
    for idx, line in enumerate(lines):
        for sec in section_names:
            if sec in line.strip().lower():
                section_start = idx
                break
        if section_start != -1:
            break
    if section_start == -1:
        return ""
    for idx in range(section_start + 1, len(lines)):
        for nsec in next_section_names:
            if nsec in lines[idx].strip().lower():
                section_end = idx
                break
        if section_end != -1:
            break
    content = lines[section_start+1:section_end] if section_end != -1 else lines[section_start+1:]
    return "\n".join(content).strip()

def extract_education(text):
    headers = ["education", "educational background", "academic background", "academic qualification"]
    next_headers = ["experience", "work experience", "projects", "skills", "summary", "certifications"]
    section = extract_section(text, headers, next_headers)
    degree_lines = []
    for line in section.splitlines():
        if any(deg in line.lower() for deg in [
            "bachelor", "master", "phd", "b.tech", "m.tech", "b.sc", "m.sc", "b.e", "m.e",
            "ba", "ma", "bs", "ms", "high school"]):
            degree_lines.append(line.strip())
        elif re.search(r"\d{4}", line):
            degree_lines.append(line.strip())
    return degree_lines if degree_lines else section

def extract_experience(text):
    headers = ["experience", "work experience", "professional experience", "employment history"]
    next_headers = ["projects", "skills", "education", "academic", "summary", "certifications"]
    section = extract_section(text, headers, next_headers)
    exp_chunks = []
    for line in section.splitlines():
        match = re.search(r"([\w\s&\.,\-\/]+),\s*([\w\s&\.,\-\/]+),?\s*(\d{4}.+)?", line)
        if match:
            exp_chunks.append(line.strip())
        elif re.search(r"\d{4}", line):
            exp_chunks.append(line.strip())
    return exp_chunks if exp_chunks else section

def extract_projects(text):
    headers = ["project", "projects", "academic projects", "notable projects", "key projects"]
    next_headers = ["experience", "work experience", "skills", "education", "summary", "certifications"]
    section = extract_section(text, headers, next_headers)
    project_lines = []
    for line in section.splitlines():
        if ":" in line or (len(line.split()) < 10 and line.istitle()):
            project_lines.append(line.strip())
        elif line.strip():
            project_lines.append(line.strip())
    return project_lines if project_lines else section

def extract_metadata(file_bytes, filename):
    try:
        if filename.lower().endswith(".pdf"):
            text = extract_text_from_pdf(file_bytes)
        elif filename.lower().endswith(".docx"):
            text = extract_text_from_docx(file_bytes)
        else:
            raise ValueError("Unsupported file type.")

        metadata = {
            "name": extract_name(text),
            "email": extract_email(text),
            "phone": extract_phone(text),
            "skills": extract_skills(text),
            "experience_years": extract_experience_years(text),
            "education": extract_education(text),
            "experience": extract_experience(text),
            "projects": extract_projects(text),
            "raw_text": text,
        }
        return metadata
    except Exception as e:
        print(f"Error extracting metadata: {e}")
        return None



def format_gemini_feedback(feedback_text):
    """Convert markdown-like AI feedback to clean, pretty HTML for Streamlit."""
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', feedback_text)
    text = re.sub(r'^\s*[\*•]\s?', '• ', text, flags=re.MULTILINE)
    text = re.sub(r'<b>(Strengths|Weaknesses and Improvement Suggestions|Specific Examples of Improvement):</b>',
                  r'<b><span style="font-size:1.1em">\1:</span></b>', text)
    text = text.replace('`', '')
    return text
