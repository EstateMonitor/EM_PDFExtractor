# Define metadata model for the PDF
class PDFMetadata:
    def __init__(self, number_of_pages: int, metadata: dict):
        self.number_of_pages = number_of_pages
        self.metadata = metadata  # TODO: Выделить только нужные поля


class Rect:
    def __init__(self, x0: float, y0: float, x1: float, y1: float, page: int):
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1
        self.page = page  # У нас трёхмерное пространство по сути, две координаты на странице и номер страницы
        self.width = x1 - x0
        self.height = y1 - y0


class LiftCompanyReport:
    def __init__(self, company_name: str):
        self.company_name = company_name
        self.reports = []


class LiftReport:
    def __init__(self, start_time: str, end_time: str, downtime_hours: int, factory_number: str, reg_number: str):
        self.start_time = start_time
        self.end_time = end_time
        self.downtime_hours = downtime_hours
        self.factory_number = factory_number
        self.reg_number = reg_number
