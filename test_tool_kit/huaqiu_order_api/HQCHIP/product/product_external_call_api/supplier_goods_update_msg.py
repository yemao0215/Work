import math
import multiprocessing
import re
import threading
import time

import jsonpath
import pandas
import requests
import yaml

from huaqiu_order_api.HC2018_admin.login.login import Login
from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_data import Data
from huaqiu_order_api.common.my_path import yaml_file, eccn_dir
class SupplierGoodsUpdateMsg:
    def __init__(self, pn2=None, goods_id=None):
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.PRODUCT_DETAIL_URL = data['PRODUCT_DETAIL_URL']
        self.headers = {"Content-Type": "application/x-www-form-urlencoded",
                        "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://www.huaqiu.com)"
                        }
        self.headers_json = {"Content-Type": "application/json; charset=UTF-8",
                             "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://www.huaqiu.com)"
                             }
        self.rss = requests.Session()
        self.pn2 = pn2
        self.goods_id = goods_id

    def count_no_update_goods_number(self):
        count_no_update_goods_number_url = "{}/spi/stock/countUnUpdateStock".format(self.PRODUCT_DETAIL_URL)
        count_no_update_goods_number_body = {"pn2List": [self.pn2], "isOffSale": False, "willOffTimes": []}
        count_no_update_goods_number_res = self.rss.post(url=count_no_update_goods_number_url, json=count_no_update_goods_number_body, headers=self.headers_json).json()
        print(count_no_update_goods_number_res)
        return self


    def api_export_supplier_stock(self):
        """导出合作库存"""
        api_export_supplier_stock_url = "{}/spi/stock/exportSupplierStocks".format(self.PRODUCT_DETAIL_URL)
        print(api_export_supplier_stock_url)
        api_export_supplier_stock_body = {"stockIdList": [self.goods_id], "notUpdated": False, "isFeature": False}
        print(api_export_supplier_stock_body)
        api_export_supplier_stock_res = self.rss.post(url=api_export_supplier_stock_url, json=api_export_supplier_stock_body, headers=self.headers_json).json()
        print(api_export_supplier_stock_res)

if __name__ == '__main__':
    pn2 = "HQCHIP-TTTEST"
    goods_id = "1012183941"
    SupplierGoodsUpdateMsg(pn2, goods_id).count_no_update_goods_number().api_export_supplier_stock()