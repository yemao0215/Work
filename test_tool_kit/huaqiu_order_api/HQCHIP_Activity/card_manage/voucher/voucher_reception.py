
import json
import time
from datetime import datetime, timedelta

import jsonpath
import requests
import yaml
from huaqiu_order_api.HQCHIP_SOO.login import SOOLogin
from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_path import yaml_file


class VoucherReception:
    ## 现金券前台使用
    def __init__(self, order_id=None, order_sn=None, order_type=None, order_amount=None, detail_number=None, unionId=None, voucher_id=None):
        """
        :param order_sn 订单编号
        :param order_type 订单类型  ic smt  pcb  pcba
        :param order_amount 订单总金额
        :param detail_number 扣减明细条数
        :param unionId 用户id
        :param voucher_id 用户现金券id

        """
        self.rss = requests.Session()
        self.json_head = {"Content-Type": "application/json"}
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.Activity_Center_URL = data['Activity_Center_URL']
        self.order_id = order_id
        self.order_sn = order_sn
        self.order_type = order_type
        self.unionId = unionId
        self.voucher_id = voucher_id
        self.order_amount = order_amount
        self.detail_number = detail_number
    def voucher_user_create(self):
        pass

    def user_effective_voucher(self):
        """
        用户有效现金券核对
        """
        user_effective_voucher_url = "{}/ecmc/activityapi/orderVoucher/validList".format(self.Activity_Center_URL)
        user_effective_voucher_body = {
            "appid": self.order_type,  # ic  pcb  pcba
            "timesatmp": str(int(time.time())),
            "unionId": self.unionId,
            "transactionType": self.order_type,  # ic  pcb
            "pageNum": 1,
            "pageSize": 100
        }
        user_effective_voucher_res = self.rss.post(user_effective_voucher_url, json=user_effective_voucher_body, headers=self.json_head).json()
        print(user_effective_voucher_res)
        user_usable_voucher_dict = []
        usableUserVoucherList = user_effective_voucher_res['result']["usableUserVoucherList"]
        if usableUserVoucherList !=[]:
            cardNumber_list = jsonpath.jsonpath(usableUserVoucherList, '$..cardNumber')
            balance_list = jsonpath.jsonpath(usableUserVoucherList, '$..balance')
            UserVoucherId_list = jsonpath.jsonpath(usableUserVoucherList, '$..id')
            unionId_list = jsonpath.jsonpath(usableUserVoucherList, '$..unionId')
            # 四个列表组合成字典
            user_usable_voucher_dict = {
                cardNumber: {
                    "balance": balance,
                    "unionId": unionId,
                    "UserVoucherId": UserVoucherId
                    }
                for cardNumber, balance, UserVoucherId, unionId in zip(cardNumber_list, balance_list, UserVoucherId_list, unionId_list)}
        print(user_usable_voucher_dict)
        return user_usable_voucher_dict
    def acquire_coincident_voucher(self, user_usable_voucher_dict, voucher_id_list=None):
        """获取符合的现金券，不考虑多明细不同订单金额的"""
        if user_usable_voucher_dict != []:
            max_balance_value = float('-inf')  # 初始化将现金券剩余可用金额为无穷大
            max_balance_key = None  # 初始化最大值对应的键
            for k, j in user_usable_voucher_dict.items():
                if voucher_id_list != None:
                    if isinstance(voucher_id_list, list):
                        for voucher_id in voucher_id_list:
                            if j.get("UserVoucherId") == voucher_id:
                                self.balance = j.get("balance")
                                self.voucher_id = voucher_id
                    else:
                        voucher_id_lst = voucher_id_list.split(",")
                        for voucher_id in voucher_id_lst:
                            if j.get("UserVoucherId") == voucher_id:
                                self.balance = j.get("balance")
                                self.voucher_id = voucher_id
                else:
                    if j.get("balance", float('-inf')) >= max_balance_value:
                        max_balance_value = j.get("balance")
                        max_balance_key = k
                        max_voucher_id = j.get("UserVoucherId")
                        self.balance = max_balance_value
                        self.voucher_id = max_voucher_id
        else:
            print("用户：{}没有可用的现金券".format(self.unionId))
            self.balance = 0
            self.voucher_id = None
        return self.balance, self.voucher_id
    def voucher_use(self):
        """
        现金券使用
        """
        voucher_use_url = "{}/ecmc/activityapi/orderVoucher/use".format(self.Activity_Center_URL)
        voucher_use_body = {
            "appid": self.order_type,  # ic  pcb  pcba
            "timesatmp": int(time.time()),
            "unionId": self.unionId,

        }
        detail_info = []
        user_usable_voucher_dict = self.user_effective_voucher()
        self.balance, self.voucher_id = self.acquire_coincident_voucher(user_usable_voucher_dict, self.voucher_id)
        if float(self.balance) >= float(self.order_amount):
            print("现金券id：{0}的剩余可用余额：{1}满足订单总金额：{2}".format(self.voucher_id, self.balance, self.order_amount))
            if self.detail_number != None:
                for i in range(int(self.detail_number)):
                    detail = {
                        "transactionId": str(self.order_id if self.order_id else "1") + str(i),
                        "transactionSn": str(self.order_sn if self.order_sn else "SC0111") + str(i),
                        "transactionAmount": float(self.order_amount) / int(self.detail_number),
                        "transactionType": self.order_type,
                        "userVoucherId": self.voucher_id,
                        "useSort": i + 1,
                    }
                    detail_info.append(detail)
            else:
                detail = {
                    "transactionId": str(self.order_id if self.order_id else "1"),
                    "transactionSn": str(self.order_sn if self.order_sn else "SC0111"),
                    "transactionAmount": float(self.order_amount),
                    "transactionType": self.order_type,
                    "userVoucherId": self.voucher_id,
                    "useSort": 1,
                }
                detail_info.append(detail)
            voucher_use_body["detail"] = detail_info
            print(voucher_use_body)
            voucher_use_res = self.rss.post(url=voucher_use_url, json=voucher_use_body, headers=self.json_head).json()
            logger.info(f"执行结果:{voucher_use_res}")
        return voucher_use_body
    def  voucher_rollbackUse(self, body=None):
        """现金券退还"""
        if body != None:
            for i in range(len(body["detail"])):
                body["detail"][i]["rollbackAmount"] = body["detail"][i]["transactionAmount"]
            voucher_rollbackUse_url = "{}/ecmc/activityapi/orderVoucher/rollbackUse".format(self.Activity_Center_URL)
            voucher_rollbackUse_body = body
            voucher_rollbackUse_res = self.rss.post(url=voucher_rollbackUse_url, json=voucher_rollbackUse_body, headers=self.json_head).json()
            print(voucher_rollbackUse_res)
