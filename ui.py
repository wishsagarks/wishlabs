import streamlit as st
from fpdf import FPDF
from fpdf.enums import XPos, YPos
import datetime
import os

from app.parsers import extract_metadata, COMMON_SKILLS , format_gemini_feedback
from app.scoring import traditional_ats_score, jd_based_score
from app.ai_scoring import ai_ats_score
from app.comparator import compare_scores

FONT_PATH = os.path.join("app", "fonts", "DejaVuSans.ttf")

SECTION_TIPS = {
    "name": "Your full name. Recruiters and ATSs use this to identify your application.",
    "email": "A professional email address. Recruiters will use this to contact you.",
    "phone": "Phone number for interview or offer calls.",
    "skills": "List of your technical and soft skills. These help both ATS and recruiters match you to jobs.",
    "education": "Your degrees, institutions, years attended, and relevant coursework.",
    "experience_years": "How many years of relevant work experience you have.",
    "projects": "Notable projects that showcase your skills and practical experience.",
    "summary": "A concise professional summary or objective that tells your story up front."
}

def clean_text(text):
    if not isinstance(text, str):
        return str(text)
    return ''.join(c for c in text if c.isprintable() or c in '\n\t')

class PDF(FPDF):
    def header(self):
        self.set_font("DejaVu", "B", 16)
        self.cell(
            0, 10, clean_text("ATS Resume Analysis Report"),
            align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT
        )
        self.ln(4)

