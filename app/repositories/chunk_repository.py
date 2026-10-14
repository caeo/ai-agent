from sqlalchemy import select

from sqlalchemy.orm import Session

from app.db.models.chunk import Chunk
from app.db.models.source_document import SourceDocument

from app.schemas.semantic_search import SemanticSearchResult
from app.core.enums import SourceType


class ChunkRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, chunks: list[Chunk]) -> list[Chunk]:
        self.db.add_all(chunks)
        self.db.commit()
        for chunk in chunks:
            self.db.refresh(chunk)
        return chunks

    def semantic_search(
        self,
        query_embedding: list[float],
        limit: int = 3,
        threshold: float = 0.55,
        source_type: SourceType = SourceType.KNOWLEDGE,
    ) -> list[SemanticSearchResult]:

        distance = Chunk.embedding.cosine_distance(query_embedding).label("distance")

        # Estrutura da consulta com sqlalchemy
        statement = (
            select(Chunk, distance)
            .join(SourceDocument, Chunk.source_document_id == SourceDocument.id)
            .where(
                distance <= threshold, SourceDocument.source_type == source_type.value
            )
            .order_by(distance)
            .limit(limit)
        )

        results = self.db.execute(statement)

        semantic_search_results = []

        # Converte os resultados da consulta em SemanticSearchResult
        for result in results:
            semantic_search_result = SemanticSearchResult(
                content=result.Chunk.content,
                distance=result.distance,
                source_document_id=result.Chunk.source_document_id,
            )
            semantic_search_results.append(semantic_search_result)

        return semantic_search_results
