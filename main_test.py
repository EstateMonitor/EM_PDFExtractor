# ДЕМОНСТРАЦИОННЫЙ ФАЙЛ
# ПРИМЕР РАБОТЫ С СЕРВИСОМ PDF, ОБРАБОТКА PDF-ДОКУМЕНТОВ О ПРОСТОЕ ЛИФТОВ
# НЕ БУДЕТ РАБОТАТЬ БЕЗ НАЛИЧИЯ ФАЙЛОВ В ПАПКЕ downloads
# Для работы необходимо создать папку downloads и поместить в нее PDF файлы

import json
import os

from app.repositories.pdf_repository import PDFRepository
from app.repositories.requests_repository import ReportRepository
from app.services.config_loader import ConfigLoader
from app.services.pdf_service import PDFService


def print_report(result):
    for company_report in result:
        print(f"Отчет по компании: {company_report.company_name}")
        for i, report in enumerate(company_report.reports):
            print(f"\t{i + 1}. Отчет по лифту: {report.factory_number}")
            print(f"\tВремя начала: {report.start_time}")
            print("\tВремя окончания: ", report.end_time if report.end_time else "Продолжает стоять")
            print(f"\tЧасы простоя: {report.downtime_hours}")
            print(f"\tРегистрационный номер: {report.reg_number}")
            print()


def main():
    config_loader = ConfigLoader()
    repository = PDFRepository()
    repo = ReportRepository("http://127.0.0.1:8080")

    pdf_service = PDFService(config_loader, repository)
    folder_path = "downloads"
    files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]

    for file in files:
        pdf_path = "downloads/" + file
        # Валидация PDF перед обработкой
        pdf_service.validate_pdf(pdf_path)

        # Обработка PDF
        # result, report_time = pdf_service.process_lift_pdf(pdf_path,
        #                                                    output_path="downloads/output/" + file + "_размеченный.pdf")
        # Если не передавать output_path, то разметка не будет сохранена
        result, report_time = pdf_service.process_lift_pdf(pdf_path)

        # print_report(result)
        # Соберем из отчёта json c кодировкой utf-8
        # В companies запишем отчёт по компаниям
        companies = []
        for company_report in result:
            reports = []
            for report in company_report.reports:
                reports.append({"factory_number": report.factory_number,
                                "start_time": report.start_time,
                                "end_time": report.end_time,
                                "downtime_hours": report.downtime_hours,
                                "reg_number": report.reg_number})
            companies.append({"company_name": company_report.company_name, "reports": reports})

        # Отправка сформированных данных
        data_to_send = {
            "report_time": report_time,
            "companies": companies
        }
        repo.send_report(data_to_send)

        with open("downloads/output/" + file + "_отчет.json", "w", encoding='utf-8') as f:
            json.dump({"report_time": report_time, "companies": companies}, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    main()
