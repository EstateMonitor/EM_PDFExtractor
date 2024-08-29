import pymupdf as fitz

import app.models.pdf_models as models
from app.interfaces.pdf_repository_interface import PDFRepositoryInterface
from app.models.file_model import FileModel


class PDFRepository(PDFRepositoryInterface):
    """
    Репозиторий для работы с PDF-файлами.
    Инкапсулирует работу с библиотекой PyMuPDF и предоставляет удобный интерфейс для работы с PDF.
    """

    def __init__(self):
        self.doc = None
        self.pages = None
        self.drawings = None

    def load_pdf(self, file: FileModel):
        """
        Загружает PDF-файл для дальнейшей работы в класс репозитория.

        :param file: Объект FileModel, представляющий PDF-файл.
        """
        self.doc = fitz.open(stream=file.get_content(), filetype="pdf")
        # Get pages immediately
        self.pages = [self.doc.load_page(page_num) for page_num in range(self.doc.page_count)]

    def get_sha256(self):
        """
        Возвращает SHA256 хеш PDF-файла
        :return: SHA256 хеш PDF-файла
        """
        sha256 = self.doc.get_hash("sha256")

    def save_pdf(self, output_path: str):
        """
        Сохраняет изменения в PDF-файле.

        :param output_path: Путь для сохранения PDF-файла.
        """
        self.doc.save(output_path)

    def get_num_pages(self) -> int:
        """
        Возвращает количество страниц в PDF-файле.

        :return: Количество страниц.
        """
        return self.doc.page_count

    def get_metadata(self) -> dict:
        """
        Возвращает метаданные PDF-файла (не используется в коде) #TODO реализовать сбор нужных метаданных
        :return: Метаданные PDF-файла в виде словаря
        """
        return {
            "number_of_pages": self.doc.page_count,
            "metadata": self.doc.metadata
        }

    def get_page(self, page_number: int):
        """
        Возвращает страницу PDF-файла по номеру
        :param page_number: Номер страницы
        :return: Объект страницы
        """
        return self.doc.load_page(page_number)

    def get_drawings(self, page_num=None):
        """
        Возвращает все рисунки на странице или на всех страницах
        :param page_num: Номер страницы (необязательный)
        :return: Список рисунков fitz.Drawing
        """
        if page_num is None:
            if self.drawings is None:
                self.drawings = [page.get_drawings() for page in self.pages]
            return self.drawings
        return self.pages[page_num].get_drawings()

    def get_text(self, rect: models.Rect):
        """
        Возвращает текст внутри прямоугольника на странице PDF
        :param rect: Прямоугольник с координатами и номером страницы models.Rect
        :return: Текст внутри прямоугольника
        """
        page = rect.page
        rect = fitz.Rect(rect.x0, rect.y0, rect.x1, rect.y1)
        return self.pages[page].get_textbox(rect).strip()

    def draw_rectangle(self, rect: models.Rect, color):
        """
        Рисует прямоугольник на странице PDF с указанным цветом
        :param rect: Прямоугольник с координатами и номером страницы models.Rect
        :param color: Цвет в формате (R, G, B)
        :return: None
        """
        page = rect.page
        rect = fitz.Rect(rect.x0, rect.y0, rect.x1, rect.y1)
        self.pages[page].draw_rect(rect, color=color, fill_opacity=0.1)
