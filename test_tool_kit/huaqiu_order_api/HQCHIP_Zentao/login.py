import math
import re

import jsonpath
import requests
import yaml

from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_data import Data
from huaqiu_order_api.common.my_path import yaml_file, account_yaml
from datetime import datetime
from dateutil.tz import tzutc

class ZenTaoLogin:
    def __init__(self):
        self.rss = requests.Session()
        self.json_head = {"Content-Type": "application/json"}
    def get_current_iso_utc(self):
        """
            获取当前UTC时间的ISO格式（带毫秒和Z后缀）
            返回格式：2026-01-13T11:40:56.468Z
            """
        current_time = datetime.now(tzutc())
        return current_time.isoformat(timespec='milliseconds').replace('+00:00', 'Z')
    def login(self):
        iso_time_start = self.get_current_iso_utc()
        soo_login_url = "https://auth.huaqiu.com/orgauth/login"
        soo_login_body = {"account": "yemao", "password": "Ye12345678+", "securityCode": "123"}
        soo_login_res = self.rss.post(url=soo_login_url, json=soo_login_body, headers=self.json_head)
        logger.info(f"登录完成,{soo_login_res}")
        target_login_connect_url = "https://auth.huaqiu.com/orgauth/getAuthToken?url=p.huaqiu.com"
        target_rss = self.rss.get(url=target_login_connect_url).json()
        logger.info(target_rss)
        self.token = target_rss['result']
        logger.info(f"获取重定向系统(p.huaqiu.com)的登录token:{self.token}")
        # 拿登录目标系统的cookie
        target_login_1_url = f'https://sentry.huaqiu.com/orgauth/sso/checkLogin?authToken={self.token}'
        target_login_1_res = self.rss.get(url=target_login_1_url)
        print(target_login_1_res)
        # target_login_2_url = "https://sentry.huaqiu.com/api/11/envelope/?sentry_key=04962821a6764343be6f9e28692183a3&sentry_version=7&sentry_client=sentry.javascript.vue%2F7.14.2"
        # target_login_2_body ={
        #     "sid":"c94c0b5982bd47fd9807a04bce585345","init":False,"started":iso_time_start,"timestamp":iso_time_start,"status":"ok","errors":1,"attrs":{"release":"base_org_auth_web@251231-0418","user_agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36"}}
        # target_login_2_res = self.rss.get(url=target_login_2_url)
        # print(target_login_2_res)
        return self.rss


# 使用示例
if __name__ == "__main__":
    # iso_time = ZenTaoLogin().get_current_iso_utc()
    # print(f"当前UTC时间: {iso_time}")
    ZenTaoLogin().login()