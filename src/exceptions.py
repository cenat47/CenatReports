from fastapi import HTTPException, status


# Базовые HTTP-исключения


class MainException(HTTPException):
    status_code = 500
    detail = "Неизвестная ошибка"

    def __init__(self):
        super().__init__(status_code=self.status_code, detail=self.detail)


class ObjectIsNotExistsException(MainException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Объект не найден"


class InvalidTokenException(MainException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Недействительный токен"


class ExpiredTokenException(MainException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Срок действия токена истёк"


# Регистрация, аутентификация, статус пользователя


class UserAlreadyExistsException(MainException):
    status_code = status.HTTP_409_CONFLICT
    detail = "Пользователь с данным email существует"


class WeakPasswordException(MainException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Пароль не соответствует требованиям безопасности"

    def __init__(self, detail: str = None):
        if detail:
            self.detail = detail
        super().__init__()


class InvalidCredentialsException(MainException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Неверный email или пароль"


class InvalidVerificationCodeException(MainException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Некорректный код подтверждения"


class UserNotFoundException(MainException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Пользователь не найден"


class UserNotActiveException(MainException):
    status_code = status.HTTP_403_FORBIDDEN
    detail = "Пользователь неактивен"


class EmailNotVerifiedException(MainException):
    status_code = status.HTTP_403_FORBIDDEN
    detail = "Пользователь не подтвердил email"


class IPBlockedException(MainException):
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    detail = (
        "IP-адрес временно заблокирован из-за множественных неудачных попыток входа"
    )


# Права доступа и администрирование


class PermissionDeniedException(MainException):
    status_code = status.HTTP_403_FORBIDDEN
    detail = "Недостаточно прав"


class UserSelfRoleUpdateException(MainException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Нельзя изменить роль самого себя"


# Отчёты


class TempelateIsNotExistsException(MainException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Шаблон не найден"


class ReportParametersValidationHTTPException(MainException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    detail = "Параметры не валидны"


class ReportIsNotReady(MainException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Отчёт ещё не готов, проверьте его статус"


# Базовые бизнес-исключения приложения (не HTTP)


class AppException(Exception):
    """Базовое исключение приложения."""

    pass


class ObjectAlreadyExistsException(AppException):
    """Вызывается, когда объект уже существует."""

    pass


class ReportParametersValidationException(AppException):
    """Вызывается, когда параметры отчёта не проходят валидацию."""

    pass
