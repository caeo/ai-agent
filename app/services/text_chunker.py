class TextChunker:
    def __init__(self, chunk_size=1000):
        self.chunk_size = chunk_size

    def text_split(self, text: str) -> list[str]:
        # separa o texto em chunks
        paragraphs = text.split("\n\n")

        chunks = []

        current_chunk = ""

        for paragraph in paragraphs:

            paragraph = paragraph.strip()

            if not paragraph:
                continue

            if current_chunk:
                candidate = current_chunk + "\n\n" + paragraph
            else:
                candidate = paragraph

            if len(candidate) > self.chunk_size and current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = paragraph
            else:
                current_chunk = candidate

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks
