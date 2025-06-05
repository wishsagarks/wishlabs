# ATS Resume Checker

This project is a minimal resume analysis tool that combines rule‑based section scoring with optional Gemini AI feedback. It exposes a FastAPI backend and a Streamlit web UI for uploading resumes and receiving ATS (Applicant Tracking System) style feedback.

## Features

- **Traditional scoring** – checks for key resume sections using dynamic weights for entry, mid and senior levels.
- **Job description matching** – evaluates how well your resume keywords align with a provided JD.
- **Gemini AI scoring** – calls Google Gemini to rate the resume and provide improvement suggestions.
- **PDF reports** – generate a detailed PDF with scores and section breakdown.

## Installation

1. Clone the repository and create a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Download the spaCy model:

```bash
python -m spacy download en_core_web_sm
```

4. Create a `.env` file and set your Google Gemini API key:

```bash
GOOGLE_GEMINI_API_KEY=your-key-here
```

## Running the App

Start the FastAPI backend:

```bash
uvicorn app.main:app --reload
```

In a separate terminal, launch the Streamlit UI:

```bash
streamlit run app/ui.py
```

Visit the printed localhost URL and upload a resume (`.pdf` or `.docx`). Optionally paste a job description to see JD matching and AI feedback.

## API Endpoint

The backend exposes a single POST endpoint:

```
POST /upload_resume/
```

Body parameters:

- `resume` – uploaded file
- `level` – `entry`, `mid` or `senior`
- `jd` – optional job description

It returns a JSON `ScoreResponse` containing traditional score details, JD match data, AI score, and a comparison summary.

## License


