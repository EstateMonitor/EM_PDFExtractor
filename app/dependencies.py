# api/dependencies.py
from app.repositories.pdf_repository import PDFRepository
from app.services.config_loader import ConfigLoader
from app.services.pdf_service import PDFService


def get_pdf_service() -> PDFService:
    """
    Dependency for getting the PDFService instance.
    """
    repo = PDFRepository()
    config_loader = ConfigLoader()
    pdf_service = PDFService(config_loader, repo)

    return pdf_service
