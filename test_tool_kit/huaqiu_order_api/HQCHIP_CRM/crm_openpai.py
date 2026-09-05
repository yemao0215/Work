import base64
import hashlib
import json
import math
import re
import time
import datetime

import execjs
import jsonpath
import requests
import yaml
from Crypto.Cipher import AES

from huaqiu_order_api.HC2018_admin.login.login import Login
from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_data import Data
from huaqiu_order_api.common.my_path import yaml_file, autoStockYaml_dir, crmLifeDataYaml_dir, encryption_dir
from huaqiu_order_api.common.yaml_handler import read_yaml
from huaqiu_order_api.project_sqlreview.mysql_connection import MySQLConnection


class CrmOpenAPI:
    def __init__(self,  douyin_life_data_body=None):
        self.douyin_life_data_body = douyin_life_data_body
        self.rss = requests.Session()
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.CRM_URL = data['CRM_URL']
        self.headers = {"Content-Type": "application/x-www-form-urlencoded"}
        self.headers_json = {"Content-Type": "application/json; charset=utf-8"}
    def douyin_life_data(self):

        print(self.douyin_life_data_body)
        douyin_life_data_url = "{}/crm/customer/testDouyinLifeData".format(self.CRM_URL)
        douyin_life_data_body = self.douyin_life_data_body
        douyin_life_data_res = self.rss.post(url=douyin_life_data_url, json=douyin_life_data_body,
                                              headers=self.headers_json).json()
        print(douyin_life_data_res)


    def phone_decrypt(self, encipherPassword):
        # 固定client_secret，和你JS里第一个参数保持一致
        client_secret = "de8cd2c56322fbbbb301b771de914f84"
        key = client_secret.encode("utf-8")
        iv = client_secret[16:].encode("utf-8")
        # base64解码密文
        cipher_data = base64.b64decode(encipherPassword)
        aes = AES.new(key, AES.MODE_CBC, iv)
        raw = aes.decrypt(cipher_data)
        # 剔除PKCS5填充
        pad_num = raw[-1]
        plain = raw[:-pad_num].decode("utf-8")
        logger.info(f"解密手机号：{plain}")
        return plain
if __name__ == '__main__':
    douyin_life_data_body = read_yaml(crmLifeDataYaml_dir)
    CrmOpenAPI(douyin_life_data_body=douyin_life_data_body).douyin_life_data()
    CrmOpenAPI().phone_decrypt(douyin_life_data_body.get("telephone"))