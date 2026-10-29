from pydantic import BaseModel


class Requirement(BaseModel):
    id: str
    description: str


class DocumentIdentification(BaseModel):
    version: str | None = None
    responsible: str | None = None
    date: str | None = None
    status: str | None = None


class GeneratedDocument(BaseModel):
    identification: DocumentIdentification | None = None
    objective: str | None = None
    functional_requirements: list[Requirement]
    non_functional_requirements: list[Requirement]
    technical_restrictions: list[Requirement]
