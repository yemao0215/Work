# -*- coding: utf-8 -*-
"""
day_work_timing_daily_zentaoAPI.py
==================================
自动完成「禅道日志 -> 钉钉研发日报」的每日填报（API 模式）：

  1. ZenTaoLogin().login() 获取登录 Session
  2. LogWorkHour(rss, day).zentao_work_log(day) 获取当天所有日志标题
  3. 钉钉桌面端后台打开研发日报，填入日志、次日计划、可见性、定时发送 21:00
  4. 保存并关闭

运行：python day_work_timing_daily_zentaoAPI.py
"""

import datetime
import os
import sys
import time
import traceback

from huaqiu_order_api.HQCHIP_Zentao.login import ZenTaoLogin
from huaqiu_order_api.HQCHIP_Zentao.log_work_hour import LogWorkHour


# ============================================================
# 配置
# ============================================================
DINGTALK_MAIN_HWND = 197698
SEND_HOUR = 21
SEND_MINUTE = 0
NEXT_DAY_PLAN = "测试工作日常安排与跟进处理"

SHOT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "daily_shots")


def log(msg: str) -> None:
    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)


def _set_clipboard(text: str):
    import win32clipboard
    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardData(win32clipboard.CF_UNICODETEXT, text)
    win32clipboard.CloseClipboard()


# ============================================================
# 禅道：API 获取今日日志
# ============================================================
def fetch_today_logs():
    """通过 API 获取今日禅道日志标题列表。"""
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    log(f"登录禅道 API ...")
    rss = ZenTaoLogin().login()
    log(f"获取 {today} 的日志 ...")
    logs = LogWorkHour(rss=rss, start_day=today).zentao_work_log(day=today)
    # 清洗空项
    logs = [t.strip() for t in logs if t and t.strip()]
    log(f"今日日志 {len(logs)} 条：")
    for i, t in enumerate(logs, 1):
        log(f"  {i}. {t}")
    if not logs:
        raise RuntimeError("API 未返回今日日志")
    return logs


# ============================================================
# 钉钉桌面端（静默后台操作）
# ============================================================
def _move_window_offscreen(hwnd: int):
    """把窗口移到屏幕外，用户看不到、鼠标不被抢。"""
    import win32gui
    import win32con
    # 记录原位置以便结束后恢复
    rect = win32gui.GetWindowRect(hwnd)
    # 主屏幕外（左上角为负坐标）
    win32gui.SetWindowPos(hwnd, win32con.HWND_BOTTOM, -3000, -100, rect[2]-rect[0], rect[3]-rect[1],
                          win32con.SWP_NOACTIVATE | win32con.SWP_SHOWWINDOW)
    time.sleep(0.5)
    return rect


def _send_click_to_window(hwnd: int, x: int, y: int):
    """向后台窗口发送 WM_LBUTTONDOWN/UP（不动物理鼠标）。
    x,y 是相对于窗口客户区的坐标。"""
    import win32api
    import win32con
    lparam = win32api.MAKELONG(x, y)
    win32api.PostMessage(hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lparam)
    time.sleep(0.05)
    win32api.PostMessage(hwnd, win32con.WM_LBUTTONUP, 0, lparam)


def _set_clipboard(text: str):
    import win32clipboard
    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardData(win32clipboard.CF_UNICODETEXT, text)
    win32clipboard.CloseClipboard()


