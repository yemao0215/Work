import json
import re
import time

import jsonpath
import requests
import yaml

from huaqiu_order_api.HC2018_admin.login.login import Login
from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_data import Data
from huaqiu_order_api.common.my_path import yaml_file, account_yaml, partnerYaml_dir


class SupplierUpdate:
    def __init__(self, pn2=None, keyword=None):
        self.rss = requests.Session()
        # 设置代理ip
        proxy_ip = "http://192.168.20.6:3128"
        # 设置代理
        self.proxies = {"http": proxy_ip, "https": proxy_ip}
        self.supplier_url = "https://api.mouser.com"
        self.appikey = "76f623be-ee57-4ae3-86b6-01e54048fd18"
        self.headers = {"Content-Type": "application/x-www-form-urlencoded",
                        "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://www.huaqiu.com)"
                        }
        self.headers_json = {"Content-Type": "application/json; charset=UTF-8",
                             "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://www.huaqiu.com)"
                             }
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.HQCHIP_URL = data['HQCHIP_URL']
        self.SEARCH_URL = data['SEARCH_URL']
        self.ES_SEARCH_URL = data['ES_SEARCH_URL']
        self.HC2018_ADMIN_URL = data['HC2018_ADMIN_URL']
        with open(account_yaml, 'r', encoding='utf-8') as yamlfile:
            account = yaml.load(yamlfile, Loader=yaml.FullLoader)
        # self.keyword = "0402 191KΩ 1安"
        self.keyword = keyword
        self.pn2 = pn2
        self.goods_id = [1017426139]
    def get_supplier_list(self):
        # 读取 YAML 文件
        with open(partnerYaml_dir, 'r', encoding='utf-8') as file:
            data = yaml.safe_load(file)
        partner_list = None
        # 提取列表
        if 'items' in data:
            partner_list = data['items']
            # print(partner_list)  # 输出: ['apple', 'banana', 'orange', 'grape']
        print(partner_list)
        return partner_list
    def supplier_update(self, partner_list= None):
        supplier_update_res = None
        if self.pn2 is None:
            if partner_list is not None and isinstance(partner_list, list):
                for partner in partner_list:
                    time.sleep(2)
                    print("开始执行供应商：{}".format(partner))
                    self.pn2 = partner
                    supplier_update_url = "{}/test/refreshSupplierDt".format(self.ES_SEARCH_URL)
                    supplier_update_body = {"pn2s": [self.pn2], "startId": 1}
                    supplier_update_res = self.rss.post(url=supplier_update_url, json=supplier_update_body,
                                                        headers=self.headers_json).json()
                    print(supplier_update_res)
            else:
                pass
        else:
            print("开始执行供应商：{}".format(self.pn2))
            supplier_update_url = "{}/test/refreshSupplierDt".format(self.ES_SEARCH_URL)
            supplier_update_body = {"pn2s": [self.pn2], "startId": 1}
            supplier_update_res = self.rss.post(url=supplier_update_url, json=supplier_update_body,
                                                headers=self.headers_json).json()
            print(supplier_update_res)
        return supplier_update_res

    def mian_update(self):
        suc = None
        if self.pn2 is None:
            partner_list = self.get_supplier_list()
            self.supplier_update(partner_list)
        else:
            supplier_update_res = self.supplier_update()
            suc = jsonpath.jsonpath(supplier_update_res, "$..suc")

        return suc

if __name__ == '__main__':
    pn2 = None
    SupplierUpdate(pn2=pn2).mian_update()