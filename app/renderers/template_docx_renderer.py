import uuid
import unicodedata
import re
from copy import deepcopy

from pathlib import Path

from app.schemas.requirement import (
    Requirement,
    GeneratedDocument,
    DocumentIdentification,
)

from app.renderers.docx_renderer import DocxRenderer

from docx import Document
from docx.table import Table
from docx.text.paragraph import Paragraph
from docx.document import Document as DocxDocument


class TemplateDocxRenderer:
    def load_template(self, template_path: Path) -> DocxDocument:
        docx = Document(template_path)
        return docx

    # Substitui o conteúdo de uma célula preservando sua formatação
    def fill_text_cell(self, cell, value):
        paragraph = cell.paragraphs[0]

        if paragraph.runs:
            # coloca o valor do campo específico no parágrafo a cada run
            paragraph.runs[0].text = str(value)

            # Remove o texto dos demais runs para não deixar conteúdo antigo
            for run in paragraph.runs[1:]:
                run.text = ""

        else:
            paragraph.add_run(str(value))

        for extra_paragraphs in cell.paragraphs[1:]:
            for run in extra_paragraphs.runs:
                run.text = ""

    # Preenche os campos de identificação
    def fill_identification(self, table, document_data, field_mapping):
        for row in table.rows:
            label = row.cells[0].text.strip()

            if label in field_mapping:
                field = field_mapping[label]
                value = document_data.get(field)
                value = str(value) if value is not None else "-"

                cell = row.cells[1]

                self.fill_text_cell(cell=cell, value=value)

    # Duplica uma linha modelo para preencher a tabela

    def fill_table(
        self,
        table: Table,
        requirements: list[Requirement],
        fields: list[str],
    ) -> None:

        if len(table.rows) < 2:
            raise ValueError(
                "A tabela do template precisa ter cabeçalho e linha modelo."
            )

        if len(fields) != len(table.columns):
            raise ValueError(
                "A quantidade de campos deve corresponder às colunas da tabela."
            )

        linha_modelo_xml = deepcopy(table.rows[1]._tr)

        while len(table.rows) > 1:
            nova_linha = table.rows[-1]
            table._tbl.remove(nova_linha._tr)

        for requirement in requirements:
            nova_linha_xml = deepcopy(linha_modelo_xml)

            table._tbl.append(nova_linha_xml)

            nova_linha = table.rows[-1]

            for index, field in enumerate(fields):

                cell = nova_linha.cells[index]
                # Se o arquivo possuir uma coluna que não está no schema, preencherá com "-"
                value = getattr(requirement, field, None)

                text = str(value) if value is not None else "-"

                self.fill_text_cell(cell, text)

    def inspect_tables(self, docx: DocxDocument) -> None:
        for index, table in enumerate(docx.tables):
            print(f"Tabela {index}")
            print(f"Linhas: {len(table.rows)}")
            print(f"Colunas: {len(table.columns)}")

            if table.rows:
                first_row = table.rows[0]

                for cell in first_row.cells:
                    print(cell.text.strip())

            print("---")

    def find_table(self, docx: DocxDocument, headers: list[str]) -> Table | None:
        for table in docx.tables:

            if not table.rows:
                continue

            first_row = table.rows[0]

            # list comprehension
            found_headers = [cell.text.strip() for cell in first_row.cells]

            # sem list comprehension
            # found_headers = []
            # for cell in first_row.cells:
            #     found_headers.append(cell.text.strip())

            if found_headers == headers:
                return table

        return None

    def find_table_after_heading(
        self, docx: DocxDocument, heading: str
    ) -> Table | None:

        found_heading = False

        for block in docx.iter_inner_content():

            if isinstance(block, Paragraph):
                if block.text.strip() == heading:
                    found_heading = True
                    continue

                if found_heading and block.style.name.startswith("Heading"):
                    return None

            if found_heading and isinstance(block, Table):
                return block

        return None

    def clear_table_rows(self, table: Table) -> None:

        while len(table.rows) > 1:
            row = table.rows[-1]
            table._tbl.remove(row._tr)

    def generate(
        self,
        template_path: Path,
        title: str,
        document_id: uuid.UUID,
        generated_document: GeneratedDocument,
    ) -> Path:

        docx = self.load_template(template_path=template_path)

        identification = generated_document.identification
        objective = generated_document.objective
        functional_requirements = generated_document.functional_requirements
        non_functional_requirements = generated_document.non_functional_requirements
        technical_restrictions = generated_document.technical_restrictions

        document_data = {
            "title": title,
            **(identification.model_dump() if identification is not None else {}),
        }

        field_mapping = {
            "Projeto / Demanda": "title",
            "Versão": "version",
            "Responsável": "responsible",
            "Data": "date",
            "Status": "status",
        }

        # Preencher identificação
        identification_table = self.find_table(
            docx=docx, headers=["Campo", "Preenchimento"]
        )
        if identification_table is None:
            raise ValueError("Tabela de identificação não encontrada.")
        self.fill_identification(
            table=identification_table,
            document_data=document_data,
            field_mapping=field_mapping,
        )

        # Preencher objetivo
        objective_table = self.find_table_after_heading(
            docx=docx, heading="2. Objetivo"
        )
        if objective_table is None:
            raise ValueError("Parágrafo do objetivo não encontrado.")

        objective_text = (
            objective if objective and objective.strip() else "Objetivo não informado."
        )

        self.fill_text_cell(cell=objective_table.cell(0, 0), value=objective_text)

        # Preencher requisitos funcionais
        functional_requirements_table = self.find_table(
            docx=docx, headers=["ID", "Requisito", "Prioridade"]
        )
        if functional_requirements_table is None:
            raise ValueError("Tabela de requisitos funcionais não encontrada.")

        self.fill_table(
            table=functional_requirements_table,
            requirements=functional_requirements,
            fields=["id", "description", "priority"],
        )

        # Preencher requisitos não funcionais
        non_functional_requirements_table = self.find_table(
            docx=docx, headers=["ID", "Requisito", "Categoria"]
        )
        if non_functional_requirements_table is None:
            raise ValueError("Tabela de requisitos não funcionais não encontrada.")
        self.fill_table(
            table=non_functional_requirements_table,
            requirements=non_functional_requirements,
            fields=["id", "description", "category"],
        )

        # Preencher Restrições técnicas
        technical_restrictions_table = self.find_table(
            docx=docx, headers=["ID", "Restrição"]
        )
        if technical_restrictions_table is None:
            raise ValueError("Tabela de restrições ténicas não encontrada.")
        self.fill_table(
            table=technical_restrictions_table,
            requirements=technical_restrictions,
            fields=["id", "description"],
        )

        # Apagar as linhas das tabelas que não existem no schema

        table_regra = self.find_table(docx=docx, headers=["ID", "Regra"])
        if table_regra is None:
            raise ValueError("Tabela de regras de negócio não encontrada.")
        self.clear_table_rows(table_regra)

        table_premissas = self.find_table(
            docx=docx, headers=["ID", "Tipo", "Descrição"]
        )
        if table_premissas is None:
            raise ValueError("Tabela de premissas não encontrada.")
        self.clear_table_rows(table_premissas)

        table_escopo = self.find_table(
            docx=docx, headers=["Incluído no escopo", "Fora do escopo"]
        )
        if table_escopo is None:
            raise ValueError("Tabela escopo não encontrada.")
        self.clear_table_rows(table_escopo)

        safe_name = DocxRenderer().clear_title(title)

        output_path = Path(f"generated_documents/{safe_name}_{document_id}.docx")

        output_path.parent.mkdir(parents=True, exist_ok=True)

        docx.save(output_path)

        return output_path


