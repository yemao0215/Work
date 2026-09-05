
import json
import re
from datetime import datetime, timedelta

import jsonpath
import requests
import yaml

from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_data import Data
from huaqiu_order_api.common.my_path import yaml_file, account_yaml


class PayOrder:
    def __init__(self, rss):
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.PAY_URL = data['PAY_URL']
        with open(account_yaml, 'r', encoding='utf-8') as yamlfile:
            account = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.recharge_order = getattr(Data, 'recharge_order')
        print(self.recharge_order)
        # self.recharge_order = "R23121410402690670"
        self.headers = {"Content-Type": "application/x-www-form-urlencoded",
                        "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://www.huaqiu.com)"
                        }
        self.headers_json = {"Content-Type": "text/html; charset=UTF-8",
                             "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://www.huaqiu.com)"
                             }
        self.pay_rss = rss




    def pay_order_search(self):
        # 获取当前月份的第一天
        first_day = datetime.now().replace(day=1)
        next_month = first_day.replace(day=28) + timedelta(days=4)
        # 获取当前月份的最后一天
        last_day =next_month - timedelta(days=next_month.day)
        logger.info(first_day)
        logger.info(last_day)
        first_day_time = str(first_day.strftime("%Y-%m-%d %H:%M:%S"))
        last_day_time = str(last_day.strftime("%Y-%m-%d %H:%M:%S"))
        search_url = "{}/management/account/payTrade/query".format(self.PAY_URL)
        search_body = {"mchTradeNo": self.recharge_order, "startTime": first_day_time, "endTime": last_day_time, "pageNum": 1, "pageSize": 50}
        logger.info(search_body)
        search_res = self.pay_rss.post(url=search_url, json=search_body).json()
        logger.info(search_res)
        id = jsonpath.jsonpath(search_res, "$..id")[0]
        centerTradeNo = jsonpath.jsonpath(search_res, "$..centerTradeNo")[0]
        centerTradeNoExtend = jsonpath.jsonpath(search_res, "$..centerTradeNoExtend")[0]
        payAmount = jsonpath.jsonpath(search_res, "$..payAmount")[0]
        uid = jsonpath.jsonpath(search_res, "$..userId")[0]
        setattr(Data, "pay_order_id", id)
        setattr(Data, "centerTradeNo", centerTradeNo)
        setattr(Data, "trade_no", centerTradeNoExtend)
        setattr(Data, "payAmount", float(payAmount/100))
        setattr(Data, "uid", uid)
        return centerTradeNoExtend

    def pay_order_status(self):
        self.pay_order_id = getattr(Data, 'pay_order_id')
        self.centerTradeNo = getattr(Data, 'centerTradeNo')
        pay_order_status_url = '{}/management/pay/center/queryPayOrder'.format(self.PAY_URL)
        pay_order_status_body = {"centerTradeNo": self.centerTradeNo, "id": self.pay_order_id, "payChannelId": 6}
        pay_order_status_res = self.pay_rss.post(url=pay_order_status_url, json=pay_order_status_body, headers=self.headers_json).json()
        logger.info(pay_order_status_res)
        return self