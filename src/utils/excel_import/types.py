from dataclasses import dataclass, field
from typing import List, Optional


@dataclass(frozen=True)
class CustomerKey:
    normalized_phone: str
    normalized_name: str

    @property
    def value(self) -> str:
        return f"{self.normalized_phone}|{self.normalized_name}"


@dataclass
class ImportErrorDetail:
    sheet: str
    row: int
    column: str
    error_code: str
    message: str
    value: str = ""
    action_hint: str = ""


@dataclass
class ImportRowResult:
    status: str  # success / skip / fail
    row: int
    key: str
    customer_id: Optional[int] = None
    reason_code: str = ""
    reason_message: str = ""


@dataclass
class ImportSummary:
    total_rows: int = 0
    success_count: int = 0
    skip_count: int = 0
    fail_count: int = 0
    results: List[ImportRowResult] = field(default_factory=list)
    errors: List[ImportErrorDetail] = field(default_factory=list)
    skips: List[ImportErrorDetail] = field(default_factory=list)

