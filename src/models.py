# -*- coding: utf-8 -*-
"""
Customer 데이터 모델
"""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class Customer:
    """고객 정보 데이터 모델"""

    # 기본 정보
    name: str
    phone: str
    resident_id: str = ""  # 주민등록번호 (필수)
    birth_date: Optional[str] = None
    address: Optional[str] = None
    email: Optional[str] = None
    memo: Optional[str] = None

    # 보험 정보
    driving_type: str = "none"  # 운전 여부: none(미운전)/personal(자가용)/commercial(영업용)
    commercial_detail: Optional[str] = None  # 영업용 상세: taxi, construction (콤마 구분)
    payment_method: Optional[str] = None  # 보험료 입금 방식: 계좌이체/신용카드/자동이체

    # 직업 정보
    occupation: Optional[str] = None  # 직업/사업 (예: 자영업, 회사원, 프리랜서)

    # 건강 정보
    med_medication: Optional[str] = None  # 약 복용 병력 (콤마 구분: 고혈압,당뇨병,고지혈증)
    med_hospitalized: bool = False  # 입원/수술 이력
    med_hospital_detail: Optional[str] = None  # 입원/수술 상세 내용
    med_recent_exam: bool = False  # 최근 3개월 진찰 여부
    med_recent_exam_detail: Optional[str] = None  # 최근 3개월 진찰 상세
    med_5yr_diagnosis: Optional[str] = None  # 5년 이내 진단 (콤마 구분: 암,뇌졸중,뇌출혈,심근경색,협심증,심장판막증,간경화증)
    med_5yr_custom: Optional[str] = None  # 5년 이내 사용자 정의 진단

    # 고지 내용
    notification_content: Optional[str] = None  # 보험 가입 시 고지한 내용

    # 시스템 필드
    id: Optional[int] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    def to_dict(self) -> dict:
        """Customer 객체를 딕셔너리로 변환

        Returns:
            고객 정보 딕셔너리
        """
        return {
            'id': self.id,
            'name': self.name,
            'phone': self.phone,
            'resident_id': self.resident_id,
            'birth_date': self.birth_date,
            'address': self.address,
            'email': self.email,
            'memo': self.memo,
            'occupation': self.occupation,
            'driving_type': self.driving_type,
            'commercial_detail': self.commercial_detail,
            'payment_method': self.payment_method,
            'med_medication': self.med_medication,
            'med_hospitalized': self.med_hospitalized,
            'med_hospital_detail': self.med_hospital_detail,
            'med_recent_exam': self.med_recent_exam,
            'med_recent_exam_detail': self.med_recent_exam_detail,
            'med_5yr_diagnosis': self.med_5yr_diagnosis,
            'med_5yr_custom': self.med_5yr_custom,
            'notification_content': self.notification_content,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
        }

    @staticmethod
    def from_db_row(row: tuple) -> "Customer":
        """데이터베이스 row를 Customer 객체로 변환

        Args:
            row: DB에서 조회한 튜플 (id, name, phone, resident_id, birth_date, address, email, memo,
                 occupation, driving_type, commercial_detail, payment_method,
                 med_medication, med_hospitalized, med_hospital_detail, med_recent_exam, med_recent_exam_detail,
                 med_5yr_diagnosis, med_5yr_custom, notification_content, created_at, updated_at)

        Returns:
            Customer 객체
        """
        return Customer(
            id=row[0],
            name=row[1],
            phone=row[2],
            resident_id=row[3] if row[3] else "",
            birth_date=row[4],
            address=row[5],
            email=row[6],
            memo=row[7],
            occupation=row[8],
            driving_type=row[9] if row[9] else "none",
            commercial_detail=row[10],
            payment_method=row[11],
            med_medication=row[12],
            med_hospitalized=bool(row[13]) if row[13] is not None else False,
            med_hospital_detail=row[14],
            med_recent_exam=bool(row[15]) if row[15] is not None else False,
            med_recent_exam_detail=row[16],
            med_5yr_diagnosis=row[17],
            med_5yr_custom=row[18],
            notification_content=row[19],
            created_at=row[20],
            updated_at=row[21],
        )

    @staticmethod
    def get_current_timestamp() -> str:
        """현재 시간을 문자열로 반환

        Returns:
            현재 시간 (YYYY-MM-DD HH:MM:SS 형식)
        """
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
