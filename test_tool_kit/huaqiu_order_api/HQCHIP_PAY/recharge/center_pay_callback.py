import json
import re
import time

import jsonpath
import requests
import yaml

from huaqiu_order_api.HQCHIP_Center.assets.recharge_order import recharge_order_create
from huaqiu_order_api.HQCHIP_PAY.recharge.pay_order import PayOrder
from huaqiu_order_api.HQCHIP_SOO.login import SOOLogin
from huaqiu_order_api.SSO_Reception.sso_reception import SSO_Reception
from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_data import Data
from huaqiu_order_api.common.my_path import yaml_file, account_yaml


class CenterPayCallback:
    def __init__(self):
        """
        :param phone:  登录账号
        :param psw:  登录密码
        :param goods_id:  购买的产品id
        :param numder 下单数量
        :param warehouse_id 下单仓库
        """
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.PAY_URL = data['PAY_URL']
        with open(account_yaml, 'r', encoding='utf-8') as yamlfile:
            account = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.Amount = getattr(Data, 'Amount')
        self.activity_type = [None if getattr(Data, 'activity_type', None) == '不参与' else getattr(Data, 'activity_type', None)][0]
        self.headers = {"Content-Type": "application/x-www-form-urlencoded",
                        "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://www.huaqiu.com)"
                        }
        self.headers_json = {"Content-Type": "application/json",
                             "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://www.huaqiu.com)"
                             }
        self.rss = requests.Session()


    def center_pay_callback(self):
        self.uid = getattr(Data, 'uid')
        self.payAmount = getattr(Data, 'payAmount')
        self.trade_no = getattr(Data, 'trade_no')
        # self.uid = 5146221
        # self.payAmount = 10
        # self.trade_no = "1739542714368770049X150443446"
        center_pay_callback_url = "{}/payCenter/notify/pay/ali".format(self.PAY_URL)
        # center_pay_callback_body = {"out_trade_no": self.trade_no, "total_amount": self.payAmount, "trade_status": "TRADE_SECCESS",
        #                             "trade_no": self.trade_no, "user_id": self.uid}
        center_pay_callback_body = f"out_trade_no={self.trade_no}&total_amount={self.payAmount}&trade_status=TRADE_SUCCESS&trade_no={self.trade_no}&user_id={self.uid}"
        center_pay_callback_res = self.rss.post(url=center_pay_callback_url, data=center_pay_callback_body, headers=self.headers_json).text
        logger.info(center_pay_callback_res)
        return self

    def mian_pay_callback(self):
        rss = SSO_Reception('https://uat-www.hqchip.com').login()
        recharge_order = recharge_order_create(rss, int(self.Amount), activity_type=self.activity_type)
        target_rss = SOOLogin("uat-pay.huaqiu.com", "management").target_login()
        centerTradeNoExtend = PayOrder(target_rss).pay_order_search()
        time.sleep(5)
        self.center_pay_callback()
        PayOrder(target_rss).pay_order_status()
        reception_rss = rss
        return recharge_order, centerTradeNoExtend, reception_rss
if __name__ == '__main__':
    CenterPayCallback().mian_pay_callback()
    # CenterPayCallback().center_pay_callback()

