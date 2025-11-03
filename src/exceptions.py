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

class InvalidCredentials(MainException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Неверный email или пароль"

class ExpiredTokenException(MainException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Срок действия токена истёк"

class InvalidTokenException(MainException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Недействительный токен"

class UserNotFoundExc(MainException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "User not found"

class UserNotActiveExc(MainException):
    status_code = status.HTTP_403_FORBIDDEN
    detail = "User is not active"


class AppException(Exception):
    """Базовое исключение приложения."""
    pass

class ObjectAlreadyExistsException(AppException):
    """Вызывается, когда объект уже существует."""
    pass