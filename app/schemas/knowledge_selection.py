import uuid

from typing import Literal


from pydantic import BaseModel


class SelectedExcerpt(BaseModel):

    source_document_id: uuid.UUID
    knowledge_role: Literal["norm", "guideline"]
    content: str


class KnowledgeSelection(BaseModel):
    selected_excerpts: list[SelectedExcerpt]


class CandidateSelection(BaseModel):
    selected_ids: list[str]
