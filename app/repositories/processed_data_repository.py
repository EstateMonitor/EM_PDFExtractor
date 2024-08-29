# repositories/processed_data_repository.py

import httpx

from app.exceptions import ConflictError
from app.models.processed_data_model import ProcessedDataModel


class ProcessedDataRepository:
    """
    Репозиторий для отправки обработанных данных на другой микросервис.
    """

    def __init__(self):
        """
        Инициализация репозитория для отправки обработанных данных на другой микросервис.
        """
        pass

    @staticmethod
    async def send_processed_data(data: ProcessedDataModel, endpoint: str) -> dict:
        """
        Асинхронно отправляет обработанные данные на другой микросервис.

        :param endpoint: Конечная точка целевого микросервиса.
        :param data: Объект ProcessedDataModel, содержащий данные для отправки.
        :return: Ответ от целевого микросервиса.
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(endpoint, json=data.dict())
                response.raise_for_status()
                return response.json()
            except httpx.RequestError as exc:
                print(f"An error occurred while requesting {exc.request.url!r}: {exc}")
                raise
            except httpx.HTTPStatusError as exc:
                if exc.response.status_code == 409:  # Обработка конфликта
                    raise ConflictError(exc.response.text)
                print(f"Error response {exc.response.status_code} while requesting {exc.request.url!r}: {exc}")
                raise
