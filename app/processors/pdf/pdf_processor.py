from app.processors.pdf.handlers import TableHandler, TextHandler


class PDFProcessor:
    """
    Процессор для обработки PDF-документов
    Он нужен, чтобы обрабатывать разные типы объектов в PDF-документе
    Используется в сервисном слое для обработки PDF
    Использует репозиторий для работы с PDF-документом, не зависит от способа обработки!
    Может обрабатывать любые PDF-документы,
    если есть конфигурация для обработки в которой полностью отражена структура PDF
    """

    def __init__(self, repository, config):
        """
        Процессор для обработки PDF-документов
        Иницилизируется каждый раз при обработке нового PDF
        :param repository: Репозиторий для работы с PDF-документом
        :param config: Конфигурация обработки конкретного вида PDF
        """
        self.repository = repository
        self.config = config
        # Обработчики для разных типов объектов, которые могут быть в PDF
        # У нас два типа объектов: текст и таблица
        self.handlers = {
            "text": TextHandler(self.repository),
            "table": TableHandler(self.repository)
        }

    def process_pdf(self, draw_rectangles=False):
        """
        Обработка PDF-документа по конфигурации PDF и возвращение результатов в виде словаря
        :param draw_rectangles: Рисовать ли прямоугольники вокруг обработанных объектов (для отладки)
        :return: Словарь с результатами обработки объектов
        """
        res_objects = {}
        # Обработка всех объектов в PDF по конфигурации
        for obj in self.config['pdf_structure']['objects']:
            handler = self.handlers[obj['type']]
            # Обработка объекта используя соответствующий обработчик
            result = handler.handle(obj, draw_rectangles)
            #print(f"Processed {obj['type']} named {obj['name']}: {result}")
            # Формируем словарь с результатами обработки используя имя объекта из конфига
            res_objects[obj['name']] = result
        return res_objects
