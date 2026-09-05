
import json
import time
from datetime import datetime, timedelta

import jsonpath
import yaml
from huaqiu_order_api.HQCHIP_SOO.login import SOOLogin
from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_path import yaml_file


class VoucherCard:

    def __init__(self, target_rss, voucher_name=None, expiryMode=None):
        self.activity_rss = target_rss
        self.json_head = {"Content-Type": "application/json"}
        self.voucher_name = voucher_name
        self.expiryMode = expiryMode
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.Activity_Center_URL = data['Activity_Center_URL']

    def voucher_search(self, disableStatus=None):
        """
        ：param trandsactionTypeId 可用范围
        ：param voucherShowStatus 使用状态
        ：param disableStatus 禁用状态 0 未禁用 1 禁用
        """
        search_url = "{}/ecmc/voucher/list".format(self.Activity_Center_URL)
        search_body = {"trandsactionTypeId": "", "voucherShowStatus": "", "disableStatus": "", "pageNum": 1, "pageSize": 50}
        if disableStatus != None:
            search_body["disableStatus"] = disableStatus
        search_res = self.activity_rss.post(url=search_url, json=search_body, headers=self.json_head).json()
        pages = search_res["page"]["pages"]
        voucherId = []
        faceValueMode = []
        faceTypeValue = []
        rule_voucher = []
        if pages > 1:
            for i in range(int(pages)):
                search_body["pageNum"] = i+1
                search_res = self.activity_rss.post(url=search_url, json=search_body, headers=self.json_head).json()
                voucherId_list = jsonpath.jsonpath(search_res, "$..voucherId")
                faceValue_list = jsonpath.jsonpath(search_res, "$..faceValue")
                faceValueMode_list = jsonpath.jsonpath(search_res, "$..faceValueMode")
                faceValueRate_list = jsonpath.jsonpath(search_res, "$..faceValueRate")
                faceTypeValue_list = [faceValue_list[i] if faceValueMode_list[i] == 1 else (str(faceValueRate_list[i]) + "%" if faceValueMode_list[i] == 2 else '')
                                      for i in range(len(faceValueMode_list))]
                voucherId = voucherId + voucherId_list
                faceValueMode = faceValueMode + faceValueMode_list
                faceTypeValue = faceTypeValue + faceTypeValue_list
        else:
            voucherId_list = jsonpath.jsonpath(search_res, "$..voucherId")
            faceValue_list = jsonpath.jsonpath(search_res, "$..faceValue")
            faceValueMode_list = jsonpath.jsonpath(search_res, "$..faceValueMode")
            faceValueRate_list = jsonpath.jsonpath(search_res, "$..faceValueRate")
            faceTypeValue_list = [faceValue_list[i] if faceValueMode_list[i] == 1 else (
                str(faceValueRate_list[i]) + "%" if faceValueMode_list[i] == 2 else '')
                                  for i in range(len(faceValueMode_list))]
            voucherId = voucherId + voucherId_list
            faceValueMode = faceValueMode + faceValueMode_list
            faceTypeValue = faceTypeValue + faceTypeValue_list

        for m in range(len(voucherId)):
            voucher_rule_json = {
                voucherId[m]: {
                    "faceValueMode": faceValueMode[m],
                    "faceTypeValue": faceTypeValue[m]}
            }
            rule_voucher.append(voucher_rule_json)
        # print(rule_voucher)
        return rule_voucher

    def rule_voucherId_typeValue_positioning(self, disableStatus=None, voucher_id=None):
        """指定现金券id处于现金券规则里面的现金券转换值或转换比列字典定位"""
        rule_voucher = self.voucher_search(disableStatus=disableStatus)
        for item in rule_voucher:
            for key, value in item.items():
                if key == voucher_id:
                    return value





    def voucher_add(self, expiryTime=None, faceValueMode=None, faceValue=None, faceValueRate=None):
        voucher_add_url = "{}/ecmc/voucher/save".format(self.Activity_Center_URL)
        voucher_add_body = {"voucherName": self.voucher_name, "useTransactionTypeId": [2]}
        if self.expiryMode == "1":
            now_time = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            logger.info(f"获取当前时间：{now_time}")
            now_time_one_day = str((datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"))
            logger.info(f"获取当前时间一天后的时间：{now_time_one_day}")
            voucher_add_body["voucherStartTime"] = now_time
            voucher_add_body["voucherEndTime"] = now_time_one_day
            voucher_add_body["expiryTime"] = ""
        elif self.expiryMode == "2":
            if expiryTime == None:
                expiryTime = "7"
            voucher_add_body["voucherStartTime"] = ""
            voucher_add_body["voucherEndTime"] = ""
            voucher_add_body["expiryTime"] = expiryTime
        voucher_add_body["expiryMode"] = self.expiryMode
        print(voucher_add_body)
        if faceValueMode == None:
            faceValueMode = "1"
            if faceValue == None:
                faceValue = "100"
            voucher_add_body["faceValue"] = faceValue
        elif faceValueMode == "1":
            if faceValueRate == None:
                faceValue = "100"
            voucher_add_body["faceValue"] = faceValue
        elif faceValueMode == "2":
            if faceValueRate == None:
                faceValueRate = "5"
            voucher_add_body["faceValueRate"] = faceValueRate
        voucher_add_body["faceValueMode"] = faceValueMode
        voucher_add_res = self.activity_rss.post(url=voucher_add_url, json=voucher_add_body, headers=self.json_head).json()
        logger.info(f"执行结果：{voucher_add_res}")
        return self

    def voucher_disable(self, voucher_id=None):
        """现金券禁用"""
        voucher_disable_url = "{}/ecmc/voucher/disable".format(self.Activity_Center_URL)
        voucher_disable_body = {"voucherId": voucher_id, "remarks": "测试三期"}
        voucher_disable_res = self.activity_rss.post(url=voucher_disable_url, json=voucher_disable_body,
                                                 headers=self.json_head).json()
        logger.info(f"执行结果：{voucher_disable_res}")
        return self
if __name__ == '__main__':
    target_rss = SOOLogin("uat-activity.hqchip.com", "ecmc").target_login()
    VoucherCard(target_rss, "三期测试-10", "2").voucher_search(disableStatus=0)