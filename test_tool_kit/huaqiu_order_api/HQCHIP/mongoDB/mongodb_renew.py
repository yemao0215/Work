import hashlib
import json
import math
import re
import time
import datetime
import urllib.parse

import pandas
import requests
import yaml

from huaqiu_order_api.HQCHIP.Es.es_renew import EsRenew
from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_path import yaml_file, goodsid_dir, supplier_dir


class MongodbRenew:
    def __init__(self, goods_id=None, supplier_uuid=None, other_model_name=None):
        self.goods_id = goods_id
        self.supplier_uuid = supplier_uuid
        self.other_model_name = other_model_name
        self.supplierNames ="supplier,digikey,mouser,future,element14,verical.chip1shop,arrow,master,tme.peigenesis,heillind,alliedelec,rocelec,americal" \
                            "rs,psg,icbase, "
        self.rss = requests.Session()
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.HQCHIP_URL = data['HQCHIP_URL']
        self.HQCHIP_ADMIN_URL = data['HQCHIP_ADMIN_URL']
        with open(supplier_dir, 'r', encoding='utf-8') as yamlfile:
            self.supplier_data = yaml.load(yamlfile, Loader=yaml.FullLoader)
            self.supplierNames = ','.join(self.supplier_data.keys())
        self.headers_urlencoded = {"Content-Type": "application/x-www-form-urlencoded;charset=UTF-8"}
        self.headers_json = {"Content-Type": "application/json;charset=UTF-8",
                             "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://www.huaqiu.com)"}
    def mongodb_stock_supplier_uuid_update(self):
        """更新库存的供应商编码"""
        if self.supplier_uuid != None:
            encoded_supplier_uuid = urllib.parse.quote(self.supplier_uuid)
            # print(encoded_supplier_uuid)
            mongodb_stock_supplier_uuid_update_url = "{}/testtool/updateStock.html?stockId={}&supplierUuid={}".format(self.HQCHIP_URL, self.goods_id, encoded_supplier_uuid)
            print(mongodb_stock_supplier_uuid_update_url)
            mongodb_stock_supplier_uuid_update_res = self.rss.get(url=mongodb_stock_supplier_uuid_update_url, headers=self.headers_json).json()
            print(mongodb_stock_supplier_uuid_update_res)
            return self
    def mongodb_stock_other_model_name_update(self):
        """更新库存的供应商型号"""
        if self.other_model_name != None:
            encoded_other_model_name = urllib.parse.quote(self.other_model_name)
            # print(encoded_other_model_name)
            mongodb_stock_other_model_name_update_url = "{}/testtool/updateStock.html?stockId={}&otherModelName={}".format(self.HQCHIP_URL, self.goods_id, encoded_other_model_name)
            print(mongodb_stock_other_model_name_update_url)
            mongodb_stock_other_model_name_res = self.rss.get(url=mongodb_stock_other_model_name_update_url, headers=self.headers_json).json()
            print(mongodb_stock_other_model_name_res)
        return self
    def mian_mongodb_stock_update(self):
        self.mongodb_stock_supplier_uuid_update()
        self.mongodb_stock_other_model_name_update()
        if self.goods_id != None:
            EsRenew(self.goods_id).es_goods_all().es_brand_update().es_dg_relevance_goods().es_participle_update().es_update_goods().substitute_es_all_update().es_mongodb_overseas_goods_update()

if __name__ == '__main__':
    goods_id = 1102277539
    supplier_uuid = "叶茂测试"
    other_model_name = "46015-0603"
    MongodbRenew(goods_id, supplier_uuid, other_model_name).mian_mongodb_stock_update()