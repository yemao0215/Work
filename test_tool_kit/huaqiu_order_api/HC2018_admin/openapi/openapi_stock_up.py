import hashlib
import json
import math
import time
from datetime import datetime

import requests
import yaml
from faker import Faker

from huaqiu_order_api.HC2018_admin.login.login import Login
from huaqiu_order_api.HC2018_admin.signature.openapi_signature import OpenapiSignature
from huaqiu_order_api.HC2018_admin.signature.signature_auto_stock import SignatureAutoStock
from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_path import yaml_file



class OpenAPIStockUp:
    def __init__(self, order_rec_id=None):
        self.rss = requests.Session()
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.HC2018_ADMIN_URL = data['HC2018_ADMIN_URL']
        self.headers = {"Content-Type": "application/x-www-form-urlencoded"}
        self.order_rec_id = order_rec_id if order_rec_id is not None else "2054480357750108161"
    def get_orderPrice_detail(self):
        pass
    def api_scm_stockup(self):
        uniqueIndex = "1853" + datetime.now().strftime("%Y%m%d") + "000" + str(Faker("zh_CN").random_int(1, 10000))
        logger.info("uniqueIndex：" + uniqueIndex)
        api_scm_stockup_url = "{}/openapi/ScmStockup/addSalesReq".format(self.HC2018_ADMIN_URL)
        timestamp, sign = SignatureAutoStock().signature_ceate()
        scm_stockup_body = [
            {
                "bomSupplierName": "hqchip_self",
                "bom_username": "贺鹏",
                "commitment_time": "1780566059",
                "demand_type": "2",
                "erp_goods_sn": "G5099604",
                "goods_name": "CC0402FRNPO9BN101",
                "goods_no": "CA0175105",
                "lable_type": "2",
                "minPackage": 1000,
                "order_rec_id": "2054480357750108161",
                "provider_name": "Yageo",
                "quotation_item_id": "2054470176768544769",
                "quoteRemark": "报价备注test",
                "require_number": "60",
                "sale_number": "60",
                "order_grade": 0,
                "new_order_grade": 0,
                "sale_price": "0.04350",
                "sales_username": "许江铨",
                "unionid": "26228257"
            }]

        api_scm_stockup_body = {
            "project_type": "0",
            "platform_source": "2",
            "unionid": "26228257",
            "data": json.dumps(scm_stockup_body, ensure_ascii=False),
            "signature": sign,
            "project_name": "",
            "platform": "scm",
            "uniqueIndex": int(uniqueIndex),
            "order_grade": "4",
            "project_sn": "",
            "is_project_stock": "0",
            "customer_name": "***6华秋外贸***",
            "customer_id": "10523694014193467392",
            "order_sn": "DA212605137807",
            "timestamp": timestamp,
            "controller": "ScmStockup",
            "action": "addSalesReq"
        }
        # ppp0000003
        api_scm_stockup_res = self.rss.post(url=api_scm_stockup_url, data=api_scm_stockup_body,
                                            headers=self.headers).json()
        print(api_scm_stockup_res)
    def aip_erp_stockup(self):
        """"""
        uniqueIndex = "1853" + datetime.now().strftime("%Y%m%d") + "000" + str(Faker("zh_CN").random_int(1, 10000))

if __name__ == '__main__':
    OpenAPIStockUp().api_scm_stockup()