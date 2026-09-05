import hashlib
import json
import time

import jsonpath
import requests
import yaml


from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_path import yaml_file


class AddSignAtureInterface:
    # 签名生成公共方法

    def __init__(self, app_sec=None, data=None):
        self.rss = requests.session()
        self.app_sec = app_sec
        self.appid_json = {
            "IC": "9bf4d3ed292345958a5ba88a7192829b"
        }
        self.data_str = data
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.PAY_URL = data['PAY_URL']
        self.headers = {"Content-Type": "application/x-www-form-urlencoded",
                        "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://www.huaqiu.com)"
                        }
        self.headers_json = {"Content-Type": "application/json",
                             "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://www.huaqiu.com)"
                             }

    def assets_sginature(self, app_type=None):
        if self.app_sec == None:
            if app_type != None:
                for k,v in self.appid_json.items():
                    if k == app_type:
                        self.app_sec = v
        assets_sginature_url = "{}/payCenter/test/getSignature?appId={}".format(self.PAY_URL, self.app_sec)
        # print(assets_sginature_url)
        assets_sginature_body = self.data_str
        assets_sginature_res = self.rss.post(url=assets_sginature_url, json=assets_sginature_body, headers=self.headers_json).json()
        # print(assets_sginature_res)
        signature = jsonpath.jsonpath(assets_sginature_res, '$..result')[0]
        return signature
if __name__ == '__main__':
    order_sn = "S2026030278572"
    from huaqiu_order_api.HQCHIP_SOO.login import SOOLogin
    from huaqiu_order_api.HQCHIP_PAY.log_center.access_log import PayManagementAccessLog
    target_rss = SOOLogin(system_name="pay").target_login()
    requestJson = PayManagementAccessLog(target_rss, order_sn).access_log_search()
    AddSignAtureInterface(data=requestJson).assets_sginature("IC")
