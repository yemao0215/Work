import json
import math
import time
from datetime import datetime, timedelta

import jsonpath
import yaml

from huaqiu_order_api.HQCHIP_Activity.card_manage.voucher.voucher_activity import VoucherActivity
from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_data import Data
from huaqiu_order_api.common.my_path import yaml_file


class UserVocher:

    def __init__(self, target_rss, recharge_order=None, unionId=None, activity_id=None, amount=None, disableStatus=None):
        """
        :param recharge_order 充值订单号
        """
        self.activity_rss = target_rss
        self.json_head = {"Content-Type": "application/json"}
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.Activity_Center_URL = data['Activity_Center_URL']
        self.recharge_order = recharge_order
        self.unionId = unionId
        self.activity_id = activity_id
        self.amount = amount
        self.disableStatus = disableStatus

    def user_voucher_search(self, unionIds=None, activityId=None, userVoucherId=None, lockStatus=None, disableStatus=None, withdrawalStatus=None, cardNumber=None,
                            sendStartTime=None, sendEndTime=None):
        search_url = "{}/ecmc/userVoucher/list".format(self.Activity_Center_URL)
        search_body = {"unionIds": "", "activityId": "", "userVoucherId": "", "lockStatus": "", "disableStatus": "",
                       "withdrawalStatus": "", "cardNumber": "", "sendStartTime": "", "sendEndTime": "",
                       "pageNum": 1, "pageSize": 50}
        if unionIds != None:
            search_body["unionIdList"] = unionIds if unionIds != None and isinstance(unionIds, list) else [unionIds]
        elif activityId != None:
            search_body["activityId"] = activityId
        elif userVoucherId != None:
            search_body["userVoucherId"] = userVoucherId
        elif lockStatus != None:
            search_body["lockStatus"] = lockStatus
        elif disableStatus != None:
            search_body["disableStatus"] = disableStatus
        elif withdrawalStatus != None:
            search_body["withdrawalStatus"] = withdrawalStatus
        elif cardNumber != None:
            search_body["cardNumber"] = cardNumber
        elif sendStartTime != None:
            search_body["sendStartTime"] = sendStartTime
        elif sendEndTime != None:
            search_body["sendEndTime"] = sendEndTime
        # print(search_body)
        search_res = self.activity_rss.post(url=search_url, json=search_body, headers=self.json_head).json()
        # print(search_res)
        unionId_list = jsonpath.jsonpath(search_res, "$..unionId")  # 用户id
        userVoucherId_list = jsonpath.jsonpath(search_res, '$..userVoucherId')  # 用户券id
        faceVocher_list = jsonpath.jsonpath(search_res, "$..faceValue")  # 面值
        cardNumber_list = jsonpath.jsonpath(search_res, "$..cardNumber")
        return unionId_list, userVoucherId_list, faceVocher_list, cardNumber_list
    def user_voucher_consumption(self, userVoucherId, unionId):
        """现金券的消费明细"""
        user_voucher_consumption_url = "{}/ecmc/userVoucher/logList".format(self.Activity_Center_URL)
        user_voucher_consumption_body = {"userVoucherId": userVoucherId, "unionId": unionId, "pageNum": 1, "pageSize": 50}
        # print(user_voucher_consumption_body)
        user_voucher_consumption_res = self.activity_rss.post(url=user_voucher_consumption_url, json=user_voucher_consumption_body, headers=self.json_head).json()
        total = jsonpath.jsonpath(user_voucher_consumption_res, "$..total")[0]
        transactionSn_lst= []
        if int(total) / 50 > 1:
            num = math.ceil(int(total) / 50)
            for i in range(num):
                i = i + 1
                user_voucher_consumption_body["pageNum"] = i
                user_voucher_consumption_res = self.activity_rss.post(url=user_voucher_consumption_url, json=user_voucher_consumption_body, headers=self.json_head).json()
                # 订单号或交易号
                transactionSn = jsonpath.jsonpath(user_voucher_consumption_res, "$..transactionSn")
                transactionSn_lst.append(transactionSn)
        else:
            transactionSn_lst = jsonpath.jsonpath(user_voucher_consumption_res, "$..transactionSn")
        if transactionSn_lst != []:

            if self.recharge_order in transactionSn_lst:
                msg = True
            else:
                msg = False
        else:
            msg = False
        return msg
    def mian_user_voucher_create_orientation(self):
        """生成用户现金券定位"""
        unionId = None
        userVoucherId = None
        faceVaule = None
        cardNumber = None
        unionId_list, userVoucherId_list, faceVaule_list, cardNumber_list = self.user_voucher_search(unionIds=self.unionId)
        # print(unionId_list)
        for m in range(len(unionId_list)):
            result = self.user_voucher_consumption(userVoucherId_list[m], unionId_list[m])
            # print(result)
            if result == True:
                print("定位到用户现金券面值{}".format(faceVaule_list[m]))
                unionId = unionId_list[m]
                userVoucherId = userVoucherId_list[m]
                faceVaule = faceVaule_list[m]
                cardNumber = cardNumber_list[m]
                break
            else:
                continue
        return unionId, userVoucherId, faceVaule, cardNumber
    def mian_activity_voucher_create_accounting(self):
        userVoucherId = None
        faceVaule = None
        cardNumber = None
        if self.activity_id not in [None, '']:
            create_voucher_user_amount, msg = VoucherActivity(self.activity_rss).mian_activity_voucher_amount_create(self.activity_id, self.amount, self.disableStatus)
            print(f"活动配置生成的现金券面额金额：{create_voucher_user_amount}")
            # 等待10s
            time.sleep(10)
            unionId, userVoucherId, faceVaule, cardNumber = self.mian_user_voucher_create_orientation()
            if userVoucherId != None and float(create_voucher_user_amount) == float(faceVaule):
                print(f"用户：{unionId}的用户现金券卡号：{cardNumber}现金券面值为{faceVaule}")
                logger.info(f"用户：{unionId}的用户现金券卡号：{cardNumber}现金券面值为{faceVaule}，与活动配置生成的现金券面额金额：{float(create_voucher_user_amount)}相符")
            else:
                if msg == "无规则生成金额":
                    logger.info(f"充值金额不符合现金券活动配置配置计算区间，即不生成现金券")
                else:
                    logger.error(f"生成的用户现金券异常")
        else:
            print("不参与现金券活动")
            msg = "不参与现金券活动"
        voucher_create_json = {"userVoucherId": userVoucherId, "cardNumber": cardNumber, "activityId": self.activity_id, "faceVaule": faceVaule, "msg": msg}
        return voucher_create_json
if __name__ == '__main__':
    recharge_order = "R24121213525139401"
    unionId = "5146221"
    activity_id = 2543
    amount = 5000
    # from huaqiu_order_api.HQCHIP_Activity.card_manage.voucher.voucher_activity import VoucherActivity
    from huaqiu_order_api.HQCHIP_SOO.login import SOOLogin
    target_rss = SOOLogin("uat-activity.hqchip.com", "ecmc").target_login()
    # VoucherActivity(target_rss, "三期测试-3", "2").mian_activity_voucher_amount_create(2546, 5000)
    UserVocher(target_rss, recharge_order, unionId, activity_id, amount).mian_activity_voucher_create_accounting()