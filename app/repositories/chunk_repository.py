from sqlalchemy import select

from sqlalchemy.orm import Session
from app.db.models.chunk import Chunk


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
        self, query_embedding: list[float], limit: int = 3
    ) -> list[Chunk]:

        # distance = Chunk.embedding.cosine_distance(query_embedding)

        # Estrutura da consulta com sqlalchemy
        statement = (
            select(Chunk)
            .order_by(Chunk.embedding.cosine_distance(query_embedding))
            .limit(limit)
        )

        result = self.db.execute(statement)

        chunks = result.scalars().all()

        return chunks
