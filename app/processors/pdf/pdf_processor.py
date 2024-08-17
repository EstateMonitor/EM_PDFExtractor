from app.processors.pdf.handlers import TableHandler, TextHandler


class PDFProcessor:
    def __init__(self, repository, config_loader):
        self.repository = repository
        self.config_loader = config_loader
        self.handlers = {
            "text": TextHandler(self.repository),
            "table": TableHandler(self.repository,0)
        }

    def process_pdf(self, repo, config):

        for obj in config['pdf_structure']['objects']:
            handler = self.handlers[obj['type']]
            result = handler.handle(obj)
            print(f"Processed {obj['type']} named {obj['name']}: {result}")
