from passlib.context import CryptContext
import re

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def is_valid_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def validate_password_strength(password: str) -> tuple[bool, str | None]:
    if not password.isascii():
        return (
            False,
            "Пароль должен содержать только латинские буквы, цифры и спецсимволы",
        )
    if len(password) < 8:
        return False, "Пароль должен быть минимум 8 символов"

    if not re.search(r"[A-Z]", password):
        return False, "Пароль должен содержать заглавную латинскую букву"

    if not re.search(r"[a-z]", password):
        return False, "Пароль должен содержать строчную латинскую букву"

    if not re.search(r"\d", password):
        return False, "Пароль должен содержать цифру"

    return True, None
