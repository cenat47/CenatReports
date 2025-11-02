from datetime import date

from fastapi import HTTPException, status


class MainException(HTTPException):
    status_code = 500
    detail = "Неизвестная ошибка"

    def __init__(self):
        super().__init__(status_code=self.status_code, detail=self.detail)


class ObjectIsNotExists(MainException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Обьект не найден"

class UserAlreadyExists(MainException):
    status_code = status.HTTP_409_CONFLICT
    detail = "Пользователь с данным email существует"

class AppException(Exception):
    """Базовое исключение приложения."""
    pass

class ObjectAlreadyExistsException(AppException):
    """Вызывается, когда объект уже существует."""
    pass