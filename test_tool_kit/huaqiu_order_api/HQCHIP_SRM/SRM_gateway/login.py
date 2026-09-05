import time

import jsonpath
import requests
from common.loguru_logger import logger



class GatewayUserLogin:
    # 门户登录
    def __init__(self, username):
        self.gateway_rss = requests.Session()
        self.json_head = {"Content-Type": "application/json"}
        self.file_head = {"Content-Type": "multipart/form-source_data"}
        self.username = username


    def gateway_login(self):
        """门户登录"""
        login_url = "https://uat-partner.huaqiu.com/partner/PartnerUserAdmin/doLogin"
        login_body = {"userName": self.username, "password": "666888"}
        login_res = self.gateway_rss.post(url=login_url, json=login_body, headers=self.json_head).json()
        logger.info(login_res)
        return self.gateway_rss


if __name__ == '__main__':
    GatewayUserLogin("hqchip101221").gateway_login()