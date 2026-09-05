
import json
import math
import time
from datetime import datetime, timedelta

import jsonpath
import yaml

from huaqiu_order_api.HQCHIP_Activity.card_manage.voucher.voucher_card import VoucherCard
from huaqiu_order_api.HQCHIP_SOO.login import SOOLogin
from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_data import Data
from huaqiu_order_api.common.my_path import yaml_file


class VoucherActivity:

    def __init__(self, target_rss, activity_name=None, sendMetod=None):
        self.activity_rss = target_rss
        self.json_head = {"Content-Type": "application/json"}
        self.activity_name = activity_name
        self.sendMetod = sendMetod
        self.voucher_activity_id = getattr(Data, 'voucher_activity_id', '')
        self.payAmount = getattr(Data, 'payAmount', '')
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.Activity_Center_URL = data['Activity_Center_URL']
        self.size_tool_json = {"gte": ">=", "lte": "<=", "lt": "<", "gt": ">", "eq": "=", "-1": "不限"}




    def voucher_activity_search(self, voucherId=""):
        """
        ：param voucherShowStatus 活动状态
        ：param sendMetod 发放方式
        ：param voucherId 现金券id
        """
        search_url = "{}/ecmc/activityVoucher/list".format(self.Activity_Center_URL)
        search_body = {"cAdminName": "", "voucherShowStatus": "", "voucherId": voucherId, "sendMetod": self.sendMetod, "pageNum": 1, "pageSize": 50}
        search_res = self.activity_rss.post(url=search_url, json=search_body, headers=self.json_head).json()
        print(search_res)
        activityVoucher_lst = jsonpath.jsonpath(search_res, "$..activityId")
        sendMetod_lst = jsonpath.jsonpath(search_res, "$..sendMetod")
        for i in range(len(activityVoucher_lst)):
            if activityVoucher_lst[i] == self.voucher_activity_id:
                self.activity_id = activityVoucher_lst[i]
                self.sendMetod = sendMetod_lst[i]
                logger.info(f"本次查询到活动ID为：{self.activity_id}，此时该活动的发放方式为：{self.sendMetod}")
                break
        return self

    def voucher_activity_detail_rule(self, activityId, sendMetod):
        """活动详情--支付中心发放获取规则"""
        voucher_activity_detail_url = "{}/ecmc/activityVoucher/detail".format(self.Activity_Center_URL)
        voucher_activity_detail_body = {"activityId": activityId}
        voucher_activity_detail_res = self.activity_rss.post(url=voucher_activity_detail_url, json=voucher_activity_detail_body, headers=self.json_head).json()
        # print(voucher_activity_detail_res)
        rule_voucher_activity = []
        if sendMetod == 1:
            rule_voucher_id = jsonpath.jsonpath(voucher_activity_detail_res, "$..voucherId")
            # print(rule_voucher_id)
            rule_minAmount = jsonpath.jsonpath(voucher_activity_detail_res, "$..minAmount")
            # print(rule_minAmount)
            rule_minAmountLogic = jsonpath.jsonpath(voucher_activity_detail_res, "$..minAmountLogic")
            # print(rule_minAmountLogic)
            rule_maxAmount = jsonpath.jsonpath(voucher_activity_detail_res, "$..maxAmount")
            # print(rule_maxAmount)
            rule_maxAmountLogic = jsonpath.jsonpath(voucher_activity_detail_res, "$..maxAmountLogic")
            # print(rule_maxAmountLogic)
            rule_minAmount_symbol = []
            rule_maxAmount_symbol = []
            for i in range(len(rule_minAmount)):
                if rule_minAmountLogic[i] in self.size_tool_json:
                    rule_minAmount_symbol.append(self.size_tool_json[rule_minAmountLogic[i]])

                if rule_maxAmountLogic[i] in self.size_tool_json:
                    rule_maxAmount_symbol.append(self.size_tool_json[rule_maxAmountLogic[i]])
                # 检查是否需要设置为无穷大
                if rule_maxAmount[i] == 0.0:  # 这里使用 0.0 作为判断条件
                    rule_maxAmount[i] = math.inf
            # print(rule_minAmount_symbol)
            for m in range(len(rule_minAmount)):
                rule_json = {
                    rule_voucher_id[m]: {
                        "minAmount": rule_minAmount[m],
                        "minAmountLogic": rule_minAmount_symbol[m],
                        "maxAmount": rule_maxAmount[m],
                        "maxAmountLogic": rule_maxAmount_symbol[m]}
                }
                rule_voucher_activity.append(rule_json)
        # print(rule_voucher_activity)
        return rule_voucher_activity
    def voucher_activity_add(self, customRules=None, useLimitNumber=None, voucherNumTotal=None):
        now_time_one_minutes = str((datetime.now() + timedelta(minutes=1)).strftime("%Y-%m-%d %H:%M:%S"))
        logger.info(f"获取当前时间一分钟后的时间：{now_time_one_minutes}")
        now_time_seven_day = str((datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S"))
        logger.info(f"获取当前时间七天后的时间：{now_time_seven_day}")
        voucher_activity_add_url = "{}/ecmc/activityVoucher/save".format(self.Activity_Center_URL)
        voucher_activity_add_body = {"activityName": self.activity_name, "activityStartTimeShow": now_time_one_minutes, "activityEndTimeShow": now_time_seven_day, "prompt": "测试三期",
                                     "sendMethod": "1", "customRules": "-1"}
        if self.sendMetod != None:
            voucher_activity_add_body["sendMethod"] = self.sendMetod
        if  customRules !=  None:
            voucher_activity_add_body["customRules"] = customRules
        obtain_voucher_url = "{}/ecmc/voucher/enableVoucherList".format(self.Activity_Center_URL)
        obtain_voucher_body = {"pageNum": 1, "pageSize": 50}
        obtain_voucher_res = self.activity_rss.post(url=obtain_voucher_url, json=obtain_voucher_body, headers=self.json_head).json()
        res_result = jsonpath.jsonpath(obtain_voucher_res, "$.result")[0]
        # 当选择发放方式为用户发放，不能绑定比例类的现金券
        if self.sendMetod != None and self.sendMetod == '2':
            # 这段代码是一个列表推导式，用于过滤掉满足特定条件的字典元素。
            # 具体来说，它会遍历res_result列表中的每个字典元素d，并检查字典中是否存在键为'faceValueMode'且值为2的项。
            # 如果存在这样的项，则不将该字典元素包含在新的列表中。最终，生成的新列表将只包含不满足条件的字典元素。
            res_result = [d for d in res_result if not ('faceValueMode' in d and d['faceValueMode'] == 2)]
        voucher_count = len(res_result)
        if voucher_count != 0:
            Amount = 0
            voucherList = []
            # 将res_result 列表内的值顺序按照faceValue大小顺序排一下
            res_result = sorted(res_result, key=lambda x: x["faceValue"])
            for k in res_result:
                Amount = Amount + 5000
                if self.sendMetod == "2":
                    Amount = '0'
                v = {"activityVoucherId": 0, "time": [now_time_one_minutes, now_time_one_minutes], "sendStartTimeShow": now_time_one_minutes, "sendEndTimeShow": now_time_seven_day,
                     "useLimitNum": "-1", "voucherNumTotal": "-1", "minAmount": Amount, "minAmountLogic": "gte", "maxAmountLogic": "lte"}
                maxAmount = Amount + 5000
                if self.sendMetod == "2":
                    maxAmount = '1'
                if useLimitNumber != None:
                    v["useLimitNum"] = useLimitNumber
                v["maxAmount"] = maxAmount
                if voucherNumTotal != None:
                    v["voucherNumTotal"] = voucherNumTotal
                k.update(v)
                voucherList.append(k)
            if voucher_count >= 2:
                # 将voucherList 列表内 最后一个值的字段maxAmount设置为不限规则
                voucherList[-1]["maxAmountLogic"] = "-1"
                voucherList[-1]["maxAmount"] = ""
            print(voucherList)
            voucher_activity_add_body["voucherList"] = voucherList
            voucher_activity_add_res = self.activity_rss.post(url=voucher_activity_add_url, json=voucher_activity_add_body,
                                                        headers=self.json_head).json()
            logger.info(f"执行结果：{voucher_activity_add_res}")
        else:
            logger.info("无可用现金券参与活动的创建，请检查后台数据")
        return self
    def mian_amount_activity_voucher(self, rule_voucher_activity=None, amount=None):
        """根据充值金额命中指定现金券活动规则的现金券ID"""
        voucher_id = None
        if rule_voucher_activity != None:
            for rule in rule_voucher_activity:
                for key, value in rule.items():
                    # 获取每个规则的 minAmount、minAmountLogic、maxAmount、maxAmountLogic
                    minAmount = value['minAmount']
                    minAmountLogic = value['minAmountLogic']
                    maxAmount = value['maxAmount']
                    maxAmountLogic = value['maxAmountLogic']
                    # 将字符串转换为浮动类型
                    amount = float(amount)
                    minAmount = float(minAmount)
                    maxAmount = float(maxAmount)
                    # 判断是否满足最小金额逻辑
                    if minAmountLogic == '>=' and amount < minAmount:
                        continue
                    elif minAmountLogic == '>' and amount <= minAmount:
                        continue

                    # 判断是否满足最大金额逻辑
                    if maxAmountLogic == '<=' and amount > maxAmount:
                        continue
                    elif maxAmountLogic == '<' and amount >= maxAmount:
                        continue
                    elif maxAmountLogic == '不限' and amount > maxAmount:
                        continue

                    # 如果满足规则，返回key值
                    voucher_id = key
        # print(voucher_id)
        return voucher_id, amount
    def mian_activity_amount_rule_voucher(self, voucher_id=None, disableStatus=None, amount=None):
        """根据现金券规则生成现金券金额"""
        create_voucher_user_amount = 0
        faceTypeValue_json = VoucherCard(self.activity_rss).rule_voucherId_typeValue_positioning(disableStatus=disableStatus, voucher_id=voucher_id)
        msg = ""
        if faceTypeValue_json != None:
            if faceTypeValue_json['faceValueMode'] == 1:
                print("固定金额")
                msg = "固定金额生成金额"
                create_voucher_user_amount = faceTypeValue_json['faceTypeValue']
            elif faceTypeValue_json['faceValueMode'] == 2:
                print("比列生成")
                msg = "比列生成金额"
                create_voucher_user_amount = math.ceil(amount * (float(faceTypeValue_json['faceTypeValue'].strip('%')) / 100))
        else:
            msg = "无规则生成金额"
        print(msg)
        return create_voucher_user_amount, msg

    def mian_activity_voucher_amount_create(self, activity_id=None, amount=None, disableStatus=None):
        """生成金额逻辑"""
        rule_voucher_activity = self.voucher_activity_detail_rule(activity_id, 1)
        voucher_id, amount = self.mian_amount_activity_voucher(rule_voucher_activity, amount)
        # print(voucher_id, amount)
        create_voucher_user_amount, msg = self.mian_activity_amount_rule_voucher(voucher_id, disableStatus, amount)
        # print(create_voucher_user_amount, msg)
        return create_voucher_user_amount, msg
    def voucher_activity_user_distribution(self):
        search_user_url = "{}/ecmc/activityVoucher/getUser".format(self.Activity_Center_URL)


if __name__ == '__main__':
    target_rss = SOOLogin("uat-activity.hqchip.com", "ecmc").target_login()
    # rule_voucher_activity = VoucherActivity(target_rss, "三期测试-3", "2").voucher_activity_detail_rule(2546,1)
    # VoucherActivity(target_rss, "三期测试-3", "2").mian_amount_activity_voucher(rule_voucher_activity, 500000)
    VoucherActivity(target_rss, "三期测试-3", "2").mian_activity_voucher_amount_create(2543, 5000)

