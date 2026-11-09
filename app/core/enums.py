from enum import Enum


class SourceType(str, Enum):
    KNOWLEDGE = "knowledge"
    TEMPLATE = "template"

class KnowledgeRole(str, Enum):
    NORM = "norm"
    GUIDELINE = "guideline"
    EXAMPLE = "example"