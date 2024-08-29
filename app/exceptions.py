# exceptions.py

from enum import Enum


class ErrorType(Enum):
    CONFLICT_ERROR = "ConflictError"
    # Добавляем другие типы ошибок по мере необходимости


class CustomException(Exception):
    def __init__(self, error_type: ErrorType, message: str):
        self.error_type = error_type
        self.message = message
        super().__init__(self.message)


class ConflictError(CustomException):
    def __init__(self, message: str):
        super().__init__(ErrorType.CONFLICT_ERROR, message)
