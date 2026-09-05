from playwright.sync_api import Playwright, sync_playwright, expect, TimeoutError
import ddddocr

# 等待验证码图片加载
try:
    from PIL import Image

    Image.ANTIALIAS = Image.Resampling.LANCZOS
except ImportError:
    pass

ocr = ddddocr.DdddOcr(show_ad=False)

def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False, slow_mo=600)
    context = browser.new_context(viewport={"width": 1920, "height": 1080})
    page = context.new_page()

    # ==================== ✅ 新加：自动关闭所有弹窗（包括文件选择窗口）====================
    page.on("filechooser", lambda filechooser: filechooser.set_files(r"C:\Users\WIN\Desktop\automate-test-item\test_tool_kit\huaqiu_order_api\HQCHIP_UITest\file\nextpcb\dotNet.zip"))
    page.on("dialog", lambda dialog: dialog.dismiss())
    # ==================================================================================

    # ==================== 登录流程 ====================
    page.goto("https://uat-www.nextpcb.com/", wait_until="domcontentloaded")
    page.locator(".icon-img.icon-user-new").hover()
    page.wait_for_timeout(300)
    page.get_by_role("link", name="Login").click()

    page.get_by_role("textbox", name="Email address or member ID").fill("tt1001@huaqiu.com")
    page.get_by_role("textbox", name="Password").fill("Aa123456")

    # 验证码定位
    captcha_selector = "#loginBox > div > div.login-gt > div.loginwin-form.pt-bs > div.loginwin-code.mg-b-md > div.loginwin-code-img.float-r > img"
    captcha_img = page.locator(captcha_selector)
    captcha_img.wait_for(state="visible", timeout=5000)

    # OCR识别验证码
    captcha_img.click()
    page.wait_for_timeout(1000)
    captcha_bytes = captcha_img.screenshot()
    verify_code = ocr.classification(captcha_bytes)
    print(f"🔍 自动识别验证码：{verify_code}")

    page.get_by_role("textbox", name="Verification code").fill(verify_code)

    # ==================== 登录并验证 ====================
    print("🚀 点击登录...")
    page.get_by_role("button", name="Login").click()

    login_success = False
    try:
        # 等待登录成功标识（用用户图标替代My Account，更稳定）
        page.wait_for_selector(".icon-img.icon-user-new", timeout=15000)
        print("✅ 🏁 登录成功！")
        login_success = True
    except TimeoutError:
        print("❌ ❌ 登录失败！等待超时。")
        page.screenshot(path="../debug_login_fail.png", full_page=True)
        print("📸 已保存错误截图到 debug_login_fail.png")
        if page.get_by_text("验证码错误").is_visible(timeout=3000):
            print("💡 检测到：验证码错误，建议换手动输入验证")

    # 登录失败直接退出，不执行后续流程
    if not login_success:
        context.close()
        browser.close()
        return

    # ==================== 下单流程（修复networkidle超时） ====================
    # 直接用固定等待，删除networkidle
    page.wait_for_timeout(1000)

    # 1. 进入PCB报价页
    page.get_by_role("link", name="PCB Quote", exact=True).click()
    page.wait_for_timeout(1500)

    # 2. 点击Gerber上传按钮
    page.get_by_text(" Gerber File").click()
    page.wait_for_timeout(500)

    # 3. 上传文件（同目录无需改路径）
    page.get_by_label(" Gerber File").set_input_files(r"C:\Users\WIN\Desktop\automate-test-item\test_tool_kit\huaqiu_order_api\HQCHIP_UITest\file\nextpcb\dotNet.zip")
    page.wait_for_timeout(20000)

    # 4. 校验上传成功
    if page.get_by_text("dotNet.zip").first.is_visible(timeout=5000):
        print("✅ Gerber文件上传成功！")
    else:
        print("❌ 文件上传失败，请检查文件名/路径")
        page.screenshot(path="../upload_error.png", full_page=True)
        context.close()
        browser.close()
        return

    # 5. 处理Cookie弹窗（容错）
    try:
        page.get_by_role("link", name="Accept all cookies").click(timeout=3000)
    except:
        pass

    # 6. 填写订单参数
    page.get_by_text("Follow Order Parameters").click()
    page.wait_for_timeout(500)
    page.get_by_role("textbox", name="Please fill in your special").fill("测试订单，无需理会")
    page.get_by_text("IPC Level 2 StandardIPC Level").click()
    page.wait_for_timeout(500)

    # 7. 加入购物车
    page.get_by_role("button", name=" Add to Cart").click()
    page.wait_for_timeout(30000)  # 延长等待，确保加购完成
    print("✅ 商品已加入购物车")

    # 8. 跳转到购物车（修复ERR_ABORTED）
    try:
        page.goto(
            "https://uat-www.nextpcb.com/order/cart/type/1",
            wait_until="domcontentloaded",
            timeout=30000
        )
        print("✅ 成功跳转到购物车页面")
    except Exception as e:
        print(f"⚠ 跳转异常，刷新重试: {str(e)}")
        page.reload(wait_until="domcontentloaded")
        page.wait_for_timeout(2000)

    # 9. 结算操作
    page.locator('//div[@class="ordersList"]/div[2]/div[1]/span[@class="id"]/span[@class="checkedBox  "]').first.click()
    page.wait_for_timeout(1000)
    page.get_by_role("link", name="Checkout").click()
    page.wait_for_timeout(10000)

    print("✅ 所有流程执行完成！")
    context.close()
    browser.close()

with sync_playwright() as playwright:
    run(playwright)