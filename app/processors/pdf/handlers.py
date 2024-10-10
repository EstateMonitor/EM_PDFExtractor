import re

import app.models.pdf_models as models


class TextHandler:
    """
    Обработчик текстовых блоков в PDF-документе.
    Нужен для извлечения текста или нескольких значений с использованием регулярных выражений.
    """

    def __init__(self, repository):
        self.repository = repository

    def handle(self, config, draw_rectangles: bool):
        """
        Обработка текстового поля в PDF-документе по конфигурации.
        :param config: Конфигурация обработки текстового поля.
        :param draw_rectangles: Рисовать ли прямоугольник вокруг обработанного текста (для отладки).
        :return: Словарь с несколькими значениями, если используется массив регулярных выражений.
        """
        # Вычисляем прямоугольную область для извлечения текста
        rect = self.calculate_rect(config, config['page_number'])
        text = self.repository.get_text(rect)

        if draw_rectangles:
            self.repository.draw_rectangle(rect, color=(0, 0, 1))

        # Проверяем, есть ли поле patterns для использования нескольких регулярных выражений
        if 'patterns' in config:
            return self.extract_with_multiple_patterns(config['patterns'], text)

        # Если есть только одиночное имя, возвращаем текст с этим именем
        return {config['name']: text}

    @staticmethod
    def extract_with_multiple_patterns(patterns, text):
        """
        Применяет массив регулярных выражений для выделения значений.
        :param patterns: Список регулярных выражений и целевых полей.
        :param text: Исходный текст из PDF для обработки.
        :return: Словарь с извлечёнными значениями.
        """
        extracted_data = {}

        for pattern_config in patterns:
            target = pattern_config['target']
            raw_pattern = pattern_config['regex']
            regex_pattern = raw_pattern.replace("\\\\", "\\")  # Преобразуем регулярное выражение
            match = re.search(regex_pattern, text)

            if match:
                # Добавляем совпавшую группу в словарь с именем из target
                extracted_data[target] = match.group(1).strip()
            else:
                extracted_data[target] = None  # Если нет совпадения, возвращаем None

        return extracted_data

    @staticmethod
    def calculate_rect(config, page):
        """
        Вычисление прямоугольника по конфигурации и номеру страницы.
        :param config: Конфигурация обработки текстового поля.
        :param page: Номер страницы.
        :return: Прямоугольник models.Rect.
        """
        x = config['offset']['x']
        y = config['offset']['y']
        width = config['dimensions']['width']
        height = config['dimensions']['height']
        return models.Rect(x, y, x + width, y + height, page)


