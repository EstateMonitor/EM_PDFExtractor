import app.models.pdf_models as models


class TextHandler:
    """
    Обработчик текстовых блоков в PDF-документе
    """

    def __init__(self, repository):
        self.repository = repository

    def handle(self, config, draw_rectangles: bool):
        rect = self.calculate_rect(config)
        page = config['page_number']
        text = self.repository.get_text(page, rect)
        if draw_rectangles:
            self.repository.draw_rectangle(page, rect, color=(0, 0, 1))
        return text

    @staticmethod
    def calculate_rect(config):
        x = config['offset']['x']
        y = config['offset']['y']
        width = config['dimensions']['width']
        height = config['dimensions']['height']
        return models.Rect(x, y, x + width, y + height)


class TableHandler:
    """
    Обработчик таблиц в PDF-документе.
    """

    def __init__(self, repository, page_num=0):
        self.repository = repository
        self.page_num = page_num

    def handle(self, config, draw_rectangles: bool):
        if config['method'] == 'by_pointers':
            return self.handle_by_pointers(config, draw_rectangles)
        else:
            raise ValueError(f"Unknown processing type '{config['method']}'")

    def handle_by_pointers(self, config, draw_rectangles: bool):
        # 1. Найти и отсортировать указатели блоков
        block_pointers = self.find_block_pointers(config['blocks_pointer'])
        block_pointers.sort(key=lambda b: b.y0)  # Сортировка по Y

        # 2. Найти и сортировать строки
        rows = self.find_rows(config['row_pointer'])
        rows.sort(key=lambda r: r.y0)  # Сортировка строк по Y

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
        drawings = self.repository.get_drawings(self.page_num)
        for drawing in drawings:
            if self.match_drawing(drawing, block_config['criteria']):
                block_rect = self.calculate_rect(drawing, block_config)
                block_pointers.append(block_rect)
        return block_pointers

    def find_rows(self, row_pointer_config) -> list[models.Rect]:
        rows = []
        drawings = self.repository.get_drawings(self.page_num)
        for drawing in drawings:
            if self.match_drawing(drawing, row_pointer_config['criteria']):
                row_rect = self.calculate_rect(drawing, row_pointer_config)
                rows.append(row_rect)
        return rows

    @staticmethod
    def group_rows_by_blocks(block_pointers, rows):
        blocks = []
        for i, block in enumerate(block_pointers):
            block_top = block.y0
            block_bottom = block_pointers[i + 1].y0 if i + 1 < len(block_pointers) else float('inf')

            block_rows = [row for row in rows if block_top <= row.y0 < block_bottom]
            blocks.append({
                'block_rect': block,
                'rows': block_rows
            })
        return blocks

    def extract_data_from_rect(self, header_config, rect: models.Rect, draw_rectangles: bool):
        data = {}
        x0 = rect.x0
        for header_name, width in zip(header_config['names'], header_config['column_widths']):
            cell_rect = models.Rect(x0, rect.y0, x0 + width, rect.y1)
            data[header_name] = self.repository.get_text(self.page_num, cell_rect)
            x0 += width
            if draw_rectangles:
                self.repository.draw_rectangle(self.page_num, cell_rect, color=(0, 1, 0))
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
    def calculate_rect(drawing, config) -> models.Rect:
        return models.Rect(drawing['rect'].x0 + config['offset']['x'],
                           drawing['rect'].y0 + config['offset']['y'],
                           drawing['rect'].x0 + config['offset']['x'] + config['dimensions']['width'],
                           drawing['rect'].y0 + config['offset']['y'] + config['dimensions']['height'])
