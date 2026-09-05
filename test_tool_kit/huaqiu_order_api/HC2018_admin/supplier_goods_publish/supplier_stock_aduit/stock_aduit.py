import datetime
import json
import math
import re
import time

import jsonpath
import openpyxl
import pandas as pd
import yaml
from openpyxl.cell import cell
from xpinyin import Pinyin

from huaqiu_order_api.HC2018_admin.dgk_goods_means.dgk_goods_means import GoodsMeans
from huaqiu_order_api.HC2018_admin.dgk_goods_means.stay_perfect_means import StayPerfectMeans
from huaqiu_order_api.HC2018_admin.login.login import Login
from huaqiu_order_api.HC2018_admin.work_sheet.work_sheet import WorkSheet
from huaqiu_order_api.HQCHIP_ERP.erp_order_putaway import ErpOrderPutaway
from huaqiu_order_api.HQCHIP_ERP.login import ErpLogin
from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_data import Data
from huaqiu_order_api.common.my_path import stockup_dir, yaml_file, account_yaml
from huaqiu_order_api.common.yaml_handler import write_yaml



class StockAudit:
    # 合作商库存审核
    def __init__(self, rss, goods_name=None, consign_sn=None, supplier_sn_name=None, order_id=None):
        """
        :param goods_name:  型号
        :param consign_sn:  寄售发布单号
        """
        self.rss = rss
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.HC2018_ADMIN_URL = data['HC2018_ADMIN_URL']
        self.auth_token = getattr(Data, 'dos_auth_token')
        self.goods_name = goods_name
        self.consign_sn = consign_sn
        self.supplier_sn_name = supplier_sn_name
        self.order_id = order_id
        self.headers = {"Content-Type": "application/x-www-form-urlencoded",
                        "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://www.huaqiu.com)"
                        }
        self.headers_json = {"Content-Type": "application/json; charset=UTF-8",
                             "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://www.huaqiu.com)"
                             }
        self.supplier_name_json = {"hqchip-llsjl": "测试专用账号1"}
        self.headers_json["Authorization"] = self.auth_token
    def supplier_id_search(self):
        """合作商查询"""
        supplier_id = []
        if self.supplier_sn_name != None:
            for key, v in self.supplier_name_json.items():
                if key == self.supplier_sn_name:
                    # 若存在于字典self.supplier_name_json的key
                    supplier_name = v
                    supplier_id_search_url = "{}/v1/common/BasicService/supList".format(self.HC2018_ADMIN_URL)
                    supplier_id_search_body = {"supplier_name": supplier_name, "type": 3}
                    supplier_id_search_res = self.rss.post(url=supplier_id_search_url, json=supplier_id_search_body, headers=self.headers_json).json()
                    supplier_id = jsonpath.jsonpath(supplier_id_search_res, "$..supplier_id")
                    if len(supplier_id) > 0:
                        break
            if supplier_id == []:
                supplier_id_search_url = "{}/v1/common/BasicService/supList".format(self.HC2018_ADMIN_URL)
                supplier_id_search_body = {"supplier_name": self.supplier_sn_name, "type": 3}
                supplier_id_search_res = self.rss.post(url=supplier_id_search_url, json=supplier_id_search_body,
                                                       headers=self.headers_json).json()
                supplier_id = jsonpath.jsonpath(supplier_id_search_res, "$..supplier_id")
        return supplier_id
    def stock_aduit_list(self, supplier_id=None, stock_type=None):
        """寄售审核查询
        stock_type 0全部  1寄售 2呆料(寄售) 3代售 4呆料(代售)  5期货
        """
        if not isinstance(supplier_id, list):
            supplier_id = list(supplier_id)
        order_id_count = []
        for i in range(len(supplier_id)):
            stock_aduit_list_url = "{}/v1/supplier/SupplierOrder/getUploadStock".format(self.HC2018_ADMIN_URL)
            stock_aduit_list_body = {"page": 1, "per_page": 100, "supplier_id": supplier_id[i],
                                     "stock_type": stock_type, "status": 1, "type": "0"}
            search_res = self.rss.post(url=stock_aduit_list_url, json=stock_aduit_list_body, headers=self.headers_json).json()
            total = jsonpath.jsonpath(search_res, "$..total")
            if int(total) > 100:
                total_num = math.ceil(int(total) / 100)
                for m in range(total_num):
                    i = i + 1
                    stock_aduit_list_url = "{}/v1/supplier/SupplierOrder/getUploadStock".format(self.HC2018_ADMIN_URL)
                    stock_aduit_list_body['page'] = i
                    search_res = self.rss.post(url=stock_aduit_list_url, json=stock_aduit_list_body, headers=self.headers_json).json()
                    order_id = jsonpath.jsonpath(search_res, "$..order_id")
                    order_sn = jsonpath.jsonpath(search_res, "$..order_sn")

                    if self.consign_sn != None:
                        for n in range(len(order_id)):
                            if order_sn[n] == self.consign_sn:
                                order_id_count.append(order_id[n])
                    else:
                        order_id_count = order_id + order_id_count
            else:
                order_id = jsonpath.jsonpath(search_res, "$..order_id")
                order_sn = jsonpath.jsonpath(search_res, "$..order_sn")
                stock_type = jsonpath.jsonpath(search_res, "$..stock_type")
                if self.consign_sn != None:
                    for a in range(len(order_id)):
                        if order_sn[a] == self.consign_sn:
                            order_id_count.append(order_id[a])
                else:
                    order_id_count = order_id + order_id_count
        return order_id_count
    def stock_aduit(self, order_id=None):
        """库存审核"""
        stock_aduit_url = "{}/v1/supplier/SupplierOrder/auditOrder".format(self.HC2018_ADMIN_URL)
        stock_aduit_body = {"id": order_id, "audit_status": 1, "is_lower_shelf": 0, "cdt_str": "", "cdt_end": "", "hdt_str":"", "hdt_end": ""}
        for i in range(3):
            print(f"第{i+1}次审核")
            stock_aduit_res = self.rss.post(url=stock_aduit_url, json=stock_aduit_body, headers=self.headers_json).json()
            print("审核结果：{0}".format(stock_aduit_res))
            if i == 3:
                break
        return self
    def mian_stock_aduit_consign(self):
        """寄售审核"""
        if self.order_id == None:
            supplier_id = self.supplier_id_search()
            order_id_count = self.stock_aduit_list(supplier_id, 1)
            for i in range(len(order_id_count)):
                self.stock_aduit(order_id_count[i])
        else:
            self.stock_aduit(self.order_id)
        return self


if __name__ == '__main__':
    target_rss = Login().login()
    StockAudit(target_rss).stock_aduit(4826)