def generate_pdf_report(resume_name, level, ats_score, jd_score, ai_score, sections, warnings, feedback):
    pdf = PDF()
    pdf.add_font("DejaVu", "", FONT_PATH)
    pdf.add_font("DejaVu", "B", FONT_PATH)
    pdf.add_page()
    pdf.set_font("DejaVu", "", 12)
    pdf.cell(0, 10, clean_text(f"Date: {datetime.date.today().isoformat()}"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.cell(0, 10, clean_text(f"Resume: {resume_name}"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.cell(0, 10, clean_text(f"Level: {level.capitalize()}"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(6)
    pdf.set_font("DejaVu", "B", 14)
    pdf.cell(0, 10, clean_text("Scores"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("DejaVu", "", 12)
    pdf.cell(0, 10, clean_text(f"ATS Score: {ats_score}/100"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.cell(0, 10, clean_text(f"JD Match Score: {jd_score if jd_score is not None else '—'}/100"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.cell(0, 10, clean_text(f"Gemini AI Score: {ai_score}/100"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(6)
    pdf.set_font("DejaVu", "B", 14)
    pdf.cell(0, 10, clean_text("Section Breakdown"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("DejaVu", "", 12)
    for s in sections:
        label = s['section'].replace("_", " ").capitalize()
        pdf.cell(0, 10, clean_text(f"{label} (Importance: {s['weight']}%): {'✔️' if s['present'] else '✗'}"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(4)
    if warnings:
        pdf.set_text_color(255, 0, 0)
        for warning in warnings:
            pdf.multi_cell(0, 10, clean_text(f"⚠️ {warning}"))
        pdf.set_text_color(0, 0, 0)
    pdf.ln(6)
    pdf.set_font("DejaVu", "B", 14)
    pdf.cell(0, 10, clean_text("Gemini AI Feedback"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("DejaVu", "", 11)
    pdf.multi_cell(0, 8, clean_text(feedback))
    pdf.ln(2)
    return bytes(pdf.output(name=None))

st.set_page_config(
    page_title="AI-Powered ATS Resume Checker",
    layout="centered"
)

st.title("📄 ATS Resume Checker & AI Feedback")
st.caption("Upload your resume and get actionable ATS, JD, and Gemini-powered insights!")

with st.form("upload_form", clear_on_submit=False):
    resume_file = st.file_uploader("Upload your resume (.pdf or .docx)", type=["pdf", "docx"])
    level = st.selectbox("Select Resume Level", ["entry", "mid", "senior"], index=0)
    jd = st.text_area("Paste Job Description (optional)", height=150)
    submit_btn = st.form_submit_button("Analyze Resume")

if submit_btn:
    if not resume_file:
        st.warning("Please upload a resume!")
        st.stop()

    with st.spinner("Analyzing your resume, please wait..."):
        # 1. Parse resume for metadata
        metadata = extract_metadata(resume_file.getvalue(), resume_file.name)
        if not metadata or not isinstance(metadata, dict):
            st.error("Failed to extract information from resume. Please check your file.")
            st.stop()
        ats_result = traditional_ats_score(metadata, level)


        # 2. Rule-based ATS score
        ats_result = traditional_ats_score(metadata, level)
        ats_score = ats_result["score"]
        ats_details = ats_result["details"]

        # 3. JD-based scoring (optional, if JD provided)
        jd_score_result = jd_based_score(metadata, jd, level) if jd else None
        jd_score = jd_score_result["score"] if jd_score_result else None

        # 4. Gemini AI scoring (text + JD)
        ai_score, ai_feedback = ai_ats_score(resume_file.getvalue(), resume_file.name, jd, level)

        sections = ats_details.get("sections", [])
        warnings = ats_details.get("warnings", [])
        skills_bonus = ats_details.get("skills_bonus", 0)

        # 5. Real-time comparison
        comp = compare_scores(ats_result, ai_score, jd_score_result)

    st.subheader("Results Overview")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("ATS Score", f"{ats_score}/100")
    with c2:
        st.metric("JD Match Score", f"{jd_score}/100" if jd_score is not None else "—")
    with c3:
        st.metric("Gemini AI Score", f"{ai_score}/100")

    pdf_bytes = generate_pdf_report(
        resume_name=resume_file.name,
        level=level,
        ats_score=ats_score,
        jd_score=jd_score,
        ai_score=ai_score,
        sections=sections,
        warnings=warnings,
        feedback=ai_feedback,
    )
    st.download_button(
        label="⬇️ Download Full ATS Report (PDF)",
        data=pdf_bytes,
        file_name=f"ATS_Report_{resume_file.name.split('.')[0]}_{level}_{datetime.date.today().isoformat()}.pdf",
        mime="application/pdf"
    )

    st.markdown("---")
    st.subheader(f"Section Breakdown ({level.capitalize()} Level)")

    for s in sections:
        key = s["section"]
        label = key.replace("_", " ").capitalize()
        val = s["score"]
        weight = s["weight"]
        present = s["present"]
        bar_pct = int((val / weight) * 100) if weight > 0 else 0
        tooltip = SECTION_TIPS.get(key, "")

        if present:
            color = "#2A9D8F"
            icon = "✔️"
            status = f"{label}: Good"
        else:
            color = "#e63946"
            icon = "✗"
            status = f"{label}: Missing"

        col1, col2 = st.columns([8, 1])
        with col1:
            st.markdown(
                f"<span style='font-size:1.1em;color:{color};font-weight:700'>{icon} {label}</span> "
                f"<span style='font-size:0.95em;color:#888;'>(Weight: {weight}%)</span>",
                unsafe_allow_html=True,
            )
        with col2:
            if tooltip:
                st.markdown(
                    f"<span title='{tooltip}' style='cursor: help; font-size:1.2em'>ℹ️</span>",
                    unsafe_allow_html=True,
                )

        st.progress(bar_pct, text=status)
        if s.get("matched_skills"):
            st.caption(f"Matched Skills: {', '.join(s['matched_skills'])}")
        if s.get("warnings"):
            for warn in s["warnings"]:
                st.error(f"⚠️ {warn}")

    if skills_bonus:
        st.success(f"Skills Bonus: +{skills_bonus} points for listing many relevant skills!")

    if warnings:
        for warning in warnings:
            st.error(f"⚠️ {warning}")

    st.markdown("<br>", unsafe_allow_html=True)

    st.subheader("Gemini AI Feedback & Suggestions")
    st.markdown(format_gemini_feedback(ai_feedback), unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("Traditional vs AI Comparison")
    st.write(comp.get("traditional_vs_ai", ""))
    st.info(f"Recommendation: {comp.get('recommendation', '')}")

    st.success("Done! Try uploading another resume or tweaking your JD for more insights.")

else:
    st.info("Upload your resume and get a real ATS score + Gemini-powered feedback instantly. Paste a JD for job-targeted analysis.")
