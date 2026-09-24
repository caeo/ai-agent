import uuid

from sqlalchemy.orm import Session
from app.db.models.source_document import SourceDocument


class SourceDocumentRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, source_document: SourceDocument) -> SourceDocument:
        self.db.add(source_document)
        self.db.commit()
        self.db.refresh(source_document)
        return source_document

    def get_by_id(self, source_document_id: uuid.UUID) -> SourceDocument | None:
        return self.db.get(SourceDocument, source_document_id)
