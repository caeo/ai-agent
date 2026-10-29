import uuid

from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse

from sqlalchemy.orm import Session

from app.db.session import get_db

from app.repositories.document_repository import DocumentRepository
from app.repositories.chunk_repository import ChunkRepository

from app.schemas.document import DocumentRequest, DocumentResponse

from app.services.document_service import DocumentService
from app.services.embedding_service import EmbeddingService
from app.services.retrieval_service import RetrievalService
from app.services.ai_service import AIService

from app.renderers.docx_renderer import DocxRenderer
from app.renderers.template_docx_renderer import TemplateDocxRenderer

router = APIRouter()


# Centraliza a definição das instâncias
def get_document_service(db: Session = Depends(get_db)) -> DocumentService:
    document_repository = DocumentRepository(db)
    chunk_repository = ChunkRepository(db)

    embedding_service = EmbeddingService()
    retrieval_service = RetrievalService(chunk_repository, embedding_service)
    ai_service = AIService()

    docx_renderer = DocxRenderer()
    template_docx_renderer = TemplateDocxRenderer()

    document_service = DocumentService(
        document_repository,
        ai_service,
        docx_renderer,
        retrieval_service,
        template_docx_renderer,
        active_template_path=Path(
            r"C:\Users\silva.csc\Desktop\ai-agent\uploads\d933350f-dca6-4d8e-b635-1c32929dc463.docx"
        ),
        # active_template_path=None,
    )

    return document_service


@router.post("/documents", response_model=DocumentResponse)
def create_document(
    request: DocumentRequest, service: DocumentService = Depends(get_document_service)
) -> DocumentResponse:

    document = service.create(request)

    return document


@router.get("/documents/{document_id}", response_model=DocumentResponse)
def get_by_id(
    document_id: uuid.UUID,
    service: DocumentService = Depends(get_document_service),
) -> DocumentResponse:

    document = service.get_by_id(document_id)

    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")

    return document


@router.get("/documents/{document_id}/download")
def download_document(
    document_id: uuid.UUID, service: DocumentService = Depends(get_document_service)
) -> FileResponse:

    document = service.get_document_by_id(document_id)

    # Caso em que o documento não existe
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")

    # O registro existe no banco, mas o arquivo não foi encontrado.
    if not Path(document.file_path).exists():
        raise HTTPException(status_code=404, detail="Document file not found")

    return FileResponse(
        path=document.file_path,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=f"{document.title}.docx",
    )
