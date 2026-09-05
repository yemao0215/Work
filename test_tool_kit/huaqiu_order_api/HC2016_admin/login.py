import math
import re

import jsonpath
import requests
import yaml

from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_data import Data
from huaqiu_order_api.common.my_path import yaml_file, account_yaml


class HC2016Login:
    def __init__(self):
        self.rss = requests.Session()
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.HQCHIP_ADMIN_URL = data['HQCHIP_ADMIN_URL']
        self.headers = {"Content-Type": "application/x-www-form-urlencoded",
                        "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://www.huaqiu.com)"
                        }
        self.headers_json = {"Content-Type": "application/json; charset=UTF-8",
                             "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://www.huaqiu.com)"
                             }
    def hc2016_login(self):
        """HC2016后台登录"""
        login_url = "{}/Admin/Public/checkLogin/".format(self.HQCHIP_ADMIN_URL)
        self.body = {"user_name": "admin", "password": "HQ@uat@666"}
        logger.info(f"开始执行登录账号：{self.body}")
        self.rss.post(url=login_url, data=self.body, headers=self.headers)
        logger.info(f"登录完成")
        return self.rss