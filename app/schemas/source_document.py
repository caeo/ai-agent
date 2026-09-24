import uuid
from pydantic import BaseModel


class SourceDocumentRequest(BaseModel):
    filename: str
    file_path: str


class SourceDocumentResponse(BaseModel):
    id: uuid.UUID
    filename: str
    file_path: str
