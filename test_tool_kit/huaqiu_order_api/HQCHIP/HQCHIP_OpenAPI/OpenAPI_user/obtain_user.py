
import hashlib
import json
import re
import time

from urllib.parse import quote

import requests
import yaml


from huaqiu_order_api.HQCHIP.HQCHIP_OpenAPI.Openapi_signature.signature import SignAture
from huaqiu_order_api.HQCHIP_Center.order_center.get_ic_order import get_ic_order
from huaqiu_order_api.HQCHIP_ERP.login import ErpLogin
from huaqiu_order_api.HQCHIP_SOO.login import SOOLogin
from huaqiu_order_api.SSO_Reception.sso_reception import SSO_Reception

from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_data import Data

from huaqiu_order_api.common.my_path import yaml_file


class OpenAPIObtainUser:
    # 开放接口订单详情查询

    def __init__(self):
        self.hc2016_rss = requests.Session()
        self.json_head = {"Content-Type": "application/json"}
        self.form_head = {'Content-Type': 'application/x-www-form-urlencoded'}
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.app_key = data['APP_KEY']
        self.app_sec = data['APP_SEC']
        self.HQCHIP_ADMIN_URL = data['HQCHIP_ADMIN_URL']
        self.ERP_URL = data['ERP_URL']

    def hc2016_login(self):
        """HC2016后台登录"""
        login_url = "{}/Admin/Public/checkLogin/".format(self.HQCHIP_ADMIN_URL)
        self.body = {"user_name": "admin", "password": "HQ@uat@666"}
        logger.info(f"开始执行登录账号：{self.body}")
        self.hc2016_rss.post(url=login_url, data=self.body, headers=self.form_head)
        logger.info(f"登录完成")
        return self
    def openapi_user_search(self):
        self.hc2016_login()
        search_url = "{}/Admin/Openapi/index".format(self.HQCHIP_ADMIN_URL)
        search_body = {"pageNum": 1, "name": "", "user_id": "", "app_key": self.app_key}
        search_res = self.hc2016_rss.post(url=search_url, data=search_body, headers=self.form_head).text
        search_res_split = search_res.split(">编辑</a></td>")[1].split('<a href="/Admin/Openapi/screct/id/35" target="ajaxTodo" style="color: grey;">重置</a>')[0]
        user_id = re.search(r'(<td>[\d]*</td>)', search_res_split).group(1).split("<td>")[1].split("</td>")[0]
        phone = self.user_phone_obtain(user_id)
        return phone
    def user_phone_obtain(self, user_id):
        erp_rss = SOOLogin("uat-e.hqchip.com", "AuthLogin").target_login()
        user_search_url = "{}/users".format(self.ERP_URL)
        user_search_body = {"pageNum": 1, "numPerPage": 20, "keytype": "hqchip_uid", "keyword2": user_id}
        user_search_res = erp_rss.post(url=user_search_url, data=user_search_body, headers=self.form_head).text
        sid_user_id = user_search_res.split('<tr target="sid_user_id" rel="')[1].split('">')[0]
        user_phone_obtain_url = "{}/Admin/Public/viewSecrecy".format(self.ERP_URL)
        user_phone_obtain_body = {"controller": "Users", "action": "action", "model": "users", "field": "mobile", "pk": sid_user_id, "session_name": "", "dimension": 0}
        user_phone_obtain_res = erp_rss.post(url=user_phone_obtain_url, data=user_phone_obtain_body, headers=self.form_head).json()
        phone = user_phone_obtain_res["data"]
        setattr(Data, 'key_phone', phone)
        return phone
if __name__ == '__main__':
    OpenAPIObtainUser().openapi_user_search()
