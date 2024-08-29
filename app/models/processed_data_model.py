# models/processed_data_model.py

from typing import List

from pydantic import BaseModel


class ProcessedDataModel(BaseModel):
    """
    Модель данных для отправки обработанных данных на другой микросервис.
    """
    filename: str  # Имя файла
    file_sha256: str  # SHA256 хеш файла
    report_time: str  # Время из отчёта
    companies: List[dict]  # Пример структуры данн
