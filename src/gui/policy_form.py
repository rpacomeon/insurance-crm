# -*- coding: utf-8 -*-
"""
보험 계약 추가/편집 폼
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Callable
from datetime import datetime

from models import Policy
from gui.theme import COLORS, FONTS, SPACING
from utils.validators import (
    validate_premium,
    validate_billing_day,
    validate_contract_dates,
    validate_card_number,
    validate_card_expiry,
)


class PolicyForm:
    """보험 계약 추가/편집 폼 클래스"""

    def __init__(
        self,
        parent: tk.Tk,
        customer_id: int,
        policy: Optional[Policy] = None,
        on_save: Optional[Callable] = None,
    ):
        """폼 초기화

        Args:
            parent: 부모 윈도우
            customer_id: 고객 ID
            policy: 수정할 계약 (None이면 추가 모드)
            on_save: 저장 후 호출될 콜백 함수
        """
        self.parent = parent
        self.customer_id = customer_id
        self.policy = policy
        self.on_save = on_save
        self.is_edit_mode = policy is not None

        # 모달 윈도우 생성
        self.window = tk.Toplevel(parent)
        self.window.title("계약 정보 수정" if self.is_edit_mode else "새 계약 추가")
        self.window.geometry("600x750")
        self.window.resizable(False, False)
        self.window.configure(bg=COLORS["bg_main"])

        # 모달 설정
        self.window.transient(parent)
        self.window.grab_set()

        # ===== 입력 변수 =====
        # 기본 정보
        self.insurer_var = tk.StringVar()
        self.product_name_var = tk.StringVar()
        self.premium_var = tk.StringVar()

        # 결제 정보
        self.payment_method_var = tk.StringVar(value="card")  # "card" / "transfer"
        self.billing_cycle_var = tk.StringVar(value="monthly")  # "monthly" / "yearly"
        self.billing_day_var = tk.StringVar()

        # 카드 정보
        self.card_issuer_var = tk.StringVar()
        self.card_number_var = tk.StringVar()
        self.card_expiry_var = tk.StringVar()
        self.card_number_part1_var = tk.StringVar()
        self.card_number_part2_var = tk.StringVar()
        self.card_number_part3_var = tk.StringVar()
        self.card_number_part4_var = tk.StringVar()
        self.card_expiry_mm_var = tk.StringVar()
        self.card_expiry_yy_var = tk.StringVar()

        # 계약 기간
        self.contract_start_date_var = tk.StringVar()
        self.contract_end_date_var = tk.StringVar()
        self.contract_start_year_var = tk.StringVar()
        self.contract_start_month_var = tk.StringVar()
        self.contract_start_day_var = tk.StringVar()
        self.contract_end_year_var = tk.StringVar()
        self.contract_end_month_var = tk.StringVar()
        self.contract_end_day_var = tk.StringVar()

        # 메모
        self.memo_var = tk.StringVar()

        # ===== 기존 계약 데이터 로드 (수정 모드) =====
        if self.is_edit_mode:
            self._load_policy_data()

        # UI 구성
        self._create_widgets()

        # 윈도우 중앙 배치
        self._center_window()

    def _load_policy_data(self):
        """기존 계약 데이터를 입력 필드에 로드"""
        self.insurer_var.set(self.policy.insurer)
        self.product_name_var.set(self.policy.product_name)
        self.premium_var.set(f"{self.policy.premium:,}")  # 천 단위 쉼표
        self.payment_method_var.set(self.policy.payment_method)
        self.billing_cycle_var.set(self.policy.billing_cycle)
        self.billing_day_var.set(str(self.policy.billing_day))

        # 카드 정보
        if self.policy.card_issuer:
            self.card_issuer_var.set(self.policy.card_issuer)
        if self.policy.card_number:
            self._set_segmented_field_values(self.policy.card_number, 4, [
                self.card_number_part1_var,
                self.card_number_part2_var,
                self.card_number_part3_var,
                self.card_number_part4_var,
            ])
            self.card_number_var.set(self.policy.card_number)
        if self.policy.card_expiry:
            self._set_segmented_field_values(self.policy.card_expiry, 2, [
                self.card_expiry_mm_var,
                self.card_expiry_yy_var,
            ])
            self.card_expiry_var.set(self.policy.card_expiry)

        # 계약 기간
        self._set_segmented_date_values(self.policy.contract_start_date, [
            self.contract_start_year_var,
            self.contract_start_month_var,
            self.contract_start_day_var,
        ], 4, 2, 2)
        self.contract_start_date_var.set(self.policy.contract_start_date)
        if self.policy.contract_end_date:
            self._set_segmented_date_values(self.policy.contract_end_date, [
                self.contract_end_year_var,
                self.contract_end_month_var,
                self.contract_end_day_var,
            ], 4, 2, 2)
            self.contract_end_date_var.set(self.policy.contract_end_date)

        # 메모
        if self.policy.memo:
            self.memo_var.set(self.policy.memo)

    def _create_widgets(self):
        """UI 위젯 생성"""
        # 캔버스 + 스크롤바 (스크롤 가능)
        canvas = tk.Canvas(self.window, bg=COLORS["bg_main"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.window, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=COLORS["bg_main"])

        scrollable_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # 레이아웃
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # 마우스 휠 스크롤
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", on_mousewheel)

        # ===== 섹션 생성 =====
        self._create_basic_info_section(scrollable_frame)
        self._create_payment_info_section(scrollable_frame)
        self._create_card_info_section(scrollable_frame)
        self._create_contract_period_section(scrollable_frame)
        self._create_memo_section(scrollable_frame)

        # ===== 하단 버튼 =====
        self._create_buttons(scrollable_frame)

        # 결제 수단 변경 시 카드 정보 활성화/비활성화
        self.payment_method_var.trace_add("write", lambda *args: self._on_payment_method_change())
        self._on_payment_method_change()  # 초기 상태 설정

    def _create_basic_info_section(self, parent):
        """섹션 1: 계약 기본 정보"""
        section_frame = tk.Frame(parent, bg=COLORS["bg_main"])
        section_frame.pack(fill="x", padx=SPACING["padding_large"], pady=(SPACING["padding_large"], 0))

        # 섹션 제목
        title_label = tk.Label(
            section_frame,
            text="■ 섹션 1: 계약 기본 정보",
            font=FONTS["subtitle"],
            bg=COLORS["bg_main"],
            fg=COLORS["text_primary"],
        )
        title_label.pack(anchor="w", pady=(0, SPACING["padding_medium"]))

        # 보험사
        self._create_input_row(section_frame, "보험사 *", self.insurer_var, "예: 삼성생명")

        # 상품명
        self._create_input_row(section_frame, "상품명 *", self.product_name_var, "예: 종신보험")

        # 보험료 (월 기준)
        self._create_input_row(section_frame, "보험료 (월) *", self.premium_var, "예: 50000")

    def _create_payment_info_section(self, parent):
        """섹션 2: 결제 정보"""
        section_frame = tk.Frame(parent, bg=COLORS["bg_main"])
        section_frame.pack(fill="x", padx=SPACING["padding_large"], pady=(SPACING["section_gap"], 0))

        # 섹션 제목
        title_label = tk.Label(
            section_frame,
            text="■ 섹션 2: 결제 정보",
            font=FONTS["subtitle"],
            bg=COLORS["bg_main"],
            fg=COLORS["text_primary"],
        )
        title_label.pack(anchor="w", pady=(0, SPACING["padding_medium"]))

        # 결제 수단 (라디오버튼)
        payment_frame = tk.Frame(section_frame, bg=COLORS["bg_main"])
        payment_frame.pack(fill="x", pady=SPACING["padding_small"])

        label = tk.Label(
            payment_frame,
            text="결제 수단 *",
            font=FONTS["form_label"],
            bg=COLORS["bg_main"],
            width=15,
            anchor="w",
        )
        label.pack(side="left")

        radio_frame = tk.Frame(payment_frame, bg=COLORS["bg_main"])
        radio_frame.pack(side="left", fill="x", expand=True)

        tk.Radiobutton(
            radio_frame,
            text="카드",
            variable=self.payment_method_var,
            value="card",
            font=FONTS["body"],
            bg=COLORS["bg_main"],
        ).pack(side="left", padx=SPACING["padding_medium"])

        tk.Radiobutton(
            radio_frame,
            text="계좌이체",
            variable=self.payment_method_var,
            value="transfer",
            font=FONTS["body"],
            bg=COLORS["bg_main"],
        ).pack(side="left")

        # 납부 주기 (라디오버튼)
        cycle_frame = tk.Frame(section_frame, bg=COLORS["bg_main"])
        cycle_frame.pack(fill="x", pady=SPACING["padding_small"])

        label = tk.Label(
            cycle_frame,
            text="납부 주기 *",
            font=FONTS["form_label"],
            bg=COLORS["bg_main"],
            width=15,
            anchor="w",
        )
        label.pack(side="left")

        radio_frame = tk.Frame(cycle_frame, bg=COLORS["bg_main"])
        radio_frame.pack(side="left", fill="x", expand=True)

        tk.Radiobutton(
            radio_frame,
            text="월납",
            variable=self.billing_cycle_var,
            value="monthly",
            font=FONTS["body"],
            bg=COLORS["bg_main"],
        ).pack(side="left", padx=SPACING["padding_medium"])

        tk.Radiobutton(
            radio_frame,
            text="연납",
            variable=self.billing_cycle_var,
            value="yearly",
            font=FONTS["body"],
            bg=COLORS["bg_main"],
        ).pack(side="left")

        # 납부일 (스핀박스)
        day_frame = tk.Frame(section_frame, bg=COLORS["bg_main"])
        day_frame.pack(fill="x", pady=SPACING["padding_small"])

        label = tk.Label(
            day_frame,
            text="납부일 *",
            font=FONTS["form_label"],
            bg=COLORS["bg_main"],
            width=15,
            anchor="w",
        )
        label.pack(side="left")

        spinbox = tk.Spinbox(
            day_frame,
            from_=1,
            to=31,
            textvariable=self.billing_day_var,
            font=FONTS["form_input"],
            width=10,
        )
        spinbox.pack(side="left")

        hint = tk.Label(
            day_frame,
            text="(1~31일)",
            font=FONTS["small"],
            bg=COLORS["bg_main"],
            fg=COLORS["text_hint"],
        )
        hint.pack(side="left", padx=SPACING["padding_small"])

    def _create_card_info_section(self, parent):
        """섹션 3: 카드 정보 (조건부 활성화)"""
        self.card_section_frame = tk.Frame(parent, bg=COLORS["bg_main"])
        self.card_section_frame.pack(fill="x", padx=SPACING["padding_large"], pady=(SPACING["section_gap"], 0))

        # 섹션 제목
        title_label = tk.Label(
            self.card_section_frame,
            text="■ 섹션 3: 카드 정보 (결제 수단이 '카드'일 때만 입력)",
            font=FONTS["subtitle"],
            bg=COLORS["bg_main"],
            fg=COLORS["text_primary"],
        )
        title_label.pack(anchor="w", pady=(0, SPACING["padding_medium"]))

        # 카드사
        self.card_issuer_entry = self._create_input_row(
            self.card_section_frame, "카드사", self.card_issuer_var, "예: 신한카드", return_entry=True
        )

        # 카드 번호 16자리
        self.card_number_entries = self._create_segmented_input_row(
            self.card_section_frame,
            "카드 번호 (16자리)",
            [
                (self.card_number_part1_var, 4),
                (self.card_number_part2_var, 4),
                (self.card_number_part3_var, 4),
                (self.card_number_part4_var, 4),
            ],
            [" ", " ", " "],
            "예: 1234 5678 9012 3456",
        )

        # 유효기간 (MM/YY)
        self.card_expiry_entries = self._create_segmented_input_row(
            self.card_section_frame,
            "유효기간 (MM/YY)",
            [
                (self.card_expiry_mm_var, 2),
                (self.card_expiry_yy_var, 2),
            ],
            [" "],
            "예: 12 26",
        )

    def _create_contract_period_section(self, parent):
        """섹션 4: 계약 기간"""
        section_frame = tk.Frame(parent, bg=COLORS["bg_main"])
        section_frame.pack(fill="x", padx=SPACING["padding_large"], pady=(SPACING["section_gap"], 0))

        # 섹션 제목
        title_label = tk.Label(
            section_frame,
            text="■ 섹션 4: 계약 기간",
            font=FONTS["subtitle"],
            bg=COLORS["bg_main"],
            fg=COLORS["text_primary"],
        )
        title_label.pack(anchor="w", pady=(0, SPACING["padding_medium"]))

        # 시작일
        self.contract_start_date_entries = self._create_segmented_input_row(
            section_frame,
            "시작일 *",
            [
                (self.contract_start_year_var, 4),
                (self.contract_start_month_var, 2),
                (self.contract_start_day_var, 2),
            ],
            [" ", " "],
            "예: 2026 02 15",
        )

        # 종료일 (선택)
        self.contract_end_date_entries = self._create_segmented_input_row(
            section_frame,
            "종료일 (선택)",
            [
                (self.contract_end_year_var, 4),
                (self.contract_end_month_var, 2),
                (self.contract_end_day_var, 2),
            ],
            [" ", " "],
            "예: 2027 02 15",
        )

    def _create_memo_section(self, parent):
        """섹션 5: 메모"""
        section_frame = tk.Frame(parent, bg=COLORS["bg_main"])
        section_frame.pack(fill="x", padx=SPACING["padding_large"], pady=(SPACING["section_gap"], 0))

        # 섹션 제목
        title_label = tk.Label(
            section_frame,
            text="■ 섹션 5: 메모",
            font=FONTS["subtitle"],
            bg=COLORS["bg_main"],
            fg=COLORS["text_primary"],
        )
        title_label.pack(anchor="w", pady=(0, SPACING["padding_medium"]))

        # 메모 입력
        self._create_input_row(section_frame, "메모", self.memo_var, "특이사항 입력")

    def _create_input_row(self, parent, label_text, var, placeholder="", return_entry=False, width=30):
        """입력 행 생성 헬퍼

        Args:
            parent: 부모 프레임
            label_text: 라벨 텍스트
            var: StringVar 변수
            placeholder: 플레이스홀더 텍스트
            return_entry: True면 Entry 위젯 반환
            width: Entry 위젯 폭 (기본: 30)

        Returns:
            Entry 위젯 (return_entry=True일 때)
        """
        row_frame = tk.Frame(parent, bg=COLORS["bg_main"])
        row_frame.pack(fill="x", pady=SPACING["padding_small"])

        label = tk.Label(
            row_frame,
            text=label_text,
            font=FONTS["form_label"],
            bg=COLORS["bg_main"],
            width=15,
            anchor="w",
        )
        label.pack(side="left")

        entry = tk.Entry(row_frame, textvariable=var, font=FONTS["form_input"], width=width)
        entry.pack(side="left", fill="x", expand=True)

        if placeholder:
            hint = tk.Label(
                row_frame,
                text=placeholder,
                font=FONTS["small"],
                bg=COLORS["bg_main"],
                fg=COLORS["text_hint"],
            )
            hint.pack(side="left", padx=SPACING["padding_small"])

        if return_entry:
            return entry

    def _create_segmented_input_row(
        self,
        parent,
        label_text,
        segments,
        separators,
        placeholder="",
    ):
        row_frame = tk.Frame(parent, bg=COLORS["bg_main"])
        row_frame.pack(fill="x", pady=SPACING["padding_small"])

        label = tk.Label(
            row_frame,
            text=label_text,
            font=FONTS["form_label"],
            bg=COLORS["bg_main"],
            width=15,
            anchor="w",
        )
        label.pack(side="left")

        entries = []
        max_lengths = []
        for seg_var, seg_len in segments:
            max_lengths.append(seg_len)
            entry = tk.Entry(
                row_frame,
                textvariable=seg_var,
                font=FONTS["form_input"],
                width=seg_len + 1,
                justify="center",
            )
            entry.pack(side="left")
            entries.append(entry)
        for idx, sep in enumerate(separators):
            if sep and idx < len(entries):
                sep_label = tk.Label(
                    row_frame,
                    text=sep,
                    font=FONTS["form_input"],
                    bg=COLORS["bg_main"],
                    fg=COLORS["text_hint"],
                )
                sep_label.pack(side="left", padx=2)

        for idx, entry in enumerate(entries):
            prev_entry = entries[idx - 1] if idx > 0 else None
            next_entry = entries[idx + 1] if idx + 1 < len(entries) else None
            entry.bind(
                "<KeyRelease>",
                lambda e, ent=entry, m=max_lengths[idx], prev=prev_entry, nxt=next_entry: self._on_segment_key_release(
                    e, ent, m, prev, nxt
                ),
            )

        if placeholder:
            hint = tk.Label(
                row_frame,
                text=placeholder,
                font=FONTS["small"],
                bg=COLORS["bg_main"],
                fg=COLORS["text_hint"],
            )
            hint.pack(side="left", padx=SPACING["padding_small"])

        return entries

    def _on_segment_key_release(self, event, entry, max_length, prev_entry, next_entry):
        digits = "".join(ch for ch in entry.get() if ch.isdigit())
        if digits != entry.get():
            entry.delete(0, "end")
            entry.insert(0, digits)
        if len(digits) > max_length:
            entry.delete(max_length, tk.END)
            digits = entry.get()

        nav_keys = {
            "Left",
            "Right",
            "Up",
            "Down",
            "Tab",
            "Shift_L",
            "Shift_R",
            "Control_L",
            "Control_R",
            "Alt_L",
            "Alt_R",
            "Home",
            "End",
            "Prior",
            "Next",
            "Delete",
        }
        if event.keysym == "BackSpace" and prev_entry is not None and not digits:
            prev_entry.focus_set()
            prev_entry.icursor(tk.END)
            return
        if len(digits) == max_length and next_entry is not None and event.keysym not in nav_keys:
            next_entry.focus_set()
            next_entry.icursor(0)

    def _set_segmented_field_values(self, raw_value, segment_length, vars_list):
        value = "".join(ch for ch in (raw_value or "") if ch.isdigit())
        for index, var in enumerate(vars_list):
            start = index * segment_length
            var.set(value[start : start + segment_length])

    def _set_segmented_date_values(self, raw_value, vars_list, year_len, month_len, day_len):
        if not raw_value:
            vars_list[0].set("")
            vars_list[1].set("")
            vars_list[2].set("")
            return

        if "-" in raw_value:
            parts = raw_value.split("-")
            if len(parts) == 3:
                vars_list[0].set(parts[0])
                vars_list[1].set(parts[1])
                vars_list[2].set(parts[2])
                return

        digits = "".join(ch for ch in raw_value if ch.isdigit())
        vars_list[0].set(digits[:year_len])
        vars_list[1].set(digits[year_len : year_len + month_len])
        vars_list[2].set(digits[year_len + month_len : year_len + month_len + day_len])

    def _sync_segmented_fields(self):
        self.card_number_var.set(
            f"{self.card_number_part1_var.get().strip()}"
            f"{self.card_number_part2_var.get().strip()}"
            f"{self.card_number_part3_var.get().strip()}"
            f"{self.card_number_part4_var.get().strip()}"
        )
        card_expiry_mm = self.card_expiry_mm_var.get().strip()
        card_expiry_yy = self.card_expiry_yy_var.get().strip()
        if card_expiry_mm or card_expiry_yy:
            self.card_expiry_var.set(f"{card_expiry_mm}/{card_expiry_yy}")
        else:
            self.card_expiry_var.set("")

        start_date_fields = (
            self.contract_start_year_var.get().strip(),
            self.contract_start_month_var.get().strip(),
            self.contract_start_day_var.get().strip(),
        )
        if any(start_date_fields):
            self.contract_start_date_var.set(f"{start_date_fields[0]}-{start_date_fields[1]}-{start_date_fields[2]}")
        else:
            self.contract_start_date_var.set("")

        end_date_fields = (
            self.contract_end_year_var.get().strip(),
            self.contract_end_month_var.get().strip(),
            self.contract_end_day_var.get().strip(),
        )
        if any(end_date_fields):
            self.contract_end_date_var.set(f"{end_date_fields[0]}-{end_date_fields[1]}-{end_date_fields[2]}")
        else:
            self.contract_end_date_var.set("")

    def _create_buttons(self, parent):
        """하단 버튼 생성"""
        button_frame = tk.Frame(parent, bg=COLORS["bg_main"])
        button_frame.pack(fill="x", padx=SPACING["padding_large"], pady=SPACING["padding_large"])

        # 저장 버튼
        save_btn = tk.Button(
            button_frame,
            text="저장",
            font=FONTS["button"],
            bg=COLORS["btn_add"],
            fg=COLORS["text_on_primary"],
            command=self._on_save_click,
            width=10,
            relief="flat",
            cursor="hand2",
        )
        save_btn.pack(side="left", padx=(0, SPACING["padding_medium"]))

        # 취소 버튼
        cancel_btn = tk.Button(
            button_frame,
            text="취소",
            font=FONTS["button"],
            bg=COLORS["btn_exit"],
            fg=COLORS["text_on_primary"],
            command=self.window.destroy,
            width=10,
            relief="flat",
            cursor="hand2",
        )
        cancel_btn.pack(side="left")

    def _on_payment_method_change(self):
        """결제 수단 변경 시 카드 정보 필드 활성화/비활성화"""
        if self.payment_method_var.get() == "card":
            # 카드 정보 활성화
            state = "normal"
        else:
            # 계좌이체: 카드 정보 비활성화
            state = "disabled"

        # Entry 위젯 상태 변경
        if hasattr(self, 'card_issuer_entry'):
            self.card_issuer_entry.config(state=state)
        if hasattr(self, 'card_number_entries'):
            for entry in self.card_number_entries:
                entry.config(state=state)
        if hasattr(self, 'card_expiry_entries'):
            for entry in self.card_expiry_entries:
                entry.config(state=state)

    def _on_save_click(self):
        """저장 버튼 클릭 핸들러"""
        # ===== 입력 검증 =====
        # 보험사
        insurer = self.insurer_var.get().strip()
        if not insurer:
            messagebox.showerror("입력 오류", "보험사를 입력해주세요")
            return

        # 상품명
        product_name = self.product_name_var.get().strip()
        if not product_name:
            messagebox.showerror("입력 오류", "상품명을 입력해주세요")
            return

        # 보험료
        is_valid, error_msg = validate_premium(self.premium_var.get())
        if not is_valid:
            messagebox.showerror("입력 오류", error_msg)
            return
        premium = int(self.premium_var.get().replace(",", ""))

        # 납부일
        is_valid, error_msg = validate_billing_day(self.billing_day_var.get())
        if not is_valid:
            messagebox.showerror("입력 오류", error_msg)
            return
        billing_day = int(self.billing_day_var.get())

        self._sync_segmented_fields()

        # 계약 기간
        is_valid, error_msg = validate_contract_dates(
            self.contract_start_date_var.get(),
            self.contract_end_date_var.get()
        )
        if not is_valid:
            messagebox.showerror("입력 오류", error_msg)
            return

        # 카드 정보 (결제 수단이 "카드"일 때만 검증)
        card_issuer = None
        card_number = None
        card_expiry = None

        if self.payment_method_var.get() == "card":
            # 카드사는 선택
            card_issuer = self.card_issuer_var.get().strip() or None

            # 카드 번호 16자리
            is_valid, error_msg = validate_card_number(self.card_number_var.get())
            if not is_valid:
                messagebox.showerror("입력 오류", error_msg)
                return
            card_number = self.card_number_var.get().strip() or None

            # 유효기간
            is_valid, error_msg = validate_card_expiry(self.card_expiry_var.get())
            if not is_valid:
                messagebox.showerror("입력 오류", error_msg)
                return
            card_expiry = self.card_expiry_var.get().strip() or None

        # ===== Policy 객체 생성 =====
        policy = Policy(
            customer_id=self.customer_id,
            insurer=insurer,
            product_name=product_name,
            premium=premium,
            payment_method=self.payment_method_var.get(),
            billing_cycle=self.billing_cycle_var.get(),
            billing_day=billing_day,
            card_issuer=card_issuer,
            card_number=card_number,
            card_expiry=card_expiry,
            contract_start_date=self.contract_start_date_var.get().strip(),
            contract_end_date=self.contract_end_date_var.get().strip() or None,
            memo=self.memo_var.get().strip() or None,
        )

        # 수정 모드일 경우 ID 유지
        if self.is_edit_mode:
            policy.id = self.policy.id
            policy.status = self.policy.status
            policy.next_payment_date = self.policy.next_payment_date
            policy.last_payment_date = self.policy.last_payment_date
            policy.created_at = self.policy.created_at

        # ===== 콜백 호출 =====
        if self.on_save:
            self.on_save(policy)

        # 윈도우 닫기
        self.window.destroy()

    def _center_window(self):
        """윈도우를 화면 중앙에 배치"""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f"{width}x{height}+{x}+{y}")
