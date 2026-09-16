import json
import uuid


from app.services.ai_service import AIService

from app.schemas.document import DocumentRequest, DocumentResponse
from app.schemas.requirement import GeneratedDocument

from app.renderers.docx_renderer import DocxRenderer

from app.prompts.requirements_prompt import requirements_prompt

from app.repositories.document_repository import DocumentRepository

from app.db.models.document import Document


class DocumentService:

    def __init__(self, repository: DocumentRepository):
        self.repository = repository

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

        ai_service = AIService()

        generated_response = ai_service.generate(requirements_prompt(request.context))
        generated_data = json.loads(generated_response)
        generated_document = GeneratedDocument(**generated_data)


        docx_renderer = DocxRenderer()
        file_path = docx_renderer.generate(
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
