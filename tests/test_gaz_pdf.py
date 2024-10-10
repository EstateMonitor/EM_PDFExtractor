import asyncio

from app.models.file_model import FileModel
from app.repositories.pdf_repository import PDFRepository
from app.services.config_loader import ConfigLoader
from app.services.pdf_service import PDFService


def test_processing_gaz_pdf():
    # Arrange
    filename = "../downloads/gaz_1.pdf"
    with open(filename, "rb") as f:  # Используем бинарный режим
        file_content = f.read()
        file = FileModel(filename, file_content)
        output_path = "../output/gaz_1_output.pdf"
        config_loader = ConfigLoader()
        repo = PDFRepository()
        pdf_service = PDFService(config_loader, repo)

        # Act
        # Используем asyncio.run для вызова асинхронного метода
        asyncio.run(pdf_service.process_gaz_pdf(file, output_path))


test_processing_gaz_pdf()
