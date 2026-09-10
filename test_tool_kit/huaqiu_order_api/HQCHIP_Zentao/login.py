import math
import re

import jsonpath
import requests
import yaml
import execjs

from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_data import Data
from huaqiu_order_api.common.my_path import yaml_file, account_yaml, encryption_auth_dir
from datetime import datetime
from dateutil.tz import tzutc

class ZenTaoLogin:
    def __init__(self):
        self.rss = requests.Session()
        self.json_head = {"Content-Type": "application/json"}
        self.serialzed_enc_auth_url = "https://auth.huaqiu.com/orgauth/getKey"

    def login(self):
        soo_login_url = "https://auth.huaqiu.com/orgauth/loginHq"
        passwordEncrypt = self.encrypt("Ye123456789+")
        soo_login_body = {"account": "yemao", "password": passwordEncrypt, "securityCode": ""}
        soo_login_res = self.rss.post(url=soo_login_url, json=soo_login_body, headers=self.json_head)
        logger.info(f"登录完成,{soo_login_res}")
        target_login_connect_url = "https://auth.huaqiu.com/orgauth/getAuthToken?url=p.huaqiu.com"
        target_rss = self.rss.get(url=target_login_connect_url).json()
        logger.info(target_rss)
        self.token = target_rss['result']
        logger.info(f"获取重定向系统(p.huaqiu.com)的登录token:{self.token}")
        target_login_url = f"https://p.huaqiu.com/index.php?m=cas&f=tokenlogin&sn=3d885fa6a3f788ee8c07482bb6ccf566&authToken={self.token}"
        target_login_res = self.rss.get(url=target_login_url)
        print(target_login_res)
        return self.rss

    def encrypt(self, data):
        """密码前置js加密"""
        serialzed_enc_res = self.rss.get(url=self.serialzed_enc_auth_url).json()
        # print(serialzed_enc_base64_res)
        serialzed_enc_auth = serialzed_enc_res["result"]
        # # 读取JavaScript文件内容
        with open(encryption_auth_dir, "r", encoding="utf-8") as f:
            js_content = f.read()
        # 编译JavaScript代码
        js_runtime = execjs.compile(js_content)
        # 调用JavaScript函数
        encipherPassword = js_runtime.call("encryptWithPublicKey", serialzed_enc_auth, data)
        print(encipherPassword)
        return encipherPassword


# 使用示例
if __name__ == "__main__":
    # iso_time = ZenTaoLogin().get_current_iso_utc()
    # print(f"当前UTC时间: {iso_time}")
    ZenTaoLogin().login()