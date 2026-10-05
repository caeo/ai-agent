import json
import uuid


from app.services.ai_service import AIService
from app.services.retrieval_service import RetrievalService

from app.schemas.document import DocumentRequest, DocumentResponse
from app.schemas.requirement import GeneratedDocument

from app.renderers.docx_renderer import DocxRenderer

from app.prompts.requirements_prompt import requirements_prompt

from app.repositories.document_repository import DocumentRepository

from app.db.models.document import Document


class DocumentService:

    def __init__(
        self,
        repository: DocumentRepository,
        ai_service: AIService,
        docx_renderer: DocxRenderer,
        retrieval_service: RetrievalService,
    ):
        self.repository = repository
        self.ai_service = ai_service
        self.docx_renderer = docx_renderer
        self.retrieval_service = retrieval_service

    def get_by_id(self, document_id: uuid.UUID) -> DocumentResponse | None:

        db_document = self.repository.get_by_id(document_id)

        if db_document is None:
            return None

        generated_document = GeneratedDocument(**db_document.content)

        return DocumentResponse(
            id=db_document.id,
            title=db_document.title,
            content=generated_document,
            status=db_document.status,
            download_url=f"/documents/{db_document.id}/download",
        )

    def get_document_by_id(self, document_id: uuid.UUID) -> Document | None:
        return self.repository.get_by_id(document_id)

    def create(self, request: DocumentRequest) -> DocumentResponse:

        document_id = uuid.uuid4()

        retrieved_context = self.retrieval_service.retrieve_context(request.context)

        # print("===== CONTEXTO RECUPERADO PELO RAG =====")
        # print(retrieved_context)
        # print("========================================")

        prompt = requirements_prompt(request.context, retrieved_context)

        generated_response = self.ai_service.generate(prompt)
        print("===== RESPOSTA BRUTA DO LLM =====")
        print(repr(generated_response))
        print("=================================")
        generated_data = json.loads(generated_response)
        generated_document = GeneratedDocument(**generated_data)

        file_path = self.docx_renderer.generate(
            request.title, document_id, generated_document
        )

        db_document = Document(
            id=document_id,
            title=request.title,
            document_type="requirements",
            status="generated",
            file_path=str(file_path),
            content=generated_document.model_dump(),
        )

        saved_document = self.repository.create(db_document)

        document_created = DocumentResponse(
            id=saved_document.id,
            title=saved_document.title,
            content=generated_document,
            status=saved_document.status,
            download_url=f"/documents/{saved_document.id}/download",
        )

        return document_created
