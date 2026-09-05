import json

import execjs
import jsonpath
import requests
import yaml


from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_data import Data
from huaqiu_order_api.common.my_path import yaml_file, account_yaml, encryption_auth_dir
class PayManagementAccessLog:
    # 访问日志
    def __init__(self, rss, order_sn):
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.PAY_URL = data['PAY_URL']
        self.order_sn = getattr(Data, 'order_sn', order_sn)
        self.rss = rss
        self.headers = {"Content-Type": "application/x-www-form-urlencoded",
                        "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://www.huaqiu.com)"
                        }
        self.headers_json = {"Content-Type": "application/json",
                             "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://www.huaqiu.com)"
                             }
    def access_log_search(self):
        search_url = "{}/management/log/query/payApiCallLog".format(self.PAY_URL)
        search_body = {
                "requestJson": self.order_sn,
                "responseJson": "",
                "ipAddress": "",
                "uri": "/payCenter/payV3/center/acquire",
                "startTime": "",
                "endTime": "",
                "pageSize": 20,
                "pageNum": 1,
                "total": 1
        }
        search_res = self.rss.post(url=search_url, json=search_body, headers=self.headers_json).json()
        requestJson = jsonpath.jsonpath(search_res, '$..requestJson')[0]
        return json.loads(requestJson)
if __name__ == '__main__':
    order_sn = None
    from huaqiu_order_api.HQCHIP_SOO.login import SOOLogin
    target_rss = SOOLogin(system_name="pay").target_login()
    PayManagementAccessLog(target_rss, order_sn).access_log_search()
