# Define metadata model for the PDF
class PDFMetadata:
    def __init__(self, number_of_pages: int, metadata: dict):
        self.number_of_pages = number_of_pages
        self.metadata = metadata  # TODO: Выделить только нужные поля


class Rect:
    def __init__(self, x0, y0, x1, y1):
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1
        self.width = x1 - x0
        self.height = y1 - y0
