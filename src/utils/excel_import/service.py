from typing import Dict, Set

from models import Customer

from .normalizer import build_customer_key, normalize_name, normalize_phone
from .reader import read_customers_sheet
from .types import ImportErrorDetail, ImportRowResult, ImportSummary
from .validator import validate_customer_row


class CustomerExcelImportService:
    def __init__(self, db_manager):
        self.db = db_manager

    def preview_import(self, file_path: str) -> ImportSummary:
        return self._process(file_path=file_path, commit=False)

    def commit_import(self, file_path: str) -> ImportSummary:
        return self._process(file_path=file_path, commit=True)

    def _process(self, file_path: str, commit: bool) -> ImportSummary:
        summary = ImportSummary()
        rows, read_errors = read_customers_sheet(file_path)
        summary.total_rows = len(rows)

        if read_errors:
            summary.errors.extend(read_errors)
            summary.fail_count = len(read_errors)
            return summary

        existing_customers = self.db.get_all_customers()
        existing_keys: Set[str] = set()
        existing_phone_to_name: Dict[str, str] = {}
        for customer in existing_customers:
            key = build_customer_key(customer.name, customer.phone).value
            existing_keys.add(key)
            existing_phone_to_name[normalize_phone(customer.phone)] = normalize_name(customer.name)

        seen_file_keys: Set[str] = set()

        for row in rows:
            row_no = int(row.get("__row_number", 0) or 0)
            row_errors = validate_customer_row(row)
            if row_errors:
                summary.errors.extend(row_errors)
                summary.results.append(
                    ImportRowResult(
                        status="fail",
                        row=row_no,
                        key="",
                        reason_code=row_errors[0].error_code,
                        reason_message=row_errors[0].message,
                    )
                )
                summary.fail_count += 1
                continue

            key = build_customer_key(row.get("name", ""), row.get("phone", "")).value
            phone = normalize_phone(row.get("phone", ""))
            name = normalize_name(row.get("name", ""))

            if key in seen_file_keys:
                detail = ImportErrorDetail(
                    sheet="customers",
                    row=row_no,
                    column="phone+name",
                    error_code="E201",
                    message="duplicate key inside file",
                    value=key,
                    action_hint="동일 고객행을 하나만 남겨주세요",
                )
                summary.errors.append(detail)
                summary.results.append(
                    ImportRowResult(
                        status="fail",
                        row=row_no,
                        key=key,
                        reason_code=detail.error_code,
                        reason_message=detail.message,
                    )
                )
                summary.fail_count += 1
                continue
            seen_file_keys.add(key)

            if phone in existing_phone_to_name and existing_phone_to_name[phone] != name:
                detail = ImportErrorDetail(
                    sheet="customers",
                    row=row_no,
                    column="phone",
                    error_code="E106",
                    message="phone already exists with different name",
                    value=row.get("phone", ""),
                    action_hint="기존 고객명과 전화번호 조합을 확인하세요",
                )
                summary.errors.append(detail)
                summary.results.append(
                    ImportRowResult(
                        status="fail",
                        row=row_no,
                        key=key,
                        reason_code=detail.error_code,
                        reason_message=detail.message,
                    )
                )
                summary.fail_count += 1
                continue

            if key in existing_keys:
                skip_detail = ImportErrorDetail(
                    sheet="customers",
                    row=row_no,
                    column="phone+name",
                    error_code="E202",
                    message="existing customer kept as-is",
                    value=key,
                    action_hint="기존 고객은 수정하지 않고 유지됩니다",
                )
                summary.skips.append(skip_detail)
                summary.results.append(
                    ImportRowResult(
                        status="skip",
                        row=row_no,
                        key=key,
                        reason_code=skip_detail.error_code,
                        reason_message=skip_detail.message,
                    )
                )
                summary.skip_count += 1
                continue

            if not commit:
                summary.results.append(ImportRowResult(status="success", row=row_no, key=key))
                summary.success_count += 1
                continue

            try:
                customer = self._build_customer_from_row(row)
                customer_id = self.db.add_customer(customer)
                existing_keys.add(key)
                existing_phone_to_name[phone] = name
                summary.results.append(
                    ImportRowResult(status="success", row=row_no, key=key, customer_id=customer_id)
                )
                summary.success_count += 1
            except Exception as e:
                detail = ImportErrorDetail(
                    sheet="customers",
                    row=row_no,
                    column="db",
                    error_code="E901",
                    message="failed to insert customer",
                    value=str(e),
                    action_hint="입력값 및 중복 데이터를 확인하세요",
                )
                summary.errors.append(detail)
                summary.results.append(
                    ImportRowResult(
                        status="fail",
                        row=row_no,
                        key=key,
                        reason_code=detail.error_code,
                        reason_message=detail.message,
                    )
                )
                summary.fail_count += 1

        return summary

    @staticmethod
    def _build_customer_from_row(row: dict) -> Customer:
        driving_type = (row.get("driving_type", "") or "").strip() or "none"
        payment_method = (row.get("payment_method", "") or "").strip() or None
        return Customer(
            name=normalize_name(row.get("name", "")),
            phone=normalize_phone(row.get("phone", "")),
            resident_id=(row.get("resident_id", "") or "").strip(),
            address=(row.get("address", "") or "").strip() or None,
            occupation=(row.get("occupation", "") or "").strip() or None,
            driving_type=driving_type,
            payment_method=payment_method,
            memo=(row.get("memo", "") or "").strip() or None,
        )

