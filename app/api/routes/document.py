import uuid

from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse

from sqlalchemy.orm import Session

from app.db.session import get_db

from app.repositories.document_repository import DocumentRepository

from app.schemas.document import DocumentRequest, DocumentResponse

from app.services.document_service import DocumentService

router = APIRouter()


@router.post("/documents", response_model=DocumentResponse)
def create_document(
    request: DocumentRequest, db: Session = Depends(get_db)
) -> DocumentResponse:
    repository = DocumentRepository(db)
    service = DocumentService(repository)

    return service.create(request)


@router.get("/documents/{document_id}", response_model=DocumentResponse)
def get_by_id(
    document_id: uuid.UUID, db: Session = Depends(get_db)
) -> DocumentResponse:
    repository = DocumentRepository(db)
    service = DocumentService(repository)

    document = service.get_by_id(document_id)

    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")

    return document


@router.get("/documents/{document_id}/download")
def download_document(
    document_id: uuid.UUID, db: Session = Depends(get_db)
) -> FileResponse:
    repository = DocumentRepository(db)
    service = DocumentService(repository)

    db_document = service.get_document_by_id(document_id)

    if not Path(db_document.file_path).exists():
        raise HTTPException(status_code=404, detail="Document file not found")

    return FileResponse(
        path=db_document.file_path,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=f"{db_document.title}.docx",
    )
