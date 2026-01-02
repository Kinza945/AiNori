from cryptography.fernet import Fernet, InvalidToken

from config import settings


def _get_fernet() -> Fernet:
    return Fernet(settings.encryption_secret)


def encrypt(value: str) -> str:
    fernet = _get_fernet()
    token = fernet.encrypt(value.encode("utf-8"))
    return token.decode("utf-8")


def decrypt(value: str) -> str:
    fernet = _get_fernet()
    try:
        decrypted = fernet.decrypt(value.encode("utf-8"))
    except InvalidToken as exc:  # pragma: no cover - runtime safety
        raise ValueError("Не удалось расшифровать значение") from exc
    return decrypted.decode("utf-8")
