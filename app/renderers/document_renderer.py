from app.schemas.requirement import GeneratedDocument


class DocumentRenderer:

    def generate_text(self, title: str, document: GeneratedDocument) -> str:

        functional_requirements = document.functional_requirements
        non_functional_requirements = document.non_functional_requirements
        technical_restrictions = document.technical_restrictions

        content = f"# {title} \n\n"

        content += "1. Requisitos Funcionais\n"

        for requirement in functional_requirements:
            content += f"{requirement.id} - {requirement.description}\n"

        content += "\n2. Requisitos Não Funcionais\n"

        for requirement in non_functional_requirements:
            content += f"{requirement.id} - {requirement.description}\n"

        content += "\n3. Restrições Técnicas\n"

        for restriction in technical_restrictions:
            content += f"{restriction.id} - {restriction.description}\n"

        return content
