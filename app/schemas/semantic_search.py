import uuid
from pydantic import BaseModel


class SemanticSearchResult(BaseModel):
    content: str
    distance: float
    source_document_id: uuid.UUID
