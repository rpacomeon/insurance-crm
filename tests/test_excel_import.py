# -*- coding: utf-8 -*-
import sys
import tempfile
import shutil
from pathlib import Path

import pytest
from openpyxl import Workbook

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from database import DatabaseManager
from models import Customer
from utils.excel_import.reader import read_customers_sheet
from utils.excel_import.report import export_error_report
from utils.excel_import.service import CustomerExcelImportService


@pytest.fixture
def temp_dir():
    root = Path(tempfile.mkdtemp())
    yield root
    shutil.rmtree(root, ignore_errors=True)


@pytest.fixture
def db(temp_dir):
    database = DatabaseManager(str(temp_dir / "test_crm.db"))
    yield database
    database.close()


def _write_customers_xlsx(path: Path, rows: list[list[str]]):
    wb = Workbook()
    ws = wb.active
    ws.title = "customers"
    ws.append(["name", "phone", "resident_id", "address", "occupation", "driving_type", "payment_method", "memo"])
    for row in rows:
        ws.append(row)
    wb.save(path)


def test_read_customers_sheet_missing_sheet(temp_dir):
    path = temp_dir / "missing_sheet.xlsx"
    wb = Workbook()
    wb.active.title = "wrong_name"
    wb.save(path)

    rows, errors = read_customers_sheet(str(path))
    assert rows == []
    assert len(errors) == 1
    assert errors[0].error_code == "E001"


def test_preview_insert_skip_fail_counts(db, temp_dir):
    existing = Customer(name="기존고객", phone="01011112222", resident_id="900101-1234567")
    db.add_customer(existing)

    path = temp_dir / "preview_case.xlsx"
    _write_customers_xlsx(
        path,
        [
            ["신규고객", "010-9999-8888", "", "", "", "personal", "신용카드", ""],     # success
            ["기존고객", "010-1111-2222", "", "", "", "none", "", ""],               # skip (E202)
            ["신규고객", "010-9999-8888", "", "", "", "personal", "신용카드", ""],     # fail duplicate (E201)
        ],
    )

    svc = CustomerExcelImportService(db)
    summary = svc.preview_import(str(path))

    assert summary.total_rows == 3
    assert summary.success_count == 1
    assert summary.skip_count == 1
    assert summary.fail_count == 1
    assert any(s.error_code == "E202" for s in summary.skips)
    assert any(e.error_code == "E201" for e in summary.errors)


def test_commit_inserts_only_new_and_keeps_existing(db, temp_dir):
    old = Customer(name="보존고객", phone="01012341234", resident_id="800101-1234567", memo="keep_me")
    old_id = db.add_customer(old)
    old_saved = db.get_customer(old_id)
    assert old_saved is not None
    assert old_saved.memo == "keep_me"

    path = temp_dir / "commit_case.xlsx"
    _write_customers_xlsx(
        path,
        [
            ["보존고객", "010-1234-1234", "", "", "", "none", "", "changed_in_file"],  # skip
            ["추가고객", "010-5555-6666", "", "서울", "회사원", "personal", "신용카드", "new"],  # success
        ],
    )

    svc = CustomerExcelImportService(db)
    summary = svc.commit_import(str(path))

    assert summary.success_count == 1
    assert summary.skip_count == 1
    assert summary.fail_count == 0

    # Existing customer must remain unchanged.
    old_after = db.get_customer(old_id)
    assert old_after is not None
    assert old_after.memo == "keep_me"

    added = db.search_customers("추가고객")
    assert len([c for c in added if c.phone == "01055556666"]) == 1


def test_export_error_report_file_created(db, temp_dir):
    path = temp_dir / "error_case.xlsx"
    _write_customers_xlsx(
        path,
        [
            ["", "010-1234-5678", "", "", "", "none", "", ""],  # E101
            ["고객A", "abc", "", "", "", "none", "", ""],        # E103
        ],
    )

    svc = CustomerExcelImportService(db)
    summary = svc.preview_import(str(path))

    report_path = temp_dir / "report.csv"
    ok, error = export_error_report(summary.errors, summary.skips, str(report_path))
    assert ok is True
    assert error is None
    assert report_path.exists()

