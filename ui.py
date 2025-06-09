import streamlit as st
from fpdf import FPDF
import datetime
import os
import base64
import io
import matplotlib.pyplot as plt # type: ignore
from fpdf.enums import XPos, YPos

from app.parsers import extract_metadata, COMMON_SKILLS, format_gemini_feedback
from app.scoring import traditional_ats_score, jd_based_score
from app.ai_scoring import ai_ats_score
from app.comparator import compare_scores

FONT_PATH = os.path.join("app", "fonts", "DejaVuSans.ttf")

st.set_page_config(
    page_title="ATS Resume Checker & AI Feedback",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- Circular Score Chart ---
def circular_score(value, label, color="#1976d2"):
    fig, ax = plt.subplots(figsize=(2, 2), subplot_kw=dict(aspect="equal"))
    val = max(0, min(100, int(value)))
    wedges, _ = ax.pie(
        [val, 100-val],
        startangle=90,
        colors=[color, "#23272f"],
        wedgeprops=dict(width=0.22, edgecolor='white')
    )
    # Center text
    ax.text(0, 0.15, f"{val}", ha='center', va='center', fontsize=22, fontweight="bold", color=color)
    ax.text(0, -0.18, "/100", ha='center', va='center', fontsize=10, color="#fff")
    ax.text(0, 0.45, label, ha='center', va='center', fontsize=11, color="#eee")
    plt.axis("off")
    fig.patch.set_alpha(0.0)
    return fig

# --- PDF Generator for ATS summary ---


def strip_html(text):
    # Remove HTML tags for clean PDF output
    return re.sub('<[^<]+?>', '', text)
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
    max_width = 190  # Instead of 0, A4 minus margins

    pdf.cell(max_width, 10, clean_text(f"Date: {datetime.date.today().isoformat()}"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.cell(max_width, 10, clean_text(f"Resume: {resume_name}"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.cell(max_width, 10, clean_text(f"Level: {level.capitalize()}"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(6)
    pdf.set_font("DejaVu", "B", 14)
    pdf.cell(max_width, 10, clean_text("Scores"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("DejaVu", "", 12)
    pdf.cell(max_width, 10, clean_text(f"ATS Score: {ats_score}/100"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.cell(max_width, 10, clean_text(f"JD Match Score: {jd_score if jd_score is not None else '—'}/100"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.cell(max_width, 10, clean_text(f"Gemini AI Score: {ai_score}/100"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(6)
    pdf.set_font("DejaVu", "B", 14)
    pdf.cell(max_width, 10, clean_text("Section Breakdown"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("DejaVu", "", 12)
    for s in sections:
        label = s['section'].replace("_", " ").capitalize()
        txt = clean_text(f"{label} (Importance: {s['weight']}%): {'✔️' if s['present'] else '✗'}")
        pdf.multi_cell(max_width, 10, txt)
    pdf.ln(4)
    if warnings:
        pdf.set_text_color(255, 0, 0)
        for warning in warnings:
            # Split long warnings into chunks to avoid line-break error
            warning_chunks = [warning[i:i+80] for i in range(0, len(warning), 80)]
            for chunk in warning_chunks:
                pdf.multi_cell(max_width, 10, clean_text(f"⚠️ {chunk}"))
        pdf.set_text_color(0, 0, 0)
    pdf.ln(6)
    pdf.set_font("DejaVu", "B", 14)
    pdf.cell(max_width, 10, clean_text("Gemini AI Feedback"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("DejaVu", "", 11)
    # Feedback: split into lines, break long lines, avoid HTML/emoji-only lines
    feedback_lines = clean_text(feedback).split("\n")
    for line in feedback_lines:
        for chunk in [line[i:i+110] for i in range(0, len(line), 110)]:
            pdf.multi_cell(max_width, 8, chunk)
    pdf.ln(2)
    return bytes(pdf.output(name=None))

# --- PDF Preview (right side) ---
def show_resume_file(file_bytes, filename, metadata=None):
    if filename.lower().endswith(".pdf"):
        try:
            b64 = base64.b64encode(file_bytes).decode()
            st.markdown(
                f'<iframe src="data:application/pdf;base64,{b64}" width="100%" height="700px" '
                f'style="border-radius:14px; border:2px solid #eee;background:transparent"></iframe>',
                unsafe_allow_html=True,
            )
        except Exception as e:
            st.warning(f"PDF preview failed: {e}")
            st.download_button(
                "Download your uploaded file", file_bytes, filename=filename
            )
    elif filename.lower().endswith(".docx"):
        st.info("Preview for DOCX files is not supported. See the parsed text below:")
        if metadata and "raw_text" in metadata:
            st.text_area("Extracted Resume Text", metadata["raw_text"], height=400)
        st.download_button(
            "Download your uploaded file", file_bytes, filename=filename
        )
    else:
        st.error("Unsupported file type for preview.")
# --- Sidebar ---
with st.sidebar:
    st.markdown("### 🟩 WishLabs ATS Checker")
    st.markdown("---")
    st.markdown("#### 🏠 Home")
    st.markdown("#### 🔥 TOP FIXES")
    st.markdown("- Use of bullets <span style='color:#e74c3c'>4</span>", unsafe_allow_html=True)
    st.markdown("- Education")
    st.markdown("- Summary")
    st.markdown("- Leadership")
    st.markdown("- Repetition <span style='color:#e74c3c'>5</span>", unsafe_allow_html=True)
    st.markdown("##### <span style='color:#888'>14 MORE ISSUES</span>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("#### ✅ COMPLETED")
    st.markdown("- Buzzwords <span style='color:#43a047'>10</span>", unsafe_allow_html=True)
    st.markdown("- Unnecessary sections <span style='color:#43a047'>10</span>", unsafe_allow_html=True)
    st.markdown("- Contact details <span style='color:#43a047'>10</span>", unsafe_allow_html=True)
    st.markdown("##### <span style='color:#888'>1 MORE CHECK</span>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("#### 🛠 TOOLS")
    st.markdown("- Line Analysis")
    st.markdown("- ATS Keywords <span style='color:#f1c40f'>Pro</span>", unsafe_allow_html=True)
    st.markdown("- Magic Write <span style='color:#f1c40f'>Pro</span>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("##### Resources: [Sample Bullets](#) | [Templates](#)")
    st.markdown("<br>", unsafe_allow_html=True)

# --- Main UI Logic ---
if "results" not in st.session_state:
    st.markdown("<h2>📄 ATS Resume Checker & AI Feedback</h2>", unsafe_allow_html=True)
    st.caption("Upload your resume and get actionable ATS, JD, and Gemini-powered insights! All analysis is instant & private.")

    with st.form("upload_form", clear_on_submit=False):
        resume_file = st.file_uploader("Upload your resume (.pdf or .docx)", type=["pdf", "docx"])
        level = st.selectbox("Select Resume Level", ["entry", "mid", "senior"], index=0)
        jd = st.text_area("Paste Job Description (optional)", height=150)
        submit_btn = st.form_submit_button("Analyze Resume")

    if submit_btn and resume_file:
        metadata = extract_metadata(resume_file.getvalue(), resume_file.name)
        ats_result = traditional_ats_score(metadata, level)
        jd_result = jd_based_score(metadata, jd, level) if jd else None
        ai_score, ai_feedback = ai_ats_score(resume_file.getvalue(), resume_file.name, jd, level)
        comp = compare_scores(ats_result, ai_score, jd_result)
        st.session_state["results"] = {
            "ats": ats_result,
            "jd": jd_result,
            "ai": {"score": ai_score, "feedback": ai_feedback},
            "comp": comp,
            "name": metadata.get("name", "User"),
            "filename": resume_file.name,
            "file_bytes": resume_file.getvalue(),
            "level": level,
            "metadata": metadata
        }
        st.rerun()
    elif submit_btn and not resume_file:
        st.error("Please upload a resume file to proceed.")

else:
    results = st.session_state["results"]
    ats_score = results["ats"]["score"]
    jd_score = results["jd"]["score"] if results["jd"] else 0
    ai_score = results["ai"]["score"]
    name = results["name"].split()[0].capitalize() if results["name"] else "User"
    comp = results["comp"]
    feedback_html = format_gemini_feedback(results["ai"]["feedback"])
    file_bytes = results["file_bytes"]
    filename = results["filename"]
    level = results["level"]

    # --- Parse fixes and strengths (use your own logic if better!) ---
    fix_lines, strength_lines = [], []
    in_strength_block = False
    for line in feedback_html.splitlines():
        if "Strengths" in line:
            in_strength_block = True
            continue
        if any(kw in line.lower() for kw in ["weakness", "improvement", "fix:", "consider", "suggest", "add", "improve", "should"]):
            in_strength_block = False
            if line.strip().startswith("•") or "<b>" in line or ":" in line:
                fix_lines.append(line)
        elif in_strength_block and (line.strip().startswith("•") or "<b>" in line):
            strength_lines.append(line)
        elif in_strength_block and line.strip():
            strength_lines.append(line)
    # Add ATS missing as fixes
    for section in results["ats"]["details"]["sections"]:
        if not section["present"] and section["weight"] >= 10:
            label = section["section"].replace("_", " ").capitalize()
            fix_lines.append(f"Add or improve your <b>{label}</b> section.")

    if not fix_lines:
        fix_lines.append("No critical weaknesses detected.")

    if not strength_lines:
        for line in feedback_html.splitlines():
            if any(kw in line.lower() for kw in ["good", "well", "strength", "effective"]):
                strength_lines.append(line)
    if not strength_lines:
        strength_lines.append("AI did not highlight any major strengths.")

    # --- UI Layout: Main & PDF Preview (right) ---
    left_col, right_col = st.columns([3, 2], gap="large")
    with left_col:
        st.markdown(f"<h2 style='margin-bottom:0.2em'>Hello, {name}!</h2>", unsafe_allow_html=True)
        st.markdown("<small>Welcome to your resume review.</small>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        score_cols = st.columns([1, 1, 1], gap="small")
        with score_cols[0]:
            st.pyplot(circular_score(ats_score, "ATS", "#1976d2"), transparent=True)
        with score_cols[1]:
            st.pyplot(circular_score(jd_score, "JD", "#ff9900"), transparent=True)
        with score_cols[2]:
            st.pyplot(circular_score(ai_score, "Gemini", "#43a047"), transparent=True)
        st.markdown("---")
        # Fixes
        st.markdown("<h4>🚨 Top Fixes</h4>", unsafe_allow_html=True)
        for i, fix in enumerate(fix_lines[:3]):
            st.markdown(
                f"""<div style="background:linear-gradient(90deg,#f44336,#ffb3b3);margin-bottom:12px;padding:13px 15px 11px 14px;border-radius:12px;box-shadow:0 2px 8px #0002;">
                    <span style='font-size:1.18em;font-weight:600;'>❗ FIX #{i+1}:</span> 
                    <span style="font-size:1.05em;">{fix}</span>
                </div>""", unsafe_allow_html=True
            )
        if len(fix_lines) > 3:
            if st.button("Show More Fixes"):
                for fix in fix_lines[3:]:
                    st.markdown(
                        f"""<div style="background:linear-gradient(90deg,#f44336,#ffb3b3);margin-bottom:10px;padding:11px 14px;border-radius:12px;box-shadow:0 2px 8px #0002;">
                            <span style='font-size:1.12em;font-weight:600;'>❗ FIX:</span> 
                            <span style="font-size:1em;">{fix}</span>
                        </div>""", unsafe_allow_html=True
                    )
        # Strengths
        st.markdown("<h4>✅ What You Did Well</h4>", unsafe_allow_html=True)
        for i, pos in enumerate(strength_lines[:3]):
            st.markdown(
                f"""<div style="background:linear-gradient(90deg,#34eb77,#c8fce7);margin-bottom:12px;padding:13px 15px 11px 14px;border-radius:12px;box-shadow:0 2px 8px #0002;">
                    <span style='font-size:1.18em;font-weight:600;'>🌟 STRENGTH #{i+1}:</span>
                    <span style="font-size:1.05em;">{pos}</span>
                </div>""", unsafe_allow_html=True
            )
        if len(strength_lines) > 3:
            if st.button("Show More Strengths"):
                for pos in strength_lines[3:]:
                    st.markdown(
                        f"""<div style="background:linear-gradient(90deg,#34eb77,#c8fce7);margin-bottom:10px;padding:11px 14px;border-radius:12px;box-shadow:0 2px 8px #0002;">
                            <span style='font-size:1.12em;font-weight:600;'>🌟 STRENGTH:</span>
                            <span style="font-size:1em;">{pos}</span>
                        </div>""", unsafe_allow_html=True
                    )
        st.markdown("---")
        # Traditional vs AI Score
        st.markdown("### 🤝 Traditional vs. Gemini AI Score")
        st.markdown(
            f'''<div style="margin-bottom:15px;padding:17px 18px;border-radius:16px;background:linear-gradient(90deg,#1976d2,#43a047,#ffd600);color:#fff;box-shadow:0 2px 9px #0003;">
                <span style="font-size:1.16em;font-weight:700;">Insight:</span> {comp["traditional_vs_ai"]}<br>
                <span style="font-size:1.08em;">Recommendation: <span style="color:#ff0">{comp["recommendation"]}</span></span>
            </div>''', unsafe_allow_html=True
        )
        pdf_bytes = generate_pdf_report(
            resume_name=filename,   # from session_state
            level=level,
            ats_score=ats_score,
            jd_score=jd_score,
            ai_score=ai_score,
            sections=results["ats"]["details"].get("sections", []),
            warnings=results["ats"]["details"].get("warnings", []),
            feedback=results["ai"]["feedback"],
        )
        st.download_button(
            label="⬇️ Download ATS Summary PDF",
            data=pdf_bytes,
            file_name=f"ATS_Summary_{filename.split('.')[0]}_{level}_{datetime.date.today().isoformat()}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔄 Analyze Another Resume"):
            st.session_state.clear()
            st.rerun()
    with right_col:
        st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)
        st.markdown("### Resume Preview")
        show_resume_file(file_bytes, filename, metadata=metadata)

# Custom CSS
st.markdown("""
    <style>
        .stApp { background-color: #17191d; }
        .stButton > button { border-radius: 10px; border: none; font-size: 1.13em; background:#1976d2;color:white }
        .stDownloadButton button { border-radius: 10px; font-size:1.11em;background:#222245;color:white;}
        .stFileUploader { border-radius: 9px; }
        .stTextArea textarea { border-radius: 9px; }
        .stSelectbox select { border-radius: 9px; }
        .sidebar .sidebar-content { background: #23272f !important; }
        .element-container { margin-bottom: 0.7rem !important; }
    </style>
""", unsafe_allow_html=True)
