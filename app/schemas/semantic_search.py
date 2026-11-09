import uuid
from pydantic import BaseModel
from app.core.enums import KnowledgeRole

class SemanticSearchResult(BaseModel):
    content: str
    distance: float
    source_document_id: uuid.UUID
    filename: str
    knowledge_role: KnowledgeRole | None = None
    applicability: str | None = None


