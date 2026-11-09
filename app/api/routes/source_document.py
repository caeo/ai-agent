from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Form

from app.core.enums import SourceType, KnowledgeRole

from app.db.session import get_db

from sqlalchemy.orm import Session

from app.services.file_storage_service import FileStorageService
from app.services.text_chunker import TextChunker
from app.services.source_document_service import SourceDocumentService
from app.services.embedding_service import EmbeddingService
from app.services.docx_text_extractor import DocxTextExtractor

from app.schemas.source_document import SourceDocumentRequest, SourceDocumentResponse


from app.repositories.chunk_repository import ChunkRepository
from app.repositories.source_document_repository import SourceDocumentRepository

router = APIRouter()


def get_source_document_service(db: Session = Depends(get_db)) -> SourceDocumentService:
    chunk_repository = ChunkRepository(db)
    source_document_repository = SourceDocumentRepository(db)

    embedding_service = EmbeddingService()
    text_chunker = TextChunker()

    source_document_service = SourceDocumentService(
        source_document_repository, chunk_repository, text_chunker, embedding_service
    )

    return source_document_service


@router.post("/source-documents")
async def upload(
    file: UploadFile = File(...),
    source_type: SourceType = Form(SourceType.KNOWLEDGE),
    knowledge_role: KnowledgeRole | None = Form(None),
    applicability: str | None = Form(None, max_length=1000),
    source_document_service: SourceDocumentService = Depends(
        get_source_document_service
    ),
) -> SourceDocumentResponse:

    file_service = FileStorageService()
    docx_text_extractor = DocxTextExtractor()

    content = await file.read()

    # Se applicability não for None, ele retira os espaços
    applicability = (
        applicability.strip()
        if applicability is not None
        else None
    )

    # checka se o knowledge_role é None
    if source_type == SourceType.KNOWLEDGE:
        if knowledge_role is None:
            raise HTTPException(
                status_code=422,
                detail="Informe o papel do documento de conhecimento."
            )

        if not applicability:
            raise HTTPException(status_code=422, detail="Informe em quais situações o conhecimento se aplica.")

    # Checka se knowledge_role não é nada e se tem applicability, porque um template não deve ter metadados de conhecimento.
    elif knowledge_role is not None or applicability:
        raise HTTPException(
            status_code=422,
            detail="Templates não devem receber metadados de conhecimento."
        )

    # arquivo vazio
    if not content:
        raise HTTPException(
            status_code=400,
            detail="O arquivo enviado está vazio.",
        )

    # arquivo não é .docx
    if not file.filename.lower().endswith(".docx"):
        raise HTTPException(
            status_code=415,
            detail="O arquivo enviado não é um .docx.",
        )

    file_path = file_service.save(file.filename, content=content)

    extracted_text = docx_text_extractor.extract(file_path)

    # Erro ao extrair o texto do arquivo .docx
    if not extracted_text.strip():
        raise HTTPException(
            status_code=422, detail="Não foi possível extrair o texto do arquivo .docx."
        )

    source_document_request = SourceDocumentRequest(
        file_path=str(file_path), filename=str(file.filename), source_type=source_type, knowledge_role=knowledge_role, applicability=applicability
    )

    source_document_response = source_document_service.ingest(
        source_document_request, extracted_text
    )

    return source_document_response
