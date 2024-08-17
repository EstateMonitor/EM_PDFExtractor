import pymupdf as fitz

import app.models.pdf_models as models
from app.interfaces.pdf_repository_interface import PDFRepositoryInterface


class PDFRepository(PDFRepositoryInterface):
    def __init__(self):
        self.doc = None
        self.pages = None
        self.drawings = None

    def load_pdf(self, file_path):
        self.doc = fitz.open(file_path)
        # Get pages immediately
        self.pages = [self.doc.load_page(page_num) for page_num in range(self.doc.page_count)]

    def get_metadata(self) -> dict:
        return {
            "number_of_pages": self.doc.page_count,
            "metadata": self.doc.metadata
        }

    def get_page(self, page_number: int):
        return self.doc.load_page(page_number)

    def save_pdf(self, output_path):
        if self.doc:
            self.doc.save(output_path)

    def get_drawings(self, page_num=None):
        if page_num is None:
            if self.drawings is None:
                self.drawings = [page.get_drawings() for page in self.pages]
            return self.drawings
        return self.pages[page_num].get_drawings()

    def get_text(self, page_num: int, rect: models.Rect):
        rect = fitz.Rect(rect.x0, rect.y0, rect.x1, rect.y1)
        return self.pages[page_num].get_textbox(rect).strip()

    def draw_rectangle(self, page_num: int, rect: models.Rect, color):
        self.pages[page_num].draw_rect(rect, color=color, fill_opacity=0.1)
