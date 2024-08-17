import app.models.pdf_models as models


class TextHandler:
    """
    Обработчик текстовых блоков в PDF-документе
    """

    def __init__(self, repository):
        self.repository = repository

    def handle(self, config):
        rect = self.calculate_rect(config)
        page = config['page_number']
        text = self.repository.get_text(page, rect)
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
    Обработчик таблиц в PDF-документе
    """

    def __init__(self, repository, page: int):
        self.repository = repository
        self.page_num = page

    def handle(self, config):
        if config['method'] == 'by_pointers':
            return self.handle_by_pointers(config)
        else:
            raise ValueError(f"Unknown processing type '{config['processing_type']}'")

    def handle_by_pointers(self, config):
        # 1. Найти и отсортировать указатели блоков
        block_pointers = self.find_block_pointers(config['blocks_pointer'])

        # 2. Отсортировать строки
        block_pointers.sort(key=lambda b: b['y0'])  # Сортировка по Y

        # 3. Найти и группировать строки
        rows = self.find_rows(config['row_pointer'])
        rows.sort(key=lambda r: r.y0)  # Сортировка строк по Y
        blocks = self.group_rows_by_blocks(block_pointers, rows)

        # 4. Обработать блоки и строки
        result = []
        for block in blocks:
            block_header = self.extract_headers(config['blocks_pointer']['headers'], block['block_rect'])
            rows_headers = [self.extract_headers(config['row_pointer']['headers'], row) for row in block['rows']]
            result.append({
                "block": block_header,
                "rows": rows_headers
            })
        return result

    def find_block_pointers(self, block_config):
        block_pointers = []

        drawings = self.repository.get_drawings(self.page_num)
        for drawing in drawings:
            if self.match_drawing(drawing, block_config['criteria']):
                block_rect = self.calculate_rect(drawing, block_config)
                block_pointers.append({
                    'block_rect': block_rect,
                    'y0': block_rect.y0  # Для сортировки по оси Y
                })
        if len(block_pointers) != 1 and block_config['multiple'] is False:
            raise ValueError(f"Expected 1 drawing, got {len(drawings)}")
        return block_pointers

    def find_rows(self, row_pointer_config):
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
            # Определяем границы для строк текущего блока
            block_top = block['y0']
            block_bottom = block_pointers[i + 1]['y0'] if i + 1 < len(block_pointers) else float('inf')

            block_rows = [row for row in rows if block_top <= row.y0 < block_bottom]
            blocks.append({
                'block_rect': block['block_rect'],
                'rows': block_rows
            })
        return blocks

    def extract_headers(self, header_config, rect: models.Rect):
        data = {}
        x0 = rect.x0
        for header_name, width in zip(header_config['names'], header_config['column_widths']):
            cell_rect = models.Rect(x0, rect.y0, x0 + width, rect.y1)
            data[header_name] = self.repository.get_text(self.page_num, cell_rect)
            x0 += width
        return data

    @staticmethod
    def match_drawing(drawing, criteria: dict, inaccuracy=0.1):
        valid = True
        for criterion, criterion_value in criteria.items():
            if criterion == 'height':
                valid = valid and abs(drawing['rect'].height - criterion_value) < inaccuracy
            elif criterion == 'width':
                valid = valid and abs(drawing['rect'].width - criterion_value) < inaccuracy
            else:
                raise ValueError(f"Unknown criterion '{criterion}'")
        return valid

    @staticmethod
    def calculate_rect(drawing, config) -> models.Rect:
        return models.Rect(drawing['rect'].x0 + config['offset']['x'],
                           drawing['rect'].y0 + config['offset']['y'],
                           drawing['rect'].x0 + config['offset']['x'] + config['dimensions']['width'],
                           drawing['rect'].y0 + config['offset']['y'] + config['dimensions']['height'])

    def get_block_headers(self, block_config, block_rect) -> list[str]:
        headers = []
        offset = 0
        for header_name, width in zip(block_config['headers']['names'],
                                      block_config['headers']['column_widths']):
            header_rect = models.Rect(block_rect.x0 + offset,
                                      block_rect.y0,
                                      block_rect.x0 + width + offset,
                                      block_rect.y1)
            offset += width
            headers.append(self.repository.get_text(self.page_num, header_rect))
        return headers
