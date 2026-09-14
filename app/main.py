from fastapi import FastAPI
from app.schemas.document import DocumentRequest, DocumentResponse
from app.services.document_service import DocumentService
from app.api.routes.document import router as document_router

app = FastAPI()


@app.get("/health")
def health():
    return {"status": "ok"}


app.include_router(document_router)
