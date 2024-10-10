from app.processors.pdf.handlers import TableHandler, TextHandler


class PDFProcessor:
    """
    Процессор для обработки PDF-документов.
    Использует репозиторий для работы с PDF-документом, не зависит от способа обработки.
    Может обрабатывать любые PDF-документы, если есть конфигурация, в которой полностью отражена структура PDF.
    """

    def __init__(self, repository, config):
        """
        Инициализация процессора для обработки PDF-документов.
        :param repository: Репозиторий для работы с PDF-документом.
        :param config: Конфигурация обработки конкретного вида PDF.
        """
        self.repository = repository
        self.config = config
        # Обработчики для разных типов объектов, которые могут быть в PDF
        self.handlers = {
            "text": TextHandler(self.repository),
            "table": TableHandler(self.repository)
        }

    def process_pdf(self, draw_rectangles=False):
        """
        Обработка PDF-документа по конфигурации и возвращение результатов в виде словаря.
        :param draw_rectangles: Рисовать ли прямоугольники вокруг обработанных объектов (для отладки).
        :return: Словарь с результатами обработки объектов.
        """
        res_objects = {}
        # Обработка всех объектов в PDF по конфигурации
        for obj in self.config['pdf_structure']['objects']:
            handler = self.handlers[obj['type']]
            # Обработка объекта используя соответствующий обработчик
            result = handler.handle(obj, draw_rectangles)

            # Если результат — словарь, добавляем все элементы в итоговый результат
            if isinstance(result, dict):
                res_objects.update(result)
            else:
                # Иначе сохраняем результат под именем из конфига
                res_objects[obj['name']] = result

        return res_objects
