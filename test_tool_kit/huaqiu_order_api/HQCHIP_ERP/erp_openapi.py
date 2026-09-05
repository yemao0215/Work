import json
import time
from datetime import datetime, timedelta

import requests
import yaml
from huaqiu_order_api.common.my_path import yaml_file

class ErpOpenAPI:
    def __init__(self):
        self.rss = requests.Session()
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.ERP_URL = data['ERP_URL']
        self.headers = {'Content-Type': 'application/x-www-form-urlencoded',
                        "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://www.huaqiu.com)"
                        }
    def scm_purchase_gather_status(self):
        scm_purchase_gather_status_url = "{}/erpapi/ApiScmPurchase/getPurchaseList".format(self.ERP_URL)
        print(scm_purchase_gather_status_url)
        scm_purchase_gather_status_body = {
            "params": json.dumps(["2061647218551549953"])
        }
        print(scm_purchase_gather_status_body)
        scm_purchase_gather_status_res = self.rss.post(url=scm_purchase_gather_status_url, data=scm_purchase_gather_status_body, headers=self.headers).json()
        print(scm_purchase_gather_status_res)
        return self
    def scm_purchase_create(self):
        """SCM补货创建推送备货计划"""
        scm_purchase_create_url = "{}/erpapi/ApiScmPurchase/createPurchase".format(self.ERP_URL)
        scm_purchase_create_body_items = {
            "items":
                [
                    {
                        "batchNumber": "",
                        "bomSupplierName": "digikey",
                        "customerId": "1808699918544068610",
                        "customerName": "深圳市怡亚通供应链股份有限公司",
                        "dt": "2",
                        "errorTip": "",
                        "goodsNo": "G50154156",
                        "goodsNumber": "20",
                        "lableType": "2",
                        "lockPurchaseItemId": "2062374199098310657",
                        "minPackage": "0",
                        "newOrderGrade": "4",
                        "orderGrade": "0",
                        "packageType": "0",
                        "pickingPrice": "2.58000",
                        "projectName": "",
                        "projectSn": "",
                        "purchaseRemark": "采购说明test",
                        "quotationUserName": "贺鹏",
                        "quoteRemark": "报价备注test",
                        "salePrice": "6.98000",
                        "scmOfferItemId": "2062373754598502401",
                        "scmOrderItemId": "2062373985625014274",
                        "stockType": "3",
                        "supplierName": "DIGIKEY",
                        "supplierUuid": "1003001017949681",
                        "warehouseCode": "2",
                        "outsourceOrderSn": "WW00126625225626", #委外单号,
                    }
                ],
                "scmOrderId": "2062373967300100097",
                "scmOrderSn": "DA212606040507",
                "uniqueIndex": "2062374199098310658",
                "createUid": "4578876"

        }
        scm_purchase_create_body = {"params": json.dumps(scm_purchase_create_body_items)}
        scm_purchase_create__res = self.rss.post(url=scm_purchase_create_url, data=scm_purchase_create_body, headers=self.headers).json()
        print(scm_purchase_create__res)
        return self
    def  set_bom_engineer_review(self):
        set_bom_engineer_review_url = "{}/erpapi/ApiBomOrder/setBomEngineerReview".format(self.ERP_URL)
        set_bom_engineer_review_body = {
            "platform": "bom",
            "timestamp": int(time.time()),
            "signature": ""


        }
        params = {
                    "bomId": 1159,  # erp_bom主键id
                    "remark": "asd",
                    "items": [
                                {
                                    "confirmId": 11192,  # erp_bom_confirm主键confirm_id
                                    "customerConfirmRemark": "客户调整说明55226333",
                                    "customerConfirm": 1
                                },
                                {
                                    "confirmId": 11193,  # erp_bom_confirm主键confirm_id
                                    "customerConfirmRemark": "客户调整说明233325666",
                                    "customerConfirm": 2
                                },
                                {
                                    "confirmId": 11194,  # erp_bom_confirm主键confirm_id
                                    "customerConfirmRemark": "客户调整说明23332566645435434",
                                    "customerConfirm": 3
                                },
                                {
                                    "confirmId": 11195,  # erp_bom_confirm主键confirm_id
                                    "customerConfirmRemark": "客户调整说明23332566645435434rtirgbrr",
                                    "customerConfirm": 4
                                }
                        ],
                    "distributionTime": str((datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"))
            }
        set_bom_engineer_review_body["params"] = json.dumps(params)
        set_bom_engineer_review_res = self.rss.post(url=set_bom_engineer_review_url, data=set_bom_engineer_review_body, headers=self.headers).json()

        print(set_bom_engineer_review_res)
        return self

if __name__ == '__main__':
    ErpOpenAPI().set_bom_engineer_review()