class TableHandler:
    """
    Обработчик таблиц в PDF-документе.
    Нужен для извлечения данных из таблицы, может использовать разные методы обработки
    Реализован только один, но оставлена возможность добавления других методов
    """

    def __init__(self, repository):
        self.repository = repository

    def handle(self, config, draw_rectangles: bool):
        """
        Обработка таблицы в PDF-документе по конфигурации
        :param config: Конфигурация обработки таблицы
        :param draw_rectangles: Рисовать ли прямоугольники вокруг обработанных объектов (для отладки)
        :return: Список словарей с данными из таблицы
        """
        if config['method'] == 'by_pointers':  # Обработка таблицы по указателям, единственный метод пока-что
            return self.handle_by_pointers(config, draw_rectangles)
        else:
            raise ValueError(f"Unknown processing type '{config['method']}'")

    def handle_by_pointers(self, config, draw_rectangles: bool):
        """
        Обработка таблицы по указателям блоков и строк
        Использует указатели блоков и строк для обработки таблицы
        Указателями могут быть любой вид объектов в PDF, которые можно найти по признакам
        :param config: Конфигурация обработки таблицы
        :param draw_rectangles: Рисовать ли прямоугольники вокруг обработанных объектов (для отладки)
        :return: Список словарей с данными из таблицы
        """
        # 1. Найти и отсортировать указатели блоков на всех страницах
        # ( Блоками мы называем части таблицы, которые имеют собственный заголовок и строки с данными )
        # ( В нашем случае с лифтами заголовок блока это просто название компании,
        # но тут может быть что угодно, метод универсальный )

        block_pointers = self.find_block_pointers(config['blocks_pointer'])
        block_pointers.sort(key=lambda b: (b.page, b.y0))  # Сортировка по странице и координате Y
        # При чём сортировка по странице более приоритетна, чтобы сначала шли блоки с одной страницы

        # 2. Найти и сортировать строки на всех страницах
        rows = self.find_rows(config['row_pointer'])
        rows.sort(key=lambda r: (r.page, r.y0))  # Сортировка строк по странице и координате Y

        # 3. Группировка строк по блокам
        blocks = self.group_rows_by_blocks(block_pointers, rows)

        # 4. Обработать блоки и строки
        result = []
        for block in blocks:
            block_header = self.extract_data_from_rect(config['blocks_pointer']['headers'], block['block_rect'],
                                                       draw_rectangles)
            rows_headers = [self.extract_data_from_rect(config['row_pointer']['headers'], row, draw_rectangles) for row
                            in block['rows']]
            result.append({
                "block": block_header,
                "rows": rows_headers
            })
        return result

    def find_block_pointers(self, block_config) -> list[models.Rect]:
        """
        Находит указатели блоков на всех страницах
        :param block_config:
        :return:
        """
        block_pointers = []
        num_pages = self.repository.get_num_pages()
        for page_num in range(num_pages):
            # Получаем все рисунки на странице
            drawings = self.repository.get_drawings(page_num)
            for drawing in drawings:
                # Проверяем, что рисунок соответствует критериям
                if self.match_drawing(drawing, block_config['criteria']):
                    # Мы сохраняем полную координату прямоугольника, то есть включая ширину, высоту и номер страницы
                    block_rect = self.calculate_rect(drawing, block_config, page_num)
                    block_pointers.append(block_rect)
        return block_pointers

    def find_rows(self, row_pointer_config) -> list[models.Rect]:
        """
        Находит строки на всех страницах по указателям
        :param row_pointer_config: Конфигурация указателей строк
        :return: Список прямоугольников строк models.Rect
        """
        # Тут всё ровно так же, как и с блоками, только с другими критериями
        rows = []
        num_pages = self.repository.get_num_pages()
        for page_num in range(num_pages):
            drawings = self.repository.get_drawings(page_num)
            for drawing in drawings:
                if self.match_drawing(drawing, row_pointer_config['criteria']):
                    row_rect = self.calculate_rect(drawing, row_pointer_config, page_num)
                    rows.append(row_rect)
        return rows

    @staticmethod
    def group_rows_by_blocks(block_pointers, rows):
        """
        Группирует строки по блокам, используя их положение на странице
        Самый сложный метод
        :param block_pointers: Все блоки на всех страницах
        :param rows: Все строки на всех страницах
        :return: Список блоков с принадлежащими им строками
        """
        blocks = []
        row_index = 0  # Индекс текущей строки

        for i, block in enumerate(block_pointers):  # Проходим по всем блокам
            current_block = block
            # Следующий блок, если он есть
            next_block = block_pointers[i + 1] if i + 1 < len(block_pointers) else None
            # Строки, принадлежащие текущему блоку
            block_rows = []

            while row_index < len(rows):  # Проходим по всем строкам
                row = rows[row_index]  # Текущая строка

                # Проверяем, находится ли строка на той же странице, что и блок
                if row.page == current_block.page:
                    # Строка принадлежит текущему блоку, если она находится между текущим блоком и следующим блоком
                    # Но если следующий блок не на той же странице, то строка принадлежит текущему блоку в любом случае
                    if current_block.y0 <= row.y0 < (
                            next_block.y0 if next_block and row.page == next_block.page else float('inf')):
                        block_rows.append(row)
                        row_index += 1  # Сокращаем список строк, чтобы не обрабатывать их повторно
                    else:
                        break  # Строка находится за пределами текущего блока, переход к следующему блоку

                # Если строка на следующей странице после текущего блока...
                elif row.page > current_block.page:
                    # ...и она выше следующего блока на этой странице, значит она принадлежит текущему блоку
                    if not next_block or row.y0 < next_block.y0:
                        block_rows.append(row)
                        row_index += 1  # Сокращаем список строк, чтобы не обрабатывать их повторно
                    else:
                        break  # Строка относится к следующему блоку

                else:
                    row_index += 1  # Строка уже обработана, переходим к следующей

            # Прошлись по всем строкам, принадлежащим текущему блоку. Упаковываем их в блок
            blocks.append({
                'block_rect': current_block,
                'rows': block_rows
            })

        return blocks

    def extract_data_from_rect(self, header_config, rect: models.Rect, draw_rectangles: bool):
        """
        Извлекает данные из прямоугольника на странице, !используется как для блоков, так и для строк!
        :param header_config: Конфигурация заголовков столбцов
        :param rect: Прямоугольник с данными
        :param draw_rectangles: Рисовать ли прямоугольники вокруг обработанных объектов (для отладки)
        :return: Словарь с данными из прямоугольника
        """
        data = {}
        x0 = rect.x0
        for header_name, width in zip(header_config['names'], header_config['column_widths']):
            cell_rect = models.Rect(x0, rect.y0, x0 + width, rect.y1, rect.page)
            data[header_name] = self.repository.get_text(cell_rect)
            x0 += width
            if draw_rectangles:
                self.repository.draw_rectangle(cell_rect, color=(0, 1, 0))
        return data

    @staticmethod
    def match_drawing(drawing, criteria: dict, inaccuracy=0.1):
        """
        Проверяет, соответствует ли рисунок критериям указанным в конфигурации
        Можно реализовать любые критерии для поиска, например, по размеру, цвету, шрифту и т.д.
        Пока-что реализовано только сравнение размеров, их хватает для нашей задачи
        :param drawing: Рисунок fitz.Drawing
        :param criteria: Критерии для сравнения
        :param inaccuracy: Допустимая погрешность для сравнения размеров
        :return: True, если рисунок соответствует критериям, иначе False
        """
        for criterion, criterion_value in criteria.items():
            if criterion == 'height':
                if not abs(drawing['rect'].height - criterion_value) < inaccuracy:
                    return False
            elif criterion == 'width':
                if not abs(drawing['rect'].width - criterion_value) < inaccuracy:
                    return False
            else:
                raise ValueError(f"Unknown criterion '{criterion}'")
        return True

    @staticmethod
    def calculate_rect(drawing, config, page_num) -> models.Rect:
        """
        Вычисляет прямоугольник по рисунку и конфигурации
        Нужен для того, чтобы учесть смещение и размеры прямоугольника
        :param drawing: Рисунок fitz.Drawing
        :param config: Конфигурация обработки
        :param page_num: Номер страницы
        :return: Прямоугольник models.Rect
        """
        return models.Rect(
            x0=drawing['rect'].x0 + config['offset']['x'],
            y0=drawing['rect'].y0 + config['offset']['y'],
            x1=drawing['rect'].x0 + config['offset']['x'] + config['dimensions']['width'],
            y1=drawing['rect'].y0 + config['offset']['y'] + config['dimensions']['height'],
            page=page_num
        )
