import math
import re

import jsonpath
import requests
import yaml


from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_data import Data
from huaqiu_order_api.common.my_path import yaml_file, account_yaml, supplier_dir


class SupplierGoods:
    # 合作库存
    def __init__(self, rss, goods_id=None, goods_name=None, supplier_name=None):
        self.rss = rss
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.HQCHIP_ADMIN_URL = data['HQCHIP_ADMIN_URL']
        self.headers = {"Content-Type": "application/x-www-form-urlencoded",
                        "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://www.huaqiu.com)"
                        }
        self.headers_json = {"Content-Type": "application/json; charset=UTF-8",
                             "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://www.huaqiu.com)"
                             }
        # with open(supplier_dir, 'r', encoding='utf-8') as yamlfile:
        #     self.supplier_data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        #     self.overseas_supplier_data = {key: value for key, value in self.supplier_data.items() if key != 'supplier'}
        self.goods_id = goods_id
        self.goods_name = goods_name
        self.supplier_name = supplier_name
    def supplier_sn_search(self):
        """供应商的展示供应商名称查询"""
    def supplier_sn_goods_search(self):
        """合作库存查询"""
