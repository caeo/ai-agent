import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db.models.document import Document


class DocumentRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, document: Document) -> Document:
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        return document

    def get_by_id(self, document_id: uuid.UUID) -> Document | None:
        return self.db.get(Document, document_id)

    def list_all(self) -> list[Document]:
        statement = select(Document)
        result = list(self.db.scalars(statement).all())

        return result
