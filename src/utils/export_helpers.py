# -*- coding: utf-8 -*-
"""
CSV 내보내기 헬퍼 함수
"""

import csv
from typing import List, Tuple, Optional
from pathlib import Path

# models.py에서 Customer를 import할 수 없으므로 TYPE_CHECKING 사용
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from models import Customer


def export_to_csv(customers: List, file_path: str) -> Tuple[bool, Optional[str]]:
    """고객 리스트를 CSV 파일로 내보내기

    Args:
        customers: Customer 객체 리스트
        file_path: 저장할 CSV 파일 경로

    Returns:
        (성공 여부, 에러 메시지)
        성공 시: (True, None)
        실패 시: (False, "에러 메시지")

    Example:
        >>> customers = db.get_all_customers()
        >>> success, error = export_to_csv(customers, "customers.csv")
        >>> if success:
        ...     print("CSV 내보내기 성공")
    """
    try:
        # UTF-8 BOM 인코딩 (Excel 한글 호환)
        with open(file_path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)

            # CSV 헤더
            headers = [
                "이름", "전화번호", "주민등록번호", "생년월일", "주소", "이메일",
                "운전여부", "영업상세", "입금방식",
                "약복용", "입원여부", "입원상세", "5년진단",
                "고지내용", "메모", "생성일시", "수정일시"
            ]
            writer.writerow(headers)

            # 데이터 rows
            for customer in customers:
                # 운전여부 변환
                driving_map = {
                    "none": "미운전",
                    "personal": "자가용",
                    "commercial": "영업용"
                }
                driving_text = driving_map.get(customer.driving_type, customer.driving_type)

                # 영업용 상세
                commercial_detail = ""
                if customer.commercial_detail:
                    details = customer.commercial_detail.split(",")
                    detail_map = {"taxi": "택시", "construction": "건설용"}
                    commercial_detail = ", ".join([detail_map.get(d.strip(), d.strip()) for d in details])

                # 입원여부
                hospitalized = "있음" if customer.med_hospitalized else "없음"

                row = [
                    customer.name,
                    customer.phone,
                    customer.resident_id,
                    customer.birth_date or "",
                    customer.address or "",
                    customer.email or "",
                    driving_text,
                    commercial_detail,
                    customer.payment_method or "",
                    customer.med_medication or "",
                    hospitalized,
                    customer.med_hospital_detail or "",
                    customer.med_5yr_diagnosis or "",
                    customer.notification_content or "",
                    customer.memo or "",
                    customer.created_at or "",
                    customer.updated_at or "",
                ]
                writer.writerow(row)

        return (True, None)

    except PermissionError:
        return (False, "파일이 다른 프로그램에서 사용 중입니다. 파일을 닫고 다시 시도해주세요.")
    except Exception as e:
        return (False, f"CSV 내보내기 실패: {str(e)}")
