# -*- coding: utf-8 -*-
"""
고객 추가/편집 폼 - 피플라이프 대전행복사업단 스타일 (확장 버전)
보험 정보 + 건강 정보 + 고지 내용 포함
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Callable

from models import Customer
from gui.theme import COLORS, FONTS, SPACING, SIZES
from utils.validators import (
    validate_name,
    validate_phone,
    validate_email,
    validate_birth_date,
    validate_resident_id,
)


class CustomerForm:
    """고객 추가/편집 폼 클래스 - 확장 버전"""

    def __init__(
        self,
        parent: tk.Tk,
        customer: Optional[Customer] = None,
        on_save: Optional[Callable] = None,
    ):
        """폼 초기화

        Args:
            parent: 부모 윈도우
            customer: 수정할 고객 (None이면 추가 모드)
            on_save: 저장 후 호출될 콜백 함수
        """
        self.parent = parent
        self.customer = customer
        self.on_save = on_save
        self.is_edit_mode = customer is not None

        # 모달 윈도우 생성 (크기 확대)
        self.window = tk.Toplevel(parent)
        self.window.title("고객 정보 수정" if self.is_edit_mode else "새 고객 추가")
        self.window.geometry("700x750")
        self.window.resizable(False, False)
        self.window.configure(bg=COLORS["bg_main"])

        # 모달 설정
        self.window.transient(parent)
        self.window.grab_set()

        # ===== 기본 정보 입력 변수 =====
        self.name_var = tk.StringVar()
        self.phone_var = tk.StringVar()
        self.resident_id_front_var = tk.StringVar()  # 주민등록번호 앞 6자리
        self.resident_id_back_var = tk.StringVar()   # 주민등록번호 뒤 7자리
        self.address_var = tk.StringVar()
        self.occupation_var = tk.StringVar()  # 직업/사업

        # ===== 보험 정보 입력 변수 =====
        self.driving_type_var = tk.StringVar(value="none")  # none/personal/commercial
        self.commercial_taxi_var = tk.BooleanVar(value=False)
        self.commercial_construction_var = tk.BooleanVar(value=False)
        self.payment_method_var = tk.StringVar()

        # ===== 건강 정보 입력 변수 =====
        self.med_hypertension_var = tk.BooleanVar(value=False)  # 고혈압
        self.med_diabetes_var = tk.BooleanVar(value=False)  # 당뇨병
        self.med_hyperlipidemia_var = tk.BooleanVar(value=False)  # 고지혈증
        self.med_hospitalized_var = tk.BooleanVar(value=False)  # 입원/수술 여부
        self.med_recent_exam_var = tk.BooleanVar(value=False)  # 최근 3개월 진찰 여부
        self.med_cancer_var = tk.BooleanVar(value=False)  # 암
        self.med_stroke_var = tk.BooleanVar(value=False)  # 뇌졸중
        self.med_hemorrhage_var = tk.BooleanVar(value=False)  # 뇌출혈
        self.med_infarction_var = tk.BooleanVar(value=False)  # 심근경색
        self.med_angina_var = tk.BooleanVar(value=False)  # 협심증
        self.med_valve_var = tk.BooleanVar(value=False)  # 심장판막증
        self.med_cirrhosis_var = tk.BooleanVar(value=False)  # 간경화증
        self.custom_diagnosis_var = tk.StringVar()  # 사용자 정의 진단

        # ===== 기존 고객 데이터 로드 (수정 모드) =====
        if self.is_edit_mode:
            self._load_customer_data()

        # UI 구성
        self._create_widgets()

        # 윈도우 중앙 배치
        self._center_window()

    def _load_customer_data(self):
        """기존 고객 데이터를 입력 필드에 로드"""
        # 기본 정보
        self.name_var.set(self.customer.name)
        self.phone_var.set(self.customer.phone)

        # 주민등록번호 분리
        if self.customer.resident_id:
            parts = self.customer.resident_id.split("-")
            if len(parts) == 2:
                self.resident_id_front_var.set(parts[0])
                self.resident_id_back_var.set(parts[1])

        self.address_var.set(self.customer.address or "")
        self.occupation_var.set(self.customer.occupation or "")

        # 보험 정보
        self.driving_type_var.set(self.customer.driving_type or "none")
        if self.customer.commercial_detail:
            details = [d.strip() for d in self.customer.commercial_detail.split(",")]
            if "taxi" in details:
                self.commercial_taxi_var.set(True)
            if "construction" in details:
                self.commercial_construction_var.set(True)
        self.payment_method_var.set(self.customer.payment_method or "")

        # 건강 정보 - 약 복용
        if self.customer.med_medication:
            medications = [m.strip() for m in self.customer.med_medication.split(",")]
            if "고혈압" in medications:
                self.med_hypertension_var.set(True)
            if "당뇨병" in medications:
                self.med_diabetes_var.set(True)
            if "고지혈증" in medications:
                self.med_hyperlipidemia_var.set(True)

        # 입원/수술 여부
        self.med_hospitalized_var.set(self.customer.med_hospitalized)

        # 최근 3개월 진찰
        self.med_recent_exam_var.set(self.customer.med_recent_exam)

        # 5년 이내 진단
        if self.customer.med_5yr_diagnosis:
            diagnoses = [d.strip() for d in self.customer.med_5yr_diagnosis.split(",")]
            if "암" in diagnoses:
                self.med_cancer_var.set(True)
            if "뇌졸중" in diagnoses:
                self.med_stroke_var.set(True)
            if "뇌출혈" in diagnoses:
                self.med_hemorrhage_var.set(True)
            if "심근경색" in diagnoses:
                self.med_infarction_var.set(True)
            if "협심증" in diagnoses:
                self.med_angina_var.set(True)
            if "심장판막증" in diagnoses:
                self.med_valve_var.set(True)
            if "간경화증" in diagnoses:
                self.med_cirrhosis_var.set(True)

        # 사용자 정의 진단
        if self.customer.med_5yr_custom:
            self.custom_diagnosis_var.set(self.customer.med_5yr_custom)

    def _center_window(self):
        """윈도우를 화면 중앙에 배치"""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f"{width}x{height}+{x}+{y}")

    def _create_widgets(self):
        """UI 위젯 생성"""
        # 상단 헤더 바 (오렌지)
        header = tk.Frame(self.window, bg=COLORS["primary"], height=50)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        title_text = "고객 정보 수정" if self.is_edit_mode else "새 고객 추가"
        tk.Label(
            header,
            text=title_text,
            font=FONTS["header_title"],
            bg=COLORS["primary"],
            fg=COLORS["text_on_primary"],
        ).pack(side=tk.LEFT, padx=SPACING["padding_large"], pady=10)

        # 메인 폼 영역 (스크롤 가능)
        form_outer = tk.Frame(self.window, bg=COLORS["bg_main"])
        form_outer.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        # Canvas + Scrollbar
        canvas = tk.Canvas(form_outer, bg=COLORS["bg_white"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(form_outer, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=COLORS["bg_white"])

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # 스크롤 휠 바인딩
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        inner = tk.Frame(scrollable_frame, bg=COLORS["bg_white"])
        inner.pack(fill=tk.BOTH, expand=True, padx=25, pady=20)

        # ===== 기본 정보 섹션 =====
        self._create_section_header(inner, "기본 정보")

        self._create_field(inner, "이름", self.name_var, required=True)
        self._create_field(inner, "전화번호", self.phone_var, placeholder="예: 010-1234-5678", required=True)
        self._create_resident_id_field(inner)
        self._create_field(inner, "주소", self.address_var)
        self._create_field(inner, "직업/사업", self.occupation_var, placeholder="예: 자영업, 회사원, 프리랜서")

        # ===== 보험 정보 섹션 =====
        self._create_section_header(inner, "보험 정보")
        self._create_driving_type_field(inner)
        self._create_payment_method_field(inner)

        # ===== 건강 정보 섹션 =====
        self._create_section_header(inner, "건강 정보")
        self._create_medication_field(inner)
        self._create_hospitalized_field(inner)
        self._create_recent_exam_field(inner)
        self._create_5yr_diagnosis_field(inner)

        # ===== 고지/메모 섹션 =====
        self._create_section_header(inner, "고지/메모")
        self._create_notification_field(inner)
        self._create_memo_field(inner)

        # 필수 필드 안내
        tk.Label(
            inner,
            text="* 필수 항목입니다",
            font=FONTS["small"],
            fg=COLORS["error"],
            bg=COLORS["bg_white"],
            anchor=tk.W,
        ).pack(fill=tk.X, pady=(10, 0))

        # 버튼 영역
        btn_frame = tk.Frame(self.window, bg=COLORS["bg_main"])
        btn_frame.pack(fill=tk.X, padx=20, pady=(0, 15))

        # 저장 버튼
        btn_save = tk.Button(
            btn_frame,
            text="저장",
            font=FONTS["button"],
            bg=COLORS["primary"],
            fg=COLORS["text_on_primary"],
            activebackground=COLORS["primary_dark"],
            activeforeground=COLORS["text_on_primary"],
            relief="flat",
            bd=0,
            padx=40,
            pady=12,
            cursor="hand2",
            command=self._on_save,
        )
        btn_save.pack(side=tk.LEFT, padx=(0, 10))

        # 취소 버튼
        btn_cancel = tk.Button(
            btn_frame,
            text="취소",
            font=FONTS["button"],
            bg=COLORS["btn_exit"],
            fg=COLORS["text_on_primary"],
            activebackground="#616161",
            activeforeground=COLORS["text_on_primary"],
            relief="flat",
            bd=0,
            padx=40,
            pady=12,
            cursor="hand2",
            command=self._on_cancel,
        )
        btn_cancel.pack(side=tk.LEFT)

    def _create_section_header(self, parent: tk.Frame, title: str):
        """섹션 헤더 생성"""
        section_frame = tk.Frame(parent, bg=COLORS["bg_white"])
        section_frame.pack(fill=tk.X, pady=(20, 10))

        tk.Label(
            section_frame,
            text=f"── {title} " + "─" * 50,
            font=("Malgun Gothic", 11, "bold"),
            bg=COLORS["bg_white"],
            fg=COLORS["text_secondary"],
            anchor=tk.W,
        ).pack(fill=tk.X)

    def _create_field(
        self,
        parent: tk.Frame,
        label_text: str,
        variable: tk.StringVar,
        placeholder: str = "",
        required: bool = False,
    ):
        """일반 입력 필드 생성"""
        field_frame = tk.Frame(parent, bg=COLORS["bg_white"])
        field_frame.pack(fill=tk.X, pady=(8, 0))

        # 라벨
        label_frame = tk.Frame(field_frame, bg=COLORS["bg_white"])
        label_frame.pack(fill=tk.X)

        display_text = f"{label_text} *" if required else label_text
        tk.Label(
            label_frame,
            text=display_text,
            font=FONTS["form_label"],
            bg=COLORS["bg_white"],
            fg=COLORS["error"] if required else COLORS["text_primary"],
            anchor=tk.W,
        ).pack(side=tk.LEFT)

        if placeholder:
            tk.Label(
                label_frame,
                text=f"  ({placeholder})",
                font=FONTS["small"],
                bg=COLORS["bg_white"],
                fg=COLORS["text_hint"],
                anchor=tk.W,
            ).pack(side=tk.LEFT)

        # 입력 필드
        entry_container = tk.Frame(field_frame, bg=COLORS["border"], bd=0)
        entry_container.pack(fill=tk.X, pady=(5, 0))

        entry = tk.Entry(
            entry_container,
            textvariable=variable,
            font=FONTS["form_input"],
            bg=COLORS["bg_white"],
            fg=COLORS["text_primary"],
            insertbackground=COLORS["primary"],
            relief="flat",
            bd=0,
        )
        entry.pack(fill=tk.X, ipady=6, padx=2, pady=2)

    def _create_resident_id_field(self, parent: tk.Frame):
        """주민등록번호 입력 필드 생성 (앞6 + 뒤7)"""
        field_frame = tk.Frame(parent, bg=COLORS["bg_white"])
        field_frame.pack(fill=tk.X, pady=(8, 0))

        # 라벨
        tk.Label(
            field_frame,
            text="주민등록번호 *",
            font=FONTS["form_label"],
            bg=COLORS["bg_white"],
            fg=COLORS["error"],
            anchor=tk.W,
        ).pack(fill=tk.X)

        # 입력 영역
        input_frame = tk.Frame(field_frame, bg=COLORS["bg_white"])
        input_frame.pack(fill=tk.X, pady=(5, 0))

        # 앞 6자리
        front_container = tk.Frame(input_frame, bg=COLORS["border"], bd=0)
        front_container.pack(side=tk.LEFT)

        front_entry = tk.Entry(
            front_container,
            textvariable=self.resident_id_front_var,
            font=FONTS["form_input"],
            bg=COLORS["bg_white"],
            fg=COLORS["text_primary"],
            insertbackground=COLORS["primary"],
            relief="flat",
            bd=0,
            width=10,
        )
        front_entry.pack(ipady=6, padx=2, pady=2)

        # 하이픈
        tk.Label(
            input_frame,
            text=" - ",
            font=FONTS["form_input"],
            bg=COLORS["bg_white"],
            fg=COLORS["text_primary"],
        ).pack(side=tk.LEFT)

        # 뒤 7자리
        back_container = tk.Frame(input_frame, bg=COLORS["border"], bd=0)
        back_container.pack(side=tk.LEFT)

        back_entry = tk.Entry(
            back_container,
            textvariable=self.resident_id_back_var,
            font=FONTS["form_input"],
            bg=COLORS["bg_white"],
            fg=COLORS["text_primary"],
            insertbackground=COLORS["primary"],
            relief="flat",
            bd=0,
            width=12,
        )
        back_entry.pack(ipady=6, padx=2, pady=2)

        # 안내 텍스트
        tk.Label(
            input_frame,
            text="  (예: 900115-1234567)",
            font=FONTS["small"],
            bg=COLORS["bg_white"],
            fg=COLORS["text_hint"],
        ).pack(side=tk.LEFT)

    def _create_driving_type_field(self, parent: tk.Frame):
        """운전 여부 라디오버튼 필드"""
        field_frame = tk.Frame(parent, bg=COLORS["bg_white"])
        field_frame.pack(fill=tk.X, pady=(8, 0))

        # 라벨
        tk.Label(
            field_frame,
            text="운전 여부",
            font=FONTS["form_label"],
            bg=COLORS["bg_white"],
            fg=COLORS["text_primary"],
            anchor=tk.W,
        ).pack(fill=tk.X)

        # 라디오버튼 영역
        radio_frame = tk.Frame(field_frame, bg=COLORS["bg_white"])
        radio_frame.pack(fill=tk.X, pady=(5, 0))

        tk.Radiobutton(
            radio_frame,
            text="미운전",
            variable=self.driving_type_var,
            value="none",
            font=FONTS["form_input"],
            bg=COLORS["bg_white"],
            fg=COLORS["text_primary"],
            selectcolor=COLORS["bg_white"],
            activebackground=COLORS["bg_white"],
            command=self._on_driving_type_changed,
        ).pack(side=tk.LEFT, padx=(0, 15))

        tk.Radiobutton(
            radio_frame,
            text="자가용",
            variable=self.driving_type_var,
            value="personal",
            font=FONTS["form_input"],
            bg=COLORS["bg_white"],
            fg=COLORS["text_primary"],
            selectcolor=COLORS["bg_white"],
            activebackground=COLORS["bg_white"],
            command=self._on_driving_type_changed,
        ).pack(side=tk.LEFT, padx=(0, 15))

        tk.Radiobutton(
            radio_frame,
            text="영업용",
            variable=self.driving_type_var,
            value="commercial",
            font=FONTS["form_input"],
            bg=COLORS["bg_white"],
            fg=COLORS["text_primary"],
            selectcolor=COLORS["bg_white"],
            activebackground=COLORS["bg_white"],
            command=self._on_driving_type_changed,
        ).pack(side=tk.LEFT)

        # 영업용 상세 (조건부 표시)
        self.commercial_detail_frame = tk.Frame(field_frame, bg=COLORS["bg_white"])
        self.commercial_detail_frame.pack(fill=tk.X, pady=(5, 0))

        tk.Checkbutton(
            self.commercial_detail_frame,
            text="택시",
            variable=self.commercial_taxi_var,
            font=FONTS["form_input"],
            bg=COLORS["bg_white"],
            fg=COLORS["text_primary"],
            selectcolor=COLORS["bg_white"],
            activebackground=COLORS["bg_white"],
        ).pack(side=tk.LEFT, padx=(20, 15))

        tk.Checkbutton(
            self.commercial_detail_frame,
            text="건설용",
            variable=self.commercial_construction_var,
            font=FONTS["form_input"],
            bg=COLORS["bg_white"],
            fg=COLORS["text_primary"],
            selectcolor=COLORS["bg_white"],
            activebackground=COLORS["bg_white"],
        ).pack(side=tk.LEFT)

        # 초기 상태 설정
        self._on_driving_type_changed()

    def _on_driving_type_changed(self):
        """운전 여부 변경 시 영업용 상세 표시/숨김"""
        if self.driving_type_var.get() == "commercial":
            self.commercial_detail_frame.pack(fill=tk.X, pady=(5, 0))
        else:
            self.commercial_detail_frame.pack_forget()
            # 체크박스 초기화
            self.commercial_taxi_var.set(False)
            self.commercial_construction_var.set(False)

    def _create_payment_method_field(self, parent: tk.Frame):
        """보험료 입금 방식 Combobox"""
        field_frame = tk.Frame(parent, bg=COLORS["bg_white"])
        field_frame.pack(fill=tk.X, pady=(8, 0))

        # 라벨
        tk.Label(
            field_frame,
            text="보험료 입금 방식",
            font=FONTS["form_label"],
            bg=COLORS["bg_white"],
            fg=COLORS["text_primary"],
            anchor=tk.W,
        ).pack(fill=tk.X)

        # Combobox
        combo = ttk.Combobox(
            field_frame,
            textvariable=self.payment_method_var,
            values=["계좌이체", "신용카드", "자동이체"],
            font=FONTS["form_input"],
            state="readonly",
        )
        combo.pack(fill=tk.X, pady=(5, 0))

    def _create_medication_field(self, parent: tk.Frame):
        """약 복용(병력) 체크박스 필드"""
        field_frame = tk.Frame(parent, bg=COLORS["bg_white"])
        field_frame.pack(fill=tk.X, pady=(8, 0))

        # 라벨
        tk.Label(
            field_frame,
            text="약 복용 (병력)",
            font=FONTS["form_label"],
            bg=COLORS["bg_white"],
            fg=COLORS["text_primary"],
            anchor=tk.W,
        ).pack(fill=tk.X)

        # 체크박스 영역
        check_frame = tk.Frame(field_frame, bg=COLORS["bg_white"])
        check_frame.pack(fill=tk.X, pady=(5, 0))

        tk.Checkbutton(
            check_frame,
            text="고혈압",
            variable=self.med_hypertension_var,
            font=FONTS["form_input"],
            bg=COLORS["bg_white"],
            fg=COLORS["text_primary"],
            selectcolor=COLORS["bg_white"],
            activebackground=COLORS["bg_white"],
        ).pack(side=tk.LEFT, padx=(0, 15))

        tk.Checkbutton(
            check_frame,
            text="당뇨병",
            variable=self.med_diabetes_var,
            font=FONTS["form_input"],
            bg=COLORS["bg_white"],
            fg=COLORS["text_primary"],
            selectcolor=COLORS["bg_white"],
            activebackground=COLORS["bg_white"],
        ).pack(side=tk.LEFT, padx=(0, 15))

        tk.Checkbutton(
            check_frame,
            text="고지혈증",
            variable=self.med_hyperlipidemia_var,
            font=FONTS["form_input"],
            bg=COLORS["bg_white"],
            fg=COLORS["text_primary"],
            selectcolor=COLORS["bg_white"],
            activebackground=COLORS["bg_white"],
        ).pack(side=tk.LEFT)

    def _create_hospitalized_field(self, parent: tk.Frame):
        """입원/수술 이력 체크박스 + 상세 입력"""
        field_frame = tk.Frame(parent, bg=COLORS["bg_white"])
        field_frame.pack(fill=tk.X, pady=(8, 0))

        # 체크박스
        tk.Checkbutton(
            field_frame,
            text="입원 또는 수술 이력 있음",
            variable=self.med_hospitalized_var,
            font=FONTS["form_input"],
            bg=COLORS["bg_white"],
            fg=COLORS["text_primary"],
            selectcolor=COLORS["bg_white"],
            activebackground=COLORS["bg_white"],
            command=self._on_hospitalized_changed,
        ).pack(anchor=tk.W)

        # 상세 입력란 (조건부 표시)
        self.hospital_detail_frame = tk.Frame(field_frame, bg=COLORS["bg_white"])
        self.hospital_detail_frame.pack(fill=tk.X, pady=(5, 0))

        detail_container = tk.Frame(self.hospital_detail_frame, bg=COLORS["border"], bd=0)
        detail_container.pack(fill=tk.X)

        self.hospital_detail_text = tk.Text(
            detail_container,
            height=2,
            font=FONTS["form_input"],
            bg=COLORS["bg_white"],
            fg=COLORS["text_primary"],
            insertbackground=COLORS["primary"],
            wrap=tk.WORD,
            relief="flat",
            bd=0,
        )
        self.hospital_detail_text.pack(fill=tk.X, padx=2, pady=2, ipady=3)

        # 기존 데이터 로드
        if self.is_edit_mode and self.customer.med_hospital_detail:
            self.hospital_detail_text.insert("1.0", self.customer.med_hospital_detail)

        # 초기 상태 설정
        self._on_hospitalized_changed()

    def _on_hospitalized_changed(self):
        """입원/수술 체크박스 변경 시 상세 입력란 표시/숨김"""
        if self.med_hospitalized_var.get():
            self.hospital_detail_frame.pack(fill=tk.X, pady=(5, 0))
        else:
            self.hospital_detail_frame.pack_forget()

    def _create_recent_exam_field(self, parent: tk.Frame):
        """최근 3개월 진찰 소견 라디오버튼 + 상세 입력"""
        field_frame = tk.Frame(parent, bg=COLORS["bg_white"])
        field_frame.pack(fill=tk.X, pady=(8, 0))

        # 질문 라벨 (긴 텍스트)
        question_label = tk.Label(
            field_frame,
            text="최근 3개월 이내 의사로부터 진찰 또는 검사(건강검진 포함)를\n통하여 입원, 수술, 추가검사, 재검사 필요 소견을 받은 사실이 있었습니까?",
            font=FONTS["form_label"],
            bg=COLORS["bg_white"],
            fg=COLORS["text_primary"],
            anchor=tk.W,
            justify=tk.LEFT,
        )
        question_label.pack(fill=tk.X, pady=(0, 5))

        # 라디오버튼 영역
        radio_frame = tk.Frame(field_frame, bg=COLORS["bg_white"])
        radio_frame.pack(fill=tk.X, pady=(5, 0))

        tk.Radiobutton(
            radio_frame,
            text="예",
            variable=self.med_recent_exam_var,
            value=True,
            font=FONTS["form_input"],
            bg=COLORS["bg_white"],
            fg=COLORS["text_primary"],
            selectcolor=COLORS["bg_white"],
            activebackground=COLORS["bg_white"],
            command=self._on_recent_exam_changed,
        ).pack(side=tk.LEFT, padx=(0, 15))

        tk.Radiobutton(
            radio_frame,
            text="아니오",
            variable=self.med_recent_exam_var,
            value=False,
            font=FONTS["form_input"],
            bg=COLORS["bg_white"],
            fg=COLORS["text_primary"],
            selectcolor=COLORS["bg_white"],
            activebackground=COLORS["bg_white"],
            command=self._on_recent_exam_changed,
        ).pack(side=tk.LEFT)

        # 상세 입력란 (조건부 표시)
        self.recent_exam_detail_frame = tk.Frame(field_frame, bg=COLORS["bg_white"])
        self.recent_exam_detail_frame.pack(fill=tk.X, pady=(5, 0))

        detail_container = tk.Frame(self.recent_exam_detail_frame, bg=COLORS["border"], bd=0)
        detail_container.pack(fill=tk.X)

        self.recent_exam_detail_text = tk.Text(
            detail_container,
            height=2,
            font=FONTS["form_input"],
            bg=COLORS["bg_white"],
            fg=COLORS["text_primary"],
            insertbackground=COLORS["primary"],
            wrap=tk.WORD,
            relief="flat",
            bd=0,
        )
        self.recent_exam_detail_text.pack(fill=tk.X, padx=2, pady=2, ipady=3)

        # 기존 데이터 로드
        if self.is_edit_mode and self.customer.med_recent_exam_detail:
            self.recent_exam_detail_text.insert("1.0", self.customer.med_recent_exam_detail)

        # 초기 상태 설정
        self._on_recent_exam_changed()

    def _on_recent_exam_changed(self):
        """최근 3개월 진찰 라디오버튼 변경 시 상세 입력란 표시/숨김"""
        if self.med_recent_exam_var.get():
            self.recent_exam_detail_frame.pack(fill=tk.X, pady=(5, 0))
        else:
            self.recent_exam_detail_frame.pack_forget()

    def _create_5yr_diagnosis_field(self, parent: tk.Frame):
        """5년 이내 진단 체크박스 필드"""
        field_frame = tk.Frame(parent, bg=COLORS["bg_white"])
        field_frame.pack(fill=tk.X, pady=(8, 0))

        # 라벨
        tk.Label(
            field_frame,
            text="5년 이내 진단",
            font=FONTS["form_label"],
            bg=COLORS["bg_white"],
            fg=COLORS["text_primary"],
            anchor=tk.W,
        ).pack(fill=tk.X)

        # 체크박스 영역 (1행)
        check_frame_1 = tk.Frame(field_frame, bg=COLORS["bg_white"])
        check_frame_1.pack(fill=tk.X, pady=(5, 0))

        tk.Checkbutton(
            check_frame_1,
            text="암",
            variable=self.med_cancer_var,
            font=FONTS["form_input"],
            bg=COLORS["bg_white"],
            fg=COLORS["text_primary"],
            selectcolor=COLORS["bg_white"],
            activebackground=COLORS["bg_white"],
        ).pack(side=tk.LEFT, padx=(0, 15))

        tk.Checkbutton(
            check_frame_1,
            text="뇌졸중",
            variable=self.med_stroke_var,
            font=FONTS["form_input"],
            bg=COLORS["bg_white"],
            fg=COLORS["text_primary"],
            selectcolor=COLORS["bg_white"],
            activebackground=COLORS["bg_white"],
        ).pack(side=tk.LEFT, padx=(0, 15))

        tk.Checkbutton(
            check_frame_1,
            text="뇌출혈",
            variable=self.med_hemorrhage_var,
            font=FONTS["form_input"],
            bg=COLORS["bg_white"],
            fg=COLORS["text_primary"],
            selectcolor=COLORS["bg_white"],
            activebackground=COLORS["bg_white"],
        ).pack(side=tk.LEFT, padx=(0, 15))

        tk.Checkbutton(
            check_frame_1,
            text="심근경색",
            variable=self.med_infarction_var,
            font=FONTS["form_input"],
            bg=COLORS["bg_white"],
            fg=COLORS["text_primary"],
            selectcolor=COLORS["bg_white"],
            activebackground=COLORS["bg_white"],
        ).pack(side=tk.LEFT)

        # 체크박스 영역 (2행 - 새 항목)
        check_frame_2 = tk.Frame(field_frame, bg=COLORS["bg_white"])
        check_frame_2.pack(fill=tk.X, pady=(5, 0))

        tk.Checkbutton(
            check_frame_2,
            text="협심증",
            variable=self.med_angina_var,
            font=FONTS["form_input"],
            bg=COLORS["bg_white"],
            fg=COLORS["text_primary"],
            selectcolor=COLORS["bg_white"],
            activebackground=COLORS["bg_white"],
        ).pack(side=tk.LEFT, padx=(0, 15))

        tk.Checkbutton(
            check_frame_2,
            text="심장판막증",
            variable=self.med_valve_var,
            font=FONTS["form_input"],
            bg=COLORS["bg_white"],
            fg=COLORS["text_primary"],
            selectcolor=COLORS["bg_white"],
            activebackground=COLORS["bg_white"],
        ).pack(side=tk.LEFT, padx=(0, 15))

        tk.Checkbutton(
            check_frame_2,
            text="간경화증",
            variable=self.med_cirrhosis_var,
            font=FONTS["form_input"],
            bg=COLORS["bg_white"],
            fg=COLORS["text_primary"],
            selectcolor=COLORS["bg_white"],
            activebackground=COLORS["bg_white"],
        ).pack(side=tk.LEFT)

        # 사용자 정의 진단 입력란
        custom_frame = tk.Frame(field_frame, bg=COLORS["bg_white"])
        custom_frame.pack(fill=tk.X, pady=(8, 0))

        tk.Label(
            custom_frame,
            text="기타:",
            font=FONTS["form_input"],
            bg=COLORS["bg_white"],
            fg=COLORS["text_primary"],
        ).pack(side=tk.LEFT, padx=(0, 5))

        entry_container = tk.Frame(custom_frame, bg=COLORS["border"], bd=0)
        entry_container.pack(side=tk.LEFT, fill=tk.X, expand=True)

        custom_entry = tk.Entry(
            entry_container,
            textvariable=self.custom_diagnosis_var,
            font=FONTS["form_input"],
            bg=COLORS["bg_white"],
            fg=COLORS["text_primary"],
            insertbackground=COLORS["primary"],
            relief="flat",
            bd=0,
        )
        custom_entry.pack(fill=tk.X, ipady=4, padx=2, pady=2)

    def _create_notification_field(self, parent: tk.Frame):
        """고지 내용 Text 입력란"""
        field_frame = tk.Frame(parent, bg=COLORS["bg_white"])
        field_frame.pack(fill=tk.X, pady=(8, 0))

        # 라벨
        tk.Label(
            field_frame,
            text="고지 내용",
            font=FONTS["form_label"],
            bg=COLORS["bg_white"],
            fg=COLORS["text_primary"],
            anchor=tk.W,
        ).pack(fill=tk.X)

        # Text 입력란
        text_container = tk.Frame(field_frame, bg=COLORS["border"], bd=0)
        text_container.pack(fill=tk.X, pady=(5, 0))

        self.notification_text = tk.Text(
            text_container,
            height=3,
            font=FONTS["form_input"],
            bg=COLORS["bg_white"],
            fg=COLORS["text_primary"],
            insertbackground=COLORS["primary"],
            wrap=tk.WORD,
            relief="flat",
            bd=0,
        )
        self.notification_text.pack(fill=tk.X, padx=2, pady=2, ipady=3)

        # 기존 데이터 로드
        if self.is_edit_mode and self.customer.notification_content:
            self.notification_text.insert("1.0", self.customer.notification_content)

    def _create_memo_field(self, parent: tk.Frame):
        """메모 Text 입력란"""
        field_frame = tk.Frame(parent, bg=COLORS["bg_white"])
        field_frame.pack(fill=tk.X, pady=(8, 0))

        # 라벨
        tk.Label(
            field_frame,
            text="메모",
            font=FONTS["form_label"],
            bg=COLORS["bg_white"],
            fg=COLORS["text_primary"],
            anchor=tk.W,
        ).pack(fill=tk.X)

        # Text 입력란
        text_container = tk.Frame(field_frame, bg=COLORS["border"], bd=0)
        text_container.pack(fill=tk.X, pady=(5, 0))

        self.memo_text = tk.Text(
            text_container,
            height=3,
            font=FONTS["form_input"],
            bg=COLORS["bg_white"],
            fg=COLORS["text_primary"],
            insertbackground=COLORS["primary"],
            wrap=tk.WORD,
            relief="flat",
            bd=0,
        )
        self.memo_text.pack(fill=tk.X, padx=2, pady=2, ipady=3)

        # 기존 데이터 로드
        if self.is_edit_mode and self.customer.memo:
            self.memo_text.insert("1.0", self.customer.memo)

    def _validate_inputs(self) -> bool:
        """입력 검증"""
        # 이름 검증
        name = self.name_var.get().strip()
        is_valid, error = validate_name(name)
        if not is_valid:
            messagebox.showerror("입력 오류", error)
            return False

        # 전화번호 검증
        phone = self.phone_var.get().strip()
        is_valid, error = validate_phone(phone)
        if not is_valid:
            messagebox.showerror("입력 오류", error)
            return False

        # 주민등록번호 검증
        resident_id = f"{self.resident_id_front_var.get().strip()}-{self.resident_id_back_var.get().strip()}"
        is_valid, error = validate_resident_id(resident_id)
        if not is_valid:
            messagebox.showerror("입력 오류", error)
            return False

        return True

    def _on_save(self):
        """저장 버튼 클릭 핸들러"""
        # 입력 검증
        if not self._validate_inputs():
            return

        # 약 복용 리스트
        medications = []
        if self.med_hypertension_var.get():
            medications.append("고혈압")
        if self.med_diabetes_var.get():
            medications.append("당뇨병")
        if self.med_hyperlipidemia_var.get():
            medications.append("고지혈증")
        med_medication_str = ",".join(medications) if medications else None

        # 영업용 상세
        commercial_details = []
        if self.commercial_taxi_var.get():
            commercial_details.append("taxi")
        if self.commercial_construction_var.get():
            commercial_details.append("construction")
        commercial_detail_str = ",".join(commercial_details) if commercial_details else None

        # 5년 이내 진단
        diagnoses = []
        if self.med_cancer_var.get():
            diagnoses.append("암")
        if self.med_stroke_var.get():
            diagnoses.append("뇌졸중")
        if self.med_hemorrhage_var.get():
            diagnoses.append("뇌출혈")
        if self.med_infarction_var.get():
            diagnoses.append("심근경색")
        if self.med_angina_var.get():
            diagnoses.append("협심증")
        if self.med_valve_var.get():
            diagnoses.append("심장판막증")
        if self.med_cirrhosis_var.get():
            diagnoses.append("간경화증")
        diagnosis_str = ",".join(diagnoses) if diagnoses else None

        # 입원/수술 상세
        hospital_detail = self.hospital_detail_text.get("1.0", tk.END).strip() or None

        # 최근 3개월 진찰 상세
        recent_exam_detail = self.recent_exam_detail_text.get("1.0", tk.END).strip() or None

        # 사용자 정의 진단
        custom_diagnosis = self.custom_diagnosis_var.get().strip() or None

        # 주민등록번호
        resident_id = f"{self.resident_id_front_var.get().strip()}-{self.resident_id_back_var.get().strip()}"

        # 고객 객체 생성
        customer = Customer(
            name=self.name_var.get().strip(),
            phone=self.phone_var.get().strip(),
            resident_id=resident_id,
            birth_date=None,  # 주민번호로 대체됨
            address=self.address_var.get().strip() or None,
            email=None,
            memo=self.memo_text.get("1.0", tk.END).strip() or None,
            occupation=self.occupation_var.get().strip() or None,
            driving_type=self.driving_type_var.get(),
            commercial_detail=commercial_detail_str,
            payment_method=self.payment_method_var.get() or None,
            med_medication=med_medication_str,
            med_hospitalized=self.med_hospitalized_var.get(),
            med_hospital_detail=hospital_detail,
            med_recent_exam=self.med_recent_exam_var.get(),
            med_recent_exam_detail=recent_exam_detail,
            med_5yr_diagnosis=diagnosis_str,
            med_5yr_custom=custom_diagnosis,
            notification_content=self.notification_text.get("1.0", tk.END).strip() or None,
        )

        # 수정 모드인 경우 ID 유지
        if self.is_edit_mode:
            customer.id = self.customer.id
            customer.created_at = self.customer.created_at

        # 콜백 호출
        if self.on_save:
            try:
                self.on_save(customer)
                self.window.destroy()
            except Exception as e:
                messagebox.showerror("저장 실패", f"오류가 발생했습니다:\n{e}")
        else:
            self.window.destroy()

    def _on_cancel(self):
        """취소 버튼 클릭 핸들러"""
        self.window.destroy()
