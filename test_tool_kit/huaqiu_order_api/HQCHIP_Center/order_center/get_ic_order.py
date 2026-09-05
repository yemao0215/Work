import calendar
import json
import re
import time
import jsonpath
import yaml


# from huaqiu_order_api.SSO_Reception.sso_reception import SSO_Reception
# from huaqiu_order_-api.common.my_data import Data
from huaqiu_order_api.common.my_data import Data
from huaqiu_order_api.common.my_path import yaml_file

with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
    data = yaml.load(yamlfile, Loader=yaml.FullLoader)
passport_url = data['PassPort_URL']
center_java_url = data['center_java_url']
center_php_url = data['center_php_url']
HQCHIP_URL = data['HQCHIP_URL']
Assets_Center_url = data['Assets_Center_url']

def get_ic_order(rss, order_sn):
    """获取芯城订单的订单id order_id"""
    token = getattr(Data, 'token')
    headers = {"Authorization": token,
                    "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://www.huaqiu.com)"
                    }
    get_ic_order_search_url = "{}/hqapi/usericorder/getlistinfoV2?page=1&order_keyword={}&order_goods_keyword=&otime=0&ostatus=".format(HQCHIP_URL, order_sn)
    res = rss.get(url=get_ic_order_search_url, headers=headers).json()
    all_count = jsonpath.jsonpath(res, '$..all_count')
    if all_count[0] == '1':
        order_list = jsonpath.jsonpath(res, '$..order_list')[0]
        for k in order_list:
            if k['order_sn'] == order_sn:
                return k['order_id'], k['custom_sn']