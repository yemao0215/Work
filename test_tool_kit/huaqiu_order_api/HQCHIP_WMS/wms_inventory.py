import datetime
import json
import math
import time
import jsonpath
import requests
import yaml

from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_data import Data
from huaqiu_order_api.common.my_path import yaml_file, account_yaml


class WmsInventory:

    def __init__(self, target_rss, goodsCode=None, goodsName=None):
        self.wms_rss = target_rss
        self.pda_rss = requests.Session()
        self.json_head = {"Content-Type": "application/json"}
        self.pda_json_head = {"Content-Type": "application/json", "User-Agent":"okhttp/3.14.9", "Connection":"keep-alive"}
        self.json_head = {"Content-Type": "application/json"}
        self.inventory_no = getattr(Data, 'inventory_no', '')
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
        self.goods_name = goodsName
        self.goods_code = goodsCode


    def wms_inventory(self):
        """
        WMS盘点查询
        :return:
        """
        inventory_no_count = []
        inventory_no_count_new = []
        labelNumber_sn_count = []
        checkFlag_count = []
        inventory_no = []
        search_url = "{}/wms/warehouse/inventoryCheck/getInventoryCheckList".format(self.WMS_URL)
        for i in range(3):

            try:
                search_body = {
                    "pageNum": 1,
                    "pageSize": 100,
                    "counted": True,
                    "inventoryNo": self.inventory_no,
                    "transformNo": self.transform_no,
                    "checkStatus": 7
                }
                search_res = self.wms_rss.post(url=search_url, data=json.dumps(search_body), headers=self.json_head).json()
                total = jsonpath.jsonpath(search_res, "$..total")[0]
                if math.ceil(int(total) / 100) > 1:
                    num = math.ceil(int(total) / 100)

                    for j in range(num):
                        search_body["pageNum"] = j + 1
                        search_res = self.wms_rss.post(url=search_url, data=json.dumps(search_body), headers=self.json_head).json()
                        inventory_no = jsonpath.jsonpath(search_res, "$..inventoryNo")
                        if isinstance(inventory_no_count, list) and isinstance(inventory_no, list):
                            inventory_no_count = inventory_no_count + inventory_no
                else:
                    inventory_no = jsonpath.jsonpath(search_res, "$..inventoryNo")
                    if isinstance(inventory_no_count, list) and isinstance(inventory_no, list):
                        inventory_no_count = inventory_no_count + inventory_no
            except:
                search_body = {
                    "pageNum": 1,
                    "pageSize": 100,
                    "counted": True,
                    "inventoryNo": self.inventory_no,
                    "transformNo": self.transform_no,
                    "checkStatus": 1
                }
                search_res = self.wms_rss.post(url=search_url, data=json.dumps(search_body), headers=self.json_head).json()
                total = jsonpath.jsonpath(search_res, "$..total")[0]
                if math.ceil(int(total) / 100) > 1:
                    num = math.ceil(int(total) / 100)
                    for j in range(num):
                        search_body["pageNum"] = j + 1
                        search_res = self.wms_rss.post(url=search_url, data=json.dumps(search_body), headers=self.json_head).json()
                        inventory_no = jsonpath.jsonpath(search_res, "$..inventoryNo")
                        if isinstance(inventory_no_count, list) and isinstance(inventory_no, list):
                            inventory_no_count = inventory_no_count + inventory_no
                else:
                    inventory_no = jsonpath.jsonpath(search_res, "$..inventoryNo")
                    if isinstance(inventory_no_count, list) and isinstance(inventory_no, list):
                        inventory_no_count = inventory_no_count + inventory_no
        print(inventory_no_count)
        inventory_no_count = list(set(inventory_no_count))
        if self.labelNumber_sn != "":
            for k in inventory_no_count:
                search_body = {
                    "pageNum": 1,
                    "pageSize": 100,
                    "counted": True,
                    "inventoryNo": k,
                    "transformNo": "",
                    "checkStatus": ""
                }
                search_res = self.wms_rss.post(url=search_url, json=search_body, headers=self.json_head).json()
                inventoryCheckId = jsonpath.jsonpath(search_res, "$..id")[0]
                inventory_detail_url = "{}/wms/warehouse/inventoryCheck/getInventoryCheckRecordList".format(self.WMS_URL)
                inventory_detail_body = {
                    "pageNum": 1,
                    "pageSize": 100,
                    "inventoryCheckId": inventoryCheckId,
                    "counted": True
                }
                inventory_detail_res = self.wms_rss.post(url=inventory_detail_url, json=inventory_detail_body, headers=self.json_head).json()
                total = jsonpath.jsonpath(inventory_detail_res, "$..total")[0]
                if math.ceil(int(total) / 100) > 1:
                    num = math.ceil(int(total) / 100)
                    for j in range(num):
                        inventory_detail_body["pageNum"] = j + 1
                        inventory_detail_res = self.wms_rss.post(url=search_url, json=search_body, headers=self.json_head).json()
                        labelNumber_sn = jsonpath.jsonpath(inventory_detail_res, "$..labelNumber")
                        checkFlag = jsonpath.jsonpath(inventory_detail_res, "$..checkFlag")
                        if isinstance(labelNumber_sn_count, list) and isinstance(labelNumber_sn, list) and isinstance(checkFlag, list):
                            labelNumber_sn_count = labelNumber_sn_count + labelNumber_sn
                            checkFlag_count = checkFlag_count + checkFlag
                else:
                    labelNumber_sn = jsonpath.jsonpath(inventory_detail_res, "$..labelNumber")
                    checkFlag = jsonpath.jsonpath(inventory_detail_res, "$..checkFlag")
                    if isinstance(labelNumber_sn_count, list) and isinstance(labelNumber_sn, list) and isinstance(checkFlag, list):
                        labelNumber_sn_count = labelNumber_sn_count + labelNumber_sn
                        checkFlag_count = checkFlag_count + checkFlag
                for m in range(len(labelNumber_sn_count)):
                    if labelNumber_sn_count[m] == self.labelNumber_sn and checkFlag_count[m] == 0:
                        inventory_no_count_new.append(k)
                inventory_no_count = inventory_no_count_new
        else:
            inventory_no_count = inventory_no_count
        print(inventory_no_count)
        return inventory_no_count
    def wms_inventory_add(self):
        """新建盘点单"""
        search_url = "{}/wms/warehouse/inventory/queryInventoryPage".format(self.WMS_URL)
        search_body = {
                        "storeId": "9",
                        "pageNum": 1,
                        "pageSize": 20,
                        "orderBy": [

                        ],
                        "counted": True,
                        "goodsInfo": "",
                        "customerGoodsCode": "",
                        "goodsCode": self.goods_code,
                        "goodsName": self.goods_name,
                        "time": [

                        ],
                        "businessType": "",
                        "labelNumber": "",
                        "locationCode": "",
                        "shelfCode": "",
                        "inboundCode": "",
                        "receiveDocCode": "",
                        "erpInboundCode": "",
                        "soi": "",
                        "consignerCode": "",
                        "supplierCode": "",
                        "ownerCode": "",
                        "goodsBrand": "",
                        "alarmFlag": "",
                        "lockStatus": "",
                        "iqcCheckStatus": "",
                        "goodsCatName1": "",
                        "controlStatus": "",
                        "goodsStatus": "",
                        "goodsDesc": "",
                        "goodsEncapsulation": "",
                        "mslFlag": "",
                        "hasGoodsWeight": ""
                    }
        search_res = self.wms_rss.post(url=search_url, data=json.dumps(search_body), headers=self.json_head).json()
        result = jsonpath.jsonpath(search_res, "$..result")[0]
        # 获取当前时间
        currentDate = datetime.datetime.now()

        # 获取第二天的当前时间
        nextDayDate = currentDate + datetime.timedelta(days=1)

        # 格式化
        formattedCurrentDateTime = currentDate.strftime("%Y-%m-%d %H:%M:%S")
        formattedCurrentDateOnly = currentDate.strftime("%Y-%m-%d")
        formattedCurrentTimeOnly = currentDate.strftime("%H:%M:%S")
        formattedNextDayDateTime = nextDayDate.strftime("%Y-%m-%d %H:%M:%S")

        wms_inventory_add_url = "{}/wms/warehouse/inventory/saveAndSubmitInventoryCheck".format(self.WMS_URL)
        wms_inventory_add_body = {
            "inventoryCheckDto": {
                "checkType": 1,
                "ownerCode": 1,
                "inventoryDate": formattedCurrentDateOnly,
                "creater": "",
                "cTime": "",
                "inventoryTime": formattedCurrentTimeOnly,
                "inventoryStartTime": formattedCurrentDateTime,
                "inventoryClassify": 1
            },
            "inventoryPageDtoList": result
        }
        wms_inventory_add_res = self.wms_rss.post(url=wms_inventory_add_url, josn=wms_inventory_add_body, headers=self.json_head).json()
        print(f"新增成功，打印执行结果：{wms_inventory_add_res}")
        return self

    def wms_inventory_confirm_audit(self):
        """盘点确认审核"""
        search_url = "{}/wms/warehouse/inventoryCheck/getInventoryCheckList".format(self.WMS_URL)
        search_body = {
            "storeId": "1",
            "pageNum": 1,
            "pageSize": 100,
            "counted": True,
            "inventoryNo": self.inventory_no,
            "transformNo": "",
            "checkType": "",
            "checkStatus": 2,
            "createUser": "",
            "goodsCode": self.goods_code,
            "goodsName": self.goods_name,
            "inventoryClassify": ""
        }
        search_res = self.wms_rss.post(url=search_url, josn=search_body, headers=self.json_head).json()
        inventory_id = jsonpath.jsonpath(search_res, "$..id")
        if inventory_id != []:
            for i in inventory_id:
                wms_inventory_confirm_url = "{}/wms/warehouse/inventory/warehouseCheck".format(self.WMS_URL)
                wms_inventory_confirm_body = [
                    {
                        "id": i
                    }
                ]
                wms_inventory_confirm_res = self.wms_rss.post(url=wms_inventory_confirm_url, josn=wms_inventory_confirm_body, headers=self.json_head).json()
                print(f"确认成功，打印执行结果：{wms_inventory_confirm_res}")
                wms_inventory_upload_url = "{}/wms/warehouse/inventory/warehouseCheck".format(self.WMS_URL)
                wms_inventory_upload_body = {"id": i}
                wms_inventory_upload_res = self.wms_rss.post(url=wms_inventory_upload_url, josn=wms_inventory_upload_body, headers=self.json_head).json()
                print(f"上传成功，打印执行结果：{wms_inventory_upload_res}")
                wms_inventory_audit_url = "{}/wms/warehouse/inventoryCheck/auditInvCheckRecord".format(self.WMS_URL)
                wms_inventory_audit_body = [i]
                wms_inventory_audit_res = self.wms_rss.post(url=wms_inventory_audit_url, josn=wms_inventory_audit_body, headers=self.json_head).json()
                print(f"审核成功，打印执行结果：{wms_inventory_audit_res}")
        return self
if __name__ == '__main__':
    from huaqiu_order_api.HQCHIP_SOO.login import SOOLogin
    from huaqiu_order_api.HQCHIP_WMS.HQCHIP_PDA_UAT.pda_theupper import PdaTheupper
    from huaqiu_order_api.HQCHIP_WMS.HQCHIP_PDA_UAT.pda_login import PdaLogin
    target_rss = SOOLogin("uat-wms.huaqiu.com", "wms/base").target_login()
    WmsInventory(target_rss).wms_inventory()

