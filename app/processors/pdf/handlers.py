import app.models.pdf_models as models


class TextHandler:
    """
    Обработчик текстовых блоков в PDF-документе
    """

    def __init__(self, repository):
        self.repository = repository

    def handle(self, config, draw_rectangles: bool):
        rect = self.calculate_rect(config, config['page_number'])
        text = self.repository.get_text(rect)
        if draw_rectangles:
            self.repository.draw_rectangle(rect, color=(0, 0, 1))
        return text

    @staticmethod
    def calculate_rect(config, page):
        x = config['offset']['x']
        y = config['offset']['y']
        width = config['dimensions']['width']
        height = config['dimensions']['height']
        return models.Rect(x, y, x + width, y + height, page)


class TableHandler:
    """
    Обработчик таблиц в PDF-документе.
    """

    def __init__(self, repository):
        self.repository = repository

    def handle(self, config, draw_rectangles: bool):
        if config['method'] == 'by_pointers':
            return self.handle_by_pointers(config, draw_rectangles)
        else:
            raise ValueError(f"Unknown processing type '{config['method']}'")

    def handle_by_pointers(self, config, draw_rectangles: bool):
        # 1. Найти и отсортировать указатели блоков на всех страницах
        block_pointers = self.find_block_pointers(config['blocks_pointer'])
        block_pointers.sort(key=lambda b: (b.page, b.y0))  # Сортировка по странице и координате Y

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
        block_pointers = []
        num_pages = self.repository.get_num_pages()
        for page_num in range(num_pages):
            drawings = self.repository.get_drawings(page_num)
            for drawing in drawings:
                if self.match_drawing(drawing, block_config['criteria']):
                    block_rect = self.calculate_rect(drawing, block_config, page_num)
                    block_pointers.append(block_rect)
        return block_pointers

    def find_rows(self, row_pointer_config) -> list[models.Rect]:
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
        blocks = []
        row_index = 0  # Индекс текущей строки

        for i, block in enumerate(block_pointers):  # Проходим по всем блокам
            current_block = block
            next_block = block_pointers[i + 1] if i + 1 < len(block_pointers) else None

            block_rows = []

            while row_index < len(rows):
                row = rows[row_index]

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
        return models.Rect(
            x0=drawing['rect'].x0 + config['offset']['x'],
            y0=drawing['rect'].y0 + config['offset']['y'],
            x1=drawing['rect'].x0 + config['offset']['x'] + config['dimensions']['width'],
            y1=drawing['rect'].y0 + config['offset']['y'] + config['dimensions']['height'],
            page=page_num
        )
