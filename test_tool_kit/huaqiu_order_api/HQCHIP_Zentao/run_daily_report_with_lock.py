# -*- coding: utf-8 -*-
"""
run_daily_report_with_lock.py
==============================
包装脚本：执行原日报脚本，完成后自动锁屏。

不修改原脚本逻辑，只在末尾加锁屏。
用法：python run_daily_report_with_lock.py
"""

import os
import subprocess
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TARGET_SCRIPT = os.path.join(BASE_DIR, "day_work_timing_daily_zentaoAPI.py")
PYTHON = sys.executable


def main():
    # 1. 执行原脚本
    env = os.environ.copy()
    env["PYTHONPATH"] = os.path.join(BASE_DIR, "..", "..")
    result = subprocess.run([PYTHON, TARGET_SCRIPT], env=env)

    # 2. 无论成功失败，完成后锁屏
    import ctypes
    ctypes.windll.user32.LockWorkStation()
    print(f"原脚本退出码: {result.returncode}，已锁屏")


if __name__ == "__main__":
    main()
