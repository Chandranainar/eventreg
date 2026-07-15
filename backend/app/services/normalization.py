import re

from app.core.error import ApiError


def normalise_email(value: str) -> str:
    return value.strip().lower()


def normalise_phone(value: str) -> str:
    digits = re.sub(r"\D", "", value.strip())
    if len(digits) == 12 and digits.startswith("91"):
        digits = digits[2:]
    elif len(digits) == 11 and digits.startswith("0"):
        digits = digits[1:]
    if len(digits) != 10 or digits[0] not in {"6", "7", "8", "9"}:
        raise ApiError(422, "INVALID_PHONE", "Please enter a valid Indian mobile number.")
    return digits
