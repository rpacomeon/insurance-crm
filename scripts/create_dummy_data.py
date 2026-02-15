# -*- coding: utf-8 -*-
"""
더미 데이터 생성 스크립트 (v2)
30명 고객 + 다양한 보험 계약 + 모든 필드 완벽 채움
"""

import sys
import os
import random
import argparse
from pathlib import Path
from datetime import datetime, timedelta

# src 경로 추가
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from database import DatabaseManager
from models import Customer, Policy


def _generate_extra_customers(start_index: int, count: int):
    """Generate additional random customer rows for load testing."""
    first_names = [
        "민준", "서연", "지훈", "수빈", "예린", "도윤", "하은", "지안", "현우", "유진",
        "태윤", "지수", "서준", "가은", "시우", "나은", "주원", "채원", "윤서", "다은",
    ]
    last_names = ["김", "이", "박", "최", "정", "강", "조", "윤", "장", "임"]
    occupations = ["회사원", "자영업", "공무원", "교사", "간호사", "프리랜서", "기술직", "영업직"]
    addresses = [
        "서울시 강남구", "서울시 마포구", "서울시 송파구", "경기도 성남시",
        "경기도 수원시", "인천시 남동구", "대전시 유성구", "부산시 해운대구",
    ]
    payment_methods = ["계좌이체", "신용카드", "자동이체"]
    driving_types = ["none", "personal", "commercial"]

    rows = []
    for idx in range(count):
        serial = start_index + idx + 1
        name = random.choice(last_names) + random.choice(first_names)
        phone = f"010-{random.randint(1000, 9999)}-{serial:04d}"
        yy = random.randint(70, 99)
        mm = random.randint(1, 12)
        dd = random.randint(1, 28)
        gender = random.choice([1, 2, 3, 4])
        resident_id = f"{yy:02d}{mm:02d}{dd:02d}-{gender}{random.randint(0, 999999):06d}"

        rows.append(
            dict(
                name=name,
                phone=phone,
                resident_id=resident_id,
                address=random.choice(addresses),
                occupation=random.choice(occupations),
                driving_type=random.choice(driving_types),
                payment_method=random.choices(payment_methods, weights=[50, 30, 20], k=1)[0],
                med_medication=random.choice([None, "고혈압약", "당뇨약"]) if random.random() < 0.2 else None,
                med_recent_exam=True if random.random() < 0.15 else False,
                med_5yr_diagnosis=random.choice([None, "암", "뇌졸중"]) if random.random() < 0.1 else None,
                memo=f"LOAD TEST #{serial}",
            )
        )
    return rows


