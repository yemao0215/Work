import yaml
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService

import pcb_tool
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from huaqiu_order_api.common.my_path import pcb_config_yaml_dir


class Factory:
    def __init__(self):
        with open(pcb_config_yaml_dir, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.HQJFPCB_URL = data['HQJFPCB_URL']

    def ui_login(self):
        # 增加自动下载chorme驱动
        service = ChromeService(ChromeDriverManager().install())
        opt = webdriver.ChromeOptions()
        opt.add_experimental_option('excludeSwitches', ['enable-automation'])
        opt.add_argument('--headless')  # 这个和下面那两条是控制浏览器无头模式，注释掉就会开启浏览器跑
        opt.add_argument('--disable-gpu')
        opt.add_argument('window-size=1920x1080')
        driver = webdriver.Chrome('chromedriver', 0, options=opt, service=service) # 增加自动下载chorme驱动
        driver.get('{0}/hqjfpcb'.format(self.HQJFPCB_URL))
        driver.maximize_window()
        WebDriverWait(driver, 20, 0.5).until(
            EC.presence_of_element_located(('xpath',
                                            '//div[@class="tab-box"]//div[contains(string(), "账号密码登录")]'))).click()  # 等待登录成功后点击账号密码登录按钮
        driver.find_element(By.XPATH, '//input[@name="Username"]').send_keys('admin')  # 输入账号
        driver.find_element(By.XPATH, '//input[@name="password"]').send_keys('HQ@uat＠666')  # 输入密码
        driver.find_element(By.CLASS_NAME, 'el-button.el-button--primary.el-button--medium').click()  # 点击登录
        WebDriverWait(driver, 20, 0.5).until(
            EC.presence_of_element_located(('xpath', '//*[@id="navTab"]/div[2]/div[1]/div/div[1]/p[1]/span')))  # 等待
        return driver

    def get_phpsessid(self):
        global cookie
        driver = self.ui_login()
        cookies = driver.get_cookies()
        for cookie in cookies:
            if cookie['name'] == 'PHPSESSID':
                driver.quit()
                print(cookie['value'])
        params = {'PHPSESSID': cookie['value']}
        pcb_tool.PcbTools().write_yaml(params)



