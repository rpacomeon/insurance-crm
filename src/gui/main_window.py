# -*- coding: utf-8 -*-
"""
메인 윈도우 - 피플라이프 대전행복사업단 고객관리 (확장 버전)
좌측 테이블 + 우측 상세 패널 레이아웃
생일 인디케이터 + 유병자 인디케이터 + CSV 다운로드
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
from datetime import datetime

from database import DatabaseManager
from models import Customer
from gui.customer_form import CustomerForm
from gui.theme import COLORS, FONTS, SPACING, SIZES, APP_INFO
from utils.file_helpers import backup_database, restore_database
from utils.export_helpers import export_to_csv


class MainWindow:
    """메인 윈도우 클래스 - 확장 버전"""

    def __init__(self, root: tk.Tk):
        """메인 윈도우 초기화

        Args:
            root: tkinter 루트 윈도우
        """
        self.root = root
        self.root.title(APP_INFO["title"])
        self.root.geometry("1400x800")  # 크기 확대
        self.root.configure(bg=COLORS["bg_main"])
        self.root.minsize(1200, 700)

        # 데이터베이스 초기화
        self.db = DatabaseManager("data/crm.db")

        # 선택된 고객 ID
        self.selected_customer_id = None

        # 필터 상태
        self.filter_mode = "all"  # "all" / "birthday" / "medical"

        # 스타일 설정
        self._setup_styles()

        # UI 구성
        self._create_header()
        self._create_search_bar()
        self._create_main_content()  # 좌측 테이블 + 우측 상세 패널
        self._create_footer()

        # 초기 데이터 로드
        self.load_customers()

        # 윈도우 중앙 배치
        self._center_window()

    def _center_window(self):
        """윈도우를 화면 중앙에 배치"""
        self.root.update_idletasks()
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (w // 2)
        y = (self.root.winfo_screenheight() // 2) - (h // 2)
        self.root.geometry(f"{w}x{h}+{x}+{y}")

    def _setup_styles(self):
        """ttk 스타일 설정"""
        style = ttk.Style()
        style.theme_use("clam")

        # Treeview 스타일
        style.configure(
            "Custom.Treeview",
            font=FONTS["table_body"],
            rowheight=SIZES["table_row_height"],
            background=COLORS["table_row_even"],
            fieldbackground=COLORS["table_row_even"],
            foreground=COLORS["text_primary"],
            borderwidth=0,
        )
        style.configure(
            "Custom.Treeview.Heading",
            font=FONTS["table_heading"],
            background=COLORS["table_header_bg"],
            foreground=COLORS["table_header_fg"],
            borderwidth=0,
            relief="flat",
            padding=(10, 8),
        )
        style.map(
            "Custom.Treeview.Heading",
            background=[("active", COLORS["primary_dark"])],
        )
        style.map(
            "Custom.Treeview",
            background=[("selected", COLORS["table_selected"])],
            foreground=[("selected", COLORS["text_primary"])],
        )

        # 스크롤바 스타일
        style.configure(
            "Custom.Vertical.TScrollbar",
            troughcolor=COLORS["bg_main"],
            background=COLORS["primary"],
            arrowcolor=COLORS["text_on_primary"],
            borderwidth=0,
            width=14,
        )

    def _create_header(self):
        """상단 헤더 (브랜드 영역)"""
        header = tk.Frame(
            self.root,
            bg=COLORS["bg_header"],
            height=SIZES["header_height"],
        )
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        # 좌측: 브랜드 타이틀
        brand_frame = tk.Frame(header, bg=COLORS["bg_header"])
        brand_frame.pack(side=tk.LEFT, padx=SPACING["padding_large"])

        tk.Label(
            brand_frame,
            text=APP_INFO["company"],
            font=FONTS["header_title"],
            bg=COLORS["bg_header"],
            fg=COLORS["text_on_primary"],
        ).pack(side=tk.LEFT, pady=SPACING["padding_large"])

        tk.Label(
            brand_frame,
            text="  |  " + APP_INFO["short_title"],
            font=FONTS["body"],
            bg=COLORS["bg_header"],
            fg="#FFE0B2",
        ).pack(side=tk.LEFT, pady=SPACING["padding_large"])

        # 우측: 새 고객 추가 버튼
        btn_add = tk.Button(
            header,
            text="+ 새 고객 추가",
            font=FONTS["button"],
            bg=COLORS["bg_white"],
            fg=COLORS["primary"],
            activebackground="#FFF3E0",
            activeforeground=COLORS["primary_dark"],
            relief="flat",
            bd=0,
            padx=SPACING["button_padx"],
            pady=SPACING["button_pady"],
            cursor="hand2",
            command=self._on_add_customer,
        )
        btn_add.pack(
            side=tk.RIGHT,
            padx=SPACING["padding_large"],
            pady=SPACING["padding_large"],
        )

    def _create_search_bar(self):
        """검색 바"""
        search_frame = tk.Frame(
            self.root,
            bg=COLORS["bg_white"],
            pady=SPACING["padding_medium"],
        )
        search_frame.pack(fill=tk.X, padx=SPACING["padding_large"])

        # 검색 레이블
        tk.Label(
            search_frame,
            text="고객 검색",
            font=FONTS["body_bold"],
            bg=COLORS["bg_white"],
            fg=COLORS["text_primary"],
        ).pack(side=tk.LEFT, padx=(SPACING["padding_medium"], 10))

        # 검색 입력 필드
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self._on_search)

        search_container = tk.Frame(
            search_frame,
            bg=COLORS["border"],
            bd=0,
        )
        search_container.pack(
            side=tk.LEFT,
            fill=tk.X,
            expand=True,
            padx=SPACING["padding_medium"],
        )

        self.search_entry = tk.Entry(
            search_container,
            textvariable=self.search_var,
            font=FONTS["search"],
            bg=COLORS["bg_white"],
            fg=COLORS["text_primary"],
            insertbackground=COLORS["primary"],
            relief="flat",
            bd=0,
        )
        self.search_entry.pack(
            fill=tk.X,
            ipady=10,
            padx=2,
            pady=2,
        )

        # 안내 텍스트
        tk.Label(
            search_frame,
            text="이름/전화번호",
            font=FONTS["small"],
            bg=COLORS["bg_white"],
            fg=COLORS["text_hint"],
        ).pack(side=tk.LEFT, padx=SPACING["padding_medium"])

        # 고객 수 표시
        self.count_label = tk.Label(
            search_frame,
            text="",
            font=FONTS["small"],
            bg=COLORS["bg_white"],
            fg=COLORS["text_secondary"],
        )
        self.count_label.pack(side=tk.RIGHT, padx=SPACING["padding_medium"])

        # 필터 버튼 영역
        filter_frame = tk.Frame(
            self.root,
            bg=COLORS["bg_white"],
            pady=SPACING["padding_small"],
        )
        filter_frame.pack(fill=tk.X, padx=SPACING["padding_large"])

        tk.Label(
            filter_frame,
            text="필터:",
            font=FONTS["body_bold"],
            bg=COLORS["bg_white"],
            fg=COLORS["text_primary"],
        ).pack(side=tk.LEFT, padx=(SPACING["padding_medium"], 10))

        # 필터 버튼들
        self._create_filter_button(filter_frame, "생일자만 보기", "birthday")
        self._create_filter_button(filter_frame, "유병자만 보기", "medical")
        self._create_filter_button(filter_frame, "전체 보기", "all")

        # 필터 상태 표시
        self.filter_status_label = tk.Label(
            filter_frame,
            text="",
            font=FONTS["small"],
            bg=COLORS["bg_white"],
            fg=COLORS["text_secondary"],
        )
        self.filter_status_label.pack(side=tk.LEFT, padx=(20, 0))

    def _create_main_content(self):
        """메인 컨텐츠 영역 (좌측 테이블 + 우측 상세 패널)"""
        # 메인 컨테이너
        main_container = tk.Frame(self.root, bg=COLORS["bg_main"])
        main_container.pack(
            fill=tk.BOTH,
            expand=True,
            padx=SPACING["padding_large"],
            pady=(SPACING["padding_small"], SPACING["padding_medium"]),
        )

        # 좌측: 테이블 영역 (70%)
        table_container = tk.Frame(
            main_container,
            bg=COLORS["bg_white"],
            bd=1,
            relief="solid",
            highlightbackground=COLORS["border"],
            highlightthickness=1,
        )
        table_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        self._create_table(table_container)

        # 우측: 상세 패널 영역 (30%, 고정 폭)
        detail_container = tk.Frame(
            main_container,
            bg=COLORS["bg_white"],
            bd=1,
            relief="solid",
            highlightbackground=COLORS["border"],
            highlightthickness=1,
            width=350,
        )
        detail_container.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(5, 0))
        detail_container.pack_propagate(False)

        self._create_detail_panel(detail_container)

    def _create_table(self, parent: tk.Frame):
        """고객 목록 테이블"""
        # 스크롤바
        scrollbar_y = ttk.Scrollbar(
            parent,
            orient=tk.VERTICAL,
            style="Custom.Vertical.TScrollbar",
        )
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)

        # Treeview 테이블 (컬럼 변경)
        columns = ("생일", "유병", "고객명", "전화번호", "주민번호", "운전", "입금")
        self.tree = ttk.Treeview(
            parent,
            columns=columns,
            show="headings",
            yscrollcommand=scrollbar_y.set,
            style="Custom.Treeview",
            selectmode="browse",
        )
        scrollbar_y.config(command=self.tree.yview)

        # 컬럼 설정
        self.tree.heading("생일", text="🎂", anchor=tk.CENTER)
        self.tree.heading("유병", text="💊", anchor=tk.CENTER)
        self.tree.heading("고객명", text="고객명", anchor=tk.W)
        self.tree.heading("전화번호", text="전화번호", anchor=tk.CENTER)
        self.tree.heading("주민번호", text="주민번호", anchor=tk.CENTER)
        self.tree.heading("운전", text="운전", anchor=tk.CENTER)
        self.tree.heading("입금", text="입금방식", anchor=tk.CENTER)

        self.tree.column("생일", width=40, minwidth=40, anchor=tk.CENTER)
        self.tree.column("유병", width=40, minwidth=40, anchor=tk.CENTER)
        self.tree.column("고객명", width=100, minwidth=80, anchor=tk.W)
        self.tree.column("전화번호", width=130, minwidth=110, anchor=tk.CENTER)
        self.tree.column("주민번호", width=130, minwidth=110, anchor=tk.CENTER)
        self.tree.column("운전", width=80, minwidth=60, anchor=tk.CENTER)
        self.tree.column("입금", width=90, minwidth=70, anchor=tk.CENTER)

        self.tree.pack(fill=tk.BOTH, expand=True)

        # 교대 행 색상 + 인디케이터 색상
        self.tree.tag_configure("odd", background=COLORS["table_row_odd"])
        self.tree.tag_configure("even", background=COLORS["table_row_even"])
        self.tree.tag_configure("birthday", foreground="#FFB300")  # 생일 인디케이터 색상
        self.tree.tag_configure("medical", foreground="#90EE90")  # 유병자 인디케이터 색상 (연두색)

        # 이벤트 바인딩
        self.tree.bind("<<TreeviewSelect>>", self._on_row_select)  # 싱글클릭
        self.tree.bind("<Double-Button-1>", self._on_double_click)  # 더블클릭

    def _create_detail_panel(self, parent: tk.Frame):
        """우측 상세 패널"""
        # 헤더
        header = tk.Frame(parent, bg=COLORS["primary"], height=50)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(
            header,
            text="고객 상세정보",
            font=("Malgun Gothic", 12, "bold"),
            bg=COLORS["primary"],
            fg=COLORS["text_on_primary"],
        ).pack(side=tk.LEFT, padx=15, pady=12)

        # 스크롤 가능한 상세 영역
        self.detail_canvas = tk.Canvas(parent, bg=COLORS["bg_white"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=self.detail_canvas.yview)
        self.detail_frame = tk.Frame(self.detail_canvas, bg=COLORS["bg_white"])

        # scrollregion 안전하게 갱신
        def _update_scroll_region():
            self.detail_frame.update_idletasks()
            bbox = self.detail_canvas.bbox("all")
            if bbox:
                self.detail_canvas.configure(scrollregion=bbox)

        self.detail_frame.bind("<Configure>", lambda e: _update_scroll_region())

        # ✨ 수정: width 추가 (350 - 14 - 16 = 320)
        self.detail_canvas.create_window((0, 0), window=self.detail_frame, anchor="nw", width=320)
        self.detail_canvas.configure(yscrollcommand=scrollbar.set)

        self.detail_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # ✨ 수정: 마우스 휠 바인딩 개선
        def _on_mousewheel(event):
            self.detail_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            return "break"

        self.detail_canvas.bind("<MouseWheel>", _on_mousewheel)
        self.detail_canvas.bind("<Enter>", lambda e: self.detail_canvas.focus_set())

        # 초기 안내 메시지
        self._show_detail_placeholder()

    def _show_detail_placeholder(self):
        """상세 패널에 안내 메시지 표시"""
        for widget in self.detail_frame.winfo_children():
            widget.destroy()

        tk.Label(
            self.detail_frame,
            text="고객을 선택하세요",
            font=FONTS["body"],
            bg=COLORS["bg_white"],
            fg=COLORS["text_hint"],
        ).pack(padx=20, pady=50)

        # ✨ 추가: scrollregion 리셋
        self.detail_frame.update_idletasks()
        self.detail_canvas.configure(scrollregion=(0, 0, 320, 100))

    def _show_customer_detail(self, customer: Customer):
        """상세 패널에 고객 정보 표시"""
        for widget in self.detail_frame.winfo_children():
            widget.destroy()

        inner = tk.Frame(self.detail_frame, bg=COLORS["bg_white"])
        inner.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # ===== 기본 정보 =====
        self._add_section_header(inner, "기본 정보")
        self._add_detail_row(inner, "이름", customer.name)
        self._add_detail_row(inner, "전화", customer.phone)
        self._add_detail_row(inner, "주민", customer.resident_id)
        self._add_detail_row(inner, "주소", customer.address or "-")
        self._add_detail_row(inner, "직업", customer.occupation or "-")

        # ===== 보험 정보 =====
        self._add_section_header(inner, "보험 정보")

        # 운전 여부
        driving_map = {"none": "미운전", "personal": "자가용", "commercial": "영업용"}
        driving_text = driving_map.get(customer.driving_type, customer.driving_type)
        if customer.driving_type == "commercial" and customer.commercial_detail:
            details = customer.commercial_detail.split(",")
            detail_map = {"taxi": "택시", "construction": "건설용"}
            detail_text = ", ".join([detail_map.get(d.strip(), d.strip()) for d in details])
            driving_text += f" ({detail_text})"
        self._add_detail_row(inner, "운전", driving_text)

        self._add_detail_row(inner, "입금", customer.payment_method or "-")

        # ===== 건강 정보 =====
        self._add_section_header(inner, "건강 정보")
        self._add_detail_row(inner, "약복용", customer.med_medication or "-")

        # 최근 3개월 진찰
        recent_exam = "있음" if customer.med_recent_exam else "없음"
        if customer.med_recent_exam_detail:
            recent_exam += f" - {customer.med_recent_exam_detail}"
        self._add_detail_row(inner, "최근진찰", recent_exam)

        # 5년 이내 진단
        diagnosis_display = customer.med_5yr_diagnosis or "-"
        if customer.med_5yr_custom:
            if diagnosis_display == "-":
                diagnosis_display = customer.med_5yr_custom
            else:
                diagnosis_display += f", {customer.med_5yr_custom}"
        self._add_detail_row(inner, "5년진단", diagnosis_display)

        # ===== 고지/메모 =====
        self._add_section_header(inner, "고지/메모")
        self._add_detail_row(inner, "고지", customer.notification_content or "-", multiline=True)
        self._add_detail_row(inner, "메모", customer.memo or "-", multiline=True)

        # ✨ 추가: scrollregion 강제 갱신
        self.detail_frame.update_idletasks()
        bbox = self.detail_canvas.bbox("all")
        if bbox:
            self.detail_canvas.configure(scrollregion=bbox)

    def _add_section_header(self, parent: tk.Frame, title: str):
        """섹션 헤더 추가"""
        frame = tk.Frame(parent, bg=COLORS["bg_white"])
        frame.pack(fill=tk.X, pady=(15, 5))

        tk.Label(
            frame,
            text=f"── {title} ──────────────",
            font=("Malgun Gothic", 10, "bold"),
            bg=COLORS["bg_white"],
            fg=COLORS["text_secondary"],
            anchor=tk.W,
        ).pack(fill=tk.X)

    def _add_detail_row(self, parent: tk.Frame, label: str, value: str, multiline: bool = False):
        """상세 정보 행 추가"""
        frame = tk.Frame(parent, bg=COLORS["bg_white"])
        frame.pack(fill=tk.X, pady=3)

        tk.Label(
            frame,
            text=f"{label}:",
            font=("Malgun Gothic", 9, "bold"),
            bg=COLORS["bg_white"],
            fg=COLORS["text_secondary"],
            anchor=tk.W,
            width=8,
        ).pack(side=tk.LEFT)

        if multiline and len(value) > 30:
            # 여러 줄 텍스트
            text_label = tk.Label(
                frame,
                text=value,
                font=("Malgun Gothic", 9),
                bg=COLORS["bg_white"],
                fg=COLORS["text_primary"],
                anchor=tk.W,
                justify=tk.LEFT,
                wraplength=220,
            )
            text_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        else:
            tk.Label(
                frame,
                text=value,
                font=("Malgun Gothic", 9),
                bg=COLORS["bg_white"],
                fg=COLORS["text_primary"],
                anchor=tk.W,
            ).pack(side=tk.LEFT, fill=tk.X, expand=True)

    def _create_footer(self):
        """하단 버튼 영역"""
        footer = tk.Frame(
            self.root,
            bg=COLORS["bg_white"],
            height=SIZES["footer_height"],
            bd=0,
        )
        footer.pack(
            fill=tk.X,
            padx=SPACING["padding_large"],
            pady=(0, SPACING["padding_medium"]),
        )
        footer.pack_propagate(False)

        # 좌측 버튼 그룹
        left_group = tk.Frame(footer, bg=COLORS["bg_white"])
        left_group.pack(side=tk.LEFT, fill=tk.Y, pady=SPACING["padding_medium"])

        self._create_button(left_group, "수정", COLORS["btn_edit"], self._on_edit_customer)
        self._create_button(left_group, "삭제", COLORS["btn_delete"], self._on_delete_customer)

        # ✨ 추가: 카톡 복사 버튼 (수정/삭제 옆)
        self.btn_copy_kakao = self._create_button(
            left_group,
            "📋 카톡 복사",
            COLORS["primary"],
            self._on_copy_kakao
        )
        self.btn_copy_kakao.config(state="disabled")  # 초기에는 비활성화

        # 구분선
        separator = tk.Frame(left_group, bg=COLORS["border"], width=2)
        separator.pack(side=tk.LEFT, fill=tk.Y, padx=12, pady=5)

        self._create_button(left_group, "백업", COLORS["btn_backup"], self._on_backup)
        self._create_button(left_group, "복원", COLORS["btn_restore"], self._on_restore)
        self._create_button(left_group, "CSV 다운로드", COLORS["btn_refresh"], self._on_csv_download)
        self._create_button(left_group, "새로고침", COLORS["btn_refresh"], self.load_customers)

        # 우측: 종료 버튼
        self._create_button(footer, "종료", COLORS["btn_exit"], self._on_exit, side=tk.RIGHT)

    def _create_button(
        self,
        parent: tk.Frame,
        text: str,
        color: str,
        command,
        side: str = tk.LEFT,
    ):
        """통일된 스타일의 버튼 생성"""
        btn = tk.Button(
            parent,
            text=text,
            font=FONTS["button_small"],
            bg=color,
            fg=COLORS["text_on_primary"],
            activebackground=color,
            activeforeground=COLORS["text_on_primary"],
            relief="flat",
            bd=0,
            padx=SPACING["button_padx"],
            pady=10,
            cursor="hand2",
            command=command,
        )
        btn.pack(side=side, padx=4)
        return btn

    def _create_filter_button(self, parent: tk.Frame, text: str, mode: str):
        """필터 버튼 생성"""
        btn = tk.Button(
            parent,
            text=text,
            font=FONTS["small"],
            bg=COLORS["bg_main"],
            fg=COLORS["text_primary"],
            activebackground=COLORS["primary"],
            activeforeground=COLORS["text_on_primary"],
            relief="flat",
            bd=0,
            padx=12,
            pady=6,
            cursor="hand2",
            command=lambda: self._apply_filter(mode),
        )
        btn.pack(side=tk.LEFT, padx=2)
        return btn

    def load_customers(self, customers=None):
        """고객 목록을 테이블에 로드"""
        # 기존 데이터 삭제
        for item in self.tree.get_children():
            self.tree.delete(item)

        # 고객 데이터 로드
        if customers is None:
            customers = self.db.get_all_customers()

        # 오늘 날짜 (MM-DD)
        today = datetime.now().strftime("%m-%d")

        # 생일자 및 유병자 카운트
        birthday_count = 0
        medical_count = 0

        # 생일자 우선 정렬 + 필터 적용
        def is_birthday_today(cust):
            """생일인지 확인"""
            if cust.resident_id:
                try:
                    resident_front = cust.resident_id.split("-")[0]
                    if len(resident_front) == 6:
                        birth_mmdd = resident_front[2:4] + "-" + resident_front[4:6]
                        return birth_mmdd == today
                except:
                    pass
            return False

        def is_patient(cust):
            """유병자 여부 판단 (약 복용, 최근 진찰, 5년 진단, 사용자 정의 진단)"""
            return any([
                cust.med_medication,
                cust.med_recent_exam,
                cust.med_5yr_diagnosis,
                cust.med_5yr_custom,
            ])

        # 필터 적용
        filtered_customers = []
        for customer in customers:
            is_bday = is_birthday_today(customer)
            is_med = is_patient(customer)

            if is_bday:
                birthday_count += 1
            if is_med:
                medical_count += 1

            # 필터 모드에 따라 선택
            if self.filter_mode == "birthday" and not is_bday:
                continue
            elif self.filter_mode == "medical" and not is_med:
                continue

            filtered_customers.append(customer)

        # 생일자 우선 정렬
        def sort_key(cust):
            is_bday = is_birthday_today(cust)
            return (0 if is_bday else 1, cust.name)

        filtered_customers.sort(key=sort_key)

        # 테이블에 추가
        for i, customer in enumerate(filtered_customers):
            tag = "odd" if i % 2 else "even"

            # 생일 인디케이터 (촛불)
            birthday_icon = ""
            if is_birthday_today(customer):
                birthday_icon = "🕯️"

            # 유병자 인디케이터 (십자가)
            medical_icon = ""
            if is_patient(customer):
                medical_icon = "✚"

            # 운전 여부
            driving_map = {"none": "미운전", "personal": "자가용", "commercial": "영업용"}
            driving_text = driving_map.get(customer.driving_type, "-")

            # 주민번호 전체 표시 (로컬 전용)
            resident_display = customer.resident_id or "-"

            self.tree.insert(
                "",
                tk.END,
                values=(
                    birthday_icon,
                    medical_icon,
                    customer.name,
                    customer.phone,
                    resident_display,
                    driving_text,
                    customer.payment_method or "-",
                ),
                tags=(tag, str(customer.id)),  # customer.id를 tag에 포함
            )

        # 고객 수 업데이트
        count = len(filtered_customers)
        total_count = len(customers)
        self.count_label.config(text=f"총 {count}명")

        # 필터 상태 표시
        self.filter_status_label.config(
            text=f"(전체 {total_count}명 | 생일자 {birthday_count}명 | 유병자 {medical_count}명)"
        )

    def _apply_filter(self, mode: str):
        """필터 적용"""
        self.filter_mode = mode
        self.load_customers()

    def _on_search(self, *args):
        """검색 이벤트 핸들러"""
        keyword = self.search_var.get().strip()

        if not keyword:
            self.load_customers()
        else:
            results = self.db.search_customers(keyword)
            self.load_customers(results)

    def _on_row_select(self, event):
        """테이블 행 선택 이벤트 (싱글클릭) - 우측 패널 업데이트"""
        selected = self.tree.selection()
        if not selected:
            self._show_detail_placeholder()
            # ✨ 추가: 카톡 복사 버튼 비활성화
            self.btn_copy_kakao.config(state="disabled")
            return

        # 선택된 행의 customer.id 찾기
        item = self.tree.item(selected[0])
        tags = item["tags"]

        # tags에서 customer.id 추출 (숫자인 tag)
        customer_id = None
        for tag in tags:
            try:
                customer_id = int(tag)
                break
            except ValueError:
                continue

        if customer_id is None:
            self._show_detail_placeholder()
            # ✨ 추가: 카톡 복사 버튼 비활성화
            self.btn_copy_kakao.config(state="disabled")
            return

        # 고객 정보 조회 및 표시
        customer = self.db.get_customer(customer_id)
        if customer:
            self.selected_customer_id = customer_id
            self._show_customer_detail(customer)
            # ✨ 추가: 카톡 복사 버튼 활성화
            self.btn_copy_kakao.config(state="normal")
        else:
            self._show_detail_placeholder()
            # ✨ 추가: 카톡 복사 버튼 비활성화
            self.btn_copy_kakao.config(state="disabled")

    def _on_add_customer(self):
        """새 고객 추가 버튼 핸들러"""
        def save_customer(customer: Customer):
            """고객 저장 콜백"""
            try:
                self.db.add_customer(customer)
                messagebox.showinfo(
                    "추가 완료",
                    f"{customer.name}님이 추가되었습니다.",
                )
                self.load_customers()
            except Exception as e:
                raise Exception(f"고객 추가 실패: {e}")

        CustomerForm(self.root, on_save=save_customer)

    def _on_edit_customer(self):
        """수정 버튼 핸들러"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning(
                "선택 필요",
                "수정할 고객을 목록에서 선택해주세요.",
            )
            return

        # tags에서 customer.id 추출
        item = self.tree.item(selected[0])
        tags = item["tags"]

        customer_id = None
        for tag in tags:
            try:
                customer_id = int(tag)
                break
            except ValueError:
                continue

        if customer_id is None:
            messagebox.showerror("오류", "고객 정보를 찾을 수 없습니다.")
            return

        customer = self.db.get_customer(customer_id)
        if not customer:
            messagebox.showerror("오류", "고객 정보를 찾을 수 없습니다.")
            return

        def save_customer(updated_customer: Customer):
            """고객 수정 콜백"""
            try:
                self.db.update_customer(updated_customer)
                messagebox.showinfo(
                    "수정 완료",
                    f"{updated_customer.name}님의 정보가 수정되었습니다.",
                )
                self.load_customers()
                # 우측 패널 갱신
                if self.selected_customer_id == customer_id:
                    self._show_customer_detail(updated_customer)
            except Exception as e:
                raise Exception(f"고객 수정 실패: {e}")

        CustomerForm(self.root, customer=customer, on_save=save_customer)

    def _on_delete_customer(self):
        """삭제 버튼 핸들러"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning(
                "선택 필요",
                "삭제할 고객을 목록에서 선택해주세요.",
            )
            return

        item = self.tree.item(selected[0])
        values = item["values"]
        customer_name = values[2]  # 고객명

        # tags에서 customer.id 추출
        tags = item["tags"]
        customer_id = None
        for tag in tags:
            try:
                customer_id = int(tag)
                break
            except ValueError:
                continue

        if not messagebox.askyesno(
            "삭제 확인",
            f"{customer_name}님의 정보를 삭제하시겠습니까?\n\n이 작업은 되돌릴 수 없습니다.",
        ):
            return

        try:
            if self.db.delete_customer(customer_id):
                messagebox.showinfo("삭제 완료", f"{customer_name}님이 삭제되었습니다.")
                self.load_customers()
                self._show_detail_placeholder()
            else:
                messagebox.showerror("오류", "고객 삭제에 실패했습니다.")
        except Exception as e:
            messagebox.showerror("오류", f"삭제 중 오류 발생:\n{e}")

    def _on_copy_kakao(self):
        """카톡 복사 버튼 핸들러"""
        if self.selected_customer_id is None:
            messagebox.showwarning("선택 필요", "복사할 고객을 선택해주세요.")
            return

        customer = self.db.get_customer(self.selected_customer_id)
        if customer:
            self._copy_to_clipboard(customer)
        else:
            messagebox.showerror("오류", "고객 정보를 찾을 수 없습니다.")

    def _on_backup(self):
        """백업 버튼 핸들러"""
        backup_path = filedialog.asksaveasfilename(
            title="백업 파일 저장 위치 선택",
            defaultextension=".db",
            filetypes=[("Database files", "*.db"), ("All files", "*.*")],
            initialfile=f"crm_backup_{Path('data/crm.db').stem}.db",
        )

        if not backup_path:
            return

        try:
            db_path = Path("data/crm.db")
            backup_dir = Path(backup_path).parent

            success, result_path, error = backup_database(db_path, backup_dir)

            if success:
                import shutil

                shutil.move(result_path, backup_path)
                messagebox.showinfo(
                    "백업 완료",
                    f"백업이 완료되었습니다.\n\n저장 위치:\n{backup_path}",
                )
            else:
                messagebox.showerror("백업 실패", error)
        except Exception as e:
            messagebox.showerror("오류", f"백업 중 오류 발생:\n{e}")

    def _on_restore(self):
        """복원 버튼 핸들러"""
        if not messagebox.askyesno(
            "복원 확인",
            "백업 파일로 복원하면 현재 데이터가 모두 교체됩니다.\n\n계속하시겠습니까?",
        ):
            return

        backup_path = filedialog.askopenfilename(
            title="복원할 백업 파일 선택",
            filetypes=[("Database files", "*.db"), ("All files", "*.*")],
        )

        if not backup_path:
            return

        try:
            self.db.close()

            db_path = Path("data/crm.db")
            success, error = restore_database(Path(backup_path), db_path)

            self.db = DatabaseManager("data/crm.db")

            if success:
                messagebox.showinfo("복원 완료", "백업 파일로 복원되었습니다.")
                self.load_customers()
            else:
                messagebox.showerror("복원 실패", error)
        except Exception as e:
            messagebox.showerror("오류", f"복원 중 오류 발생:\n{e}")

    def _on_csv_download(self):
        """CSV 다운로드 버튼 핸들러"""
        # 저장 위치 선택
        today_str = datetime.now().strftime("%Y%m%d")
        csv_path = filedialog.asksaveasfilename(
            title="CSV 파일 저장 위치 선택",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=f"고객목록_{today_str}.csv",
        )

        if not csv_path:
            return

        try:
            # 전체 고객 데이터 조회
            customers = self.db.get_all_customers()

            # CSV 내보내기
            success, error = export_to_csv(customers, csv_path)

            if success:
                messagebox.showinfo(
                    "다운로드 완료",
                    f"CSV 파일이 저장되었습니다.\n\n저장 위치:\n{csv_path}",
                )
            else:
                messagebox.showerror("다운로드 실패", error)
        except Exception as e:
            messagebox.showerror("오류", f"CSV 다운로드 중 오류 발생:\n{e}")

    def _on_double_click(self, event):
        """테이블 더블클릭 이벤트 (수정 기능 호출)"""
        self._on_edit_customer()

    def _copy_to_clipboard(self, customer: Customer):
        """고객 정보를 카카오톡 형식으로 클립보드에 복사"""
        try:
            import pyperclip

            # 운전 정보
            driving_map = {"none": "미운전", "personal": "자가용", "commercial": "영업용"}
            driving_text = driving_map.get(customer.driving_type, "-")
            if customer.driving_type == "commercial" and customer.commercial_detail:
                details = customer.commercial_detail.split(",")
                detail_map = {"taxi": "택시", "construction": "건설용"}
                detail_text = ", ".join([detail_map.get(d.strip(), d.strip()) for d in details])
                driving_text += f" ({detail_text})"

            # 최근 진찰
            recent_exam_text = "아니오"
            if customer.med_recent_exam:
                recent_exam_text = "예"
                if customer.med_recent_exam_detail:
                    recent_exam_text += f" ({customer.med_recent_exam_detail})"

            # 5년 진단
            diagnosis_text = customer.med_5yr_diagnosis or "-"
            if customer.med_5yr_custom:
                if diagnosis_text == "-":
                    diagnosis_text = customer.med_5yr_custom
                else:
                    diagnosis_text += f", {customer.med_5yr_custom}"

            # 카톡 형식 생성
            kakao_format = f"""━━━━━━━━━━━━━━━━━━━━
