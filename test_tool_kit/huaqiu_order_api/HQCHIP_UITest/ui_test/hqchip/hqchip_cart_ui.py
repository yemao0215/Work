import os
from datetime import datetime

from playwright.sync_api import Playwright, sync_playwright, expect, TimeoutError
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

import ddddocr

from huaqiu_order_api.common.my_path import uiTest_img_hqchip_suess, uiTest_img_hqchip_full

# 等待验证码图片加载
try:
    from PIL import Image

    Image.ANTIALIAS = Image.Resampling.LANCZOS
except ImportError:
    pass

ocr = ddddocr.DdddOcr(show_ad=False)

def run(playwright: Playwright, url=None, username=None, password=None) -> None:
    browser = playwright.chromium.launch(headless=False, slow_mo=600)
    context = browser.new_context(viewport={"width": 1920, "height": 1080})
    page = context.new_page()
    page.goto("{}".format(url.strip() if url and url.strip() else "https://uat-www.hqchip.com"), wait_until="domcontentloaded")
    page.wait_for_timeout(300)
    try:
        page.wait_for_selector('//a[@class="close"]', state="visible", timeout=2000)
        page.locator('//a[@class="close"]').click()
    except:
        print("无弹窗广告需要关闭")
    page.locator('//a[text()="登录"]').first.click()
    # 直接定位 iframe 内的元素，无需显式切换
    frame = page.frame_locator('iframe[name="sso-LoginIframe"]')
    page.wait_for_timeout(3000)
    frame.locator('//span[text()="密码登录"]').nth(1).click()
    frame.locator('//input[@placeholder="用户名/邮箱/手机号码"]').click()
    frame.locator('//input[@placeholder="用户名/邮箱/手机号码"]').fill("{}".format(username.strip() if username and username.strip() else "15070739195"))
    frame.locator('//input[@placeholder="请输入密码"]').click()
    frame.locator('//input[@placeholder="请输入密码"]').fill("{}".format(password.strip() if password and password.strip() else "ye123456"))
    try:
        # 等待滑块容器出现
        frame.locator('#aliyunCaptcha-sliding-body').wait_for(state='visible', timeout=5000)
        print("✅ 找到阿里云滑块，开始自动滑动验证")
        # 定位 滑块 + 滑块容器
        slider = frame.locator('#aliyunCaptcha-sliding-slider')
        target = frame.locator('#aliyunCaptcha-sliding-body')
        # 最稳定的滑动方式：直接拖拽到目标末端
        slider.drag_to(target,
                       force=True,
                       source_position={"x": 10, "y": 10},  # 点滑块左边
                       target_position={"x": 378, "y": 10}  # 拖到容器最右侧
                       )
        # 等待验证成功
        frame.locator('#aliyunCaptcha-sliding-text:has-text("滑动完成")').wait_for(state='visible', timeout=3000)
        print("✅ 阿里云滑块验证成功！")
    except:
        print("⚠️ 未出现滑块或验证超时，跳过滑动")
        pass
    frame.locator('//span[text()="同意网站"]/../label[@class="protocal-check" and @for="protocal2"]').click()
    frame.locator('//button[@class="ui-btn submit-btn" and text()="登录"]').click()

    login_success = False
    try:
        # 等待登录成功标识（用用户图标替代My Account，更稳定）
        page.wait_for_selector('//a[@class="logout" and text()="退出"]', timeout=15000)
        print("✅ 🏁 登录成功！")
        login_success = True
    except TimeoutError:
        print("❌ ❌ 登录失败！等待超时。")
        page.screenshot(path="../debug_login_fail.png", full_page=True)
        print("📸 已保存错误截图到 debug_login_fail.png")
        if page.get_by_text("验证码错误").is_visible(timeout=3000):
            print("💡 检测到：验证码错误，建议换手动输入验证")
    if login_success == False:
        print("登录失败，停止后续操作")
        return
    # 搜索商品
    page.locator('//input[@placeholder="元器件型号、描述、参数"]').click()
    page.locator('//input[@placeholder="元器件型号、描述、参数"]').fill("0402WGJ0103TCE")
    try:
        page.wait_for_selector('//div[text()="预发布环境"]', state="visible", timeout=2000)
        page.locator('//div[text()="预发布环境"]').click()
    except TimeoutError:
        print("未找到预发布环境提示")
    page.locator('//button[@class="search-btn home"]').click()
    page.wait_for_timeout(15000)
    # page.pause()
    rows = page.locator('//span[text()="加入购物车"]')
    locator_count = rows.count()
    print("统计到加入购物车元素个数：", locator_count)
    add_cart_buttons = page.locator("span.add_cart.J_addToCart.track-event:has-text('加入购物车')")
    # 依次点击
    for i in range(locator_count):
        # 每次重新获取，避免 stale element
        btn = add_cart_buttons.nth(i)
        # 确保元素可见并点击
        try:
            btn.scroll_into_view_if_needed(timeout=5000)
            # 可选：获取所在行的型号，便于调试
            row = btn.locator("xpath=ancestor::*[3]")
            goods_id = row.locator("div.col2 a").first.get_attribute("data-goodsid")
            model = row.locator("div.col2 a").first.get_attribute("data-goodsname")
            print(f"正在点击第 {i + 1} 个订货商品：{model}, goods_id: {goods_id}")
            btn.click(timeout=5000)
        except Exception as e:
            print(f"点击第 {i + 1} 个按钮时出错: {e}")
            # 可能按钮不可见或已失效，跳过继续下一个
        try:
            dialog = page.wait_for_selector(".ui-dialog-body", state="visible", timeout=2000)
            close_btn = page.locator(".ui-dialog-body .close-btn")
            close_btn.click(timeout=1000)
            # 等待弹窗消失
            page.wait_for_selector(".ui-dialog-body", state="hidden", timeout=2000)
            print(f"第 {i + 1} 次购物车操作触发的弹窗已关闭")
        except PlaywrightTimeoutError:
            # 没有弹窗或超时，正常继续
            print(f"第 {i+1} 次购物车操作未出现弹窗")
        except Exception as e:
            print(f"处理弹窗时发生其他错误：{e}")
        print(f"已点击第 {i+1} 个")
        # 可根据需要添加短暂等待，避免过快
        page.wait_for_timeout(1000)

    page.goto(("{}".format(url.strip() if url and url.strip() else "https://uat-www.hqchip.com") + "/cart.html"), wait_until="domcontentloaded")
    while True:
        # 购物车判断操作
        cart_rows = page.locator('//a[text()="删除"]')
        cart_count = cart_rows.count()
        if cart_count == 0:
            print("购物车已清空")
            break
        # 点击第一个删除链接
        first_delete = cart_rows.first
        # 获取当前商品型号名称（通过当前删除链接所在行）
        row = first_delete.locator("xpath=ancestor::tr")
        model_name = row.locator("td.col2 a").first.inner_text()  # 根据 HTML 结构定位
        try:
            print(f"正在操作删除型号名称：{model_name}的记录")
            first_delete.scroll_into_view_if_needed()
            first_delete.click(timeout=3000)
        except Exception as e:
            print(f"点击删除按钮失败: {e}")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            page.screenshot(path=os.path.join(uiTest_img_hqchip_full, f"delete_fail_{model_name}_{timestamp}.png"), full_page=True)
            break
        # 等待确认弹窗出现
        try:
            page.wait_for_selector('a:has-text("确定")', state="visible", timeout=3000)
            page.locator('a:has-text("确定")').click(timeout=3000)
        except PlaywrightTimeoutError:
            print("未出现确认弹窗，可能已删除成功")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            page.screenshot(path=os.path.join(uiTest_img_hqchip_full, f"delete_fail_{model_name}_{timestamp}.png"), full_page=True)
        except Exception as e:
            print(f"点击确定按钮时出错: {e}")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            page.screenshot(path=os.path.join(uiTest_img_hqchip_full, f"delete_fail_{model_name}_{timestamp}.png"), full_page=True)
        # 等待页面更新（删除操作可能需要时间）
        page.wait_for_timeout(1500)
    print("✅ 所有流程执行完成！")
    context.close()
    browser.close()

with sync_playwright() as playwright:
    url = "https://www.hqchip.com"
    username = "qaulau@qq.com"
    password = "a123456"
    env = "uat"
    if env == "pro":
        run(playwright, url=url, username=username, password=password)
    else:
        run(playwright)