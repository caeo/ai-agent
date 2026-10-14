import uuid
from app.core.enums import SourceType

from pydantic import BaseModel


class SourceDocumentRequest(BaseModel):
    filename: str
    file_path: str
    source_type: SourceType = SourceType.KNOWLEDGE


class SourceDocumentResponse(BaseModel):
    id: uuid.UUID
    filename: str
    file_path: str
    source_type: SourceType
