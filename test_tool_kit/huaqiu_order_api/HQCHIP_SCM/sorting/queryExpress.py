import hashlib
import math
import time
from datetime import datetime, timedelta

import jsonpath
import requests
import yaml

from huaqiu_order_api.HC2018_admin.login.login import Login
from huaqiu_order_api.HQCHIP_SOO.login import SOOLogin

from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_data import Data
from huaqiu_order_api.common.my_path import yaml_file, account_yaml


class queryExpress:
    # 快递签收
    def __init__(self, rss=None):
        self.scm_rss = rss
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.SCM_URL = data['SCM_URL']
        with open(account_yaml, 'r', encoding='utf-8') as yamlfile:
            account = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.warehouse_type = int(account["HQCHIP_GOODS"]["warehouse_id"])
        self.number = account["HQCHIP_GOODS"]["number"]
        self.user_name = account["PassPort"]["name"]
        self.json_head = {"Content-Type": "application/json"}
        self.form_head = {"Content-Type": "multipart/form-data"}
        # 快递单号
        self.express_sn = getattr(Data, 'express_sn', '')

    def query_express(self):
        # 查看关联订单号
        search_relevance_order_url = "{}/scm/sorting/express/getShippingNoRelativeOrder".format(self.SCM_URL)
        search_relevance_order_body = {"body": {"expressBillNumber": self.express_sn, "relationBillNumber": ""}}
        print(f"查看关联订单号body为：{search_relevance_order_body}")
        search_relevance_order_res = self.scm_rss.post(url=search_relevance_order_url, json=search_relevance_order_body, headers=self.json_head).json()
        print(f"查看关联订单号执行结果为：{search_relevance_order_res}")
        relevance_order = jsonpath.jsonpath(search_relevance_order_res, '$..data')[0]
        print(f"关联订单号为：{relevance_order}")

        # 签收快递
        sign_express_url = "{}/scm/sorting/express/expressSign".format(self.SCM_URL)
        sign_express_body = {
            "expressCompany": 3,
            "expressBillNumber": self.express_sn,
            "parcelType": 1,
            "parcelNum": 1,
            "receiver": self.user_name,
            "relationBillNumber": relevance_order[0],
            "locationCode": "",
            "iqcRemark": "",
            "csRemark": "",
            "signMethod": 0,
            f"smtFileList[{relevance_order[0]}].file_name": "undefined",
            f"smtFileList[{relevance_order[0]}].url": "undefined"
        }
        print(f"签收快递body为：{sign_express_body}")
        sign_express_res = self.scm_rss.post(url=sign_express_url, data=sign_express_body).json()
        print(f"签收快递执行结果为：{sign_express_res}")
        if sign_express_res['suc'] ==  True:
            print("签收快递成功")

        else:
            print("签收快递失败")
        self.relevance_order = relevance_order[0]
        return self
    def express_sort_inn(self):
        """分拣入库"""
        search_url = "{}/scm/sorting/receiveDetail/page".format(self.SCM_URL)
        search_body = {
            "body": {
                "checkStatusList": [], "labelNo": "", "materialMode": "",
                "customerGoodsName": "", "orderBy": [], "shipStatusList": [],
                "deliveryNo": "", "statusList": [], "smtOrderSn": self.relevance_order},
            "header": {"pageNum": 1, "pageSize": 500}}
        search_res = self.scm_rss.post(url=search_url, json=search_body, headers=self.json_head).json()
        print(f"分拣入库第一步执行结果为：{search_res}")
        id = jsonpath.jsonpath(search_res, '$..id')
        bomId = jsonpath.jsonpath(search_res, '$..bomId')
        bomItemSourceId = jsonpath.jsonpath(search_res, '$..bomItemSourceId')
        labelNo = jsonpath.jsonpath(search_res, '$..labelNo')
        planReceiveQty = jsonpath.jsonpath(search_res, '$..planInboundQty')
        for i in range(len(id)):
            express_sort_inn_url = "{}/scm/sorting/receiveDetail/saveReceiveDetail".format(self.SCM_URL)
            express_sort_inn_body = {
                "body": {
                    "id": id[i], "bomId": bomId[i], "bomItemSourceId": bomItemSourceId[i],
                    "planReceiveQty": planReceiveQty[i], "actualQty": planReceiveQty[i],
                    "beEmptyComponent": 0, "labelNo": "", "beException": 1, "beOvershoot": 0, "bePlugin": 0,
                    "bePrint": False, "bomItemId": 0, "checkResultFlag": 0, "checkResultList": [],
                   "inWarehouse": 1, "locationCode": "","overshootQty": 0, "packagingAngle": "",
                   "receiveRemark": "", "silkScreen": "", "specialRemark": ""}}
            express_sort_inn_res = self.scm_rss.post(url=express_sort_inn_url, json=express_sort_inn_body, headers=self.json_head).json()
            print(f"分拣入库第一步执行结果为：{express_sort_inn_res}")
            if labelNo == False:
                print_label_url = "{}/scm/sorting/receiveDetail/batchPrintReceiveLabel".format(self.SCM_URL)
                print_label_body = {"body": {"ids": [id[i]], "batchNumber": "", "dateCode": "", "printerName": "123456"}}
                print_label_res = self.scm_rss.post(url=print_label_url, json=print_label_body, headers=self.json_head).json()
                print(f"分拣入库-打印标签第二步执行结果为：{print_label_res}")
                if "body" in print_label_res:  # 当print_label_res里面存在body，说明打印标签生成成功
                    sort_inn_collate_url = "{}/scm/sorting/receiveDetail/check".format(self.SCM_URL)
                    sort_inn_collate_body = {"body": [id[i]]}
                    sort_inn_collate_res = self.scm_rss.post(url=sort_inn_collate_url, json=sort_inn_collate_body, headers=self.json_head).json()
                    print(f"分拣入库-核对第三步执行结果为：{sort_inn_collate_res}")
                    # 确认发料
                    checkReceiveLabel_url = "{}/scm/sorting/receiveDetail/checkReceiveLabel".format(self.SCM_URL)
                    checkReceiveLabel_body = {"body": {"smtOrderSn": self.relevance_order, "receiveDetailIdList": id[i]}}
                    checkReceiveLabel_res = self.scm_rss.post(url=checkReceiveLabel_url, json=checkReceiveLabel_body, headers=self.json_head).json()
                    print(f"确认发料第一步执行结果为：{checkReceiveLabel_res}")
                    batchShip_url = "{}/scm/sorting/receiveDetail/batchShip".format(self.SCM_URL)
                    batchShip_body = {"body": [{"goodsNo": i+1, "id": id[i], "shipNum": planReceiveQty[i]}]}
                    batchShip_res = self.scm_rss.post(url=batchShip_url, json=batchShip_body, headers=self.json_head).json()
                    print(f"确认发料第二步执行结果为：{batchShip_res}")
        return self
    def express_sort_run(self, express_sn=None):
        """快递"""
        scm_target_rss = SOOLogin(system_name="scm").target_login()
        setattr(Data, 'express_sn', express_sn)
        queryExpress(scm_target_rss).query_express().express_sort_inn()
        return self
if __name__ == '__main__':
    # rss = SSO_Reception('15912757721', 'a123456', 'https://uat-smt.hqchip.com').login()
    # order_sn = SmtOrder(rss, 15912757721).smt_tmp_save().place_an_order()
    express_sn = "SF202408200001269"
    scm_target_rss = SOOLogin(system_name="scm").target_login()
    queryExpress(scm_target_rss).express_sort_inn()
