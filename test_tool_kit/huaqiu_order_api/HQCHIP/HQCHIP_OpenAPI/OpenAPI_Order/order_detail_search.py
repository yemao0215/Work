
import hashlib
import json
import time

from urllib.parse import quote

import requests
import yaml

from huaqiu_order_api.HQCHIP.HQCHIP_OpenAPI.OpenAPI_user.obtain_user import OpenAPIObtainUser
from huaqiu_order_api.HQCHIP.HQCHIP_OpenAPI.Openapi_signature.signature import SignAture
from huaqiu_order_api.HQCHIP_Center.order_center.get_ic_order import get_ic_order
from huaqiu_order_api.SSO_Reception.sso_reception import SSO_Reception

from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_data import Data

from huaqiu_order_api.common.my_path import yaml_file, account_yaml
from huaqiu_order_api.common.yaml_handler import write_yaml


class OrderDetailSearch:
    # 开放接口订单详情查询

    def __init__(self):
        self.openapi_rss = requests.Session()
        self.json_head = {"Content-Type": "application/json"}
        self.form_head = {'User-Agent': 'HQCHIP OpenAPI Python-SDK/1.0', "X-Request-Version": '1.0'}
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.app_key = data['APP_KEY']
        self.app_sec = data['APP_SEC']
        self.url = data['OPENAPI_UAT_URL']
    def query_url_arguments(self, data):
        """将body参数转换成可拼接至url的参数"""
        lt = []
        for k, v in data.items():
            lt.append(k + '=' + quote(str(v)))
        # 这个是在for循环外面的，就是将列表的元素之间用用&符号连接起来
        query_string = '&'.join(lt)
        return query_string
    def order_detail_search(self, order_sn=None, order_id=None, out_order_no=None ):
        if order_sn != None and order_id in [None, '']:
            phone = OpenAPIObtainUser().openapi_user_search()
            if phone != "13632845795":
                phone = "13632845795"
                setattr(Data, 'key_phone', phone)
            pass_port_user_msg = {"phone": phone, "name": "qaulau@qq.com", "password": "a123456"}
            user_msg = {'PassPort': pass_port_user_msg}
            write_yaml(account_yaml, user_msg)
            rss = SSO_Reception('https://uat-www.hqchip.com').login()
            order_id, out_order_no = get_ic_order(rss, order_sn)
            print(order_id, out_order_no)
            setattr(Data, 'ic_order_id', order_id)
            setattr(Data, 'out_order_no', out_order_no)
        openapi_detail_url = '{0}/order/detail'.format(self.url)
        # print(openapi_detail_url)
        params = {
            'app_key': self.app_key,
            'timestamp': int(time.time()),
        }
        data = {'order_id': order_id, 'out_order_no': out_order_no}
        params['sign'] = SignAture(self.app_sec).hqchip_sign_main(params, data)
        sys_params = params.copy()
        sys_params.update(data)
        print(sys_params)
        openapi_detail_url = openapi_detail_url + "?" + self.query_url_arguments(sys_params)
        openapi_make_res = self.openapi_rss.get(url=openapi_detail_url, headers=self.form_head, timeout=10).json()
        logger.info(openapi_make_res)
        error_message = openapi_make_res['error_message']
        if error_message == '':
            data = openapi_make_res['data']
            logger.debug('=*' * 50)
            print(data)
            return data
        else:
            logger.info('错误信息：'f"{error_message}")
            return error_message

if __name__ == '__main__':
    OrderDetailSearch().order_detail_search(order_sn="S2025040217447")