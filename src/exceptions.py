from fastapi import HTTPException, status


class MainException(HTTPException):
    status_code = 500
    detail = "Неизвестная ошибка"

    def __init__(self):
        super().__init__(status_code=self.status_code, detail=self.detail)


class ObjectIsNotExistsException(MainException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Обьект не найден"


class UserAlreadyExistsException(MainException):
    status_code = status.HTTP_409_CONFLICT
    detail = "Пользователь с данным email существует"


class InvalidCredentialsException(MainException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Неверный email или пароль"


class ExpiredTokenException(MainException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Срок действия токена истёк"


class InvalidTokenException(MainException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Недействительный токен"


class PermissionDeniedException(MainException):
    status_code = status.HTTP_403_FORBIDDEN
    detail = "Недостаточно прав"


class UserNotFoundException(MainException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "User not found"


class ReportIsNotReady(MainException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Отчет еще не готов"


class UserNotActiveException(MainException):
    status_code = status.HTTP_403_FORBIDDEN
    detail = "User is not active"


class InvalidVerificationCodeException(MainException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Некорректный код подтверждения"


class EmailNotVerifiedException(MainException):
    status_code = status.HTTP_403_FORBIDDEN
    detail = "Пользователь не подтвердил email"


class AppException(Exception):
    """Базовое исключение приложения."""

    pass


class ObjectAlreadyExistsException(AppException):
    """Вызывается, когда объект уже существует."""

    pass
