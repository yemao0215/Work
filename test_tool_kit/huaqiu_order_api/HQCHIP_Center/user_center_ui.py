import os

import requests
import yaml


from huaqiu_order_api.HQCHIP_Center.user_center import user_information, login_code_obtain, login_password_update
# from huaqiu_order_api.HQCHIP_Center.user_center import get_username
from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_data import Data
from huaqiu_order_api.common.my_path import yaml_file, account_yaml
import time
from selenium import webdriver
from selenium.common import NoSuchElementException, WebDriverException
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from loguru import logger
from selenium.webdriver.support.ui import WebDriverWait


class UserCenterUI:
    # 前台系统单点
    def __init__(self, target_reception_url, phone=None,pwd=None):
        """
        :param phone:  登录账号
        :param psw:  登录密码
        :param goods_id:  购买的产品id
        :param numder 下单数量
        :param warehouse_id 下单仓库
        :param target_reception_url 目标前台系统URL
        """
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.PassPort_URL = data['PassPort_URL']
        self.HQCHIP_URL = data['HQCHIP_URL']
        self.HQPCB_URL = data['HQPCB_URL']
        with open(account_yaml, 'r', encoding='utf-8') as yamlfile:
            account = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.phone = account["PassPort"]["phone"]
        self.psw = account["PassPort"]["pwd"]
        if phone != None and pwd != None:
            self.phone = phone
            self.psw = pwd
        self.rss = requests.Session()
        self.target_reception_url = target_reception_url
        self.url = '{}/login/dologin.html'.format(self.PassPort_URL)
        self.body = {'siteid': 12, 'account': self.phone, 'password': self.psw}
        self.headers = {"Content-Type": "application/x-www-form-urlencoded"}
    def center_push(self):
        #####
        opt = webdriver.ChromeOptions()
        opt.add_experimental_option('excludeSwitches', ['enable-automation'])
        opt.add_argument("--disable-blink-features=AutomationControlled")
        # opt.add_argument('--headless')  # 这个和下面那两条是控制浏览器无头模式，注释掉就会开启浏览器跑
        opt.add_argument('--disable-gpu')
        # driver = webdriver.Chrome(options=opt)
        try:
            print('chormedriver版本与Chrome兼容，无需重新下载chromedriver')
            service = ChromeService(
                executable_path=r'C:\Users\WIN\.wdm\drivers\chromedriver\win64\120.0.6099.109\chromedriver-win32/chromedriver.exe')
            driver = webdriver.Chrome(service=service, options=opt)
        except WebDriverException:
            print('chormedriver版本与Chrome不兼容，需重新下载chromedriver')
            service = ChromeService(executable_path=ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=opt)
        driver.get('https://uat-www.hqchip.com/users/login.html?back_act=https%3A%2F%2Fuat-www.hqchip.com%2Fmycenter%2F')
        driver.maximize_window()
        # 开屏广告处理
        # el = WebDriverWait(driver, timeout=3).until(lambda d: d.find_element(By.XPATH,'XPATH'))
        time.sleep(3)
        try:
            driver.find_element(By.XPATH, '//a[@class="close"]').click()
        except NoSuchElementException:
            pass
        # 点击登录
        driver.find_element(By.XPATH, '//a[text()="登录"]').click()
        # 切换iframe
        iframe = driver.find_element(By.XPATH, '//iframe[@name="sso-LoginIframe"]')
        driver.switch_to.frame(iframe)
        time.sleep(3)
        # 点击登录窗口中的验验证码登录
        driver.find_element(By.XPATH, '//div[@class=" scan-code-login"]//span[@class="J_smsLogin"]').click()
        time.sleep(2)
        # 输入手机号码
        # driver.find_element(By.XPATH, '//input[@placeholder="请输入手机号').clear()
        driver.find_element(By.XPATH, '//input[@placeholder="输入手机号"]').send_keys(self.phone)
        # 操作滑动验证块
        try:
            sliding_block = driver.find_element(By.XPATH, '//div[@id="nc_1_n1t"]/span')
            action = ActionChains(driver)
            action.click_and_hold(sliding_block)
            action.move_by_offset(336, 0).release().perform()
            driver.find_element(By.XPATH, '//form[@class="g-hide ui-form J_sms_login J_sso_valid"]//label[@for="smsIpt"]').click()
            time.sleep(5)
            code = login_code_obtain(self.phone)
            time.sleep(2)
            driver.find_element(By.XPATH, '//input[@placeholder="输入验证码"]').send_keys(code)
            sliding_block = driver.find_element(By.XPATH, '//div[@id="nc_1_n1t"]/span')
            action = ActionChains(driver)
            action.click_and_hold(sliding_block)
            action.move_by_offset(336, 0).release().perform()
            time.sleep(5)
            driver.find_element(By.XPATH, '//button[text()="注册/登录"]').click()
            time.sleep(5)
            # 获取登录后的cookies
            cookies = driver.get_cookies()
            # print(cookies)
            token = None
            for cookie in cookies:
                if cookie["name"] == "auth_token":
                    token = cookie["value"]
                    break
            if token:
                print("Token:", token)
                setattr(Data, 'token', token)
            else:
                print("Token not found in cookies")
        except NoSuchElementException:
            pass
            logger.info(f"没有检测到滑块，不需要滑动解锁")

        time.sleep(2)