if __name__ == '__main__':
    order_id = None
    order_sn = None
    order_type = "ic"
    order_amount = '100'
    detail_number = 5
    unionId = 6060991
    voucher_id = None
    body = {'appid': 'ic', 'timesatmp': 1734415772, 'unionId': 6060991,
            'detail': [
                {'transactionId': '10', 'transactionSn': 'SC01110', 'transactionAmount': 20.0, 'transactionType': 'ic', 'userVoucherId': '1868568469926125569', 'useSort': 1},
                {'transactionId': '11', 'transactionSn': 'SC01111', 'transactionAmount': 20.0, 'transactionType': 'ic', 'userVoucherId': '1868568469926125569', 'useSort': 2},
                {'transactionId': '12', 'transactionSn': 'SC01112', 'transactionAmount': 20.0, 'transactionType': 'ic', 'userVoucherId': '1868568469926125569', 'useSort': 3},
                {'transactionId': '13', 'transactionSn': 'SC01113', 'transactionAmount': 20.0, 'transactionType': 'ic', 'userVoucherId': '1868568469926125569', 'useSort': 4},
                {'transactionId': '14', 'transactionSn': 'SC01114', 'transactionAmount': 20.0, 'transactionType': 'ic', 'userVoucherId': '1868568469926125569', 'useSort': 5}]}
    VoucherReception(order_id, order_sn, order_type, order_amount, detail_number, unionId, voucher_id).voucher_use()
    # VoucherReception(order_id, order_sn, order_type, order_amount, detail_number, unionId, voucher_id).voucher_rollbackUse(body)
    # VoucherReception(order_id, order_sn, order_type, order_amount, detail_number, unionId, voucher_id).user_effective_voucher()


