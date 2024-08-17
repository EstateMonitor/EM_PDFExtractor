from datetime import datetime

from app.interfaces.pdf_service_interface import PDFServiceInterface
from app.models.pdf_models import LiftCompanyReport, LiftReport
from app.processors.pdf.pdf_processor import PDFProcessor
from app.repositories.pdf_repository import PDFRepository
from app.services.config_loader import ConfigLoader


class PDFService(PDFServiceInterface):
    def __init__(self, config_loader: ConfigLoader, repository: PDFRepository):
        self.config_loader = config_loader
        self.repository = repository

    def process_lift_pdf(self, pdf_path: str, output_path=None) -> list[LiftCompanyReport]:
        """
        Обрабатывает PDF-документ о простое лифтов и возвращает массив моделей данных.
        """
        config_path = "core/configs/pdf_structures/lift_report_test.yml"
        try:
            config = self.config_loader.load_config(config_path)
            processor = PDFProcessor(self.repository, config)

            # Загрузка PDF
            self.repository.load_pdf(pdf_path)

            # Обработка PDF с использованием процессора
            extracted_data = processor.process_pdf(draw_rectangles=output_path is not None)
            if output_path:
                self.repository.save_pdf(output_path)
                print(f"Размеченный PDF сохранен: {output_path}")

            print("PDF обработан")

            # Преобразование в модели данных
            lift_company_reports = self._convert_to_models(extracted_data)
            return lift_company_reports

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
            raise FileNotFoundError(f"Файл '{pdf_path}' не найден.")
        except Exception as e:
            print(f"Ошибка валидации PDF: {e}")
            raise e

    def _convert_to_models(self, extracted_data) -> list[LiftCompanyReport]:
        """
        Преобразует извлеченные данные в модели LiftCompanyReport и LiftReport с валидацией.
        """
        lift_company_reports = []

        for block in extracted_data['stoppages_data']:
            company_name = block['block']['company_name']
            company_report = LiftCompanyReport(company_name)

            for row in block['rows']:
                start_time = self._convert_to_rfc3339(row.get('start_time', ''))
                end_time = self._convert_to_rfc3339(row.get('end_time', '')) if row.get('end_time') else ''
                downtime_hours = row.get('downtime_hours', '')
                factory_number = row.get('factory_number', '')
                reg_number = row.get('serial_number', '')

                # Валидация обязательных полей
                if not all([start_time, downtime_hours, factory_number, reg_number]):
                    raise ValueError(f"Обязательные поля отсутствуют или пусты: {row}")

                lift_report = LiftReport(
                    start_time=start_time,
                    end_time=end_time,
                    downtime_hours=int(downtime_hours),
                    factory_number=factory_number,
                    reg_number=reg_number
                )
                company_report.reports.append(lift_report)

            lift_company_reports.append(company_report)

        return lift_company_reports

    @staticmethod
    def _convert_to_rfc3339(datetime_str: str) -> str:
        """
        Преобразует строку с датой и временем в формат RFC 3339.
        Ожидаемый формат строки: 'дд.мм.гггг чч:мм'
        """
        try:
            dt = datetime.strptime(datetime_str, "%d.%m.%Y %H:%M")
            return dt.isoformat()
        except ValueError as e:
            raise ValueError(f"Ошибка преобразования времени '{datetime_str}': {e}")
