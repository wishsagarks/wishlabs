import io
from fastapi.testclient import TestClient
from app.main import app
from fpdf import FPDF

client = TestClient(app)

def create_pdf_bytes():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, "John Doe")
    out = io.BytesIO()
    pdf.output(out)
    return out.getvalue()


def test_health_endpoint():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_upload_resume_endpoint():
    pdf_bytes = create_pdf_bytes()
    files = {"resume": ("resume.pdf", pdf_bytes, "application/pdf")}
    data = {"level": "entry"}
    resp = client.post("/upload_resume/", files=files, data=data)
    assert resp.status_code == 200
    body = resp.json()
    assert "ats_score" in body
    assert "ai_score" in body
