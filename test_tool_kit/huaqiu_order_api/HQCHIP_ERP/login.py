import requests
import yaml

from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_data import Data
from huaqiu_order_api.common.my_path import yaml_file, account_yaml


class ErpLogin:


    def __init__(self):
        """
        :param account:  登录ERP账号
        :param psw:  登录ERP密码
        :param order_sn:  前台商城生成订单编号
        :param uesr:    前台商城生成订单编号的用户名称
        """
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.ERP_URL = data['ERP_URL']
        with open(account_yaml, 'r', encoding='utf-8') as yamlfile:
            account = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.account = account["HQCHIP_ERP"]["user"]
        self.password = account["HQCHIP_ERP"]["pwd"]
        self.rss = requests.Session()
        self.login_url = '{}/public/checkLogin/'.format(self.ERP_URL)
        self.body = {'account': self.account, 'password': self.password}
        self.headers = {'Content-Type': 'application/x-www-form-urlencoded',
                        "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://www.huaqiu.com)"
                        }

    def login(self):
        """
        登录ERP
        """
        logger.info(f"开始执行登录账号:{self.body}")
        self.rss.post(url=self.login_url, data=self.body, headers=self.headers)
        logger.info(f"登录完成")
        return self.rss

    def logout_login_audit(self, audit_account, audit_pwd):
        logout_url = "{}/public/logout".format(self.ERP_URL)
        self.rss.get(url=logout_url)
        logger.info(f"退出登录成功")

        # 登录审核人账号
        login_audit_body = {'account': audit_account, 'password': audit_pwd}
        logger.info(f"开始执行登录审核人账号:{login_audit_body}")
        login_audit_url = self.login_url
        self.rss.post(url=login_audit_url, data=login_audit_body, headers=self.headers)
        logger.info(f"登录完成")
        return self.rss