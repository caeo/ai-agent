from pydantic import BaseModel
from app.schemas.requirement import GeneratedDocument


class DocumentRequest(BaseModel):
    title: str
    context: str


class DocumentResponse(BaseModel):
    title: str
    content: GeneratedDocument
    status: str
