from app.schemas.document import DocumentRequest, DocumentResponse
from app.services.ai_service import AIService
from app.schemas.requirement import GeneratedDocument
from app.renderers.document_renderer import DocumentRenderer
from app.renderers.docx_renderer import DocxRenderer
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
        3. Não invente tecnologias que não estejam explicitamente presentes no contexto.
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
        15. Os exemplos servem apenas para explicar a classificação. Não inclua nenhum exemplo no resultado se ele não estiver presente no contexto.
        16. Cada requisito deve pertencer a apenas uma categoria.
        17. Nunca repita o mesmo requisito em categorias diferentes.
        18. Se o requisito determinar uma tecnologia, plataforma, banco de dados, sistema operacional ou ambiente específico, classifique-o somente como restrição técnica.
        19. Requisitos de desempenho, disponibilidade, segurança, confiabilidade ou escalabilidade devem ser classificados como requisitos não funcionais, desde que não sejam apenas uma restrição tecnológica. 
        20. Em caso de dúvida entre requisito não funcional e restrição técnica, priorize restrição técnica quando houver uma tecnologia ou plataforma explicitamente determinada.
        
        CONCEITOS PARA USAR NA CLASSIFICAÇÃO:
        
        1. Requisitos Funcionais: descrevem o que o sistema deve fazer, ou seja, as funcionalidades que ele deve possuir.
            - exemplos: login, cadastro, consulta, agendamento, emissão de relatório.
            
        2. Requisitos Não Funcionais: descrevem como o sistema deve se comportar, ou seja, as características de qualidade que ele deve possuir.
            - exemplos: desempenho, disponibilidade, segurança, escalabilidade.
            
        3. Restrições Técnicas: descrevem limitações técnicas que o sistema deve obedecer, como tecnologias específicas que devem ser utilizadas ou evitadas.
            - exemplos: Oracle, PostgreSQL, Java, Windows.
            
        



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
        ],
        "technical_restrictions": [
            {{
            "id": "RT01",
            "description": "descrição"
            }}
        ]
        }}
        

        """

        generated_response = ai_service.generate(prompt)
        generated_data = json.loads(generated_response)
        generated_document = GeneratedDocument(**generated_data)

        renderer = DocumentRenderer()
        rendered_document = renderer.generate_text(document.title, generated_document)
        print(rendered_document)
        print(type(generated_document))

        docx_renderer = DocxRenderer()
        document_id, file_path = docx_renderer.generate(
            document.title, generated_document
        )

        print("document_id: ", document_id, "\nfile_path: ", file_path)

        document_created = DocumentResponse(
            id=document_id, title=document.title, content=generated_document, status="generated", download_url= f"/documents/{document_id}/download"
        )

        print(generated_document)

        return document_created
