import os
import re

from playwright.sync_api import Playwright, sync_playwright, expect

from huaqiu_order_api.common.my_path import uiTest_img_2018


def run(playwright: Playwright, goods_name=None) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context(color_scheme="dark", viewport={"width":1920,"height":1080}) # storage_state="auth.json",
    page = context.new_page()
    page.goto("https://uat-hc2018.hqchip.com/#/login")
    page.get_by_placeholder("用户名").click()
    page.get_by_placeholder("用户名").fill("admin")
    page.get_by_placeholder("密码").fill("HQ@uat@666")
    page.get_by_role("button", name="登录").click()
    login_success = False
    try:
        # 等待登录成功标识（用用户图标替代My Account，更稳定）
        page.wait_for_selector('//div[text()="备货"]', timeout=15000)
        print("✅ 🏁 登录成功！")
        login_success = True
    except TimeoutError:
        print("❌ ❌ 登录失败！等待超时。")
        page.screenshot(path=os.path.join(uiTest_img_2018, "debug_login_fail.png"), full_page=True)
        print("📸 已保存错误截图到 debug_login_fail.png")
    # 新增
    page.goto("https://uat-hc2018.hqchip.com/#/goods-data/information")
    page.wait_for_timeout(4000)
    page.locator('//div[text()="预发布环境"]').click()
    page.locator('//div[@class="handl-row"]/button/span[text()="新增"]').click(timeout=10000)
    # 1. 点击输入框,等待级联选择器出现
    page.locator('//label[text()="商品分类："]/../div[contains(@class,"el-form-item__content")]//input[@placeholder="请选择"]').click()
    page.wait_for_selector('//div[@class="el-popper el-cascader__dropdown"  and  @x-placement="bottom-start"]//span[text()="刘丽的测试分类1"]', state="visible", timeout=50000)
    # 2. 点击一级菜单 茂茂测试分类
    page.locator('//div[@class="el-popper el-cascader__dropdown"  and  @x-placement="bottom-start"]//span[text()="茂茂测试分类"]').click()
    # 3. 悬停至二级分类
    page.locator('//div[@class="el-popper el-cascader__dropdown"  and  @x-placement="bottom-start"]/div[@class="el-cascader-panel"]/div[2]').hover()
    # 2. 点击二级菜单 搜索V4
    page.locator('//div[@class="el-popper el-cascader__dropdown"  and  @x-placement="bottom-start"]//span[text()="搜索V4"]/../label//span[@class="el-radio__inner"]').click()
    page.get_by_placeholder("请输入商品型号").click()
    page.get_by_placeholder("请输入商品型号").fill(goods_name)
    page.get_by_placeholder("请输入制造商").click()
    page.get_by_placeholder("请输入制造商").fill("Yageo")
    page.get_by_role("listitem").filter(has_text="Yageo").click()
    page.get_by_role("button", name="更新名称").click()
    page.locator("a").filter(has_text="自动更新").click()
    page.locator('//div[@id="attrs-ext-1014"]//tbody/tr[1]/td[2]//input').click()
    # page.locator('//div[@class="el-table__body-wrapper is-scrolling-none"]//tr[@class="el-table__row"]//input[@placeholder="请选择" and @class="el-input__inner"]').click()
    page.wait_for_selector('//div[@class="el-select-dropdown el-popper" and  @x-placement="bottom-start"]', state="visible", timeout=50000)
    page.locator('//div[@class="el-select-dropdown el-popper" and  @x-placement="bottom-start"]//span[text()="卷装(TR)"]').click()
    page.locator('//div[@id="attrs-ext-1014"]//tbody/tr[1]/td[3]//input').click()
    page.locator('//div[@id="attrs-ext-1014"]//tbody/tr[1]/td[3]//input').fill("1000")
    page.locator("div").filter(has_text=re.compile(r"^商品重量：g$")).get_by_role("textbox").click()
    page.locator("div").filter(has_text=re.compile(r"^商品重量：g$")).get_by_role("textbox").fill("0.011")
    page.get_by_role("button", name="提交").click()
    # 短暂等待通知出现
    add_success = False
    try:
        page.wait_for_selector('.el-message__content:has-text("已存在")', timeout=3000)
        print("提示：商品已存在")
        page.screenshot(path=os.path.join(uiTest_img_2018, "debug_goodsAdd_fail.png"), full_page=True)
        print("📸 已保存错误截图到 debug_goodsAdd_fail.png")
        page.locator('//div[@class="app-main flex"]/div/div/div[7]/div/div[1]/button').click()
        add_success = False
    except:

        print("未出现已存在提示")
        add_success = True
        # 搜索 提审
        page.get_by_placeholder("多个关键词用%隔开").fill(goods_name)
        page.get_by_role("button", name="搜索").click()
        print("✅ 搜索完成")
        page.wait_for_timeout(500)
        page.locator('//div[@class="el-table__fixed-right"]/div[@class="el-table__fixed-body-wrapper"]/table[@class="el-table__body"]/tbody/tr[1]/td[29]/div/a[3]').click()
        page.wait_for_selector('.el-message-box', state="visible", timeout=50000)
        page.locator('//div[@class="el-message-box__btns"]/button[2]').click()

        # 审核
        page.goto("https://uat-hc2018.hqchip.com/#/goods-data/examine-verify")
        page.locator('//div[text()="资料审核"]').click()
        page.wait_for_timeout(4000)
        for i in range(3):
            page.get_by_placeholder("请输入型号").fill(goods_name)
            page.get_by_role("row", name="序号 审批号 编码 型号 品牌 分类 提交类型 提审人 提审时间 审核状态 审核日志 操作").locator("span").nth(1).click()
            page.locator('//div[@class="mg-b-sm"]/button[1]').click()
            page.wait_for_timeout(4000)
        page.goto("https://uat-hc2018.hqchip.com/#/goods-data/information")
    page.wait_for_timeout(4000)
    page.get_by_placeholder("多个关键词用%隔开").fill(goods_name)
    page.screenshot(path=os.path.join(uiTest_img_2018, "debug_goodsAdd_search_input_fail.png"), full_page=True)
    print("📸 已保存截图到 debug_goodsAdd_search_input_fail.png")
    page.locator('//div[@class="app-container pd-t-xs"]/div[2]//button').click()
    page.wait_for_timeout(4000)
    page.screenshot(path=os.path.join(uiTest_img_2018, "debug_goodsAdd_search_fail.png"), full_page=True)
    print("📸 已保存截图到 debug_goodsAdd_search_fail.png")
    if add_success == True:
        print("✅ 审核后搜索完成")
    else:
        print("✅ 资料列表页搜索完成")


    # ---------------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    goods_name = ("CESHI20260601")
    run(playwright, goods_name=goods_name)
