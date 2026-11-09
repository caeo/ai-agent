from sqlalchemy import select

from sqlalchemy.orm import Session

from app.db.models.chunk import Chunk
from app.db.models.source_document import SourceDocument

from app.schemas.semantic_search import SemanticSearchResult
from app.core.enums import SourceType, KnowledgeRole


class ChunkRepository:
    def __init__(self, db: Session):
        self.db = db

    # Adiciona os chunks no banco de dados e retorna a lista de chunks criados
    def create(self, chunks: list[Chunk]) -> list[Chunk]:
        self.db.add_all(chunks)
        self.db.commit()
        for chunk in chunks:
            self.db.refresh(chunk)
        return chunks

    # Faz a busca semântica dos chunks no banco de dados com base no embedding da query
    def semantic_search(
        self,
        query_embedding: list[float],
        limit: int = 3,
        threshold: float = 0.55,
        source_type: SourceType = SourceType.KNOWLEDGE,
        knowledge_role: KnowledgeRole | None = None,
    ) -> list[SemanticSearchResult]:

        distance = Chunk.embedding.cosine_distance(query_embedding).label("distance")

        statement = (
            select(
                Chunk.content,
                Chunk.source_document_id,
                SourceDocument.filename,
                SourceDocument.knowledge_role,
                SourceDocument.applicability,
                distance,
            )
            .join(SourceDocument, Chunk.source_document_id == SourceDocument.id)
            .where(
                SourceDocument.source_type == source_type.value,
                distance <= threshold,
            )
        )

        # Se o source_type for knowledge, faz a instrução filtrar os documentos que tem knowledge_role e applicability preenchidos e se existir knowledge_role for passado, filtra por knowledge_role
        if source_type == SourceType.KNOWLEDGE:

            # a instrução
            statement = statement.where(
                SourceDocument.knowledge_role.in_(
                    [role.value for role in KnowledgeRole]
                ),
                SourceDocument.applicability.is_not(None),
                SourceDocument.applicability != "",
            )

            if knowledge_role is not None:
                statement = statement.where(
                    SourceDocument.knowledge_role == knowledge_role.value
                )

        statement = statement.order_by(distance).limit(limit)
        rows = self.db.execute(statement).mappings()

        return [SemanticSearchResult(**row) for row in rows]
