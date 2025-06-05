# app/rule_based_parser.py
import fitz  # PyMuPDF
import docx

def parse_resume(resume_bytes, filename):
    """
    Extracts plain text from a PDF or DOCX resume.
    Returns the text.
    """
    ext = filename.split('.')[-1].lower()
    if ext == "pdf":
        with fitz.open(stream=resume_bytes, filetype="pdf") as doc:
            text = "\n".join(page.get_text() for page in doc)
    elif ext == "docx":
        doc = docx.Document(resume_bytes)
        text = "\n".join(para.text for para in doc.paragraphs)
    else:
        raise ValueError("Unsupported file type")
    return text
