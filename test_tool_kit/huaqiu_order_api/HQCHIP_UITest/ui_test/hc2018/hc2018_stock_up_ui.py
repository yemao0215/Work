import os
import re
from datetime import datetime

import pandas as pd
import yaml
from playwright.sync_api import Playwright, sync_playwright, expect

from huaqiu_order_api.common.my_path import uiTest_img_2018, stockup_dir, yaml_file


def get_first_value(col_value):
    if col_value and len(col_value) > 0 and col_value[0] is not None:
        return col_value[0]
    return None


with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
    data = yaml.load(yamlfile, Loader=yaml.FullLoader)
HC2018_ADMIN_URL = data['HC2018_ADMIN_URL_odl']

def get_user_info(name):
    """
    根据姓名key获取账号密码
    :param name: 姓名，如 "超级管理员"
    :return: username, password
    """
    user_pwd_json = {
        "叶茂": {"username": "yemao","password": "12345678"},
        "陶婷": {"username": "taoting","password": "12345678"},
        "超级管理员": {"username": "admin","password": "HQ@uat@666"},
        "张进": {"username": "zhangjin","password" : "123456"},
        "仇芳梅": {"username": "qiufm@hqchip.com", "password": "12345678"},
        "刘教威": {"username": "liujiaowei", "password": "12345678"},
        "贺鹏": {"username": "qiufm@hepeng.com", "password": "12345678"}
    }
    if name not in user_pwd_json:
        raise Exception(f"未找到用户：{name}")

    user_info = user_pwd_json[name]
    return user_info["username"], user_info["password"]


def get_auditor_from_table(page):
    """
    适配华秋HC2018 el-table 固定列表格
    精准提取【审核人】字段
    """
    try:
        # 1. 读取表头，找到【审核人】在哪一列
        headers = page.locator(".el-table__header th").all_inner_texts()
        headers = [h.strip() for h in headers]
        auditor_index = None

        for i, title in enumerate(headers):
            if "审核人" in title:
                auditor_index = i
                break

        if auditor_index is None:
            print("❌ 未找到【审核人】列")
            return None

        print(f"✅ 审核人列索引：{auditor_index}")


        # 2. 先判断：表格有没有数据行
        row_locator = page.locator(".el-table__body tbody tr.el-table__row")

        # ✅ 关键：如果一行数据都没有 → 直接返回 None
        if row_locator.count() == 0:
            print("⚠️ 表格中无数据行，返回 None")
            return None
        # 3. 定位第一行数据（你页面里真实的行）
        first_row = row_locator.first

        # 4. 直接取这一行对应列的文本（最稳）
        auditor = first_row.locator("td").nth(auditor_index).inner_text().strip()

        print(f"✅ 成功获取审核人：{auditor}")
        return auditor

    except Exception as e:
        print(f"❌ 获取审核人失败：{str(e)}")
        return None
