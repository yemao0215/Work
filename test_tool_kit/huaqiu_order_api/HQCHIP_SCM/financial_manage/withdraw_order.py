import time
from datetime import datetime, timedelta

import jsonpath
import requests
import yaml

from huaqiu_order_api.HQCHIP_SOO.login import SOOLogin
from huaqiu_order_api.SSO_Reception.sso_reception import SSO_Reception
from huaqiu_order_api.common.my_data import Data
from huaqiu_order_api.common.my_path import yaml_file, account_yaml
from huaqiu_order_api.common.yaml_handler import write_yaml


class ScmWithdrawManage:
    def __init__(self, rss):
        self.rss = rss
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.Assets_Center_url = data['Assets_Center_url']
        self.PAY_URL = data['PAY_URL']
        self.SCM_URL = data['SCM_URL']
        # self.uid = getattr(Data, 'uid')
        self.withdraw_order = getattr(Data, 'withdraw_order')
        self.withdrawAmount = getattr(Data, 'withdrawAmount')
        self.login_name = getattr(Data, 'login_name', "")
        # self.withdraw_order = "W24081417513998069"
        # self.withdrawAmount = "5000"
        self.headers_json = {"Content-Type": "application/json; charset=UTF-8",
                             "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
                             }
    def withdraw_order_submit(self):
        """提交生成的提现单到审核中心"""
        withdraw_order_search_url = "{}/financialservice/withdrawal/page".format(self.SCM_URL)
        print(withdraw_order_search_url)
        withdraw_order_search_body = {
            "userId": "",
            "orderNo": self.withdraw_order,
            "salesmanName": "",
            "smtCsName": "",
            "statusList": [],
            "time": [],
            "startTime": "",
            "endTime": "",
            "pageNum": 1,
            "pageSize": 500
        }
        withdraw_order_search_res = self.rss.post(url=withdraw_order_search_url, json=withdraw_order_search_body, headers=self.headers_json).json()
        print(withdraw_order_search_res)
        withdraw_order_id = jsonpath.jsonpath(withdraw_order_search_res, "$..id")[0]
        withdraw_order_submit_url = "{}/financialservice/withdrawal/pushApproval".format(self.SCM_URL)
        withdraw_order_submit_body = {"withdrawalNo": self.withdraw_order}
        withdraw_order_submit_res = self.rss.post(url=withdraw_order_submit_url, json=withdraw_order_submit_body, headers=self.headers_json).json()
        msg = withdraw_order_submit_res["retMsg"]
        print(msg)
        if msg != "" and msg == "当前用户为管理员或者id不存在，不可提交！":
            # 切换普通账号 提交
            print(0)
            user_pwd_params = {"admin_name": "xujiangquan", "admin_pwd": "Xjq123456.","pro_pwd": "auth221313", "pro_user": "zhangbajun",
                                "pwd": 'Xjq123456.', "user": "xujiangquan"}
            HQCHIP_SOO_params = {"HQCHIP_SOO": user_pwd_params}
            write_yaml(account_yaml, HQCHIP_SOO_params)
            self.rss = SOOLogin("uat-scm.huaqiu.com", "hqScm").target_login()
            withdraw_order_submit_res = self.rss.post(url=withdraw_order_submit_url, json=withdraw_order_submit_body, headers=self.headers_json).json()
        print(withdraw_order_submit_res)
        withdraw_order_search_res = self.rss.post(url=withdraw_order_search_url, json=withdraw_order_search_body, headers=self.headers_json).json()
        audit_user_name = jsonpath.jsonpath(withdraw_order_search_res, "$..operaUserName")[0]
        return audit_user_name


if __name__ == '__main__':
    target_rss = SOOLogin("uat-scm.huaqiu.com", "hqScm").target_login()
    ScmWithdrawManage(target_rss).withdraw_order_submit()