if __name__ == "__main__":

    requirements = [
        Requirement(id="RF01", description="Permitir cadastro de equipamentos."),
        Requirement(id="RF02", description="Permitir consulta de equipamentos."),
    ]

    technical_restrictions = [
        Requirement(id="TR01", description="Usar apenas python"),
        Requirement(id="TR02", description="Usar apenas mongodb."),
    ]

    non_functional_requirements = [
        Requirement(
            id="RNF01",
            description="O sistema deverá responder às consultas em até dois segundos.",
        ),
        Requirement(
            id="RNF02",
            description="O sistema deverá estar disponível 99,5% do tempo.",
        ),
    ]

    objective = (
        "Centralizar o cadastro, a consulta e o acompanhamento "
        "dos equipamentos de informática"
    )

    identification = DocumentIdentification(
        version="1.0",
        responsible="Equipe de Sofisticação",
        date="27/10/2026",
        status="Em elaboração",
    )

    document_data = {
        "title": "Sistema de Cadastro de Equipamentos",
        "version": "1.0",
        "responsible": "Equipe de TI",
        "date": "26/10/2026",
        "status": "Em elaboração",
    }

    field_mapping = {
        "Projeto / Demanda": "title",
        "Versão": "version",
        "Responsável": "responsible",
        "Data": "date",
        "Status": "status",
    }

    generated_document = GeneratedDocument(
        identification=identification,
        objective=objective,
        functional_requirements=requirements,
        non_functional_requirements=non_functional_requirements,
        technical_restrictions=technical_restrictions,
    )

    output_path = TemplateDocxRenderer().generate(
        template_path=r"C:\Users\silva.csc\Desktop\ai-agent\uploads\template_erquisitos_verde.docx",
        title="Documento_teste",
        document_id=uuid.uuid4(),
        generated_document=generated_document,
    )

    print(f"Documento gerado: {output_path}")
