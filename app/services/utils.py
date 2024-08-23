from datetime import datetime

from app.models.pdf_models import LiftCompanyReport, LiftReport


def convert_to_models(extracted_data) -> list[LiftCompanyReport]:
    """
    Преобразует извлеченные данные в модели LiftCompanyReport и LiftReport с валидацией.
    """
    lift_company_reports = []

    for block in extracted_data['stoppages_data']:
        company_name = block['block']['company_name']
        company_report = LiftCompanyReport(company_name)

        for row in block['rows']:
            start_time = convert_to_rfc3339(row.get('start_time', ''))
            end_time = convert_to_rfc3339(row.get('end_time', '')) if row.get('end_time') else ''
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


def convert_to_rfc3339(datetime_str: str) -> str:
    """
    Преобразует строку с датой и временем в формат RFC 3339.
    Ожидаемый формат строки: 'дд.мм.гггг чч:мм'
    """
    try:
        dt = datetime.strptime(datetime_str, "%d.%m.%Y %H:%M")
        return dt.isoformat()
    except ValueError as e:
        raise ValueError(f"Ошибка преобразования времени '{datetime_str}': {e}")
