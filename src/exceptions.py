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