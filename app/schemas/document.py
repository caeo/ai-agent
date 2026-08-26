from pydantic import BaseModel

class DocumentRequest(BaseModel):
    title: str
    context: str


class DocumentResponse(BaseModel):
    title: str
    context: str
    status: str
    
