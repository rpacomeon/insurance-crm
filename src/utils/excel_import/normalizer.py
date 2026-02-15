import re

from .types import CustomerKey


def normalize_phone(phone: str) -> str:
    value = str(phone or "").strip()
    return re.sub(r"[^0-9]", "", value)


def normalize_name(name: str) -> str:
    value = str(name or "").strip()
    return " ".join(value.split())


def build_customer_key(name: str, phone: str) -> CustomerKey:
    return CustomerKey(
        normalized_phone=normalize_phone(phone),
        normalized_name=normalize_name(name),
    )

