
import hashlib
import json
import re
import time
from datetime import datetime

import jsonpath
import requests
import yaml
from faker import Faker

from huaqiu_order_api.HQCHIP.Commonly_kit_tool.php_antisequence import PhpAntisequence
from huaqiu_order_api.HQCHIP.HQCHIP_OpenAPI.Openapi_signature.signature import SignAture
from huaqiu_order_api.HQCHIP_Center.user_center import get_invoice
from huaqiu_order_api.SSO_Reception.sso_reception import SSO_Reception
from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_data import Data
from huaqiu_order_api.common.my_path import yaml_file, account_yaml
from huaqiu_order_api.common.yaml_handler import write_yaml


class DeleteOrder:
    # 开放接口创建订单

    def __init__(self, env_type=None, order_id=None, out_order_no=None):

        self.openapi_rss = requests.Session()
        self.json_head = {"Content-Type": "application/json"}
        self.form_head = {'User-Agent': 'HQCHIP OpenAPI Python-SDK/1.0', "X-Request-Version": '1.0'}
        # self.out_order_no = "AutoTest" + datetime.now().strftime("%Y%m%d") + "000" + str(Faker("zh_CN").random_int(1, 10000))
        self.out_order_no = out_order_no
        self.env_type = env_type
        self.order_id = order_id
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.app_key = data['APP_KEY']
        self.app_sec = data['APP_SEC']
        self.url = data['OPENAPI_UAT_URL']
        if self.env_type == "pro":
            self.url = data['OPENAPI_PRO_URL']
        self.GoodsName = data['APIGoodsName']
        self.GoodsType = data['APIGoodsType']
        self.phone = data['APIPhone']
        self.remark = data['APIOderRemark']
        # self.product_num = data['APIProductNum']
        self.partial_order_alloweb = data['APIPartialOrderAlloweb']
        self.center_java_url = data['center_java_url']
        with open(account_yaml, 'r', encoding='utf-8') as yamlfile:
            account = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.phone = account["PassPort"]["phone"]
        self.goods_id =account["HQCHIP_GOODS"]["goods_id"]
        self.numder = account["HQCHIP_GOODS"]["number"]
        self.vat_type = account["HQCHIP_GOODS"]["vat_type"]

    def order_delete(self):
        """订单删除"""
        openapi_delete_url = '{}/order/delete/'.format(self.url)
        self.timestamp = int(time.time())
        params = {'app_key': self.app_key, 'timestamp': self.timestamp}
        data = {
            'order_id': self.order_id,
            'out_order_no': self.out_order_no
        }
        logger.info(data)
        # 单独的生成签名
        # sys_params = params.copy()
        # sys_params.update(data)
        # params['sign'] = self.gen_sign(self.app_sec, sys_params)

        # 统一封装 签名sign生成方法
        sgin = SignAture(self.app_sec).hqchip_sign_main(params, data)
        params['sign'] = sgin
        openapi_delete_res = self.openapi_rss.post(url=openapi_delete_url, params=params, data=data, headers=self.form_head,
                                                 timeout=10).json()
        logger.info(openapi_delete_res)
        error_message = openapi_delete_res['error_message']
        logger.info(error_message)
        return openapi_delete_res
if __name__ == '__main__':
    env_type = None
    order_id = None
    out_order_no = None
    DeleteOrder(env_type=env_type, order_id=order_id, out_order_no=out_order_no).order_delete()