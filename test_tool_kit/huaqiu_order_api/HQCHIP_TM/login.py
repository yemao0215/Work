import os
import re
from playwright.sync_api import Playwright, sync_playwright, expect
from huaqiu_order_api.common.my_path import uiTest_img_2018

def run(playwright: Playwright, goods_name=None) -> None:
    # 启动浏览器
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context(
        color_scheme="dark",
        viewport={"width": 1920, "height": 1080}
    )

    # ===================== 打开第一个标签页 =====================
    page1 = context.new_page()
    page1.goto("https://tm.elecfans.net/login#/")
    page1.get_by_placeholder("ID 或 邮箱").click()
    page1.get_by_placeholder("ID 或 邮箱").fill("yemao")
    page1.get_by_placeholder("密码").click()
    page1.get_by_placeholder("密码").fill("Yemao123456")
    page1.get_by_role("button", name="登录").click()
    page1.wait_for_timeout(4000)

    # ===================== 打开第二个标签页 =====================
    page2 = context.new_page()  # 新建标签页
    page2.goto("https://tm.elecfans.net/login#/")  # 同样访问网站
    page2.get_by_placeholder("ID 或 邮箱").click()
    page2.get_by_placeholder("ID 或 邮箱").fill("yemao")
    page2.get_by_placeholder("密码").click()
    page2.get_by_placeholder("密码").fill("Yemao123456")
    page2.get_by_role("button", name="登录").click()
    page2.wait_for_timeout(4000)

    # 保持程序不退出
    page1.wait_for_timeout(100000)
    page2.wait_for_timeout(100000)

    # 关闭
    context.close()
    browser.close()


with sync_playwright() as playwright:
    goods_name = "LiaoPeng00019"
    run(playwright, goods_name=goods_name)