def find_dingtalk_hwnd():
    """动态查找钉钉主窗口句柄。"""
    import win32gui
    result = []
    def _cb(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            cn = win32gui.GetClassName(hwnd)
            t = win32gui.GetWindowText(hwnd)
            if cn.startswith("Qt") and t == "钉钉":
                result.append((hwnd, cn, t))
    win32gui.EnumWindows(_cb, None)
    if not result:
        raise RuntimeError("找不到钉钉主窗口，请先打开钉钉并登录")
    log(f"钉钉窗口: {result[0]}")
    return result[0][0]


def fill_dingtalk_desktop(logs: list[str]):
    import win32gui
    import win32con
    from pywinauto import Desktop
    import pyautogui
    pyautogui.FAILSAFE = False

    log("连接钉钉桌面端 ...")
    hwnd = find_dingtalk_hwnd()
    d = Desktop(backend="uia")
    main = d.window(handle=hwnd)

    # 保存鼠标位置，操作完恢复
    orig_mouse = pyautogui.position()
    try:
        # 0) 激活钉钉窗口
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        time.sleep(0.3)
        win32gui.SetForegroundWindow(hwnd)
        time.sleep(1)

        # 1) 点左侧「工作台」
        cx, cy = win32gui.ClientToScreen(hwnd, (0, 0))
        log("点工作台 ...")
        pyautogui.click(cx + 30, cy + 243)
        time.sleep(5)

        # 2) 点「研发日报」
        cef = main.child_window(class_name="CefBrowserWindow")
        log("点研发日报 ...")
        opened = False
        for _ in range(3):
            for el in cef.descendants(control_type="Text"):
                try:
                    if el.element_info.name == "研发日报":
                        el.click_input()
                        opened = True
                        break
                except Exception:
                    continue
            if opened:
                break
            time.sleep(2)
        if not opened:
            raise RuntimeError("找不到研发日报")
        time.sleep(5)

        # 3) 处理草稿对话框（如果弹出来）
        cef = main.child_window(class_name="CefBrowserWindow")
        for el in main.descendants(control_type="Button"):
            try:
                if el.element_info.name == "清空":
                    el.click_input()
                    log("清空旧草稿")
                    time.sleep(3)
                    break
            except Exception:
                continue

        cef = main.child_window(class_name="CefBrowserWindow")

        # 4) 填今日工作内容（找第一个"请输入"）
        log("填今日工作内容 ...")
        content = "\n".join(f"{i}. {t}" for i, t in enumerate(logs, 1))
        placeholders = []
        for el in cef.descendants(control_type="Text"):
            try:
                if el.element_info.name == "请输入":
                    placeholders.append(el)
            except Exception:
                continue
        if not placeholders:
            raise RuntimeError("找不到输入框")
        r = placeholders[0].rectangle()
        pyautogui.click(r.left + 20, r.top + 10)
        time.sleep(0.5)
        pyautogui.hotkey("ctrl", "a")
        time.sleep(0.2)
        _set_clipboard(content)
        pyautogui.hotkey("ctrl", "v")
        time.sleep(1)

        # 5) 填次日计划（找第二个"请输入"）
        log("填次日计划 ...")
        if len(placeholders) >= 2:
            r = placeholders[1].rectangle()
            pyautogui.click(r.left + 20, r.top + 10)
            time.sleep(0.5)
        pyautogui.hotkey("ctrl", "a")
        time.sleep(0.2)
        _set_clipboard(NEXT_DAY_PLAN)
        pyautogui.hotkey("ctrl", "v")
        time.sleep(0.5)

        # 6) 滚动到底部（拖右侧滚动条）
        log("滚动到底部 ...")
        pyautogui.moveTo(1880, 300)
        pyautogui.dragTo(1880, 950, duration=1)
        time.sleep(2)

        # 7) 勾选 CheckBox（用 UIA toggle，rect全0但有效）
        log("勾选仅接收人可见和定时发送 ...")
        for el in cef.descendants(control_type="CheckBox"):
            try:
                n = el.element_info.name or ""
                if "仅接收人可见" in n:
                    if not el.get_toggle_state():
                        el.toggle()
                    time.sleep(0.3)
                elif n == "定时发送":
                    if not el.get_toggle_state():
                        el.toggle()
                    time.sleep(1)
            except Exception:
                continue

        # 8) 设时间 21:00
        now = datetime.datetime.now()
        time_text = now.strftime("%Y-%m-%d") + f" {SEND_HOUR:02d}:{SEND_MINUTE:02d}"
        log(f"设置时间 {time_text}")
        for el in cef.descendants(control_type="Edit"):
            try:
                n = el.element_info.name or ""
                if n == "选择发送时间":
                    el.click_input()
                    time.sleep(0.5)
                    break
            except Exception:
                continue
        pyautogui.hotkey("ctrl", "a")
        time.sleep(0.2)
        _set_clipboard(time_text)
        pyautogui.hotkey("ctrl", "v")
        time.sleep(0.3)
        pyautogui.press("enter")
        time.sleep(2)

        # 9) 点保存
        log("点保存 ...")
        for el in cef.descendants(control_type="Button"):
            try:
                if "保" in (el.element_info.name or ""):
                    el.click_input()
                    time.sleep(3)
                    log("已保存")
                    break
            except Exception:
                continue

        # 10) 关闭日报页面（Ctrl+W关闭标签页）
        log("关闭日报页面 ...")
        time.sleep(1)
        pyautogui.hotkey("ctrl", "w")
        time.sleep(2)

        # 截图确认
        os.makedirs(SHOT_DIR, exist_ok=True)
        shot_path = os.path.join(SHOT_DIR, f"{int(time.time())}_after_save.png")
        pyautogui.screenshot().save(shot_path)
        log(f"截图 -> {shot_path}")

    finally:
        # 恢复鼠标位置
        pyautogui.moveTo(orig_mouse.x, orig_mouse.y)


# ============================================================
# 主流程
# ============================================================
def main():
    log("=" * 60)
    log("禅道API -> 钉钉研发日报 开始")
    log("=" * 60)
    try:
        logs = fetch_today_logs()
        fill_dingtalk_desktop(logs)
        log("=" * 60)
        log("全部完成")
        log("=" * 60)
        # 删除 daily_shots 文件夹
        import shutil
        if os.path.exists(SHOT_DIR):
            shutil.rmtree(SHOT_DIR, ignore_errors=True)
            log(f"已清理 {SHOT_DIR}")
    except Exception as e:
        log(f"!! 失败: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