def create_dummy_data(customers_target: int = 30, db_filename: str = "crm_dummy.db"):
    """Dummy customers + policies for manual QA."""

    db_path = Path(__file__).parent.parent / "data" / db_filename
    if db_path.exists():
        try:
            os.remove(db_path)
        except PermissionError:
            print("[WARNING] Cannot remove existing dummy DB (file locked)")
            return

    db = DatabaseManager(str(db_path))
    today = datetime.now()
    today_str = today.strftime("%Y-%m-%d")
    today_mmdd = today.strftime("%m%d")

    # =========================================================================
    # 고객 데이터
    # =========================================================================
    customers_data = [
        # --- 1~5: 생일 오늘 (아이콘 테스트) ---
        dict(
            name="김철수", phone="010-1111-0001",
            resident_id=f"85{today_mmdd}-1234567",
            address="서울시 강남구 테헤란로 123", occupation="회사원",
            driving_type="personal", payment_method="계좌이체",
            med_medication="고혈압약", memo="VIP 고객",
        ),
        dict(
            name="이영희", phone="010-1111-0002",
            resident_id=f"90{today_mmdd}-2345678",
            address="서울시 서초구 서초대로 456", occupation="자영업",
            driving_type="commercial", commercial_detail="taxi",
            payment_method="신용카드",
            med_recent_exam=True, med_recent_exam_detail="종합건강검진",
        ),
        dict(
            name="박민수", phone="010-1111-0003",
            resident_id=f"78{today_mmdd}-1111111",
            address="경기도 성남시 분당구", occupation="프리랜서",
            driving_type="none", payment_method="계좌이체",
            med_medication="당뇨약,고지혈증약", med_5yr_diagnosis="고혈압",
        ),
        dict(
            name="최지현", phone="010-1111-0004",
            resident_id=f"92{today_mmdd}-2222222",
            address="서울시 마포구 합정동", occupation="디자이너",
            driving_type="personal", payment_method="자동이체",
        ),
        dict(
            name="정수진", phone="010-1111-0005",
            resident_id=f"88{today_mmdd}-2333333",
            address="대전시 유성구 봉명동", occupation="교사",
            driving_type="personal", payment_method="자동이체",
            memo="VIP 고객 - 소개 많이 해주심",
        ),

        # --- 6~10: 유병자 (의료 정보 다양) ---
        dict(
            name="강동원", phone="010-2222-0006",
            resident_id="750315-1444444",
            address="부산시 해운대구 중동", occupation="자영업",
            driving_type="personal", payment_method="계좌이체",
            med_medication="고혈압약,당뇨약,고지혈증약",
            med_5yr_diagnosis="고혈압", med_5yr_custom="갑상선 결절",
            notification_content="고혈압+당뇨 고지 완료",
        ),
        dict(
            name="한소희", phone="010-2222-0007",
            resident_id="830720-2555555",
            address="서울시 송파구 잠실동", occupation="간호사",
            driving_type="none", payment_method="신용카드",
            med_medication="갑상선약",
            med_recent_exam=True, med_recent_exam_detail="갑상선 초음파",
            med_hospitalized=True, med_hospital_detail="갑상선 수술 (2024)",
        ),
        dict(
            name="류현진", phone="010-2222-0008",
            resident_id="880605-1666666",
            address="인천시 남동구 구월동", occupation="운동선수",
            driving_type="personal", payment_method="계좌이체",
            med_medication="무릎 관절염약",
            med_hospitalized=True, med_hospital_detail="반월판 수술 (2023)",
            med_5yr_diagnosis="심근경색", notification_content="심근경색 이력 고지",
        ),
        dict(
            name="배수지", phone="010-2222-0009",
            resident_id="940101-2777777",
            address="서울시 강동구 천호동", occupation="배우",
            driving_type="personal", payment_method="자동이체",
            med_recent_exam=True, med_recent_exam_detail="MRI 촬영",
            med_5yr_custom="허리디스크",
        ),
        dict(
            name="공유진", phone="010-2222-0010",
            resident_id="790912-1888888",
            address="경기도 고양시 일산동구", occupation="회사원",
            driving_type="commercial", commercial_detail="construction",
            payment_method="계좌이체",
            med_medication="혈압약",
            med_5yr_diagnosis="뇌졸중", notification_content="뇌졸중 이력 고지",
        ),

        # --- 11~15: 영업용 운전 ---
        dict(
            name="송중기", phone="010-3333-0011",
            resident_id="851025-1999999",
            address="서울시 용산구 이태원로", occupation="택시기사",
            driving_type="commercial", commercial_detail="taxi",
            payment_method="자동이체",
        ),
        dict(
            name="전지현", phone="010-3333-0012",
            resident_id="810430-2000001",
            address="서울시 강북구 수유동", occupation="물류배송",
            driving_type="commercial", commercial_detail="taxi",
            payment_method="계좌이체", memo="배송기사",
        ),
        dict(
            name="이병헌", phone="010-3333-0013",
            resident_id="700815-1000002",
            address="경기도 용인시 수지구", occupation="건설현장소장",
            driving_type="commercial", commercial_detail="construction",
            payment_method="신용카드",
        ),
        dict(
            name="김태리", phone="010-3333-0014",
            resident_id="950203-2000003",
            address="서울시 성동구 성수동", occupation="영업직",
            driving_type="commercial", commercial_detail="taxi",
            payment_method="자동이체",
        ),
        dict(
            name="조인성", phone="010-3333-0015",
            resident_id="810617-1000004",
            address="대구시 수성구 범어동", occupation="운수업",
            driving_type="commercial", commercial_detail="taxi,construction",
            payment_method="계좌이체",
            med_medication="허리디스크약", notification_content="운수업 종사자 고지",
        ),

        # --- 16~20: 일반 (아이콘 없음 예상) ---
        dict(
            name="손예진", phone="010-4444-0016",
            resident_id="821121-2000005",
            address="서울시 종로구 인사동", occupation="공무원",
            driving_type="personal", payment_method="계좌이체",
        ),
        dict(
            name="현빈호", phone="010-4444-0017",
            resident_id="820925-1000006",
            address="서울시 중구 명동", occupation="회사원",
            driving_type="personal", payment_method="신용카드",
        ),
        dict(
            name="유아인", phone="010-4444-0018",
            resident_id="861010-1000007",
            address="서울시 성북구 정릉동", occupation="사업가",
            driving_type="personal", payment_method="자동이체",
        ),
        dict(
            name="김고은", phone="010-4444-0019",
            resident_id="910707-2000008",
            address="광주시 서구 치평동", occupation="약사",
            driving_type="none", payment_method="계좌이체",
        ),
        dict(
            name="서강준", phone="010-4444-0020",
            resident_id="931222-1000009",
            address="울산시 남구 삼산동", occupation="엔지니어",
            driving_type="personal", payment_method="신용카드",
        ),

        # --- 21~25: 복합 케이스 (유병 + 운전 + 메모 등) ---
        dict(
            name="마동석", phone="010-5555-0021",
            resident_id="710310-1000010",
            address="서울시 강서구 화곡동", occupation="개인사업",
            driving_type="commercial", commercial_detail="construction",
            payment_method="계좌이체",
            med_medication="고혈압약,당뇨약",
            med_hospitalized=True, med_hospital_detail="담석 수술 (2025)",
            memo="관리 필요 고객",
        ),
        dict(
            name="한지민", phone="010-5555-0022",
            resident_id="820528-2000011",
            address="제주시 연동", occupation="호텔리어",
            driving_type="personal", payment_method="자동이체",
            med_recent_exam=True, med_recent_exam_detail="유방 초음파",
            notification_content="유방 양성 종양 고지",
        ),
        dict(
            name="이정재", phone="010-5555-0023",
            resident_id="721215-1000012",
            address="서울시 동작구 사당동", occupation="변호사",
            driving_type="personal", payment_method="신용카드",
            med_5yr_diagnosis="암", med_5yr_custom="초기 위암 (완치)",
            notification_content="위암 완치 판정 고지 (2023)",
        ),
        dict(
            name="김선호", phone="010-5555-0024",
            resident_id="860401-1000013",
            address="세종시 나성동", occupation="공무원",
            driving_type="none", payment_method="계좌이체",
            med_medication="고지혈증약",
            memo="세종시 공무원 단체 보험 가입",
        ),
        dict(
            name="전도연", phone="010-5555-0025",
            resident_id="730805-2000014",
            address="서울시 광진구 자양동", occupation="교수",
            driving_type="personal", payment_method="자동이체",
            med_medication="골다공증약",
            med_5yr_diagnosis="고혈압,협심증",
            notification_content="협심증 고지 완료",
        ),

        # --- 26~30: 다양한 추가 케이스 ---
        dict(
            name="위하준", phone="010-6666-0026",
            resident_id="950515-1000015",
            address="경기도 파주시 운정", occupation="프리랜서",
            driving_type="personal", payment_method="신용카드",
        ),
        dict(
            name="김지원", phone="010-6666-0027",
            resident_id="920830-2000016",
            address="서울시 노원구 상계동", occupation="간호사",
            driving_type="none", payment_method="계좌이체",
            med_recent_exam=True, med_recent_exam_detail="건강검진",
        ),
        dict(
            name="박서준", phone="010-6666-0028",
            resident_id="881103-1000017",
            address="서울시 관악구 신림동", occupation="카페사장",
            driving_type="personal", payment_method="자동이체",
            memo="신림점 카페 운영",
        ),
        dict(
            name="수지현", phone="010-6666-0029",
            resident_id="940220-2000018",
            address="경기도 수원시 영통구", occupation="IT개발자",
            driving_type="personal", payment_method="신용카드",
        ),
        dict(
            name="이도현", phone="010-6666-0030",
            resident_id="970718-1000019",
            address="충남 천안시 서북구", occupation="대학원생",
            driving_type="none", payment_method="계좌이체",
            memo="학생 할인 적용",
        ),
    ]

    if customers_target > len(customers_data):
        extra = _generate_extra_customers(len(customers_data), customers_target - len(customers_data))
        customers_data.extend(extra)
    elif customers_target < len(customers_data):
        customers_data = customers_data[:customers_target]

    # =========================================================================
    # 고객 생성
    # =========================================================================
    print(f"\n[Creating {len(customers_data)} Customers]")
    print("=" * 60)

    customer_ids = []
    for i, data in enumerate(customers_data, 1):
        c = Customer(**data)
        cid = db.add_customer(c)
        customer_ids.append(cid)
        tag = ""
        if f"{today_mmdd}" in data.get("resident_id", ""):
            mid = data["resident_id"]
            if mid[2:6] == today_mmdd:
                tag = " [BIRTHDAY]"
        med = ""
        if data.get("med_medication") or data.get("med_5yr_diagnosis") or data.get("med_recent_exam") or data.get("med_5yr_custom"):
            med = " [MEDICAL]"
        drv = ""
        if data.get("driving_type") == "commercial":
            drv = " [COMMERCIAL]"
        print(f"  {i:2d}. {data['name']:<6} ({data['phone']}) ID={cid}{tag}{med}{drv}")

    # =========================================================================
    # 보험 계약 생성 (다양한 시나리오)
    # =========================================================================
    print(f"\n[Creating Policies]")
    print("=" * 60)

    insurers = ["삼성생명", "한화생명", "교보생명", "메리츠화재", "DB손해보험",
                "삼성화재", "현대해상", "KB손해보험", "NH농협생명", "흥국생명"]
    products = ["종신보험", "암보험", "실손보험", "연금보험", "운전자보험",
                "자동차보험", "치아보험", "어린이보험", "저축보험", "화재보험"]
    card_issuers = ["신한카드", "국민카드", "하나카드", "우리카드", "삼성카드",
                    "현대카드", "롯데카드", "BC카드"]

    policy_count = 0

    # 고객 입금방식 → 보험 계약 결제방식 매핑
    customer_pay_map = {
        "신용카드": "card",
        "계좌이체": "transfer",
        "자동이체": "transfer",
    }

    for i, cid in enumerate(customer_ids):
        # 고객별 1~3개 계약
        num_policies = 1 if i < 20 else random.choice([1, 2, 3])
        if i < 5:
            num_policies = 1  # 생일 고객은 1개씩 (명확한 테스트)

        # 고객 입금방식에 맞춰 계약 결제방식 결정
        cust_payment = customers_data[i].get("payment_method", "계좌이체")
        pay_method = customer_pay_map.get(cust_payment, "transfer")

        for j in range(num_policies):
            insurer = random.choice(insurers)
            product = random.choice(products)
            premium = random.choice([30000, 50000, 80000, 100000, 150000, 200000])
            cycle = "monthly"
            billing_day = random.randint(1, 28)

            # 날짜 시나리오 분배
            if i == 0:
                # 고객1: 오늘 납부
                next_pay = today_str
                status = "active"
            elif i == 1:
                # 고객2: 15일 연체
                next_pay = (today - timedelta(days=15)).strftime("%Y-%m-%d")
                status = "active"
            elif i == 2:
                # 고객3: 10일 후
                next_pay = (today + timedelta(days=10)).strftime("%Y-%m-%d")
                status = "active"
            elif i == 3:
                # 고객4: 3일 후
                next_pay = (today + timedelta(days=3)).strftime("%Y-%m-%d")
                status = "active"
            elif i == 4 and j == 0:
                # 고객5: 연체
                next_pay = (today - timedelta(days=5)).strftime("%Y-%m-%d")
                status = "active"
            elif i == 4 and j > 0:
                next_pay = (today + timedelta(days=20)).strftime("%Y-%m-%d")
                status = "active"
            elif 5 <= i <= 9:
                # 유병자: 다양한 날짜
                offset = random.choice([-10, -3, 0, 2, 5, 14, 30])
                next_pay = (today + timedelta(days=offset)).strftime("%Y-%m-%d")
                status = "active"
            elif 10 <= i <= 14:
                # 영업용 운전: 납부 임박/연체 섞기
                offset = random.choice([-7, -2, 1, 3, 6])
                next_pay = (today + timedelta(days=offset)).strftime("%Y-%m-%d")
                status = "active"
            elif 15 <= i <= 19:
                # 일반: 미래 날짜
                offset = random.randint(10, 60)
                next_pay = (today + timedelta(days=offset)).strftime("%Y-%m-%d")
                status = "active"
            elif 20 <= i <= 24:
                # 복합: 다양하게
                if j == 0:
                    offset = random.choice([-8, -1, 0, 2, 7])
                else:
                    offset = random.randint(10, 45)
                next_pay = (today + timedelta(days=offset)).strftime("%Y-%m-%d")
                status = "active"
            else:
                # 대량 데이터에서도 탭 분포가 나오도록 혼합
                offset = random.choice([-20, -10, -5, -2, -1, 0, 1, 2, 3, 5, 7, 10, 20, 35, 50])
                next_pay = (today + timedelta(days=offset)).strftime("%Y-%m-%d")
                status = "active"

            # 카드 정보 (카드 결제일 때만)
            card_issuer = None
            card_number = None
            card_expiry = None
            if pay_method == "card":
                card_issuer = random.choice(card_issuers)
                card_number = f"{random.randint(1000,9999)}-{random.randint(1000,9999)}-{random.randint(1000,9999)}-{random.randint(1000,9999)}"
                card_expiry = f"{random.randint(1,12):02d}/{random.randint(26,30)}"

            policy = Policy(
                customer_id=cid,
                insurer=insurer,
                product_name=product,
                premium=premium,
                payment_method=pay_method,
                billing_cycle=cycle,
                billing_day=billing_day,
                card_issuer=card_issuer,
                card_number=card_number,
                card_expiry=card_expiry,
                contract_start_date=(today - timedelta(days=random.randint(90, 730))).strftime("%Y-%m-%d"),
                next_payment_date=next_pay,
                status=status,
            )
            db.add_policy(policy)
            policy_count += 1

    print(f"  Total policies created: {policy_count}")

    # =========================================================================
    # 연체 상태 자동 갱신
    # =========================================================================
    print(f"\n[Auto-updating payment status]")
    print("=" * 60)
    result = db.auto_update_payment_status()
    print(f"  Updated to overdue: {result['updated']} policies")

    # =========================================================================
    # 검증
    # =========================================================================
    print(f"\n[Verification]")
    print("=" * 60)

    all_customers = db.get_all_customers()
    print(f"  Total customers: {len(all_customers)}")

    upcoming = db.get_upcoming_payments(days_ahead=7)
    print(f"  Upcoming payments (D-7): {len(upcoming)}")
    for p in upcoming:
        print(f"    - {p['customer'].name}: {p['policy'].next_payment_date} (D-{p['days_left']})")

    overdue = db.get_overdue_policies()
    print(f"  Overdue policies: {len(overdue)}")
    for p in overdue:
        print(f"    - {p['customer'].name}: {p['policy'].next_payment_date} ({p['overdue_days']}d overdue)")

    # 아이콘 시뮬레이션
    today_mmdd_dash = today.strftime("%m-%d")
    print(f"\n[Icon Simulation] (today={today_str})")
    print(f"  {'Name':<8} {'Bday':^5} {'Med':^5} {'Pay':^5} {'Over':^5} {'Drive':<12} {'Resident ID':<16}")
    print(f"  {'-'*8} {'-'*5} {'-'*5} {'-'*5} {'-'*5} {'-'*12} {'-'*16}")

    upcoming_cids = {p['customer'].id for p in upcoming}
    overdue_cids = {p['customer'].id for p in overdue}
    today_pay_cids = {p['customer'].id for p in upcoming if p['policy'].next_payment_date == today_str}

    for c in all_customers:
        bday = ""
        if c.resident_id:
            try:
                front = c.resident_id.split("-")[0]
                if len(front) == 6 and front[2:4] + "-" + front[4:6] == today_mmdd_dash:
                    bday = "Y"
            except Exception:
                pass
        med = "Y" if any([c.med_medication, c.med_recent_exam, c.med_5yr_diagnosis, c.med_5yr_custom]) else ""
        pay = "Y" if c.id in today_pay_cids else ""
        ovd = "Y" if c.id in overdue_cids else ""
        drv = c.driving_type or "-"

        print(f"  {c.name:<8} {bday:^5} {med:^5} {pay:^5} {ovd:^5} {drv:<12} {c.resident_id:<16}")

    db.close()

    print(f"\n{'=' * 60}")
    print(f"[SUCCESS] {len(all_customers)} customers + {policy_count} policies created!")
    print(f"Database: {db_path}")
    print(f"\nRun app with dummy data:")
    print(f"  python scripts/run_with_dummy.py --db {db_filename}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create dummy CRM data")
    parser.add_argument("--customers", type=int, default=30, help="Number of customers to create (default: 30)")
    parser.add_argument("--db", type=str, default="crm_dummy.db", help="Output DB filename under data/")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility")
    args = parser.parse_args()

    random.seed(args.seed)
    create_dummy_data(customers_target=args.customers, db_filename=args.db)
