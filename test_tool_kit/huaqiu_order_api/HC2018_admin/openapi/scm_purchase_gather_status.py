import hashlib
import json
import time
import requests
import yaml
from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_path import yaml_file


class ScmPurchaseGatherStatus:
    # 签名生成公共方法

    def __init__(self, sign=None,  timestamp=None, order_rec_id=None, project_type=None):
        self.rss = requests.Session()
        self.sign_encryption = sign
        self.timestamp = timestamp
        self.order_rec_id = order_rec_id
        self.project_type = project_type
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.HC2018_ADMIN_URL = data['HC2018_ADMIN_URL']
        self.headers = {'Content-Type': 'application/x-www-form-urlencoded',
                        "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://www.huaqiu.com)"
                        }
    def scm_purchase_gather_status(self):
        scm_purchase_gather_status_url = "{}/openapi/ScmStockup/findSelfStockInfo".format(self.HC2018_ADMIN_URL)
        scm_purchase_gather_status_body = {
            "sign": self.sign_encryption,
            "order_rec_id": self.order_rec_id,
            "project_type": self.project_type,
            "platform": "scm",
            "timestamp": self.timestamp
        }
        print(scm_purchase_gather_status_body)
        scm_purchase_gather_status_res = self.rss.post(url=scm_purchase_gather_status_url, data=scm_purchase_gather_status_body, headers=self.headers).json()
        print(scm_purchase_gather_status_res)
if __name__ == '__main__':
    from huaqiu_order_api.HC2018_admin.signature.signature_auto_stock import SignatureAutoStock
    timestamp, sign = SignatureAutoStock().signature_ceate()
    order_rec_id = "2061713027126734850"
    project_type = "0"
    ScmPurchaseGatherStatus(sign, timestamp, order_rec_id, project_type).scm_purchase_gather_status()
