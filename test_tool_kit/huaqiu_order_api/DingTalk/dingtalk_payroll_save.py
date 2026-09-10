# -*- coding: utf-8 -*-
"""
钉钉桌面自动化：打开考勤轻应用 -> 我的工资单 -> 点击目标月份工资条的"查看"

修复说明（2026-09-08 实测）：
1. 原脚本用 UIA 后端定位钉钉窗口会失败：钉钉主窗口（Qt51511QWindowIcon）不在
   UIA 顶层窗口枚举中，app.window(title="钉钉") 必然找不到窗口。
   已改为 win32 后端，按标题"钉钉"+可见+面积最大筛选出主窗口。
2. 钉钉主窗口经常处于最小化状态（最小化时窗口矩形被移到屏幕外 -32000 处），
   必须先 restore 再操作。
3. 工作台页面、考勤轻应用页面都是钉钉内嵌 CEF 浏览器渲染的网页：向主窗口投递
   WM_LBUTTONDOWN 不生效（已实测），必须向覆盖目标区域的 CEF 渲染子窗口
   （Chrome_RenderWidgetHostHWND）投递点击。本脚本所有网页内点击均走该通道。
4. 左侧导航"工作台"图标是原生 Qt 控件，直接向主窗口投递即可。
5. 工资条列表规则：今天在当月15日之前（1-14日）-> 查看前两个月记录；
   15日及之后 -> 查看前一个月记录。例如 2026-09-08 -> 2026-07。
6. 点击"查看"后会弹出"请输入查看密码"对话框（工资明细需密码验证）。
   脚本继续：点击密码输入框 -> 逐字符投递 WM_CHAR 输入密码 123456 -> 点击提交。
   密码验证通过后对话框关闭，显示该月工资明细。
   （输入走 PostMessage 通道，不抢焦点、不依赖前台窗口，用户在其他
   应用工作时也不会被打断）
7. 运行请使用 D:\\python\\python312\\python.exe（已装 pywinauto 0.6.9），
   不要用 PATH 里排最前的沙箱 python（未装 pywinauto）。

静默执行（工资属敏感信息）：
- 全程 PostMessage 点击/输入，不置顶、不抢焦点、不改变窗口 z 序，
  用户在其他应用（如 WPS）工作时互不干扰；
- 若执行前钉钉窗口最小化：临时恢复 -> 执行 -> 执行完重新最小化，
  工资明细不留在屏幕上（最小化时 CEF 网页子窗口会被销毁，页面随之消失）；

截屏保存（工资明细页）：
- 密码提交、明细加载后，用 PrintWindow(PW_RENDERFULLCONTENT) 抓取 CEF
  网页子窗口内容保存为 PNG（不依赖窗口置顶，截到的就是明细页本身）；
- 保存目录：E:\\华为云盘\\华为云盘\\hqchip\\日常\\payroll\\<当前年份>年\\，
  年份文件夹不存在则自动创建（存在则跳过）；
- 文件名 = 目标月份，如 2026-07.png；
- 截屏保存后自动点击明细弹窗右下角"取消"关闭弹窗，回到工资单列表，
  避免工资明细留在屏幕上（敏感信息保护）。

坐标校准（基于 1912x1040 窗口，客户端坐标，2026-09-08 截图核对）：
   - 工作台图标           (66, 245)   左侧导航栏
   - 我的板块"考勤"轻应用 (654, 296)  第 2 行第 2 个（区别于"考勤打卡"）
"""
import ctypes
import datetime
import os
import time
from ctypes import wintypes

from pywinauto import Desktop

u32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32
WM_LBUTTONDOWN = 0x0201
WM_LBUTTONUP = 0x0202
MK_LBUTTON = 0x0001
WM_MOUSEWHEEL = 0x020A

# 实测校准的客户端坐标（1912x1040 窗口）
NAV_X = 66            # 左侧导航栏水平中心
Y_WORKBENCH = 245     # 工作台图标
X_KQ = 654            # 我的板块"考勤"轻应用（第2行第2个）
Y_KQ = 296

CALIB_W = 1912        # 坐标校准时的窗口尺寸
CALIB_H = 1040


