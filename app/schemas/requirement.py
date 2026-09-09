from pydantic import BaseModel


class Requirement(BaseModel):
    id: str
    description: str


class GeneratedDocument(BaseModel):
    functional_requirements: list[Requirement]
    non_functional_requirements: list[Requirement]
    technical_restrictions: list[Requirement]
