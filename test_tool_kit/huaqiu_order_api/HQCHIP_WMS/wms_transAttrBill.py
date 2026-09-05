import json
import math
import time
import jsonpath
import requests
import yaml

from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_data import Data
from huaqiu_order_api.common.my_path import yaml_file, account_yaml


class WmsTransAttrBill:

    def __init__(self, target_rss):
        self.wms_rss = target_rss
        self.pda_rss = requests.Session()
        self.json_head = {"Content-Type": "application/json"}
        self.pda_json_head = {"Content-Type": "application/json", "User-Agent":"okhttp/3.14.9", "Connection":"keep-alive"}
        self.json_head = {"Content-Type": "application/json"}
        self.source_order_no = getattr(Data, 'source_order_no', '') # 来源订单号
        self.transform_no = getattr(Data, 'transform_no', '')
        self.labelNumber_sn = getattr(Data, 'labelNumber_sn', '')
        # self.inventory_no = "IN00154535"
        # self.in_order = ""
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.WMS_URL = data["WMS_URL"]
        with open(account_yaml, 'r', encoding='utf-8') as yamlfile:
            account = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.warehouse_type = account["HQCHIP_GOODS"]["warehouse_id"]

    def wms_transAttrBill(self):
        """移位单查询"""
        # 查询移位单
        transform_no_count = []
        inventory_no_count_new = []
        labelNumber_sn_count = []
        checkFlag_count = []
        search_url = "{}/wms/warehouse/transAttrBill/page".format(self.WMS_URL)
        for i in range(3):

            try:
                search_body = {"code": self.transform_no, "counted": True, "page": 1, "size": 100}
                search_res = self.wms_rss.post(url=search_url, data=json.dumps(search_body), headers=self.json_head).json()
                total = jsonpath.jsonpath(search_res, "$..total")[0]
                if math.ceil(int(total) / 100) > 1:
                    num = math.ceil(int(total) / 100)

                    for j in range(num):
                        search_body["pageNum"] = j + 1
                        search_res = self.wms_rss.post(url=search_url, data=json.dumps(search_body), headers=self.json_head).json()
                        transform_no = jsonpath.jsonpath(search_res, "$..code")
                        if isinstance(transform_no_count, list) and isinstance(transform_no, list):
                            transform_no_count = transform_no_count + transform_no
                else:
                    transform_no = jsonpath.jsonpath(search_res, "$..code")
                    if isinstance(transform_no_count, list) and isinstance(transform_no, list):
                        inventory_no_count = transform_no_count + transform_no
            except:
                search_body = {"code": self.transform_no, "counted": True, "page": 1, "size": 100}
                search_res = self.wms_rss.post(url=search_url, data=json.dumps(search_body), headers=self.json_head).json()
                total = jsonpath.jsonpath(search_res, "$..total")[0]
                if math.ceil(int(total) / 100) > 1:
                    num = math.ceil(int(total) / 100)
                    for j in range(num):
                        search_body["pageNum"] = j + 1
                        search_res = self.wms_rss.post(url=search_url, data=json.dumps(search_body), headers=self.json_head).json()
                        transform_no = jsonpath.jsonpath(search_res, "$..code")
                        if isinstance(transform_no_count, list) and isinstance(transform_no, list):
                            transform_no_count = transform_no_count + transform_no
                else:
                    transform_no = jsonpath.jsonpath(search_res, "$..code")
                    if isinstance(transform_no_count, list) and isinstance(transform_no, list):
                        transform_no_count = transform_no_count + transform_no
        transform_no_count = list(set(transform_no_count))
        return transform_no_count
    def wms_transAttrBill_operate(self, transform_no_count=None):
        """移位单操作"""
        if transform_no_count != None and isinstance(transform_no_count, list):
            for i in transform_no_count:
                search_url = "{}/wms/warehouse/transAttrBill/page".format(self.WMS_URL)
                search_body = {"code": i, "counted": True, "page": 1, "size": 100}
                search_res = self.wms_rss.post(url=search_url, json=search_body, headers=self.json_head).json()
                transCoede_id = jsonpath.jsonpath(search_res, "$..id")[0]

                # 提交
                wms_transAttr_submit_url = "{}/wms/warehouse/transAttrBill/autoDistribution".format(self.WMS_URL)
                wms_transAttr_submit_body = {"transAttrBillId": transCoede_id}
                wms_transAttr_submit_res = self.wms_rss.post(url=wms_transAttr_submit_url, json=wms_transAttr_submit_body, headers=self.json_head).json()
                logger.info("移位单提交结果：{}".format(wms_transAttr_submit_res))
        # if self.labelNumber_sn != "":
        #     for k in transform_no_count:
        #         search_body = {"code": self.transform_no, "counted": True, "page": 1, "size": 100}
        #         search_res = self.wms_rss.post(url=search_url, json=search_body, headers=self.json_head).json()
        #         inventoryCheckId = jsonpath.jsonpath(search_res, "$..id")[0]
        #         inventory_detail_url = "{}/wms/warehouse/inventoryCheck/getInventoryCheckRecordList".format(self.WMS_URL)
        #         inventory_detail_body = {
        #             "pageNum": 1,
        #             "pageSize": 100,
        #             "inventoryCheckId": inventoryCheckId,
        #             "counted": True
        #         }
        #         inventory_detail_res = self.wms_rss.post(url=inventory_detail_url, json=inventory_detail_body, headers=self.json_head).json()
        #         total = jsonpath.jsonpath(inventory_detail_res, "$..total")[0]
        #         if math.ceil(int(total) / 100) > 1:
        #             num = math.ceil(int(total) / 100)
        #             for j in range(num):
        #                 inventory_detail_body["pageNum"] = j + 1
        #                 inventory_detail_res = self.wms_rss.post(url=search_url, json=search_body, headers=self.json_head).json()
        #                 labelNumber_sn = jsonpath.jsonpath(inventory_detail_res, "$..labelNumber")
        #                 checkFlag = jsonpath.jsonpath(inventory_detail_res, "$..checkFlag")
        #                 if isinstance(labelNumber_sn_count, list) and isinstance(labelNumber_sn, list) and isinstance(checkFlag, list):
        #                     labelNumber_sn_count = labelNumber_sn_count + labelNumber_sn
        #                     checkFlag_count = checkFlag_count + checkFlag
        #         else:
        #             labelNumber_sn = jsonpath.jsonpath(inventory_detail_res, "$..labelNumber")
        #             checkFlag = jsonpath.jsonpath(inventory_detail_res, "$..checkFlag")
        #             if isinstance(labelNumber_sn_count, list) and isinstance(labelNumber_sn, list) and isinstance(checkFlag, list):
        #                 labelNumber_sn_count = labelNumber_sn_count + labelNumber_sn
        #                 checkFlag_count = checkFlag_count + checkFlag
        #         for m in range(len(labelNumber_sn_count)):
        #             if labelNumber_sn_count[m] == self.labelNumber_sn and checkFlag_count[m] == 0:
        #                 inventory_no_count_new.append(k)
        #         inventory_no_count = inventory_no_count_new
        # else:
        #     transform_no_count = transform_no_count
