import sys
import time
import jsonpath
import yaml

from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_data import Data
from huaqiu_order_api.common.my_path import yaml_file

with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
    data = yaml.load(yamlfile, Loader=yaml.FullLoader)
passport_url = data['PassPort_URL']
center_java_url = data['center_java_url']
center_php_url = data['center_php_url']
PAY_URL = data['PAY_URL']
Assets_Center_url = data['Assets_Center_url']

def ativity_withdraw_order_create(rss, recharge_order=None, paypassword=None, withdrawAmount=None):
    """按充值单整单提现"""
    timestamp = int(time.time()) // 10**13
    print(timestamp)
    token = getattr(Data, "token")
    headers = {'Content-Type': 'application/json;charset=UTF-8', 'Authorization': token}
    ativity_recharge_search_url = "{}/assets/api/service/getBillWithdraw".format(Assets_Center_url)
    ativity_recharge_search_body = {"pageNum": 1, "pageSize": 10}
    ativity_recharge_search_res = rss.post(url=ativity_recharge_search_url, json=ativity_recharge_search_body, headers=headers).json()
    activity_recharge_lst = jsonpath.jsonpath(ativity_recharge_search_res, "$..result")[0]
    withdraw_order_msg = None
    if activity_recharge_lst != []:
        if recharge_order != None:
            for k in activity_recharge_lst:
                if k["orderNo"] == recharge_order:
                    withdraw_order_msg = k
                    break
        else:
            withdraw_order_msg = activity_recharge_lst[0]
        applyAmount = withdraw_order_msg["surplusBalance"]
        currency = withdraw_order_msg["currency"]
        billTradeNo = withdraw_order_msg["tradeNo"]
        ativity_withdraw_order_create_url = "{}/assets/api/service/withdrawalOrder/createOriginalRoadWithdrawalOrder".format(Assets_Center_url)
        ativity_withdraw_order_create_body = {
            "address": [],
            "appid": 90169,
            "applyAmount": applyAmount,
            "bankAcctountName": "",
            "bankAddress": "",
            "bankCardNo": "",
            "bankCity": "",
            "bankProvince": "",
            "billTradeNo": billTradeNo,
            "currency": currency,
            "orderSource": "ic",
            "password": "123456",
            "timestamp": timestamp,
            "withdrawalWay": 4
        }
        print(ativity_withdraw_order_create_body)
        if paypassword != None:
            ativity_withdraw_order_create_body["password"] = paypassword
        if withdrawAmount != None:
            applyAmount = float(withdrawAmount) * 100
            ativity_withdraw_order_create_body["applyAmount"] = applyAmount
        ativity_withdraw_order_create_res = rss.post(url=ativity_withdraw_order_create_url, json=ativity_withdraw_order_create_body, headers=headers)
        if ativity_withdraw_order_create_res.status_code == 200:
            print(f"提现单提交成功，执行结果为{ativity_withdraw_order_create_res.json()}")
            setattr(Data, "withdrawAmount", float(applyAmount) / 100)
        return recharge_order
    else:
        logger.error("不存在可操作提现的内容")
        msg = "不存在可操作提现的内容"
        return msg

if __name__ == '__main__':
    recharge_order = "R25121114274468020"
    paypassword = "123456"
    withdrawAmount = 5000
    from huaqiu_order_api.SSO_Reception.sso_reception import SSO_Reception
    target_rss = SSO_Reception('https://uat-www.hqchip.com').login()
    ativity_withdraw_order_create(target_rss, recharge_order=recharge_order, paypassword=paypassword, withdrawAmount=withdrawAmount)