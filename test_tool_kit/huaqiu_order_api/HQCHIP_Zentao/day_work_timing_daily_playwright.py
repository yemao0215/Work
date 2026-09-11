# -*- coding: utf-8 -*-
"""
day_work_timing_daily_playwright.py
====================================
自动完成「禅道日志 -> 钉钉研发日报」的每日填报（Playwright 版）：

  1. Playwright 启动 Chromium 打开禅道，未登录则自动登录，抓取今日日志
  2. 钉钉桌面端打开研发日报，填入日志、次日计划、可见性、定时发送 21:00
  3. 保存并关闭

运行：python day_work_timing_daily_playwright.py
"""

import datetime
import os
import re
import sys
import time
import traceback


# ============================================================
# 配置
# ============================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ZENTAO_URL = "https://p.huaqiu.com"
ACCOUNT = "yemao"
PASSWORD = "Ye123456789+"

SEND_HOUR = 21
SEND_MINUTE = 0
NEXT_DAY_PLAN = "测试工作日常安排与跟进处理"

SHOT_DIR = os.path.join(BASE_DIR, "daily_shots")


def log(msg: str) -> None:
    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)


def _set_clipboard(text: str):
    import win32clipboard
    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardData(win32clipboard.CF_UNICODETEXT, text)
    win32clipboard.CloseClipboard()


# ============================================================
# 禅道：Playwright UI 自动化
# ============================================================
def fetch_today_logs_via_quark():
    """用 Playwright 打开禅道，登录，抓取今日日志。"""
    from playwright.sync_api import sync_playwright

    log("启动 Playwright Chromium ...")
    pw = sync_playwright().start()
    # 用 Playwright 自带 Chromium，后台窗口
    browser = pw.chromium.launch(
        headless=False,
        args=[
            "--window-position=-3000,0",
            "--window-size=1400,900",
            "--disable-blink-features=AutomationControlled",
        ],
    )
    context = browser.new_context(viewport=None)
    page = context.new_page()

    try:
        page.goto(ZENTAO_URL, wait_until="domcontentloaded")
        time.sleep(5)
        log(f"当前URL: {page.url}, title: {page.title()}")

        # 判断是否已登录
        if "user-login" in page.url or "登录" in page.title():
            log("未登录，走钉钉登录跳转 ...")
            # 点"钉钉登录"按钮
            btns = page.query_selector_all("button")
            for b in btns:
                txt = b.inner_text() or ""
                if "钉钉" in txt:
                    b.click()
                    break
            time.sleep(6)
            log(f"跳转后URL: {page.url}")

            # 统一登录页点"账号密码登录"
            try:
                page.get_by_text("账号密码登录", exact=False).first.click(timeout=5000)
                time.sleep(2)
            except Exception:
                log("未找到账号密码登录Tab，直接填")

            # 填账号密码
            inputs = page.query_selector_all("input")
            for inp in inputs:
                t = (inp.get_attribute("type") or "text").lower()
                if t == "password":
                    inp.fill(PASSWORD)
                elif t in ("text", ""):
                    ph = inp.get_attribute("placeholder") or ""
                    if "账号" in ph or "用户" in ph or "手机" in ph:
                        inp.fill(ACCOUNT)
            time.sleep(0.5)
            # 点登录按钮
            btns = page.query_selector_all("button")
            for b in btns:
                txt = b.inner_text() or ""
                if "登录" in txt and "钉钉" not in txt:
                    b.click()
                    break
            time.sleep(10)
            log(f"登录后URL: {page.url}")

        # 进日志日历页
        log("打开日志日历 ...")
        page.goto(ZENTAO_URL + "/index.php?m=effort&f=calendar", wait_until="domcontentloaded")
        time.sleep(6)
        os.makedirs(SHOT_DIR, exist_ok=True)
        page.screenshot(path=os.path.join(SHOT_DIR, "02_calendar.png"))

        # 取cookie调API获取日志
        log("取cookie调API获取日志 ...")
        import requests
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        cookies = {c["name"]: c["value"] for c in context.cookies()}
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "X-Requested-With": "XMLHttpRequest",
        }
        api_url = "https://p.huaqiu.com/index.php?m=effort&f=ajaxGetEfforts&userID=29&year=2026"
        resp = requests.get(api_url, cookies=cookies, headers=headers).json()
        logs = []
        if isinstance(resp, list):
            for item in resp:
                if item.get("start") == today and item.get("end") == today:
                    title = item.get("title", "")
                    title = title.replace("[T]", "").replace("-测试", "").replace("amp;", "").strip()
                    if title and title not in logs:
                        logs.append(title)
        log(f"今日日志 {len(logs)} 条：")
        for i, t in enumerate(logs, 1):
            log(f"  {i}. {t}")
        if not logs:
            raise RuntimeError("未抓到今日日志")
        return logs

    finally:
        context.close()
        browser.close()
        pw.stop()


# ============================================================
# 钉钉桌面端
# ============================================================
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

        # 3) 处理草稿对话框
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

        # 4) 填今日工作内容
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

        # 5) 填次日计划
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

        # 6) 滚动到底部
        log("滚动到底部 ...")
        pyautogui.moveTo(1880, 300)
        pyautogui.dragTo(1880, 950, duration=1)
        time.sleep(2)

        # 7) 勾选 CheckBox
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
                if el.element_info.name == "选择发送时间":
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

        # 10) 关闭日报页面
        log("关闭日报页面 ...")
        time.sleep(1)
        pyautogui.hotkey("ctrl", "w")
        time.sleep(2)

        os.makedirs(SHOT_DIR, exist_ok=True)
        shot_path = os.path.join(SHOT_DIR, f"{int(time.time())}_after_save.png")
        pyautogui.screenshot().save(shot_path)
        log(f"截图 -> {shot_path}")

    finally:
        pyautogui.moveTo(orig_mouse.x, orig_mouse.y)


# ============================================================
# 主流程
# ============================================================
def main():
    log("=" * 60)
    log("禅道(Playwright) -> 钉钉研发日报 开始")
    log("=" * 60)
    try:
        logs = fetch_today_logs_via_quark()
        fill_dingtalk_desktop(logs)
        log("=" * 60)
        log("全部完成")
        log("=" * 60)
        # 删除 daily_shots 文件夹
        import shutil
        if os.path.exists(SHOT_DIR):
            shutil.rmtree(SHOT_DIR, ignore_errors=True)
            log(f"已清理 {SHOT_DIR}")
        # 完成后锁屏（仅18:40后执行）
        now_hm = datetime.datetime.now().strftime("%H:%M")
        if now_hm > "18:40":
            import ctypes
            ctypes.windll.user32.LockWorkStation()
            log("已锁屏")
        else:
            log(f"当前时间{now_hm}，未到18:40，不锁屏")
    except Exception as e:
        log(f"!! 失败: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
