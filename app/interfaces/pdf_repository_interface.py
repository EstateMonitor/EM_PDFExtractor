from abc import ABC, abstractmethod


class PDFRepositoryInterface(ABC):
    """
    Интерфейс для репозитория работы с PDF-файлами
    """

    @abstractmethod
    def get_num_pages(self) -> int:
        """
        Возвращает количество страниц в PDF-файле
        :return: Количество страниц
        """
        pass

    @abstractmethod
    def load_pdf(self, file_path):
        """
        Загружает PDF-файл для дальнейшей работы в класс репозитория
        :param file_path: Путь к PDF-файлу
        """
        pass

    @abstractmethod
    def get_page(self, page_num):
        """
        Возвращает страницу PDF-файла по номеру
        :param page_num: Номер страницы
        :return: Объект страницы
        """
        pass

    @abstractmethod
    def save_pdf(self, output_path):
        """
        Сохраняет PDF-файл в новый файл по указанному пути
        :param output_path: Путь для сохранения PDF-файла
        """
        pass

    @abstractmethod
    def get_drawings(self, page_num):
        """
        Возвращает все рисунки на странице
        :param page_num: Номер страницы
        :return: Список рисунков fitz.Drawing
        """
        pass

    @abstractmethod
    def get_text(self, rect):
        """
        Возвращает текст внутри прямоугольника на странице PDF
        :param rect: Прямоугольник с координатами и номером страницы models.Rect
        :return: Текст внутри прямоугольника
        """
        pass

    @abstractmethod
    def draw_rectangle(self, rect, color):
        """
        Рисует прямоугольник на странице PDF с указанным цветом
        :param rect: Прямоугольник с координатами и номером страницы models.Rect
        :param color: Цвет в формате RGB (0, 0, 0)
        """
        pass
