import os

import jsonpath
import requests
import yaml

from huaqiu_order_api.HQCHIP_Center.user_center import get_address, get_invoice, get_man
from huaqiu_order_api.SSO_Reception.sso_reception import SSO_Reception
from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_data import Data
from huaqiu_order_api.common.my_path import stockup_dir, smt_yansuo_dir, bom_dir, yaml_file, account_yaml


class StencilHtysmt:
    def __init__(self):
        self.rss = requests.Session()
        self.headers = {"Content-Type": "application/json",
                        #"User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://debug.htysmt.com)"
                        }
        self.form_headers = {"Content-Type": "application/x-www-form-urlencoded",
                             "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://www.huaqiu.com)"
                             }
        self.data_headers = {"Content-Type": "multipart/form-data",
                             "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://www.huaqiu.com)"
                             }
        # self.phone = phone
        # self.token = getattr(Data, "token")
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.HTYSMT_URL = data['HTYSMT_URL']
        with open(account_yaml, 'r', encoding='utf-8') as yamlfile:
            account = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.user = account['HTYSMT']['user']
        self.pwd = account['HTYSMT']['pwd']
    def login(self):
        """登录"""
        login_url = '{}/api/logon'.format(self.HTYSMT_URL)
        login_body = {"UserName": self.user, "Password": self.pwd}
        login_res = self.rss.post(url=login_url, json=login_body, headers=self.headers).json()
        token = jsonpath.jsonpath(login_res, "$..token")[0]
        userId = jsonpath.jsonpath(login_res, "$..userId")[0]
        logger.info(f"获取到userId为：{userId}")
        setattr(Data, 'htysmt_token', token)
        setattr(Data, 'htysmt_userId', userId)
        return self.rss
if __name__ == '__main__':
    StencilHtysmt().login()
