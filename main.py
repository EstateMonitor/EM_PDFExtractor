# ДЕМОНСТРАЦИОННЫЙ ФАЙЛ
# ПРИМЕР РАБОТЫ С СЕРВИСОМ PDF, ОБРАБОТКА PDF-ДОКУМЕНТОВ О ПРОСТОЕ ЛИФТОВ
# НЕ БУДЕТ РАБОТАТЬ БЕЗ НАЛИЧИЯ ФАЙЛОВ В ПАПКЕ downloads
# Для работы необходимо создать папку downloads и поместить в нее PDF файлы

from app.repositories.pdf_repository import PDFRepository
from app.services.config_loader import ConfigLoader
from app.services.pdf_service import PDFService

config_loader = ConfigLoader()
repository = PDFRepository()

pdf_service = PDFService(config_loader, repository)

files = ["25.06 проверил.pdf", "16.06 проверил.pdf"]

for file in files:
    pdf_path = "downloads/" + file
    # Валидация PDF перед обработкой
    pdf_service.validate_pdf(pdf_path)

    # Обработка PDF
    result = pdf_service.process_lift_pdf(pdf_path, output_path="downloads/output/" + file + "_размеченный.pdf")
    # Если не передавать output_path, то разметка не будет сохранена

    for company_report in result:
        print(f"Отчет по компании: {company_report.company_name}")
        for i, report in enumerate(company_report.reports):
            print(f"\t{i + 1}. Отчет по лифту: {report.factory_number}")
            print(f"\tВремя начала: {report.start_time}")
            print("\tВремя окончания: ", report.end_time if report.end_time else "Продолжает стоять")
            print(f"\tЧасы простоя: {report.downtime_hours}")
            print(f"\tРегистрационный номер: {report.reg_number}")
            print()
