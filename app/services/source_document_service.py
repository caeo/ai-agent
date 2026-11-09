import uuid

from time import perf_counter

from app.repositories.source_document_repository import SourceDocumentRepository
from app.repositories.chunk_repository import ChunkRepository

from app.db.models.source_document import SourceDocument
from app.db.models.chunk import Chunk

from app.schemas.source_document import SourceDocumentRequest, SourceDocumentResponse

from app.services.text_chunker import TextChunker
from app.services.embedding_service import EmbeddingService


class SourceDocumentService:
    def __init__(
        self,
        source_document_repository: SourceDocumentRepository,
        chunk_repository: ChunkRepository,
        text_chunker: TextChunker,
        embedding_service: EmbeddingService,
    ):
        self.source_document_repository = source_document_repository
        self.chunk_repository = chunk_repository
        self.text_chunker = text_chunker
        self.embedding_service = embedding_service

    def ingest(
        self, request: SourceDocumentRequest, text: str
    ) -> SourceDocumentResponse:
        source_document_created = self._create_source_document(request)

        self._create_chunks(text, source_document_created.id)

        response = SourceDocumentResponse(
            id=source_document_created.id,
            filename=source_document_created.filename,
            file_path=source_document_created.file_path,
            source_type=source_document_created.source_type,
            knowledge_role=source_document_created.knowledge_role,
            applicability=source_document_created.applicability,
        )

        return response

    def _create_source_document(self, request: SourceDocumentRequest) -> SourceDocument:

        source_document = SourceDocument(
            filename=request.filename,
            file_path=request.file_path,
            source_type=request.source_type.value,
            knowledge_role=(
                request.knowledge_role.value
                if request.knowledge_role is not None
                else None
            ),
            applicability=request.applicability,
        )

        source_document_created = self.source_document_repository.create(
            source_document
        )

        return source_document_created

    def _create_chunks(self, text: str, source_document_id: uuid.UUID) -> list[Chunk]:
        inicio = perf_counter()
        print(f"[ingest] Dividindo {len(text)} caracteres...", flush=True)
        chunks = list(self.text_chunker.text_split(text))
        total = len(chunks)
        print(f"[ingest] {total} chunks em {perf_counter() - inicio:.2f}s", flush=True)

        created_chunks = []
        for index, chunk in enumerate(chunks):
            etapa = perf_counter()
            print(f"[embed] Iniciando {index + 1}/{total} ({len(chunk)} caracteres)", flush=True)
            embedding = self.embedding_service.embed(chunk)
            print(f"[embed] Concluído {index + 1}/{total} em {perf_counter() - etapa:.2f}s", flush=True)

            created_chunks.append(Chunk(
                source_document_id=source_document_id,
                content=chunk,
                chunk_index=index,
                embedding=embedding,
            ))

        print(f"[db] Salvando {total} chunks...", flush=True)
        saved_chunks = self.chunk_repository.create(created_chunks)
        print(f"[ingest] Finalizado em {perf_counter() - inicio:.2f}s", flush=True)
        return saved_chunks

    # def _create_chunks(self, text: str, source_document_id: uuid.UUID) -> list[Chunk]:

    #     chunks = self.text_chunker.text_split(text)
    #     created_chunks = []

    #     for index, chunk in enumerate(chunks):

    #         chunk_object = Chunk(
    #             source_document_id=source_document_id,
    #             content=chunk,
    #             chunk_index=index,
    #             embedding=self.embedding_service.embed(chunk),
    #         )

    #         created_chunks.append(chunk_object)

    #     saved_chunks = self.chunk_repository.create(created_chunks)

    #     return saved_chunks
