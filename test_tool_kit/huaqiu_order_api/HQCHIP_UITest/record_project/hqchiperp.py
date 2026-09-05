from playwright.sync_api import Playwright, sync_playwright, expect


def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context(color_scheme="dark", viewport={"width":1920,"height":1080})
    page = context.new_page()
    page.goto("https://uat-auth.huaqiu.com/#/login?redirect=https%3A%2F%2Fuat-e.hqchip.com%2FAuthLogin%2FssoLogin&logoutType=1")
    page.goto("https://uat-auth.huaqiu.com/#/login?noCheck=true&redirect=https%3A%2F%2Fuat-e.hqchip.com%2FAuthLogin%2FssoLogin")
    page.get_by_text("账号密码登录").first.click()
    page.get_by_placeholder("请输入账号").click()
    page.get_by_placeholder("请输入账号").fill("admin")
    page.get_by_placeholder("请输入密码").click()
    page.get_by_placeholder("请输入密码").press("CapsLock")
    page.get_by_placeholder("请输入密码").fill("HQ@uat@666")
    page.get_by_role("button", name="登录").click()
    page.close()

    # ---------------------
    context.storage_state(path="auth.json")
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)