def find_dingtalk_main_window():
    """找到钉钉主窗口：标题为'钉钉'且可见的顶层窗口中取面积最大的一个。"""
    desktop = Desktop(backend="win32")
    candidates = []
    for w in desktop.windows():
        try:
            title = (w.window_text() or "").strip()
        except Exception:
            continue
        if title == "钉钉" and w.is_visible():
            r = w.rectangle()
            candidates.append((r.width() * r.height(), w))
    if not candidates:
        raise RuntimeError("未找到钉钉主窗口，请确认钉钉已启动且未完全退出")
    return max(candidates, key=lambda x: x[0])[1]


def post_click(hwnd, client_x, client_y):
    """向指定窗口投递鼠标左键单击（client_x/client_y 为该窗口客户区坐标）。"""
    lparam = (client_y << 16) | (client_x & 0xFFFF)
    u32.PostMessageW(hwnd, WM_LBUTTONDOWN, MK_LBUTTON, lparam)
    time.sleep(0.05)
    u32.PostMessageW(hwnd, WM_LBUTTONUP, 0, lparam)


def find_cef_child(hwnd, need_contain=None):
    """查找钉钉主窗口下覆盖目标区域的 CEF 渲染子窗口（网页内容）。

    网页内容必须向该子窗口投递点击。need_contain 为 (x, y) 屏幕坐标时，
    优先返回矩形包含该点的子窗口。返回 (子窗口句柄, (left, top, right, bottom))
    或 None。
    """
    WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
    found = []

    def cb(h, lp):
        rr = wintypes.RECT()
        u32.GetWindowRect(h, ctypes.byref(rr))
        cl = ctypes.create_unicode_buffer(256)
        u32.GetClassNameW(h, cl, 256)
        if (cl.value == "Chrome_RenderWidgetHostHWND"
                and (rr.right - rr.left) > 300 and (rr.bottom - rr.top) > 300):
            found.append((h, (rr.left, rr.top, rr.right, rr.bottom)))
        return True

    u32.EnumChildWindows(hwnd, WNDENUMPROC(cb), 0)
    if need_contain is not None:
        x, y = need_contain
        for h, rr in found:
            if rr[0] <= x <= rr[2] and rr[1] <= y <= rr[3]:
                return (h, rr)
    return found[0] if found else None


def find_cef_with_recover(ding_win, point, attempts=3):
    """查找覆盖 point 的 CEF 子窗口；若失败且窗口被最小化（执行期间用户
    可能误最小化了钉钉），自动恢复窗口后重试。返回 (句柄, 矩形) 或 None。"""
    for i in range(attempts):
        cef = find_cef_child(ding_win.handle, need_contain=point)
        if cef:
            return cef
        if ding_win.is_minimized():
            print("   检测到钉钉被最小化，自动恢复后重试...")
            ding_win.restore()
            time.sleep(2)
        else:
            time.sleep(1)
    return None


def save_payslip_screenshot(ding_win, tgt_month):
    """保存工资明细页截屏到云盘 payroll 目录。

    目录规则：payroll 下按当前年份命名文件夹（如"2026年"），不存在则新建，
    存在则跳过；文件名 = 目标月份（如 2026-07.png）。
    用 PrintWindow(PW_RENDERFULLCONTENT) 抓取 CEF 网页子窗口，不依赖窗口置顶。
    返回 (完整保存路径, 文件字节数)。
    """
    from PIL import Image
    import ctypes.wintypes as wt

    base = r"E:\华为云盘\华为云盘\hqchip\日常\payroll"
    year_dir = os.path.join(base, f"{datetime.date.today().year}年")
    if os.path.isdir(year_dir):
        print(f"   文件夹已存在，跳过新建: {year_dir}")
    else:
        os.makedirs(year_dir)
        print(f"   已新建文件夹: {year_dir}")

    cef = find_cef_child(ding_win.handle)
    if not cef:
        raise RuntimeError("未找到网页渲染子窗口，无法截屏")
    ch, (c_l, c_t, c_r, c_b) = cef
    w_, h_ = c_r - c_l, c_b - c_t
    if w_ <= 0 or h_ <= 0:
        raise RuntimeError("网页渲染子窗口尺寸异常，无法截屏")

    hdc_s = u32.GetDC(ch)
    hdc_m = gdi32.CreateCompatibleDC(hdc_s)
    hbmp = gdi32.CreateCompatibleBitmap(hdc_s, w_, h_)
    gdi32.SelectObject(hdc_m, hbmp)
    u32.PrintWindow(ch, hdc_m, 0x2)  # PW_RENDERFULLCONTENT

    class BITMAPINFOHEADER(ctypes.Structure):
        _fields_ = [('biSize', wt.DWORD), ('biWidth', ctypes.c_long),
                    ('biHeight', ctypes.c_long), ('biPlanes', wt.WORD),
                    ('biBitCount', wt.WORD), ('biCompression', wt.DWORD),
                    ('biSizeImage', wt.DWORD), ('biXPelsPerMeter', ctypes.c_long),
                    ('biYPelsPerMeter', ctypes.c_long), ('biClrUsed', wt.DWORD),
                    ('biClrImportant', wt.DWORD)]

    bmih = BITMAPINFOHEADER()
    bmih.biSize = ctypes.sizeof(BITMAPINFOHEADER)
    bmih.biWidth = w_
    bmih.biHeight = -h_
    bmih.biPlanes = 1
    bmih.biBitCount = 32
    bmih.biCompression = 0
    buf = ctypes.create_string_buffer(w_ * h_ * 4)
    gdi32.GetDIBits(hdc_m, hbmp, 0, h_, buf, ctypes.byref(bmih), 0)
    img = Image.frombuffer('RGBA', (w_, h_), buf, 'raw', 'BGRA', 0, 1).convert('RGB')

    save_path = os.path.join(year_dir, f"{tgt_month}.png")
    img.save(save_path)
    size = os.path.getsize(save_path)
    if size < 10 * 1024:
        raise RuntimeError(f"截屏文件异常偏小（{size} 字节），可能未截到内容")
    return save_path, size


