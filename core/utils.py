import re


def normalize_email(email: str) -> str:
    """Lowercase and strip whitespace from email."""
    return email.lower().strip()


def is_valid_phone(phone: str) -> bool:
    """Simple E.164-ish phone validator."""
    pattern = re.compile(r"^\+?[1-9]\d{7,14}$")
    return bool(pattern.match(phone))
