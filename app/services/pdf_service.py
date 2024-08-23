from app.interfaces.pdf_service_interface import PDFServiceInterface
from app.models.pdf_models import LiftCompanyReport
from app.processors.pdf.pdf_processor import PDFProcessor
from app.repositories.pdf_repository import PDFRepository
from app.services import utils
from app.services.config_loader import ConfigLoader
from app.services.utils import convert_to_rfc3339


class PDFService(PDFServiceInterface):
    """
    Сервисный слой для обработки PDF-файлов
    Нужен для обработки PDF-документов о простое лифтов
    Инкапсулирует работу с репозиторием и процессором PDF
    Должен содержать основную логику работы с PDF
    При этом не должен содержать логику обработки PDF-документов напрямую
    Используется в контроллерах для обработки PDF-файлов (в планах, при реализаци API)
    """

    def __init__(self, config_loader: ConfigLoader, repository: PDFRepository):
        """
        Инициализация сервиса для обработки PDF-файлов
        """
        self.config_loader = config_loader
        self.repository = repository

    def process_lift_pdf(self, pdf_path: str, output_path=None) -> (list[LiftCompanyReport], str):
        """
        Обрабатывает PDF-документ о простое лифтов и возвращает массив моделей данных.

        :param pdf_path: Путь к PDF-файлу
        :param output_path: Путь для сохранения размеченного PDF-файла (необязательный)
        :return: Массив моделей LiftCompanyReport
        """
        config_path = "core/configs/pdf_structures/lift_report_test.yml"
        try:
            config = self.config_loader.load_config(config_path)
            # Использует PDFProcessor, который может обработать любой вид PDF
            # Но мы сами определяем, какие объекты в PDF нас интересуют используя конфигурацию вида PDF
            processor = PDFProcessor(self.repository, config)

            # Загрузка PDF
            self.repository.load_pdf(pdf_path)

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

    def validate_pdf(self, pdf_path: str) -> None:
        """
        Проверяет наличие и корректность PDF-документа.

        :param pdf_path: Путь к PDF-файлу
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
            raise FileNotFoundError(f"Файл '{pdf_path}' не найден.")
        except Exception as e:
            print(f"Ошибка валидации PDF: {e}")
            raise e
