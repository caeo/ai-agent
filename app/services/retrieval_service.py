from app.repositories.chunk_repository import ChunkRepository

from app.schemas.semantic_search import SemanticSearchResult
from app.services.embedding_service import EmbeddingService

from app.core.enums import SourceType


class RetrievalService:
    def __init__(
        self, chunk_repository: ChunkRepository, embedding_service: EmbeddingService
    ):
        self.chunk_repository = chunk_repository
        self.embedding_service = embedding_service

    def search(
        self,
        query: str,
        limit: int = 3,
        threshold: float = 0.55,
        source_type: SourceType = SourceType.KNOWLEDGE,
    ) -> list[SemanticSearchResult]:

        embedded_query = self.embedding_service.embed(query)

        semantic_search_results = self.chunk_repository.semantic_search(
            embedded_query, limit, threshold, source_type
        )

        return semantic_search_results

    def retrieve_context(
        self,
        query: str,
        limit: int = 3,
        threshold: float = 0.55,
        source_type: SourceType = SourceType.KNOWLEDGE,
    ) -> str:
        semantic_search_results = self.search(query, limit, threshold, source_type)

        chunk_contents = [result.content for result in semantic_search_results]

        content = "\n\n".join(chunk_contents)

        return content
