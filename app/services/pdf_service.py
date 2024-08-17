from app.interfaces.pdf_service_interface import PDFServiceInterface
from app.processors.pdf.pdf_processor import PDFProcessor
from app.repositories.pdf_repository import PDFRepository
from app.services.config_loader import ConfigLoader


class PDFService(PDFServiceInterface):
    def __init__(self, config_loader: ConfigLoader, repository: PDFRepository):
        self.config_loader = config_loader
        self.repository = repository

    def process_lift_pdf(self, pdf_path: str) -> None:
        """
        Обрабатывает PDF-документ о простое лифтов
        """
        config_path = "core/configs/pdf_structures/lift_report_test.yml"
        try:
            config = self.config_loader.load_config(config_path)
            processor = PDFProcessor(self.repository, self.config_loader)

            # Загрузка PDF
            self.repository.load_pdf(pdf_path)

            # Обработка PDF с использованием процессора
            processor.process_pdf(self.repository, config)

            print(f"PDF обработан")

        except Exception as e:
            print(f"Ошибка обработки PDF: {e}")
            raise

    def validate_pdf(self, pdf_path: str) -> None:
        """
        Проверяет наличие и корректность PDF-документа.
        """
        try:
            self.repository.load_pdf(pdf_path)

            # TODO Простая валидация, можно добавить более сложные проверки
            if not self.repository.doc.is_pdf:
                raise ValueError(f"Файл '{pdf_path}' не является PDF.")
            if self.repository.doc.needs_pass:
                raise PermissionError(f"Файл '{pdf_path}' защищен паролем.")

            print(f"Файл '{pdf_path}' успешно валидирован.")

        except FileNotFoundError:
            print(f"Файл '{pdf_path}' не найден.")
            raise
        except Exception as e:
            print(f"Ошибка валидации PDF: {e}")
            raise
