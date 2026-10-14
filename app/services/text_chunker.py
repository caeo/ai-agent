class TextChunker:
    def __init__(self, chunk_size=1000, chunk_overlap=200):

        if chunk_size <= 0:
            raise ValueError("O tamanho do chunk deve ser maior que zero.")

        if chunk_overlap < 0:
            raise ValueError("O overlap não pode ser negativo.")

        if chunk_size - chunk_overlap <= 0:
            raise ValueError("O tamanho do chunk deve ser maior que o overlap.")

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def text_split(self, text: str) -> list[str]:
        # separa o texto em chunks
        paragraphs = text.split("\n\n")

        chunks = []

        current_paragraphs = []

        for paragraph in paragraphs:

            paragraph = paragraph.strip()

            if not paragraph:
                continue

            if len(paragraph) > self.chunk_size:
                if current_paragraphs:
                    chunks.append("\n\n".join(current_paragraphs).strip())

                large_splitted_paragraph = self.split_large_paragraphs(paragraph)
                chunks.extend(large_splitted_paragraph)

                current_paragraphs = []

                continue

            if current_paragraphs:
                candidate = "\n\n".join(current_paragraphs + [paragraph])

            else:
                candidate = paragraph

            if len(candidate) > self.chunk_size and current_paragraphs:

                chunks.append("\n\n".join(current_paragraphs).strip())

                overlap = []
                overlap_size = 0

                for overlap_paragraph in reversed(current_paragraphs):
                    overlap_paragraph = overlap_paragraph.strip()

                    overlap.insert(0, overlap_paragraph)

                    overlap_size += len(overlap_paragraph)

                    if overlap_size >= self.chunk_overlap:
                        break

                current_paragraphs = overlap + [paragraph]
            else:
                current_paragraphs.append(paragraph)

        if current_paragraphs:
            chunks.append("\n\n".join(current_paragraphs).strip())

        return chunks

    def split_large_paragraphs(self, paragraph: str) -> list[str]:
        if len(paragraph) <= self.chunk_size:
            return [paragraph]

        parts = []
        start = 0

        while start < len(paragraph):
            end = min(start + self.chunk_size, len(paragraph))
            parts.append(paragraph[start:end])

            if end == len(paragraph):
                break

            start = end - self.chunk_overlap

        return parts
