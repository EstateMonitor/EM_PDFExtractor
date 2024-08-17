from app.processors.pdf.handlers import TableHandler, TextHandler


class PDFProcessor:
    def __init__(self, repository, config):
        self.repository = repository
        self.config = config
        self.handlers = {
            "text": TextHandler(self.repository),
            "table": TableHandler(self.repository)
        }

    def process_pdf(self, draw_rectangles=False):
        for obj in self.config['pdf_structure']['objects']:
            handler = self.handlers[obj['type']]
            result = handler.handle(obj, draw_rectangles)
            print(f"Processed {obj['type']} named {obj['name']}: {result}")
