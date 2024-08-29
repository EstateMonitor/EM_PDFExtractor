from app.interfaces.pdf_service_interface import PDFServiceInterface
from app.models.file_model import FileModel
from app.processors.pdf.pdf_processor import PDFProcessor
from app.repositories.pdf_repository import PDFRepository
from app.services import utils
from app.services.config_loader import ConfigLoader
from app.services.utils import convert_to_rfc3339


class PDFService(PDFServiceInterface):
    """
    Сервисный слой для обработки PDF-файлов.
    """

    def __init__(self, config_loader: ConfigLoader, repository: PDFRepository):
        """
        Инициализация сервиса для обработки PDF-файлов.
        """
        self.config_loader = config_loader
        self.repository = repository

    async def process_lift_pdf(self, file: FileModel, output_path=None):
        """
        Обрабатывает PDF-документ о простое лифтов и возвращает массив моделей данных.

        :param file: Объект FileModel, представляющий PDF-файл.
        :param output_path: Путь для сохранения размеченного PDF-файла (необязательный).
        :return: Массив моделей LiftCompanyReport.
        """
        config_path = "core/configs/pdf_structures/lift_report_v1.yml"
        try:
            config = self.config_loader.load_config(config_path)
            processor = PDFProcessor(self.repository, config)

            self.validate_pdf(file)

            # Загрузка PDF из FileModel
            self.repository.load_pdf(file)

            # Обработка PDF с использованием процессора и конфигурации отчёта о простое лифтов
            extracted_data = processor.process_pdf(draw_rectangles=output_path is not None)
            if output_path:
                self.repository.save_pdf(output_path)
                print(f"Размеченный PDF сохранен: {output_path}")

            print("PDF обработан")

            # Преобразование в модели данных
            lift_company_reports = utils.convert_to_models(extracted_data)
            return lift_company_reports, convert_to_rfc3339(extracted_data['report_time'])

        except Exception as e:
            print(f"Ошибка обработки PDF: {e}")
            raise

    def validate_pdf(self, file: FileModel) -> None:
        """
        Проверяет наличие и корректность PDF-документа.

        :param file: Объект FileModel, представляющий PDF-файл.
        """
        try:
            self.repository.load_pdf(file)

            # Простая валидация
            if not self.repository.doc.is_pdf:
                raise ValueError(f"Файл '{file.filename}' не является PDF.")
            if self.repository.doc.needs_pass:
                raise PermissionError(f"Файл '{file.filename}' защищен паролем.")

            print(f"Файл '{file.filename}' успешно валидирован.")

        except FileNotFoundError:
            print(f"Файл '{file.filename}' не найден.")
            raise FileNotFoundError(f"Файл '{file.filename}' не найден.")
        except Exception as e:
            print(f"Ошибка валидации PDF: {e}")
            raise e
