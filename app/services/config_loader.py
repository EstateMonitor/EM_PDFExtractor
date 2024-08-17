import yaml


class ConfigLoader:
    """
    Загружает конфигурационный файл YAML.
    """

    @staticmethod
    def load_config(config_path):
        # open file with encoding utf-8
        with open(config_path, 'r', encoding='utf-8') as file:
            # TODO Здесь должна быть валидация файла конфигурации
            return yaml.safe_load(file)
