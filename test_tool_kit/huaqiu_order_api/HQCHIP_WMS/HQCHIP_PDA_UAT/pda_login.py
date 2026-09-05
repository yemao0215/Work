import time

import jsonpath
import requests
import yaml

from huaqiu_order_api.HQCHIP_SOO.login import SOOLogin
from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_path import yaml_file, account_yaml


class PdaLogin:
     # UAT环境
    def __init__(self):
        self.pda_rss = requests.Session()
        self.json_head = {"Content-Type": "application/json"}
        self.pda_json_head = {"Content-Type": "application/json", "User-Agent":"okhttp/3.14.9", "Connection":"keep-alive"}
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.WMS_URL = data["WMS_URL"]
        with open(account_yaml, 'r', encoding='utf-8') as yamlfile:
            account = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.warehouse_type = int(account["HQCHIP_GOODS"]["warehouse_id"])

    def pda_login(self):
        """PDA登录"""
        pda_login = '{}/wms/base/login'.format(self.WMS_URL)  # pda登录
        pda_login_body = {"account": "admin", "password": "HQ@uat@666"}
        logger.info(f"开始执行pda登录,登录环境:{pda_login},登录账号密码:{pda_login_body}")
        pda_login_res = self.pda_rss.post(url=pda_login, json=pda_login_body, headers=self.pda_json_head)
        logger.info(f"pda登录完成,登录结果:{pda_login_res.json()}")
        select_store_url = self.WMS_URL + f'/wms/base/pda/store/selectStore?storeCode={self.warehouse_type}'
        select_store_res = self.pda_rss.get(url=select_store_url, headers=self.pda_json_head)  # 选择仓库
        logger.info(f"选择pda仓库:storeCode={self.warehouse_type} 东莞仓,返回结果:{select_store_res.json()}")

        return self.pda_rss

if __name__ == '__main__':
    pda_rss = PdaLogin().pda_login()