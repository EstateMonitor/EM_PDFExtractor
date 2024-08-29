# Модели для работы с PDF-файлами
# Они нужны, чтобы хранить данные, извлеченные из PDF-файлов и передавать их между различными слоями приложения (сервисы, репозитории и т.д.)
# Это позволяет разделить логику работы с данными и их представление
# В данном случае модели используются для хранения данных о метаданных PDF-файла и данных о простое лифтов

class PDFMetadata:
    """
    Метаданные PDF-файла
    # TODO: не используется в коде, пока что
    """

    def __init__(self, number_of_pages: int, metadata: dict):
        self.number_of_pages = number_of_pages
        self.metadata = metadata  # TODO: Выделить только нужные поля


class Rect:
    """
    Прямоугольник на странице PDF
    Содержит координаты углов и номер страницы,
    так как прямоугольник может быть на разных страницах и его полная идентификация требует страницы
    """

    def __init__(self, x0: float, y0: float, x1: float, y1: float, page: int):
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1
        self.page = page  # У нас трёхмерное пространство по сути, две координаты на странице и номер страницы
        self.width = x1 - x0
        self.height = y1 - y0


class LiftCompanyReport:
    """
    Отчет о простое лифтов для компании
    """

    def __init__(self, company_name: str):
        self.company_name = company_name
        self.reports = []

    def dict(self):
        return {
            "company_name": self.company_name,
            "reports": [report.__dict__ for report in self.reports]
        }


class LiftReport:
    """
    Отчет о простое лифта
    """

    def __init__(self, start_time: str, end_time: str, downtime_hours: int, factory_number: str, reg_number: str):
        self.start_time = start_time
        self.end_time = end_time
        self.downtime_hours = downtime_hours
        self.factory_number = factory_number
        self.reg_number = reg_number
