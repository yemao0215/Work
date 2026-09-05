import json
import re
import time
from datetime import datetime

import jsonpath
import requests
import yaml
from faker import Faker

from huaqiu_order_api.HQCHIP_Center.assets.recharge_order import recharge_order_create
from huaqiu_order_api.HQCHIP_PAY.recharge.pay_order import PayOrder
from huaqiu_order_api.HQCHIP_SOO.login import SOOLogin
from huaqiu_order_api.SSO_Reception.sso_reception import SSO_Reception
from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_data import Data
from huaqiu_order_api.common.my_path import yaml_file, account_yaml


class BanlkStatement:
    def __init__(self):
        """
        :param phone:  登录账号
        :param psw:  登录密码
        :param goods_id:  购买的产品id
        :param numder 下单数量
        :param warehouse_id 下单仓库
        """
        self.trade_out_no = "YE"+ datetime.now().strftime("%Y%m%d") + "000000" + str(Faker("zh_CN").random_int(1, 10000))
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.PAY_URL = data['PAY_URL']
        with open(account_yaml, 'r', encoding='utf-8') as yamlfile:
            account = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.Amount = getattr(Data, 'Amount')
        # self.Amount = "3073010"
        self.headers = {"Content-Type": "application/x-www-form-urlencoded",
                        "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://www.huaqiu.com)"
                        }
        self.headers_json = {"Content-Type": "application/json",
                             "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://www.huaqiu.com)"
                             }
        self.rss = requests.Session()

    def banlk_statement_create(self):
        banlk_statement_create_url = "{}/payCenter/test/pushPythonPayNotify?domain={}".format(self.PAY_URL, self.PAY_URL)
        logger.info(banlk_statement_create_url)
        banlk_statement_create_body = [{
            "received_company": "叶茂测试",
            "trade_out_no": self.trade_out_no,
            "cmb_short_account": "",
            "summary": "货款",
            "amount": int(self.Amount)*100,
            "received_banlk": "招商银行深圳梅林分行",
            "received_account": "6225887845785811",
            "action_type": "1",
            "created_at": datetime.now().strftime("%Y%m%d")
        }]
        logger.info(banlk_statement_create_body)
        banlk_statement_create_res = self.rss.post(url=banlk_statement_create_url, json=banlk_statement_create_body, headers=self.headers_json).text
        logger.info(banlk_statement_create_res)


if __name__ == '__main__':
    BanlkStatement().banlk_statement_create()