👤 고객정보

이름: {customer.name}
전화: {customer.phone}
주민: {customer.resident_id}
주소: {customer.address or '-'}
직업: {customer.occupation or '-'}

💼 보험정보
운전: {driving_text}
입금: {customer.payment_method or '-'}

💊 건강정보
약복용: {customer.med_medication or '-'}
최근진찰: {recent_exam_text}
5년진단: {diagnosis_text}

📝 메모
고지: {customer.notification_content or '-'}
메모: {customer.memo or '-'}
━━━━━━━━━━━━━━━━━━━━"""

            # 클립보드에 복사
            pyperclip.copy(kakao_format)

            # 성공 메시지
            messagebox.showinfo(
                "복사 완료",
                "고객 정보가 클립보드에 복사되었습니다.\n카카오톡에 붙여넣기(Ctrl+V) 하세요.",
            )
        except ImportError:
            messagebox.showerror(
                "오류",
                "pyperclip 모듈이 설치되지 않았습니다.\n\n명령어: pip install pyperclip",
            )
        except Exception as e:
            messagebox.showerror("오류", f"클립보드 복사 중 오류 발생:\n{e}")

    def _on_exit(self):
        """종료 버튼 핸들러"""
        if messagebox.askokcancel("종료", "프로그램을 종료하시겠습니까?"):
            self.db.close()
            self.root.quit()

    def run(self):
        """메인 루프 실행"""
        self.root.mainloop()
