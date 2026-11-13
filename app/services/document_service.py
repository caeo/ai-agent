import json
import uuid

from datetime import datetime

from pathlib import Path

from app.services.ai_service import AIService
from app.services.retrieval_service import RetrievalService

# from app.services.knowledge_selection_service import KnowledgeSelectionService

from app.schemas.document import DocumentRequest, DocumentResponse, DocumentListItem
from app.schemas.requirement import GeneratedDocument, DocumentIdentification

from app.renderers.docx_renderer import DocxRenderer
from app.renderers.template_docx_renderer import TemplateDocxRenderer

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
        template_docx_renderer: TemplateDocxRenderer,
        # knowledge_selection_service: KnowledgeSelectionService,
        active_template_path: Path | None = None,
    ):
        self.repository = repository
        self.ai_service = ai_service
        self.docx_renderer = docx_renderer
        self.retrieval_service = retrieval_service
        self.template_docx_renderer = template_docx_renderer
        self.active_template_path = active_template_path
        # self.knowledge_selection_service = knowledge_selection_service

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

    def list_all(self) -> list[DocumentListItem]:
        db_documents = self.repository.list_all()

        documents = []

        for document in db_documents:
            document_item = DocumentListItem(
                id=document.id,
                title=document.title,
                status=document.status,
                download_url=f"/documents/{document.id}/download",
            )
            documents.append(document_item)

        return documents

    def create(self, request: DocumentRequest) -> DocumentResponse:

        document_id = uuid.uuid4()

        # RECUPERA O CONTEXTO
        retrieved_context = self.retrieval_service.retrieve_generation_context(
            request.context
        )
        print("Contexto recuperado:", retrieved_context, flush=True)
        # -----------------------------------------------------------------------

        # SELEÇÃO DE CONTEXTO
        # Seleciona o contexto entre os trechos recuperados
        # print("==== SELEÇÃO DE CONTEXTO ====", flush=True)
        # selected_context = self.knowledge_selection_service.select_context(
        #     user_context=request.context,
        #     retrieved_context=retrieved_context,
        #     document_purpose="gerar um documento de requisitos",
        # )
        # print(selected_context, flush=True)
        # print("==== FIM DA SELEÇÃO DE CONTEXTO ====", flush=True)
        # -----------------------------------------------------------------------

        # MONTA O PROMPT
        # Cria o prompt com seleção de contexto
        # prompt = requirements_prompt(request.context, selected_context)

        # Prompt sem a seleção de contexto
        prompt = requirements_prompt(request.context, retrieved_context)
        # -----------------------------------------------------------------------

        # GERA O DOCUMENTO
        print("Chamando o Ollama...", flush=True)
        generated_response = self.ai_service.generate(prompt)
        print("O Ollama respondeu.", flush=True)
        print("===== RESPOSTA BRUTA DO LLM =====")
        print(repr(generated_response))
        print("=================================")

        generated_data = json.loads(generated_response)
        generated_document = GeneratedDocument(**generated_data)

        generated_document.identification = DocumentIdentification(
            version="1.0",
            responsible=None,
            date=datetime.now().strftime("%d/%m/%Y"),
            status="Em elaboração",
        )

        # Decide se vai usar um template
        if self.active_template_path is not None:
            file_path = self.template_docx_renderer.generate(
                template_path=self.active_template_path,
                title=request.title,
                document_id=document_id,
                generated_document=generated_document,
            )

        else:

            file_path = self.docx_renderer.generate(
                request.title,
                document_id=document_id,
                generated_document=generated_document,
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
