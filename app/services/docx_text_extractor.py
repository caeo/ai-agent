from pathlib import Path


from docx import Document
from docx.oxml.text.paragraph import CT_P
from docx.oxml.table import CT_Tbl

from docx.text.paragraph import Paragraph
from docx.table import Table


class DocxTextExtractor:

    def extract(self, file_path: Path) -> str:

        document = Document(file_path)

        information = []

        for element in document.element.body:
            if isinstance(element, CT_P):
                paragraph = Paragraph(element, document)

                if paragraph.text.strip():
                    information.append(paragraph.text.strip())

            elif isinstance(element, CT_Tbl):
                table = Table(element, document)
                for row in table.rows:
                    cells = [cell.text.strip() for cell in row.cells]
                    row_content = " | ".join(cells)

                    if row_content.strip():
                        information.append(row_content)

        information_content = "\n\n".join(information)

        return information_content


teste = DocxTextExtractor()


print(teste.extract("uploads\\9fe82f43-3b6f-4d47-b9c3-a93ba86c4070.docx"))
