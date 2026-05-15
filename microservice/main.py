"""
Document parser microservice.
Single endpoint POST /parse — accepts a PDF or DOCX file, returns extracted text as JSON.
Deployed as a standalone service so any client (n8n, Lovable, scripts) can call it.
"""
import io
import os
from fastapi import FastAPI, UploadFile, File, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pdfplumber
import mammoth

app = FastAPI(title="Document Parser Service", version="0.1.0")

# CORS — allow calls from any origin during development.
# In production we'd restrict to known frontends (Lovable, n8n).
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)

# Simple bearer token auth — set PARSER_API_KEY env var when running
API_KEY = os.getenv("PARSER_API_KEY", "dev-key-change-me")


def extract_pdf(content: bytes) -> str:
    """Extract text from a PDF file, joining pages with double newlines."""
    text_parts = []
    with pdfplumber.open(io.BytesIO(content)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            text_parts.append(page_text)
    return "\n\n".join(text_parts)


def extract_docx(content: bytes) -> str:
    """Extract text from DOCX as markdown — preserves heading structure."""
    result = mammoth.convert_to_markdown(io.BytesIO(content))
    return result.value


@app.get("/health")
def health():
    """Basic health check, used by Railway to confirm the service is up."""
    return {"status": "ok"}


@app.post("/parse")
async def parse(
    file: UploadFile = File(...),
    authorization: str = Header(default=None),
):
    """Parse an uploaded PDF or DOCX file and return its text content."""
    # Auth check
    if authorization != f"Bearer {API_KEY}":
        raise HTTPException(status_code=401, detail="Unauthorized")

    content = await file.read()
    filename = (file.filename or "").lower()

    if filename.endswith(".pdf"):
        text = extract_pdf(content)
        doc_type = "pdf"
    elif filename.endswith(".docx"):
        text = extract_docx(content)
        doc_type = "docx"
    else:
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files are supported")

    return {
        "filename": file.filename,
        "type": doc_type,
        "text": text,
        "char_count": len(text),
    }