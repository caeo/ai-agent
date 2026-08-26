from app.schemas.document import DocumentRequest, DocumentResponse


class DocumentService:
    def create(self, document: DocumentRequest) -> DocumentResponse:
        
        document_created = DocumentResponse(
            title=document.title,
            context=document.context,
            status="received"
        )
        return document_created
