import app.models.pdf_models as models


class TextHandler:
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
    def __init__(self, repository):
        self.repository = repository

    def handle(self, config):
        headers = self.extract_headers(config['headers'])
        rows = self.extract_rows(config['row_pointers'])
        return {"headers": headers, "rows": rows}

    def extract_headers(self, header_configs, page):
        headers = []
        for header_config in header_configs:
            rect = self.calculate_rect(header_config)
            headers.append(self.repository.get_text(page, rect))
        return headers

    def extract_rows(self, row_pointer_configs, page):
        rows = []
        for row_pointer_config in row_pointer_configs:
            drawings = self.repository.get_drawings(page)
            for drawing in drawings:
                if self.match_drawing(drawing, row_pointer_config):
                    row_rect = self.calculate_rect(row_pointer_config)
                    rows.append(self.repository.get_text(page, row_rect))
        return rows

    def match_drawing(self, drawing, config):
        return drawing['rect'].height == config['pointer']['criteria']['height']

    def calculate_rect(self, config):
        x = config['position_offset']['x']
        y = config['position_offset']['y']
        width = config['dimensions']['width']
        height = config['dimensions']['height']
        return models.Rect(x, y, x + width, y + height)

    def calculate_table_rect(self, headers, rows):
        first_row_rect = rows[0]['rect'] if rows else models.Rect(0, 0, 0, 0)
        last_row_rect = rows[-1]['rect'] if rows else models.Rect(0, 0, 0, 0)
        table_rect = models.Rect(first_row_rect.x0, first_row_rect.y0, last_row_rect.x1, last_row_rect.y1)
        return table_rect
