import re
import time

import requests
import yaml
from faker import Faker

from huaqiu_order_api.HQCHIP_Center.user_center import pay_password, login_password_update, user_information
from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_data import Data
from huaqiu_order_api.common.my_path import yaml_file
import time
from selenium import webdriver
from selenium.common import NoSuchElementException, WebDriverException
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from loguru import logger
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# passport_url = "https://uat-passport.elecfans.com"
class UserRegister:

    # 随机获取手机号码进行注册账号
    def __init__(self, phone=None):
        """
        :param phone:  登录账号
        :param psw:  登录密码
        :param goods_id:  购买的产品id
        """
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.passport_url = data['PassPort_URL']
        self.HQCHIP_URL = data['HQCHIP_URL']
        self.phone = phone
        self.rss = requests.Session()
        self.url = '{}/login/dologin.html'.format(self.passport_url)
        # self.body = {'siteid': 12, 'account': self.phone, 'password': psw}
        self.headers = {"Content-Type": "application/x-www-form-urlencoded", "User-Agent":"Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://www.huaqiu.com)"}

    def register(self, password_update_type, paypassword, new_password):
        """用户注册
        siteid 注册站点  1华强聚丰账号系统  2数据手册-pdf 3DIY 4电子论坛 5孵化器 6聚丰众筹 7电子发烧友学院 8在线研讨会 9电子发烧友活动 10发烧友触屏版 11电子发烧友门户
                        12华秋商城 13华秋商城m端 14smt商城 16webapp 17华秋电路 18发烧友VIP 19华秋电路用户中心 20华秋商城用户中心 21网络展会 22华秋DFM 23硬声APP
                        24企业号 25发烧友专题 26支付中心 27用户中心 28资产中心 29CRM 30客诉系统 31用户中心JAVA版 34华秋认证 35上海芯灵
        """
        type_send_code = 0
        push_body = None
        if self.phone == None:
            phone = Faker("zh_CN").phone_number()
            self.phone = phone
            logger.info(f"随机生成手机号码为：{self.phone}")
        # 发送手机号码验证码
        send_code_url = "{}/register/regsms".format(self.passport_url)
        send_code_body = {"account": self.phone, "areacode":"0086"}
        if type_send_code == 1:
            csessionid_value, sig_value, token_value, aliscene_value, driver = UserRegister().register_push()
            push_body = {"csessionid": csessionid_value, "sig": sig_value, "token": token_value, "aliscene": aliscene_value}
            send_code_body.update(push_body)
        send_code_res = self.rss.post(url=send_code_url, data=send_code_body, headers=self.headers).json()
        logger.info(f"发送验证码成功,返回结果为{send_code_res}")
        #获取手机号码验证码
        obtain_code_url = "{}/lookcode".format(self.passport_url)
        obtain_code_res = self.rss.get(url=obtain_code_url).text
        code = re.split(self.phone+'：', obtain_code_res)[1].split("<br>")[0]
        logger.info(f"获取手机验证码为：{code}")

        # 注册
        register_url = "{}/smsLogin/index".format(self.passport_url)
        register_body = {"account": self.phone, "areacode": "0086", "smscode": code, "siteid": 17, "agreement": 1}
        if type_send_code == 1:
            register_body.update(push_body)
            logger.info(register_body)
        register_res = self.rss.post(url=register_url, data=register_body, headers=self.headers).json()
        # print(register_res)
        if register_res["msg"] == "账号不存在":
            time.sleep(60)
            self.rss.post(url=send_code_url, data=send_code_body, headers=self.headers).json()
            obtain_code_res = self.rss.get(url=obtain_code_url).text
            new_code = re.split(self.phone + '：', obtain_code_res)[1].split("<br>")[0]
            register_body["smscode"] = new_code
            register_body["scene"] = "apply"
            register_res = self.rss.post(url=register_url, data=register_body, headers=self.headers).json()
        uid = register_res["data"]["uid"]
        token = register_res["data"]["token"]
        setattr(Data, 'uid', uid)
        setattr(Data, 'token', token)
        self.headers["Authorization"] = token
        # 隐私协议勾选
        agreement_url = "{}/ajax/updateAgreementStatus?v=pc".format(self.HQCHIP_URL)
        agreement_body = "agreementType=2&agreementStatus=1"
        agreement_res = self.rss.post(url=agreement_url, data=agreement_body, headers=self.headers).json()
        print(agreement_res)
        # 获取注册手机号码在用户中心那边结果
        username, phone, sso_uid, pcbuid = user_information(self.rss)
        print(f"获取到username：{username}，手机号码：{phone}, 华秋uid：{sso_uid}, 原PCB用户编号：{pcbuid}")
        setattr(Data, 'username', username)
        setattr(Data, 'phone', phone)
        setattr(Data, 'pcbuid', pcbuid)
        logger.info(f"注册成功,获取到uid：{uid}，token：{token}")
        if password_update_type == "3":
            logger.info("开始设置支付密码")
            # # paypassword = "123456"
            pay_password(self.rss, paypassword)
            logger.info(f"修改支付密码成功，支付密码为:{paypassword}")
            # logger.info("开始修改登录密码")
            time.sleep(60)
            # logger.info("等待60s")
            password_update_uid = login_password_update(self.rss, new_password)
            if str(password_update_uid) == uid:
                logger.info(f"注册手机号：{self.phone} 成功，并且其设置新的登录密码{new_password}，支付密码：{paypassword}")
        elif password_update_type == "2":
            logger.info("开始设置支付密码")
            # # paypassword = "123456"
            pay_password(self.rss, paypassword)
            logger.info(f"修改支付密码成功，支付密码为:{paypassword}")
        elif password_update_type == "1":
            time.sleep(60)
            # logger.info("等待60s")
            password_update_uid = login_password_update(self.rss, new_password)
            if str(password_update_uid) == uid:
                logger.info(f"注册手机号：{self.phone} 成功，并且其设置新的登录密码{new_password}")

        return self.phone, paypassword, new_password
    def register_push(self):
        opt = webdriver.ChromeOptions()
        opt.add_experimental_option('excludeSwitches', ['enable-automation'])
        opt.add_argument("--disable-blink-features=AutomationControlled")
        opt.add_argument('--headless')  # 这个和下面那两条是控制浏览器无头模式，注释掉就会开启浏览器跑
        opt.add_argument('--disable-gpu')
        # driver = webdriver.Chrome(options=opt)
        try:

            service = ChromeService(executable_path=r'C:\Users\WIN\.wdm\drivers\chromedriver\win64\137.0.7151.55\chromedriver-win32/chromedriver.exe')
            driver = webdriver.Chrome(service=service, options=opt)
            print('chormedriver版本与Chrome兼容，无需重新下载chromedriver')
        except WebDriverException as e:
            print(f'错误: {e}')
            service = ChromeService(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=opt)
            print('chormedriver版本与Chrome不兼容，需重新下载chromedriver')
        driver.get(self.HQCHIP_URL)
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
        # 进出口协议 是否可见
        try:
            element = driver.find_element(By.XPATH, '//button[text()="我已知悉 (ACCEPT)"]')
            if element.is_displayed():
                element.click()
        except NoSuchElementException:
            pass
        # 点击注册
        driver.find_element(By.XPATH, '//a[text()="注册"]').click()
        # 切换iframe
        iframe = driver.find_element(By.XPATH, '//iframe[@name="sso-RegIframe"]')
        driver.switch_to.frame(iframe)
        time.sleep(3)
        try:
            sliding_block = driver.find_element(By.XPATH, '//div[@id="nc_1_n1t"]/span')
            action = ActionChains(driver)
            action.click_and_hold(sliding_block)
            action.move_by_offset(336, 0).release().perform()
            time.sleep(5)
            # 定位到目标元素
            csessionid_element = driver.find_element(By.XPATH,
                                                     '//input[@name="csessionid"]')
            sig_element = driver.find_element(By.XPATH, '//input[@name="sig"]')
            token_element = driver.find_element(By.XPATH,
                                                '//input[@name="token"]')
            aliscene_element = driver.find_element(By.XPATH,
                                                   '//input[@name="aliscene"]')
            # 获取元素的值
            csessionid_value = csessionid_element.get_attribute("value")
            sig_value = sig_element.get_attribute("value")
            token_value = token_element.get_attribute("value")
            aliscene_value = aliscene_element.get_attribute("value")
            print(csessionid_value)
            # # driver.find_element(By.XPATH,'//button[@class="el-button base-button w-full el-button--primary"]//span[contains(string(),"登录")]').click()
            # driver.find_element(By.XPATH,'//button[text()="登录"]').click()
            return csessionid_value, sig_value, token_value, aliscene_value, driver
        except NoSuchElementException:
            pass
            logger.info(f"没有检测到滑块，不需要滑动解锁")


        # driver.get('https://www.hqchip.com')
        time.sleep(2)
        # driver.quit()

    def register_push_login_password_update(self, driver):
        driver.find_element(By.XPATH, '//input[@placeholder="请输入手机号"]').send_keys(self.phone)


if __name__ == "__main__":
    UserRegister().register("123456", "ye123456")