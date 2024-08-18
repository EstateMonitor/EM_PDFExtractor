from abc import abstractmethod, ABC


class PDFServiceInterface(ABC):
    """
    Интерфейс для сервиса обработки PDF-файлов
    """

    @abstractmethod
    def process_lift_pdf(self, pdf_path: str, output_path=None) -> None:
        """
        Обрабатывает PDF-документ о простое лифтов и возвращает массив моделей данных.
        :param pdf_path: Путь к PDF-файлу
        :param output_path: Путь для сохранения размеченного PDF-файла (необязательный)
        :return: Массив моделей LiftCompanyReport
        """
        pass

    @abstractmethod
    def validate_pdf(self, pdf_path: str) -> None:
        """
        Проверяет наличие и корректность PDF-документа.
        :param pdf_path: Путь к PDF-файлу
        """
        pass
