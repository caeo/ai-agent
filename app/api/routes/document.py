import uuid
from fastapi import APIRouter, Depends, HTTPException
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
