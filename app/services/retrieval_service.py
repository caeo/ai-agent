from app.db.models.chunk import Chunk

from app.repositories.chunk_repository import ChunkRepository

from app.services.embedding_service import EmbeddingService


class RetrievalService:
    def __init__(
        self, chunk_repository: ChunkRepository, embedding_service: EmbeddingService
    ):
        self.chunk_repository = chunk_repository
        self.embedding_service = embedding_service

    def search(self, query: str, limit: int = 3) -> list[Chunk]:

        embedded_query = self.embedding_service.embed(query)

        chunks = self.chunk_repository.semantic_search(embedded_query, limit)

        return chunks
