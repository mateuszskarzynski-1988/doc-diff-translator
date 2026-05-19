# Document Diff Translator

A proof of concept tool for semantic diff analysis between document versions (PDF/DOCX).
Upload two versions of a document and receive a prose description of what changed — with a clear distinction between semantic and cosmetic changes.

## Stack
- **Frontend:** Lovable (React)
- **Orchestration:** n8n cloud
- **Parser:** Python FastAPI microservice (Railway)
- **LLM:** Claude API (Anthropic)

## Status
This is a live POC. If the demo is unresponsive, the backend may have been deactivated — see source code on GitHub