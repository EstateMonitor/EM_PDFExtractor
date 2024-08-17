from abc import abstractmethod, ABC


class PDFServiceInterface(ABC):
    """
    Interface for PDF processing service
    """

    @abstractmethod
    def process_lift_pdf(self, pdf_path: str, output_path=None) -> None:
        pass

    @abstractmethod
    def validate_pdf(self, pdf_path: str) -> None:
        pass
