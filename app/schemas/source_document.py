import uuid
from app.core.enums import SourceType, KnowledgeRole

from pydantic import BaseModel, Field


class SourceDocumentRequest(BaseModel):
    filename: str
    file_path: str
    source_type: SourceType = SourceType.KNOWLEDGE
    knowledge_role: KnowledgeRole | None = None
    applicability: str | None = Field(default=None, max_length=1000)


class SourceDocumentResponse(BaseModel):
    id: uuid.UUID
    filename: str
    file_path: str
    source_type: SourceType
    knowledge_role: KnowledgeRole | None = None
    applicability: str | None
