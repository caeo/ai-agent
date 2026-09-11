import re
import unicodedata
import uuid
from docx import Document
from pathlib import Path
from app.schemas.requirement import GeneratedDocument


class DocxRenderer:
    @staticmethod
    def clear_title(name: str) -> str:
        normalized_name = unicodedata.normalize("NFKD", name)
        without_accents = normalized_name.encode("ascii", "ignore").decode("ascii")
        lowercase = without_accents.lower()
        safe_name = re.sub(r"[^a-z0-9]+", "_", lowercase).strip("_")
        return safe_name

    def generate(
        self, title: str, generated_document: GeneratedDocument
    ) -> tuple[str, Path]:

        docx = Document()

        functional_requirements = generated_document.functional_requirements
        non_functional_requirements = generated_document.non_functional_requirements
        technical_restrictions = generated_document.technical_restrictions

        docx.add_heading(title, level=0)
        docx.add_heading("1. Requisitos Funcionais", level=1)

        for requirement in functional_requirements:
            docx.add_paragraph(f"{requirement.id} - {requirement.description}")

        docx.add_heading("2. Requisitos Não Funcionais", level=1)

        for requirement in non_functional_requirements:
            docx.add_paragraph(f"{requirement.id} - {requirement.description}")

        docx.add_heading("3. Restrições Técnicas", level=1)

        for restriction in technical_restrictions:
            docx.add_paragraph(f"{restriction.id} - {restriction.description}")

        output_dir = Path("generated_documents")
        output_dir.mkdir(exist_ok=True)

        identifier_uuid = uuid.uuid4().hex[:8]

        filename = self.clear_title(title)
        file_path = output_dir / f"{filename}_{identifier_uuid}.docx"

        docx.save(file_path)

        return identifier_uuid, file_path