def close_payslip_detail(ding_win):
    """关闭工资明细弹窗（点击右下角'取消'），回到工资单列表页。

    优先用 UIA 定位"取消"文本；UIA 不可用（旧网页弹窗部分元素未暴露
    有效矩形）时，用实测固定坐标：明细弹窗与密码框同为弹窗右下角按钮，
    webview 位置约 (1376-1429, 661-678) -> 屏幕 (1537, 745)。
    返回弹窗是否已确认关闭（明细特征词消失）。
    """
    clicked = click_uia_text(ding_win.handle, "取消", timeout=3)
    if not clicked:
        sx, sy = 1537, 745
        cef = find_cef_with_recover(ding_win, (sx, sy))
        if cef:
            ch, (c_l, c_t, _, _) = cef
            post_click(ch, sx - c_l, sy - c_t)
            clicked = True
    if not clicked:
        return False

    close_kw = ("工资条备注", "应发工资", "税前")
    deadline = time.time() + 8
    while time.time() < deadline:
        txts = [t for t, r in window_texts(ding_win.handle)]
        if not any(k in t for t in txts for k in close_kw):
            return True
        time.sleep(0.5)
    return False


def window_texts(hwnd):
    """返回主窗口中所有非空文本元素：(文本, 屏幕矩形 or None)。"""
    w = Desktop(backend="uia").window(handle=hwnd)
    out = []

    def walk(el, d):
        if d > 12:
            return
        try:
            kids = el.children()
        except Exception:
            return
        for k in kids:
            try:
                t = (k.window_text() or "").strip()
                if t:
                    try:
                        r = k.rectangle()
                    except Exception:
                        r = None
                    out.append((t[:40], r))
            except Exception:
                pass
            walk(k, d + 1)

    walk(w, 0)
    return out


def wait_text(hwnd, text, timeout=15):
    """轮询等待窗口中文本完全等于 text 的元素出现，返回是否出现。"""
    deadline = time.time() + timeout
    while time.time() < deadline:
        if any(t == text for t, r in window_texts(hwnd)):
            return True
        time.sleep(0.5)
    return False


