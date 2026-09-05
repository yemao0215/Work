import time

import execjs
import jsonpath
import requests
import yaml

from huaqiu_order_api.HQCHIP_SOO.login import SOOLogin
from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_path import yaml_file, account_yaml, encryption_auth_dir


class FATPdaLogin:
     # FAT环境
    def __init__(self):
        self.pda_rss = requests.Session()
        self.json_head = {"Content-Type": "application/json"}
        self.pda_json_head = {"Content-Type": "application/json", "User-Agent":"okhttp/3.14.9", "Connection":"keep-alive"}
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.WMS_FAT_URL = data["WMS_FAT_URL"]
        self.serialzed_enc_auth_url = data['serialzed_enc_auth_url']
        with open(account_yaml, 'r', encoding='utf-8') as yamlfile:
            account = yaml.load(yamlfile, Loader=yaml.FullLoader)
        proxy_ip = "http://192.168.18.128:3128"
        self.proxies = {"http": proxy_ip, "https": proxy_ip}
        self.warehouse_type = int(account["HQCHIP_GOODS"]["warehouse_id"])

    def pda_login(self):
        """PDA登录"""
        pda_login = '{}/wms/base/login'.format(self.WMS_FAT_URL)  # pda登录
        pda_login_body = {"account": "admin", "password": "HQ@fat@666"}
        # passwordEncrypt = self.encrypt("HQ@fat@666")
        # logger.info(f"开始执行pda登录,登录环境:{pda_login},登录账号密码:{pda_login_body}，密码加密后：{passwordEncrypt}")
        logger.info(f"开始执行pda登录,登录环境:{pda_login},登录账号密码:{pda_login_body}，")
        # pda_login_body["password"] = passwordEncrypt
        pda_login_res = self.pda_rss.post(url=pda_login, json=pda_login_body, headers=self.pda_json_head)
        logger.info(f"pda登录完成,登录结果:{pda_login_res.json()}")
        select_store_url = '{}/wms/base/pda/store/selectStore?storeCode={}'.format(self.WMS_FAT_URL, self.warehouse_type)
        select_store_res = self.pda_rss.get(url=select_store_url, headers=self.pda_json_head)  # 选择仓库
        logger.info(f"选择pda仓库:storeCode={self.warehouse_type} 东莞仓,返回结果:{select_store_res.json()}")

        return self.pda_rss
    def encrypt(self, data):
        """密码前置js加密"""
        try:
            serialzed_enc_auth_res = self.pda_rss.get(url=self.serialzed_enc_auth_url, proxies=self.proxies).json()
            # print(serialzed_enc_base64_res)
            serialzed_enc_auth = serialzed_enc_auth_res["result"]
            print(serialzed_enc_auth)
            # # 读取JavaScript文件内容
            with open(encryption_auth_dir, "r", encoding="utf-8") as f:
                js_content = f.read()
            # 编译JavaScript代码
            js_runtime = execjs.compile(js_content)
            # 调用JavaScript函数
            encipherPassword = js_runtime.call("encrypt", serialzed_enc_auth, data)
            print(encipherPassword)
            return encipherPassword
        except Exception as e:
            print(f"Error occurred：{e}")

if __name__ == '__main__':
    pda_rss = FATPdaLogin().pda_login()