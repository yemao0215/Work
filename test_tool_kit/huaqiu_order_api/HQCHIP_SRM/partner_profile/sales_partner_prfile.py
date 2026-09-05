import json
import time
from datetime import datetime

import jsonpath
import requests
import yaml


from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_data import Data
from huaqiu_order_api.common.my_path import yaml_file, account_yaml


class SalesPartherProfile:

    def __init__(self, target_rss):

        self.srm_rss = target_rss
        self.json_head = {"Content-Type": "application/json"}
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.SRM_URL = data["SRM_URL"]
    def sales_goods_profile(self):
        search_url = "{}/partnermanage/sellGoodsCooperate/pageList".format(self.SRM_URL)
        search_body = {
            "header": {"pageNum": 1, "pageSize": 50},
            "body": {
                "transactionTag": 1,  # 1代售现货  2代售期货
                "supplierName": "",  # 供应商名称
                "supplierHtName": "",  # 后台供应商名称
                "supplierSn": "",  # 供应商编号
                "industry": "",
                "qudaoFollower": "",
                "statisticsStime": "",
                "statisticsEtime": "",
                "orderColumn": "",
                "orderType": ""
            }}
        search_res = self.srm_rss.post(url=search_url, json=search_body, headers=self.json_head).json()
        pageCount = jsonpath.jsonpath(search_res, "$..pageCount")[0]
        self.supplierName_count = []
        self.supplierHtName_count = []
        self.supplierSn_count = []

        for i in range(int(pageCount)):
            i = i + 1
            search_body["header"]["pageNum"] = i
            search_res = self.srm_rss.post(url=search_url, json=search_body, headers=self.json_head).json()
            self.supplierName = jsonpath.jsonpath(search_res, "$..supplierName")
            self.supplierHtName = jsonpath.jsonpath(search_res, "$..supplierHtName")
            self.supplierSn = jsonpath.jsonpath(search_res, "$..supplierSn")
            self.supplierName_count = self.supplierName_count + self.supplierName
            self.supplierHtName_count = self.supplierHtName_count + self.supplierHtName
            self.supplierSn_count = self.supplierSn_count + self.supplierSn
        presence_data_supplier_num = 0
        presence_data_supplier_BackName= []
        for j in range(len(self.supplierName_count)):
            search_sales_goods_detail_url = "{}/partnermanage/overview/detail".format(self.SRM_URL)
            search_sales_goods_detail_body = {
                "header": {"pageNum": 1, "pageSize": 50},
                "body": {
                    "supplierBackName": self.supplierHtName_count[j],
                    "type": False,
                    "goodsName": "",
                    "brandName": "",
                    "isOffSale": "",
                    "startTime": "",
                    "endTime": ""
                }}
            search_sales_goods_detail_res = self.srm_rss.post(url=search_sales_goods_detail_url, json=search_sales_goods_detail_body, headers=self.json_head).json()
            if search_sales_goods_detail_res["suc"] == True:
                search_sales_goods_detail_totalSize = jsonpath.jsonpath(search_sales_goods_detail_res, "$..totalSize")[0]
                if int(search_sales_goods_detail_totalSize) > 0:
                    logger.info("{}供应商存在数据".format(self.supplierName_count[j]))
                    presence_data_supplier_num = presence_data_supplier_num + 1
                    presence_data_supplier_BackName.append(self.supplierHtName_count[j])
        logger.info("存在数据{}个供应商，存在数据后台供应商名称列表为：{}".format(presence_data_supplier_num, presence_data_supplier_BackName))
if __name__ == '__main__':
    from huaqiu_order_api.HQCHIP_SOO.login import SOOLogin
    target_rss = SOOLogin("uat-srm.huaqiu.com", "partnermanage").target_login()
    SalesPartherProfile(target_rss).sales_goods_profile()