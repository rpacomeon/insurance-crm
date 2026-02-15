# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from datetime import datetime

from utils.excel_import.reader import write_customer_template
from utils.excel_import.report import export_error_report
from utils.excel_import.service import CustomerExcelImportService
from utils.excel_import.types import ImportSummary


class ImportCustomersDialog:
    def __init__(self, parent, db_manager, on_completed=None):
        self.parent = parent
        self.db = db_manager
        self.on_completed = on_completed
        self.service = CustomerExcelImportService(db_manager)
        self.latest_summary: ImportSummary | None = None

        self.window = tk.Toplevel(parent)
        self.window.title("Excel Import - Customers")
        self.window.geometry("980x620")
        self.window.transient(parent)
        self.window.grab_set()

        self.file_path_var = tk.StringVar()
        self.summary_var = tk.StringVar(value="파일을 선택하세요")

        self._build_ui()

    def _build_ui(self):
        top = tk.Frame(self.window)
        top.pack(fill="x", padx=12, pady=12)

        tk.Entry(top, textvariable=self.file_path_var).pack(side="left", fill="x", expand=True, padx=(0, 8))
        tk.Button(top, text="파일 선택", command=self._select_file).pack(side="left", padx=4)
        tk.Button(top, text="템플릿 저장", command=self._save_template).pack(side="left", padx=4)
        tk.Button(top, text="미리보기", command=self._preview).pack(side="left", padx=4)
        tk.Button(top, text="반영", command=self._commit).pack(side="left", padx=4)
        tk.Button(top, text="오류리포트", command=self._download_report).pack(side="left", padx=4)

        tk.Label(self.window, textvariable=self.summary_var, anchor="w").pack(fill="x", padx=12, pady=(0, 8))

        columns = ("type", "sheet", "row", "column", "code", "message", "value", "hint")
        self.tree = ttk.Treeview(self.window, columns=columns, show="headings")
        for col, width in [
            ("type", 70), ("sheet", 90), ("row", 60), ("column", 120),
            ("code", 80), ("message", 220), ("value", 160), ("hint", 220),
        ]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor="w")

        yscroll = ttk.Scrollbar(self.window, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=yscroll.set)
        self.tree.pack(side="left", fill="both", expand=True, padx=(12, 0), pady=(0, 12))
        yscroll.pack(side="right", fill="y", padx=(0, 12), pady=(0, 12))

    def _select_file(self):
        path = filedialog.askopenfilename(
            title="Excel 파일 선택",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
        )
        if path:
            self.file_path_var.set(path)

    def _save_template(self):
        today = datetime.now().strftime("%Y%m%d")
        path = filedialog.asksaveasfilename(
            title="템플릿 저장",
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")],
            initialfile=f"customers_template_{today}.xlsx",
        )
        if not path:
            return
        try:
            write_customer_template(path)
            messagebox.showinfo("Template", f"템플릿 저장 완료\n{path}")
        except Exception as e:
            messagebox.showerror("Template", f"템플릿 저장 실패\n{e}")

    def _preview(self):
        path = self.file_path_var.get().strip()
        if not path:
            messagebox.showwarning("Import", "Excel 파일을 먼저 선택하세요.")
            return
        self.latest_summary = self.service.preview_import(path)
        self._render_summary("미리보기 완료")

    def _commit(self):
        path = self.file_path_var.get().strip()
        if not path:
            messagebox.showwarning("Import", "Excel 파일을 먼저 선택하세요.")
            return
        if not messagebox.askyesno("Import", "신규 고객만 추가하고 기존 고객은 유지합니다. 진행할까요?"):
            return

        self.latest_summary = self.service.commit_import(path)
        self._render_summary("반영 완료")
        if self.on_completed:
            self.on_completed()

    def _download_report(self):
        if not self.latest_summary:
            messagebox.showwarning("Report", "먼저 미리보기 또는 반영을 실행하세요.")
            return

        path = filedialog.asksaveasfilename(
            title="오류 리포트 저장",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile=f"import_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        )
        if not path:
            return

        ok, error = export_error_report(self.latest_summary.errors, self.latest_summary.skips, path)
        if ok:
            messagebox.showinfo("Report", f"리포트 저장 완료\n{path}")
        else:
            messagebox.showerror("Report", f"리포트 저장 실패\n{error}")

    def _render_summary(self, prefix: str):
        summary = self.latest_summary
        if not summary:
            return

        self.summary_var.set(
            f"{prefix} | 총 {summary.total_rows}건 | "
            f"성공 {summary.success_count} | 스킵 {summary.skip_count} | 실패 {summary.fail_count}"
        )

        for item in self.tree.get_children():
            self.tree.delete(item)

        for e in summary.errors:
            self.tree.insert(
                "",
                tk.END,
                values=("ERROR", e.sheet, e.row, e.column, e.error_code, e.message, e.value, e.action_hint),
            )
        for e in summary.skips:
            self.tree.insert(
                "",
                tk.END,
                values=("SKIP", e.sheet, e.row, e.column, e.error_code, e.message, e.value, e.action_hint),
            )

