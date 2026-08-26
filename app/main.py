from fastapi import FastAPI
from app.schemas.document import DocumentRequest, DocumentResponse
from app.services.document_service import DocumentService

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/documents", response_model=DocumentResponse)
def create_document(document: DocumentRequest) -> DocumentResponse:
    service = DocumentService()
    result = service.create(document)
    return result
