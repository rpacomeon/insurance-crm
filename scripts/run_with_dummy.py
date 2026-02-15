# -*- coding: utf-8 -*-
"""
더미 데이터로 앱 실행
"""

import sys
import os
import argparse
from pathlib import Path

# src 경로 추가
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# 메인 앱 실행
from main import main


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run app with dummy DB")
    parser.add_argument("--db", type=str, default="crm_dummy.db", help="DB filename under data/")
    args = parser.parse_args()

    os.environ["CRM_DB_PATH"] = str(Path(__file__).parent.parent / "data" / args.db)

    print("=" * 60)
    print("Running app with DUMMY DATA")
    print(f"Database: {os.environ['CRM_DB_PATH']}")
    print("=" * 60)
    main()
