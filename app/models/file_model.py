# models/file_model.py

class FileModel:
    def __init__(self, filename: str, content: bytes):
        self.filename = filename
        self.content = content

    def get_filename(self) -> str:
        return self.filename

    def is_pdf(self) -> bool:
        return self.filename.endswith('.pdf')

    def get_content(self) -> bytes:
        return self.content
