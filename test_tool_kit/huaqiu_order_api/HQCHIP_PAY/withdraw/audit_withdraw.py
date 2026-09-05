import time
from datetime import datetime, timedelta

import requests
import yaml

from huaqiu_order_api.SSO_Reception.sso_reception import SSO_Reception
from huaqiu_order_api.common.my_data import Data
from huaqiu_order_api.common.my_path import yaml_file


class AuditWithdraw:
    def __init__(self):
        self.rss = requests.session()
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.Assets_Center_url = data['Assets_Center_url']
        self.PAY_URL = data['PAY_URL']
        self.uid = getattr(Data, 'uid', "5146221")
        self.withdraw_order = getattr(Data, 'withdraw_order')
        self.withdrawAmount = getattr(Data, 'withdrawAmount')
        # self.withdraw_order = "W24011517215325568"
        # self.withdrawAmount = "5000"


    def audit_withdraw_order(self):
        timestamp_now = int(time.time())
        now_time = str((datetime.now()).strftime("%Y-%m-%d %H:%M:%S"))
        audit_withdraw_order_url = "{}/assets/withdrawalOrder/AuditedWithdrawalOrder".format(self.Assets_Center_url)
        audit_withdraw_order_body = {
            "userId": self.uid,
            "passed": True,
            "orderNo": self.withdraw_order,
            "realityAmount": float(self.withdrawAmount) * 100,
            "realityTime": now_time,
            "currency": "CNY",
            "appid": "90167",
            "timestamp": timestamp_now,
            "operatorId": "22",
            "operatorJobNo": "22",
            "operatorName": "22"
        }
        sign = self.sign(audit_withdraw_order_body, app_id='90167')
        header = {"signature": sign}
        audit_withdraw_order_res = self.rss.post(url=audit_withdraw_order_url, json=audit_withdraw_order_body, headers=header).json()
        audit_withdraw_order_msg = audit_withdraw_order_res["retMsg"]
        print(audit_withdraw_order_res)
        return self.withdrawAmount, audit_withdraw_order_msg


    def sign(self, param, app_id=None):
        """加密"""
        if app_id == None:
            query = {"appId": ""}
        else:
            query = {"appId": app_id}
        sign_url = "{}/payCenter/test/getSignature".format(self.PAY_URL)
        sign_res = self.rss.post(url=sign_url, json=param, params=query).json()
        try:
            sign = sign_res["result"]
        except Exception as e:
            sign = e
        return sign



if __name__ == '__main__':
    SSO_Reception('https://uat-www.hqchip.com').login()
    AuditWithdraw().audit_withdraw_order()