def run(playwright: Playwright, type=None,goods_name=None,brand_name=None,stock_type=None) -> None:

    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context(color_scheme="dark", viewport={"width":1920,"height":1080}) # storage_state="auth.json",
    page = context.new_page()
    page.goto("{}/#/login".format(HC2018_ADMIN_URL.strip()))
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
    # 补备货列表
    page.goto("{}/#/replenish/replenish-list".format(HC2018_ADMIN_URL.strip()))
    page.wait_for_timeout(4000)
    page.locator('//div[text()="预发布环境"]').click()
    df = pd.read_excel(stockup_dir)
    # 将每一列转换为列表，存入字典
    column_lists = {col: df[col].tolist() for col in df.columns}
    # 提取型号(必填)
    goods_name = get_first_value(column_lists.get('型号(必填)'))
    # 提取品牌(必填)
    brand_name = get_first_value(column_lists.get('品牌(必填)'))
    # 提取芯城编码（注意值是字符串形式的列表，如 "['MT0000062']"）
    goods_no = get_first_value(column_lists.get('芯城编码'))
    stock_type = get_first_value(column_lists.get('补备货'))
    inventory_type = get_first_value(column_lists.get('备货类型(必填)'))
    print(f"goods_name: {goods_name}")
    print(f"brand_name: {brand_name}")
    print(f"goods_no: {goods_no}")
    print(f"stock_type: {stock_type}")
    print(f"inventory_type: {inventory_type}")
    if type == None:
        page.locator('.el-form-item__content:has(button:has-text("导入需求"))').click(timeout=10000)
        # 操作 Element-ui组件：拖拽上传组件
        # 定位隐藏的 input 元素（class="el-upload__input"）
        file_input = page.locator('input.el-upload__input[type="file"]')
        # 设置要上传的文件（支持绝对路径或相对路径）
        file_input.set_input_files(stockup_dir)
        path_file_name = os.path.basename(stockup_dir)
        # 等待上传成功的列表项出现（超时根据实际情况调整）
        uploaded_file = page.locator('.el-upload-list__item.is-success .el-upload-list__item-name')
        # 获取文本（可能会包含前图标的特殊字符，但文件名一般正常）
        uploaded_file_name = uploaded_file.inner_text().strip()
        # 断言文件名一致
        assert path_file_name == uploaded_file_name, f"文件名不匹配：期望 {path_file_name}，实际 {uploaded_file_name}"
        print("✅ 文件名校验通过")
        page.locator('//div[@class="mg-t-sm"]/div[@class="dialog-footer"]/button').click()
        try:

            page.wait_for_selector('//span[text()="导入失败"]', state="visible", timeout=2000)
            page.wait_for_timeout(4000)
            page.screenshot(path=os.path.join(uiTest_img_2018, "debug_stock_up_fail.png"), full_page=True)
            page.locator('//span[text()="导入失败"]/../button').click()
            print("❌ ❌ 导入失败")
        except:
            print("✅ 导入成功")
        page.get_by_role("button", name="重置").click()
        page.get_by_role("textbox", name="芯城编码").click()
        page.get_by_role("textbox", name="芯城编码").fill(goods_no)
        page.get_by_role("textbox", name="型号").click()
        page.get_by_role("textbox", name="型号").fill(goods_name)
        page.get_by_role("textbox", name="品牌").click()
        page.get_by_role("textbox", name="品牌").fill(brand_name)
        page.get_by_role("textbox", name="补备货").click()
        page.get_by_role("listitem").filter(has_text=f"{stock_type}").click()
        page.get_by_role("textbox", name="备货类型").click()
        page.locator("span").filter(has_text=f"{inventory_type}").click()
        page.get_by_role("textbox", name="状态").click()
        page.get_by_text("待审核").click()
        page.get_by_role("button", name="搜索").click()
    if stock_type == "备货":
        print("打开备货审核，获取当前审核人")
        page.goto('{}/#/replenish/replenish-audit'.format(HC2018_ADMIN_URL.strip()))
        page.wait_for_timeout(4000)
        page.get_by_role("textbox", name="型号").click()
        page.get_by_role("textbox", name="型号").fill(goods_name)
        page.get_by_role("textbox", name="品牌").click()
        page.get_by_role("textbox", name="品牌").fill(brand_name)
        page.get_by_role("textbox", name="审核状态").click()
        page.get_by_text("审核中").click()
        page.locator('form .el-form-item:last-child button').click()
        page.wait_for_timeout(4000)
        page.get_by_role("textbox", name="型号").click()
        page.get_by_role("textbox", name="型号").fill(goods_name)
        page.get_by_role("textbox", name="品牌").click()
        page.get_by_role("textbox", name="品牌").fill(brand_name)
        page.get_by_role("textbox", name="审核状态").click()
        page.wait_for_selector(
            '//ul[@class="el-scrollbar__view el-select-dropdown__list"]/li/span[text()="审核中"]',
            state="visible", timeout=50000)

        page.locator('//ul[@class="el-scrollbar__view el-select-dropdown__list"]/li/span[text()="审核中"]').click()
        page.locator('form .el-form-item:last-child button').click()
        page.pause()
        for i in range(3):
            print(f"第{i + 1} 次循环")
            audit_name = get_auditor_from_table(page)
            # 判断是否审核人是否当前登录相等
            login_user_name = page.locator('//span[@class="name"]').inner_text().strip()
            if not audit_name:
                print("❌ 未获取到审核人，退出循环")
                break
            if login_user_name != audit_name:
                print("判断是否审核人是否当前登录不相等")
                page.locator('//span[@class="name"]').click()
                page.locator('//span[text()="退出"]').click()
                audit_username, audit_password = get_user_info(audit_name)
                page.get_by_placeholder("用户名").click()
                page.get_by_placeholder("用户名").fill(audit_username)
                page.get_by_placeholder("密码").fill(audit_password)
                page.get_by_role("button", name="登录").click()
                page.wait_for_timeout(4000)
                page.goto('{}/#/replenish/replenish-audit'.format(HC2018_ADMIN_URL.strip()))
                page.wait_for_timeout(4000)
                page.get_by_role("textbox", name="型号").click()
                page.get_by_role("textbox", name="型号").fill(goods_name)
                page.get_by_role("textbox", name="品牌").click()
                page.get_by_role("textbox", name="品牌").fill(brand_name)
                page.get_by_role("textbox", name="审核状态").click()
                page.wait_for_selector(
                    '//ul[@class="el-scrollbar__view el-select-dropdown__list"]/li/span[text()="审核中"]',
                    state="visible", timeout=50000)

                page.locator('//ul[@class="el-scrollbar__view el-select-dropdown__list"]/li/span[text()="审核中"]').click()
                page.locator('form .el-form-item:last-child button').click()
            rows = page.locator('//span[text()="通过"]')
            locator_count = rows.count()
            if locator_count < 1:
                break
            btn = rows.nth(2)
            # 确保元素可见并点击
            try:
                btn.scroll_into_view_if_needed(timeout=5000)
                btn.click(timeout=5000)
            except Exception as e:
                print(f"点击通过按钮时出错: {e}")
                # 可能按钮不可见或已失效，跳过继续下一个

    else:
        print("打开补货审核，获取当前审核人")
        page.goto('{}/#/replenish/prepare-audit'.format(HC2018_ADMIN_URL.strip()))
        page.wait_for_timeout(4000)
        page.get_by_role("textbox", name="型号").click()
        page.get_by_role("textbox", name="型号").fill(goods_name)
        page.get_by_role("textbox", name="品牌").click()
        page.get_by_role("textbox", name="品牌").fill(brand_name)
        page.get_by_role("textbox", name="审核状态").click()
        page.wait_for_selector(
            '//ul[@class="el-scrollbar__view el-select-dropdown__list"]/li/span[text()="审核中"]',
            state="visible", timeout=50000)

        page.locator('//ul[@class="el-scrollbar__view el-select-dropdown__list"]/li/span[text()="审核中"]').click()
        page.locator('form .el-form-item:last-child button').click()
        page.pause()
        for i in range(3):
            print(f"第{i + 1} 次循环")
            audit_name = get_auditor_from_table(page)
            # 判断是否审核人是否当前登录相等
            login_user_name = page.locator('//span[@class="name"]').inner_text().strip()
            if not audit_name:
                print("❌ 未获取到审核人，退出循环")
                break
            if login_user_name != audit_name:
                print("判断是否审核人是否当前登录不相等")
                page.locator('//span[@class="name"]').click()
                page.locator('//span[text()="退出"]').click()
                audit_username, audit_password = get_user_info(audit_name)
                page.get_by_placeholder("用户名").click()
                page.get_by_placeholder("用户名").fill(audit_username)
                page.get_by_placeholder("密码").fill(audit_password)
                page.get_by_role("button", name="登录").click()
                page.wait_for_timeout(4000)
                page.goto('{}/#/replenish/prepare-audit'.format(HC2018_ADMIN_URL.strip()))
                page.wait_for_timeout(4000)
                page.get_by_role("textbox", name="型号").click()
                page.get_by_role("textbox", name="型号").fill(goods_name)
                page.get_by_role("textbox", name="品牌").click()
                page.get_by_role("textbox", name="品牌").fill(brand_name)
                page.get_by_role("textbox", name="审核状态").click()
                page.wait_for_selector(
                    '//ul[@class="el-scrollbar__view el-select-dropdown__list"]/li/span[text()="审核中"]',
                    state="visible", timeout=50000)

                page.locator('//ul[@class="el-scrollbar__view el-select-dropdown__list"]/li/span[text()="审核中"]').click()
                page.locator('form .el-form-item:last-child button').click()
            rows = page.locator('//span[text()="通过"]')
            locator_count = rows.count()
            if locator_count < 1:
                break
            btn = rows.nth(2)
            # 确保元素可见并点击
            try:
                btn.scroll_into_view_if_needed(timeout=5000)
                btn.click(timeout=5000)
            except Exception as e:
                print(f"点击通过按钮时出错: {e}")
                # 可能按钮不可见或已失效，跳过继续下一个
            page.locator('form .el-form-item:last-child button').click()


        # ---------------------
    context.close()
    browser.close()


with (sync_playwright() as playwright):
    goods_name = "LiaoPeng00010"
    type = None
    brand_name = 'Yageo'
    stock_type = "补货"
    run(playwright, type=type,goods_name=goods_name, brand_name=brand_name,stock_type=stock_type)