def click_uia_text(hwnd, text, y_center=None, timeout=5):
    """通过 CEF 子窗口点击文本完全等于 text 的元素中心。

    y_center 不为 None 时只匹配 y 中心与该值接近（±15px）的元素（同行匹配）。
    同一文本有多个 UIA 节点时取面积最小者（真实文字，避免点到单元格空白处）。
    返回是否点击成功。
    """
    deadline = time.time() + timeout
    while time.time() < deadline:
        els = window_texts(hwnd)
        hits = [r for t, r in els if t == text and r is not None]
        if y_center is not None:
            hits = [r for r in hits if abs((r.top + r.bottom) // 2 - y_center) <= 15]
        if hits:
            r = min(hits, key=lambda x: (x.right - x.left) * (x.bottom - x.top))
            cx, cy = (r.left + r.right) // 2, (r.top + r.bottom) // 2
            cef = find_cef_child(hwnd, need_contain=(cx, cy))
            if cef:
                ch, (c_l, c_t, _, _) = cef
                post_click(ch, cx - c_l, cy - c_t)
                return True
        time.sleep(0.5)
    return False


def target_month(today):
    """计算目标工资条月份。

    规则：15日之前（1-14日）取前两个月；15日及之后取前一个月。
    例如 2026-09-08 -> 2026-07；2026-09-20 -> 2026-08。
    返回 'YYYY-MM' 字符串。
    """
    offset = 2 if today.day < 15 else 1
    y, m = today.year, today.month - offset
    if m <= 0:
        y -= 1
        m += 12
    return f"{y:04d}-{m:02d}"


def main():
    """静默执行入口：记录窗口初始状态，执行结束后恢复原状态。

    工资属敏感信息：若执行前钉钉窗口处于最小化，则临时恢复操作、
    全程不置顶不抢焦点（PostMessage 通道），执行完毕后重新最小化，
    工资明细不会留在屏幕上。
    """
    ding_win = find_dingtalk_main_window()
    print(f"找到钉钉窗口: handle={ding_win.handle}")
    was_minimized = ding_win.is_minimized()
    if was_minimized:
        print("静默执行: 窗口当前最小化，临时恢复操作，执行结束后将重新最小化")
    try:
        _run(ding_win)
    finally:
        # 静默收尾：开始时最小化则结束时恢复最小化，避免工资明细留在屏幕上
        if was_minimized:
            try:
                ding_win.minimize()
                print("静默完成: 钉钉已重新最小化，工资明细未留在屏幕")
            except Exception:
                pass


def _run(ding_win):
    """完整执行流程（内部保证窗口可见）。"""
    # 若窗口最小化，先恢复（最小化时 CEF 渲染子窗口会消失，点击会失效）
    if ding_win.is_minimized():
        print("钉钉窗口处于最小化状态，正在恢复...")
        ding_win.restore()
    for _ in range(20):
        if ding_win.is_visible() and not ding_win.is_minimized():
            break
        time.sleep(0.5)

    rect = ding_win.rectangle()
    print(f"窗口位置: left={rect.left}, top={rect.top}, width={rect.width()}, height={rect.height()}")
    if abs(rect.width() - CALIB_W) > 50 or abs(rect.height() - CALIB_H) > 50:
        print("警告: 窗口尺寸与坐标校准尺寸(1912x1040)偏差较大，坐标可能不准")
    print("提示: 执行中可正常使用电脑，无需等待；请勿在此时操作钉钉窗口本身")

    # ---- 1. 打开工作台 ----
    print("1. 点击工作台")
    post_click(ding_win.handle, NAV_X, Y_WORKBENCH)
    if not wait_text(ding_win.handle, "考勤", timeout=15):
        print("   工作台未检测到'考勤'，重试点击工作台")
        post_click(ding_win.handle, NAV_X, Y_WORKBENCH)
        if not wait_text(ding_win.handle, "考勤", timeout=15):
            raise RuntimeError("工作台页面未正常加载（未检测到'考勤'图标）")

    # ---- 2. 点击考勤轻应用 ----
    print("2. 点击考勤轻应用")
    kq_screen = (rect.left + X_KQ, rect.top + Y_KQ)
    cef = find_cef_with_recover(ding_win, kq_screen)
    if not cef:
        raise RuntimeError("未找到覆盖考勤图标的 CEF 渲染子窗口")
    ch, (c_l, c_t, _, _) = cef
    post_click(ch, kq_screen[0] - c_l, kq_screen[1] - c_t)
    if not wait_text(ding_win.handle, "我的工资单", timeout=20):
        raise RuntimeError("考勤轻应用未正常打开（未检测到'我的工资单'菜单）")

    # ---- 3. 点击我的工资单 ----
    print("3. 点击我的工资单")
    if wait_text(ding_win.handle, "请输入查看密码", timeout=3):
        # 若上一次运行遗留的密码框还开着，先点取消关闭
        click_uia_text(ding_win.handle, "取消")
        time.sleep(1)
    click_uia_text(ding_win.handle, "我的工资单")
    if not wait_text(ding_win.handle, "查看", timeout=20):
        raise RuntimeError("工资单列表未加载（未检测到'查看'按钮）")

    # ---- 4. 计算目标月份并定位记录行 ----
    today = datetime.date.today()
    tgt = target_month(today)
    print(f"4. 今天是 {today}（{today.day}日），目标月份: {tgt}")

    month_rect = None
    for _ in range(30):  # 最多等 15 秒，找不到则滚动列表再找
        els = window_texts(ding_win.handle)
        month_rect = next((r for t, r in els if t == tgt and r is not None), None)
        if month_rect:
            break
        time.sleep(0.5)
    if month_rect is None:
        # 列表可能未显示目标月份：向下滚动后重试
        print("   未直接看到目标月份，滚动列表查找...")
        cef_any = find_cef_child(ding_win.handle)
        if cef_any:
            ch2, (cl2, ct2, _, _) = cef_any
            for _ in range(5):
                u32.PostMessageW(ch2, WM_MOUSEWHEEL, (120 << 16), 0)
                time.sleep(0.5)
                els = window_texts(ding_win.handle)
                month_rect = next((r for t, r in els if t == tgt and r is not None), None)
                if month_rect:
                    break
    if month_rect is None:
        raise RuntimeError(f"未找到 {tgt} 的工资条记录")

    # ---- 5. 点击该行"查看" ----
    my = (month_rect.top + month_rect.bottom) // 2
    print(f"5. 找到 {tgt} 记录行(y={my})，点击该行查看")
    if not click_uia_text(ding_win.handle, "查看", y_center=my, timeout=5):
        raise RuntimeError("未找到目标月份的'查看'按钮")

    # ---- 6. 输入查看密码并提交 ----
    print("6. 输入查看密码并提交")
    if not wait_text(ding_win.handle, "请输入查看密码", timeout=10):
        raise RuntimeError("点击查看后未出现密码验证框")

    # 输入框占位文字"请输入查看密码"即输入框内提示文字，取其 UIA 矩形定位输入框；
    # 提交按钮在输入框右侧同一行（实测偏移：按钮中心 x = 文字右缘 + 26px）
    pw_rect = None
    for _ in range(10):
        pw_rect = next((r for t, r in window_texts(ding_win.handle)
                        if t == "请输入查看密码" and r is not None), None)
        if pw_rect:
            break
        time.sleep(0.5)
    if pw_rect is None:
        raise RuntimeError("未定位到密码输入框")
    ix, iy = (pw_rect.left + pw_rect.right) // 2, (pw_rect.top + pw_rect.bottom) // 2
    sx, sy = pw_rect.right + 26, (pw_rect.top + pw_rect.bottom) // 2
    cef_pw = find_cef_with_recover(ding_win, (ix, iy))
    if not cef_pw:
        raise RuntimeError("未找到密码输入框所在的渲染子窗口")
    ch3, (cl3, ct3, _, _) = cef_pw
    print(f"   密码框: ({ix},{iy})，提交按钮: ({sx},{sy})")

    post_click(ch3, ix - cl3, iy - ct3)      # 点击输入框聚焦
    time.sleep(0.5)
    for ch in "123456":                      # 逐字符输入密码（WM_CHAR）
        u32.PostMessageW(ch3, 0x0102, ord(ch), 0)
        time.sleep(0.08)
    time.sleep(0.5)
    post_click(ch3, sx - cl3, sy - ct3)      # 点击提交

    # ---- 7. 验证：密码框应关闭，工资明细应出现 ----
    print("7. 验证...")
    if wait_text(ding_win.handle, "请输入查看密码", timeout=8):
        print("失败: 提交后密码验证框仍在（密码可能错误或被拒绝）")
    else:
        detail_keywords = ("应发工资", "基本工资", "实发", "合计", "社保",
                           "住房公积金", "专项扣除")
        deadline = time.time() + 10
        found = []
        while time.time() < deadline:
            found = [t for t, r in window_texts(ding_win.handle)
                     if any(k in t for k in detail_keywords)]
            if found:
                break
            time.sleep(0.5)
        if found:
            print(f"成功: 密码验证通过，{tgt} 工资明细已打开（检测到: {found[0]} 等）")
            save_path, size = save_payslip_screenshot(ding_win, tgt)
            print(f"截屏已保存: {save_path}（{size} 字节）")
            if close_payslip_detail(ding_win):
                print("明细弹窗已关闭，回到工资单列表")
            else:
                print("警告: 未能确认明细弹窗已关闭，请人工确认")
        else:
            print("已提交: 密码验证框已关闭，但未检测到明细特征词，请查看钉钉窗口确认")


if __name__ == "__main__":
    main()
