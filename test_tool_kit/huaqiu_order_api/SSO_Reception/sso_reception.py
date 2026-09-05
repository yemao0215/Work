import base64
import json
import re
import execjs
import requests

import yaml

from huaqiu_order_api.HQCHIP_Center.user_center import user_information, login_code_obtain, login_password_update
# from huaqiu_order_api.HQCHIP_Center.user_center import get_username
from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_data import Data
from huaqiu_order_api.common.my_path import yaml_file, account_yaml, encryption_dir
import time
from selenium import webdriver
from selenium.common import NoSuchElementException, WebDriverException, SessionNotCreatedException
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from loguru import logger
from selenium.webdriver.support.ui import WebDriverWait


class SSO_Reception:
    # 前台系统单点
    def __init__(self, target_reception_url=None, phone=None,pwd=None):
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
        self.serialzed_enc_base64_url = data['serialzed_enc_base64_url']
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
        self.body = {'siteid': 12,  'account': self.phone, 'password': self.psw} # "verify_version": "2",
        self.headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://www.huaqiu.com)"
        }

    def encrypt(self, data):
        """手机号、用户名、邮箱、密码前置js加密"""
        serialzed_enc_base64_res = self.rss.get(url=self.serialzed_enc_base64_url).text
        # print(serialzed_enc_base64_res)
        serialzed_enc_base64 = re.search(r'window.transfer = "(.*?)";', serialzed_enc_base64_res).group(1)
        # print(serialzed_enc_base64)
        decoded_bytes = base64.b64decode(serialzed_enc_base64)
        decoded_bytes_json = json.loads(decoded_bytes)
        # print(decoded_bytes_json)
        # # 读取JavaScript文件内容
        with open(encryption_dir, "r", encoding="utf-8") as f:
            js_content = f.read()
        # 编译JavaScript代码
        js_runtime = execjs.compile(js_content)
        # 调用JavaScript函数
        encipherPassword = js_runtime.call("encrypt", serialzed_enc_base64, data)
        logger.info(encipherPassword)
        result1 = js_runtime.call("decrypt", serialzed_enc_base64, encipherPassword)
        logger.info(result1)
        return encipherPassword

    def login(self):
        """手机号码+密码登录"""
        self.pwd = self.encrypt(self.psw)
        self.phone = self.encrypt(self.phone)
        self.body["account"] = self.phone
        self.body["password"] = self.pwd
        self.body["agreement"] = 1
        res = self.rss.post(url=self.url, data=self.body, headers=self.headers)
        logger.info(f"开始执行登录账号:{self.body}")
        json_res = res.json()
        logger.info(json_res)
        token = json_res["data"]["token"]
        uid = json_res["data"]["uid"]
        setattr(Data, 'token', token)
        setattr(Data, 'uid', uid)
        cookie_url = json_res["data"]["syncurl"]
        # 由于smt存在有两种域名 smt.hqchip.com，smt.hqpcb.com，而且单点登录cookie里面不存在这两种单点cookie路径信息，需要等价替代华秋商城和华秋电路的域名
        result_smt = "smt" in self.target_reception_url
        if result_smt == True:
            result_hqchip = "hqchip" in self.target_reception_url
            result_hqpcb = "hqpcb" in self.target_reception_url
            if result_hqchip == True:
                self.target_reception_url = self.HQCHIP_URL
            elif result_hqpcb == True:
                self.target_reception_url = self.HQPCB_URL
        logger.info(f"当前self.target_reception_url为{self.target_reception_url}")
        for sso_url in cookie_url:
            if sso_url.find(self.target_reception_url, 0, 26) != -1:
                # print(sso_url)
                self.headers["content-type"] = "image/jpg"
                self.rss.get(url=sso_url, headers=self.headers)  # 访问单点url生成cookie
                # 隐私协议勾选
                self.headers["content-type"] = "application/x-www-form-urlencoded"
                self.headers["Authorization"] = token
                agreement_url = "{}/ajax/updateAgreementStatus?v=pc".format(self.HQCHIP_URL)
                agreement_body = "agreementType=2&agreementStatus=1"
                agreement_res = self.rss.post(url=agreement_url, data=agreement_body, headers=self.headers).json()
                print(agreement_res)
                logger.info(f"登录成功")
                break
        else:
            logger.error(f"没有找到目标商城单点登录链接，获取单点cookie失败")
            raise IOError
        username, phone, sso_uid, pcbuid = user_information(self.rss, type="NEW")
        print(f"获取到username：{username}，手机号码：{phone}, 华秋uid：{sso_uid}, 原PCB用户编号：{pcbuid}")
        setattr(Data, 'username', username)
        setattr(Data, 'phone', phone)
        setattr(Data, 'pcbuid', pcbuid)
        # setattr(Data, 'rss', self.rss)
        return self.rss

    def selenium_driver_download(self):
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service as ChromeService
        from webdriver_manager.chrome import ChromeDriverManager
        service = ChromeService(executable_path=ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service)
        driver.quit()
    def login_code(self):
        """手机号码+验证码登录"""

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
        driver.get(self.target_reception_url)
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
            time.sleep(3)
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
        driver.quit()
        return self.rss



    def login_password_code(self):
        """手机号码+密码+验证码登录"""
        # #####
        opt = webdriver.ChromeOptions()
        opt.add_experimental_option('excludeSwitches', ['enable-automation'])
        opt.add_argument("--disable-blink-features=AutomationControlled")
        opt.add_argument('--headless')  # 这个和下面那两条是控制浏览器无头模式，注释掉就会开启浏览器跑
        opt.add_argument('--disable-gpu')
        # driver = webdriver.Chrome(options=opt)
        try:
            # chromedriver版本下载地址：https://storage.googleapis.com/chrome-for-testing-public/{Chrome版本号}/win64/chromedriver-win64.zip
            print('chormedriver版本与Chrome兼容，无需重新下载chromedriver')
            service = ChromeService(executable_path=r'C:\Users\WIN\.wdm\drivers\chromedriver\win64\131.0.6778.205\chromedriver-win32/chromedriver.exe')
            driver = webdriver.Chrome(service=service, options=opt)
        except Exception:
            print('chormedriver版本与Chrome不兼容，需重新下载chromedriver')
            service = ChromeService(executable_path=ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service)
        driver.get(self.target_reception_url)
        driver.maximize_window()
        # 开屏广告处理
        # el = WebDriverWait(driver, timeout=3).until(lambda d: d.find_element(By.XPATH,'XPATH'))
        time.sleep(3)
        try:
            driver.find_element(By.XPATH, '//a[@class="close"]').click()
        except NoSuchElementException:
            pass

        # 移除遮挡元素
        driver.execute_script("document.querySelector('div[style*=\"position:fixed;z-index:99999999;\"]').remove();")
        # 点击登录
        driver.find_element(By.XPATH, '//a[text()="登录"]').click()
        # 切换iframe
        iframe = driver.find_element(By.XPATH, '//iframe[@name="sso-LoginIframe"]')
        driver.switch_to.frame(iframe)
        # 点击登录窗口中的登录
        time.sleep(2)
        driver.find_element(By.XPATH, '//div[@class=" scan-code-login"]//span[@class="J_pwdLogin"]').click()
        # 输入错误账号、密码触发滑动验证
        driver.find_element(By.XPATH, '//input[@placeholder="用户名/邮箱/手机号码"]').clear()
        driver.find_element(By.XPATH, '//input[@placeholder="用户名/邮箱/手机号码"]').send_keys(self.phone)
        driver.find_element(By.XPATH, '//input[@placeholder="请输入密码"]').clear()
        driver.find_element(By.XPATH, '//input[@placeholder="请输入密码"]').send_keys(self.psw)
        # driver.find_element(By.XPATH, '//button[text()="登录"]').click()
        # 操作滑动验证块
        try:
            time.sleep(3)
            sliding_block = driver.find_element(By.XPATH, '//div[@id="nc_2_n1t"]/span')
            action = ActionChains(driver)
            action.click_and_hold(sliding_block)
            action.move_by_offset(336, 0).release().perform()
            driver.find_element(By.XPATH, '//button[text()="登录"]').click()
            time.sleep(5)
            # 获取登录后的cookies
            cookies = driver.get_cookies()
            print(cookies)
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
        driver.quit()
        return self
if __name__ == '__main__':
    rss = SSO_Reception('https://uat-www.hqchip.com').login()
    # login_password_update(rss, "a123456", old_password='ye123456')
    # SSO_Reception('https://uat-www.hqchip.com').encrypt("ye123456")
    # asyncio.get_event_loop().run_until_complete(SSO_Reception('https://uat-www.hqchip.com').main())