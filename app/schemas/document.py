import uuid
from pydantic import BaseModel
from app.schemas.requirement import GeneratedDocument


class DocumentRequest(BaseModel):
    title: str
    context: str


class DocumentResponse(BaseModel):
    id: uuid.UUID
    title: str
    content: GeneratedDocument
    status: str
    download_url: str
