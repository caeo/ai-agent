from pydantic import BaseModel
from app.schemas.requirement import GeneratedDocument


class DocumentRequest(BaseModel):
    title: str
    context: str


class DocumentResponse(BaseModel):
    id: str
    title: str
    content: GeneratedDocument
    status: str
    download_url: str
