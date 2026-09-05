import calendar
import json
import re
import time
import jsonpath
import yaml


from huaqiu_order_api.common.loguru_logger import logger
# from huaqiu_order_api.SSO_Reception.sso_reception import SSO_Reception
# from huaqiu_order_-api.common.my_data import Data
from huaqiu_order_api.common.my_data import Data
from huaqiu_order_api.common.my_path import yaml_file

with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
    data = yaml.load(yamlfile, Loader=yaml.FullLoader)
passport_url = data['PassPort_URL']
HQCHIP_URL = data['HQCHIP_URL']
center_java_url = data['center_java_url']
center_php_url = data['center_php_url']
PAY_URL = data['PAY_URL']
Assets_Center_url = data['Assets_Center_url']

def recharge_order_create(rss, payAmout, activity_type=None):
    timestamp = time.time()
    token = getattr(Data, "token")
    headers = {'Content-Type': 'application/json;charset=UTF-8', 'Authorization': token}
    activity_voucher_url = "{}/web/proxy/pay/payCenter/internal/getPayAppActiveList".format(center_java_url)
    activity_voucher_res = rss.get(url=activity_voucher_url, headers=headers).json()
    print("1111：{}".format(activity_voucher_res))
    activeId = ''
    recharge_order_create_body = {
                        # "activeId": activeId,
                        "appid": 90169,
                        "currency": "CNY",
                        "orderSource": "ic",
                        "amount": payAmout*100,
                        "returnUrl": "{}/mycenter/finance/balance/index".format(HQCHIP_URL),
                        "timestamp": timestamp
                    }
    if "result" in activity_voucher_res and activity_voucher_res['result'] != []:
        activeId_lst = jsonpath.jsonpath(activity_voucher_res, "$..activeId")
        activeName = jsonpath.jsonpath(activity_voucher_res, "$..activeName")
        orderSource = jsonpath.jsonpath(activity_voucher_res, "$..orderSource")
        if activity_type != None:
            for i in range(len(activeName)):
                if activity_type == orderSource[i]:
                    activeId = activeId_lst[i]
                    recharge_order_create_body['activeId'] = activeId
                    print("本次前台充值参与活动：{0}，此时activityId：{1}".format(activeName[i], activeId))

        else:
            print("本次前台充值不参与活动")
            activeId = ""
            recharge_order_create_body['activeId'] = activeId
    else:
        print("用户：{}没有可参与充值赠送现金券活动".format(getattr(Data, "uid")))
    recharge_order_create_url = '{}/assets/api/service/topUpOrder/createUserTopUpOrder'.format(Assets_Center_url)

    recharge_order_create_res = rss.post(url=recharge_order_create_url, json=recharge_order_create_body, headers=headers).json()
    logger.info(recharge_order_create_res)
    recharge_order = jsonpath.jsonpath(recharge_order_create_res, "$..orderNo")[0]
    trade_no = jsonpath.jsonpath(recharge_order_create_res, "$..tradeNo")[0]
    sync_trande_url = jsonpath.jsonpath(recharge_order_create_res, "$..cashUrl")[0]
    authKey = sync_trande_url.split("authKey=")[1].split("&centerTradeNo=")[0]
    payment_url = "{}/payCenter/payV3/transaction/payment".format(PAY_URL)
    payment_body = {"authKey": authKey, "centerTradeNo": trade_no, "payChannelId": 6, "instalments": "", "returnUrl": "v3/pay/success"}
    logger.info(payment_body)
    payment_res = rss.post(url=payment_url, json=payment_body, headers=headers).json()
    logger.info(f"执行结果:{payment_res}")
    sync_order_url = "{}/payCenter/payV3/transaction/queryOrder".format(PAY_URL)
    sync_order_body = {"authKey": authKey, "centerTradeNo": trade_no}
    sync_order_res = rss.post(url=sync_order_url, json=sync_order_body, headers=headers).json()
    logger.info(f"执行结果:{sync_order_res}")
    setattr(Data, "voucher_activity_id", activeId)
    setattr(Data, "payAmout", payAmout)
    setattr(Data, "recharge_order", recharge_order)
    logger.info(recharge_order)
    return recharge_order
if __name__ == '__main__':
    from huaqiu_order_api.SSO_Reception.sso_reception import SSO_Reception
    rss = SSO_Reception('https://uat-www.hqchip.com').login()
    recharge_order_create(rss, 5000)
