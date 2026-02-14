# -*- coding: utf-8 -*-
"""
더미 데이터로 앱 실행
"""

import sys
import os
from pathlib import Path

# src 경로 추가
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# 환경변수 설정 (더미 DB 사용)
os.environ["CRM_DB_PATH"] = str(Path(__file__).parent.parent / "data" / "crm_dummy.db")

# 메인 앱 실행
from main import main

if __name__ == "__main__":
    print("=" * 60)
    print("Running app with DUMMY DATA")
    print(f"Database: {os.environ['CRM_DB_PATH']}")
    print("=" * 60)
    main()
