# -*- coding: utf-8 -*-
"""
피플라이프 대전행복사업단 - 고객관리 시스템
Entry Point
"""

import sys
import os
from pathlib import Path


def get_base_dir() -> Path:
    """실행 기준 디렉토리 반환 (개발/PyInstaller 모두 대응)

    Returns:
        프로젝트 루트 디렉토리 경로
    """
    if getattr(sys, "frozen", False):
        # PyInstaller exe 실행 시
        return Path(sys.executable).parent
    else:
        # 개발 모드 (src/main.py 기준)
        return Path(__file__).parent.parent


def setup_paths():
    """모듈 검색 경로 설정"""
    base = get_base_dir()

    if getattr(sys, "frozen", False):
        # PyInstaller: 내부 번들 경로
        internal = Path(sys._MEIPASS)
        if str(internal / "src") not in sys.path:
            sys.path.insert(0, str(internal / "src"))
        if str(internal) not in sys.path:
            sys.path.insert(0, str(internal))
    else:
        # 개발 모드
        src_dir = str(Path(__file__).parent)
        if src_dir not in sys.path:
            sys.path.insert(0, src_dir)

    # 작업 디렉토리를 프로젝트 루트로 설정
    os.chdir(str(base))

    # data 디렉토리 자동 생성
    data_dir = base / "data"
    data_dir.mkdir(parents=True, exist_ok=True)


def main():
    """애플리케이션 진입점"""
    import tkinter as tk
    from gui.main_window import MainWindow

    root = tk.Tk()
    app = MainWindow(root)
    app.run()


if __name__ == "__main__":
    setup_paths()
    main()
