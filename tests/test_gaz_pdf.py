import os

from app.models.file_model import FileModel
from app.repositories.pdf_repository import PDFRepository
from app.services.config_loader import ConfigLoader
from app.services.pdf_service import PDFService


def test_processing_gaz_pdf():
    # Arrange
    filename = "../downloads/gaz_1.pdf"
    with open(filename, "r", encoding='utf-8') as f:
        file_content = f.read().encode("utf-8")
        file = FileModel(filename, file_content)
        output_path = "tests/data/test_output.pdf"
        config_loader = ConfigLoader()
        repo = PDFRepository()
        pdf_service = PDFService(config_loader, repo)

        # Act
        pdf_service.process_gaz_pdf(file, output_path)

        # Assert
        assert os.path.exists(output_path)
        os.remove(output_path)
        assert not os.path.exists(output_path)


test_processing_gaz_pdf()
