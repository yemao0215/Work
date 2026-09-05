import time

import jsonpath
import requests
import yaml

from huaqiu_order_api.HC2018_admin.stock_up.import_stock_up import StockUp
from huaqiu_order_api.HQCHIP_ERP.erp_stock_purchase import ErpStockPurchase
from huaqiu_order_api.HQCHIP_SOO.login import SOOLogin
from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_path import settle_goods_dir, yaml_file


# from ic_order_delivery.erp_order_cancellation import ErpOrderCancellation
# from ic_order_delivery.ic_order import IcOrder
# from coupon.loguru_logger import logger
class PassPartner:
    # 合格合作商操作

    def __init__(self, target_rss, supplier_name=None, cooperationType=None, approveStatusList=None, supplierBackName=None):
        """
        :param supplier_name 供应商名称
        :param  cooperationType 合作类型
        :param  approveStatusList 审批类型列表
        :param supplierBackName 后台供应商名称

        """
        self.srm_rss = target_rss
        self.json_head = {"Content-Type": "application/json"}
        self.file_head = {"Content-Type": "multipart/form-source_data"}
        self.supplier_name = supplier_name
        self.cooperationType = cooperationType
        self.approveStatusList = approveStatusList
        self.supplierBackName = supplierBackName
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.SRM_URL = data['SRM_URL']

    def pass_partner_list(self):
        """合格合作商"""
        if isinstance(self.approveStatusList, list) == False and self.approveStatusList != None:
            self.approveStatusList = [self.approveStatusList]
        if self.approveStatusList == None:
            self.approveStatusList = []
        search_url = "{}/partnermanage/okSupplier/okSupplierPage?_query=1".format(self.SRM_URL)
        search_body = {
            "supplierName": self.supplier_name,
            "current": 1,
            "size": 100,
            "inLibStatus": "2",
            "cooperationType": self.cooperationType,
            "approveStatusList": self.approveStatusList,
            "supplierBackName": self.supplierBackName
        }
        if self.supplierBackName != None:
            search_body["inLibStatus"] = ""
        search_res = self.srm_rss.post(url=search_url, json=search_body, headers=self.json_head).json()
        logger.info(search_res)
        if "token无效" in search_res["msg"]:
            self.srm_rss = SOOLogin("uat-srm.huaqiu.com", "partnermanage").target_login()
            search_res = self.srm_rss.post(url=search_url, json=search_body, headers=self.json_head).json()
        # recordsInfo = search_res["body"]["records"]
        self.supplierId = jsonpath.jsonpath(search_res, "$..id")
        self.supplierCode = jsonpath.jsonpath(search_res, "$..supplierCode")
        supplier_name = jsonpath.jsonpath(search_res, "$..supplierName")
        approveStatus = jsonpath.jsonpath(search_res, "$..approveStatus")

        # for i in range(len(recordsInfo)):
        #     self.supplierCode.append(recordsInfo[i]["supplierCode"])
        #     supplier_name.append(recordsInfo[i]["supplierName"])
        # for q in range(len(recordsInfo)):
        #     if self.supplier_name == supplier_name[q]:
        #         self.supplierCode = self.supplierCode[q]
        logger.info(f"获取到合作商名称列表：{supplier_name}，供应商编号列表：{self.supplierCode}")
        return self.supplierId, supplier_name, self.supplierCode, approveStatus



    def pass_partner_judge(self):
        """合格合作商列表"""
        search_url = "https://uat-srm.huaqiu.com/partnermanage/okSupplier/okSupplierPage"
        search_body = {"supplierName": self.supplier_name, "current": 1, "size": 100}
        search_res = self.srm_rss.post(url=search_url, json=search_body, headers=self.json_head).json()
        # logger.info(search_res)
        recordsInfo = search_res["body"]["records"]
        # 判断关键词是否为合格合作商 list是否为空判断,不为空 返回True，反之返回False
        if recordsInfo:
            return_value = True
        else:
            return_value = False
        return return_value
    def pass_partner_business(self):
        """业务类型判断"""
        search_url = "https://uat-srm.huaqiu.com/partnermanage/partnerSettleBusinessSet/selectPartnerSettleBusinessSet"
        search_body = {"supplierCode": self.supplierCode}
        search_res = self.srm_rss.post(url=search_url, json=search_body, headers=self.json_head).json()
        cooperationType = search_res["body"]["cooperationType"]
        return_value = ''
        if cooperationType != None:
            cooperationTypeInfo = cooperationType[1:-1].split(",")
            cooperationTypelist = list(cooperationTypeInfo)
            for i in range(len(cooperationTypelist)):
                if cooperationTypelist[i] == "5":
                    logger.info("业务设置存在代售")
                    return_value = True
                    break

        else:
            return_value = False
        return return_value
if __name__ == '__main__':
    target_rss = SOOLogin("uat-srm.huaqiu.com", "partnermanage").target_login()
    supplierBackName = "HQCHIP-JBTY"
    PassPartner(target_rss, supplierBackName=supplierBackName).pass_partner_list()