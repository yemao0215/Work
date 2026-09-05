import hashlib
import json
import time

import jsonpath
import requests
import yaml

from huaqiu_order_api.HQCHIP_PAY.signature.addSignatureInterface import AddSignAtureInterface
from huaqiu_order_api.HQCHIP_SOO.login import SOOLogin
from huaqiu_order_api.HQCHIP_PAY.log_center.access_log import PayManagementAccessLog
from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_data import Data
from huaqiu_order_api.common.my_path import yaml_file

class BalancePayment:
    def __init__(self, order_sn=None):
        self.rss = requests.session()
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.PAY_URL = data['PAY_URL']
        self.headers = {"Content-Type": "application/x-www-form-urlencoded",
                        "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://www.huaqiu.com)"
                        }
        self.headers_json = {"Content-Type": "application/json",
                             "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://www.huaqiu.com)"
                             }
        self.order_sn = getattr(Data, 'order_sn', order_sn)
    def pay_password_encry(self, pay_password=None):
        """支付密码加密"""
        pay_password_encry_url = "{}/payCenter/test/dataEncryption?appId={}&body={}".format(self.PAY_URL, "306a338cb8f048f399f35511f77a3670", pay_password)
        pay_password_encry_res = self.rss.get(url=pay_password_encry_url).json()
        pay_password_encry = pay_password_encry_res['result']
        return pay_password_encry
    def payV3_place_an_order(self,signature, data):
        # 支付V3
        payV3_place_an_order_url = "{}/payCenter/payV3/center/acquire".format(self.PAY_URL)
        payV3_place_an_order_body = data
        self.headers_json['signature'] = signature
        payV3_place_an_order_res = self.rss.post(url=payV3_place_an_order_url, json=payV3_place_an_order_body,
                                             headers=self.headers_json).json()
        self.authKey = jsonpath.jsonpath(payV3_place_an_order_res, '$..authKey')[0]
        self.centerTradeNo = jsonpath.jsonpath(payV3_place_an_order_res, '$..centerTradeNo')[0]
        return self
    def balance_place_an_order(self):
        # 切换余额支付
        balance_place_an_order_url = "{}/payCenter/payV3/transaction/payment".format(self.PAY_URL)
        balance_place_an_order_body = {
            "returnUrl": "v3/pay/success",
            "payChannelId": 3,
            "instalments": None,
            "centerTradeNo": self.centerTradeNo,
            "authKey": self.authKey
        }
        balance_place_an_order_res = self.rss.post(url=balance_place_an_order_url, json=balance_place_an_order_body,
                                             headers=self.headers_json).json()
        print(balance_place_an_order_res)
        return self


    def balance_order_pay(self):
        # 执行余额支付
        balance_order_pay_url = "{}/payCenter/payV3/assets/balanceOrCreditPay".format(self.PAY_URL)
        balance_order_pay_body = {
                "payChannelId": 3,
                "password": self.pay_password_encry("123456"),
                "centerTradeNo": self.centerTradeNo,
                "authKey": self.authKey
        }
        balance_order_pay_res = self.rss.post(url=balance_order_pay_url, json=balance_order_pay_body,
                                             headers=self.headers_json).json()
        print(balance_order_pay_res)
        return self
    def main_balance_pay(self):
        target_rss = SOOLogin(system_name="pay").target_login()
        requestJson = PayManagementAccessLog(target_rss, self.order_sn).access_log_search()
        signature = AddSignAtureInterface(data=requestJson).assets_sginature("IC")
        self.payV3_place_an_order(signature, requestJson)
        self.balance_place_an_order()
        self.balance_order_pay()
        return self
if __name__ == '__main__':
    order_sn = "S2026040353833"
    BalancePayment(order_sn).main_balance_pay()