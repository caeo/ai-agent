from app.schemas.document import DocumentRequest, DocumentResponse
from app.services.ai_service import AIService
from app.schemas.requirement import GeneratedDocument
import json


class DocumentService:

    def create(self, document: DocumentRequest) -> DocumentResponse:

        ai_service = AIService()

        prompt = f"""
        Você é um analista de requisitos.

        Sua tarefa é EXCLUSIVAMENTE extrair e organizar os requisitos
        explicitamente presentes no contexto fornecido.

        REGRAS OBRIGATÓRIAS:

        1. Não invente requisitos.
        2. Não deduza requisitos implícitos.
        3. Não acrescente tecnologias.
        4. Não acrescente campos.
        5. Não acrescente regras de segurança.
        6. Não acrescente requisitos não funcionais que não estejam explicitamente presentes no contexto.
        7. Não acrescente integrações.
        8. Não acrescente comportamentos considerados "comuns" em sistemas semelhantes.
        9. Se o contexto disser apenas "login", registre apenas que o sistema deve possuir funcionalidade de login.
        10. Se o contexto disser apenas "agendamento", registre apenas que o sistema deve possuir funcionalidade de agendamento.
        11. Não explique como essas funcionalidades devem ser implementadas.
        12. Cada requisito produzido deve poder ser diretamente associado a uma frase existente no contexto.
        13. É proibido criar um requisito apenas porque ele seria comum, útil, recomendável ou normalmente associado a outro requisito.
        14. A quantidade de requisitos não deve ser aumentada para tornar o documento mais completo.



        CONTEXTO:

        <contexto>
        {document.context}
        </contexto>

        FORMATO:

        {{
        "functional_requirements": [
            {{
            "id": "RF01",
            "description": "descrição"
            }}
        ],
        "non_functional_requirements": [
            {{
            "id": "RNF01",
            "description": "descrição"
            }}
        ]
        }}
        

        """

        generated_response = ai_service.generate(prompt)

        generated_data = json.loads(generated_response)

        generated_document = GeneratedDocument(**generated_data)

        document_created = DocumentResponse(
            title=document.title, content=generated_document, status="generated"
        )

        print(generated_document)

        return document_created
