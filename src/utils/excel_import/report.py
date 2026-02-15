import csv
from typing import List, Optional, Tuple

from .types import ImportErrorDetail


def export_error_report(
    errors: List[ImportErrorDetail],
    skips: List[ImportErrorDetail],
    file_path: str,
) -> Tuple[bool, Optional[str]]:
    try:
        with open(file_path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(["type", "sheet", "row", "column", "error_code", "message", "value", "action_hint"])

            for detail in errors:
                writer.writerow(
                    [
                        "ERROR",
                        detail.sheet,
                        detail.row,
                        detail.column,
                        detail.error_code,
                        detail.message,
                        detail.value,
                        detail.action_hint,
                    ]
                )

            for detail in skips:
                writer.writerow(
                    [
                        "SKIP",
                        detail.sheet,
                        detail.row,
                        detail.column,
                        detail.error_code,
                        detail.message,
                        detail.value,
                        detail.action_hint,
                    ]
                )
        return True, None
    except Exception as e:
        return False, str(e)

