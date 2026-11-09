import json

from app.repositories.chunk_repository import ChunkRepository

from app.schemas.semantic_search import SemanticSearchResult
from app.services.embedding_service import EmbeddingService

from app.core.enums import SourceType, KnowledgeRole


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
        knowledge_role: KnowledgeRole | None = None,
    ) -> list[SemanticSearchResult]:

        embedded_query = self.embedding_service.embed(query)

        semantic_search_results = self.chunk_repository.semantic_search(
            embedded_query, limit, threshold, source_type, knowledge_role=knowledge_role
        )

        return semantic_search_results

    def retrieve_context(
        self,
        query: str,
        limit: int = 3,
        threshold: float = 0.55,
        source_type: SourceType = SourceType.KNOWLEDGE,
        knowledge_role: KnowledgeRole | None = None,
    ) -> str:
        results = self.search(
            query, limit, threshold, source_type, knowledge_role=knowledge_role
        )

        if not results:
            return ""

        return json.dumps(
            [
                result.model_dump(mode="json", exclude={"distance"})
                for result in results
            ],
            ensure_ascii=False,
            indent=2,
        )

    # Recupera os chunks mais semelhantes dentro de cada papel,
    # respeitando os limites de quantidade e distância.
    def retrieve_generation_context(
        self,
        query: str,
        threshold: float = 0.55,
    ) -> str:

        embedded_query = self.embedding_service.embed(query)

        limits_by_role = {
            KnowledgeRole.NORM: 2,
            KnowledgeRole.EXAMPLE: 1,
            KnowledgeRole.GUIDELINE: 1,
        }

        results: list[SemanticSearchResult] = []

        for knowledge_role, limit in limits_by_role.items():
            role_results = self.chunk_repository.semantic_search(
                query_embedding=embedded_query,
                limit=limit,
                threshold=threshold,
                source_type=SourceType.KNOWLEDGE,
                knowledge_role=knowledge_role,
            )

            print(
                f"RAG | papel={knowledge_role.value} | "
                f"chunks recuperados={len(role_results)}",
                flush=True,
            )

            results.extend(role_results)

        if not results:
            return ""

        return json.dumps(
            [
                result.model_dump(mode="json", exclude={"distance"})
                for result in results
            ],
            ensure_ascii=False,
            indent=2,
        )
