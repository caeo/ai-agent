import uuid

from pathlib import Path


class FileStorageService:

    def save(self, filename: str, content: bytes) -> Path:

        document_id = uuid.uuid4()

        directory = Path("uploads")
        directory.mkdir(parents=True, exist_ok=True)

        extension = Path(filename).suffix

        stored_filename = f"{document_id}{extension}"

        file_path = directory / stored_filename
        file_path.write_bytes(content)

        return file_path
