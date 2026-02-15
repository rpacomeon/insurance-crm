from typing import Dict, List

from .normalizer import normalize_name, normalize_phone
from .types import ImportErrorDetail

ALLOWED_PAYMENT_METHODS = {"", "계좌이체", "신용카드", "자동이체"}
ALLOWED_DRIVING_TYPES = {"", "none", "personal", "commercial"}


def validate_customer_row(row: Dict[str, str], sheet_name: str = "customers") -> List[ImportErrorDetail]:
    row_no = int(row.get("__row_number", 0) or 0)
    errors: List[ImportErrorDetail] = []

    name = normalize_name(row.get("name", ""))
    phone = normalize_phone(row.get("phone", ""))
    payment_method = (row.get("payment_method", "") or "").strip()
    driving_type = (row.get("driving_type", "") or "").strip()

    if not name:
        errors.append(
            ImportErrorDetail(
                sheet=sheet_name,
                row=row_no,
                column="name",
                error_code="E101",
                message="name is required",
                action_hint="고객 이름을 입력하세요",
            )
        )

    if not phone:
        errors.append(
            ImportErrorDetail(
                sheet=sheet_name,
                row=row_no,
                column="phone",
                error_code="E102",
                message="phone is required",
                action_hint="전화번호를 입력하세요",
            )
        )
    elif len(phone) not in (10, 11):
        errors.append(
            ImportErrorDetail(
                sheet=sheet_name,
                row=row_no,
                column="phone",
                error_code="E103",
                message="invalid phone format",
                value=row.get("phone", ""),
                action_hint="01012345678 형태로 입력하세요",
            )
        )

    if payment_method not in ALLOWED_PAYMENT_METHODS:
        errors.append(
            ImportErrorDetail(
                sheet=sheet_name,
                row=row_no,
                column="payment_method",
                error_code="E104",
                message="invalid payment_method",
                value=payment_method,
                action_hint="계좌이체/신용카드/자동이체 중 선택하세요",
            )
        )

    if driving_type not in ALLOWED_DRIVING_TYPES:
        errors.append(
            ImportErrorDetail(
                sheet=sheet_name,
                row=row_no,
                column="driving_type",
                error_code="E105",
                message="invalid driving_type",
                value=driving_type,
                action_hint="none/personal/commercial 중 선택하세요",
            )
        )

    return errors

