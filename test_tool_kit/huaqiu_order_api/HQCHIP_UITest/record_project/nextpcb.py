import base64
from playwright.sync_api import Playwright, sync_playwright, TimeoutError as PlaywrightTimeoutError

# ========== 修复 PIL 报错（只执行一次） ==========
try:
    from PIL import Image
    Image.ANTIALIAS = Image.Resampling.LANCZOS
except:
    pass

import ddddocr

# ========== 验证码识别（超快） ==========
def get_captcha_code(page):
    # 等待验证码图片
    page.wait_for_selector("img.verifyImg", timeout=10000)

    # 获取图片 base64
    src = page.get_attribute("img.verifyImg", "src")
    base64_data = src.split(",")[1]

    # 补全 =
    base64_data += "=" * ((4 - len(base64_data) % 4) % 4)

    # 识别
    ocr = ddddocr.DdddOcr()
    img_bytes = base64.b64decode(base64_data)
    code = ocr.classification(img_bytes)
    print("✅ 验证码识别结果：", code)
    return code

# ========== 主逻辑（顺序完全修正！） ==========
def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context(viewport={"width": 1920, "height": 1080})
    page = context.new_page()

    # 1. 打开网站
    page.goto("https://www.nextpcb.com/login", wait_until="domcontentloaded")

    # 2. 【关键】先等待验证码出现
    page.wait_for_selector("img.verifyImg", timeout=10000)

    page.get_by_placeholder("Email address or member ID").fill("1194050164@qq.com")
    page.get_by_placeholder("Password").click()
    page.get_by_placeholder("Password").fill("Aa123456")
    page.get_by_placeholder("Verification code").click()
    page.get_by_placeholder("Verification code").press("CapsLock")
    # 获取并填写验证码
    code = get_captcha_code(page)
    if code:
        page.get_by_placeholder("Verification code").fill(code)
    else:
        print("验证码获取失败，请手动输入")

    # 6. 登录
    page.click('button[id="hq_loginSubmit"]')

    login_success = False
    try:
        # 等待登录成功标识（用用户图标替代My Account，更稳定）
        page.wait_for_selector(".icon-img.icon-user-new", timeout=15000)
        print("✅ 🏁 登录成功！")
        login_success = True
    except TimeoutError:
        print("❌ ❌ 登录失败！等待超时。")
        page.screenshot(path="debug_login_fail.png", full_page=True)
        print("📸 已保存错误截图到 debug_login_fail.png")
    page.wait_for_timeout(4000)



    # 关闭
    page.close()
    context.close()
    browser.close()

with sync_playwright() as playwright:
    run(playwright)