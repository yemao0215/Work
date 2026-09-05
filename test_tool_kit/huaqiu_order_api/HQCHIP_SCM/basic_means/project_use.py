import json
import re
import time

import jsonpath
import openpyxl
import pandas as pd
import yaml
from openpyxl.cell import cell
from xpinyin import Pinyin

from huaqiu_order_api.HC2018_admin.dgk_goods_means.dgk_goods_means import GoodsMeans
from huaqiu_order_api.HC2018_admin.dgk_goods_means.stay_perfect_means import StayPerfectMeans
from huaqiu_order_api.HC2018_admin.login.login import Login
from huaqiu_order_api.HC2018_admin.work_sheet.work_sheet import WorkSheet
from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_data import Data
from huaqiu_order_api.common.my_path import stockup_dir, yaml_file, account_yaml
from huaqiu_order_api.common.yaml_handler import write_yaml



class ProjectUse:
    #  项目客户
    def __init__(self, rss, uid=None):
        """
        :param uid:  华秋UID
        """
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.SCM_URL = data['SCM_URL']
        self.headers = {"Content-Type": "application/x-www-form-urlencoded",
                        "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://www.huaqiu.com)"
                        }
        self.headers_json = {"Content-Type": "application/json; charset=UTF-8",
                             "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://www.huaqiu.com)"
                             }
        self.rss = rss
        self.uid = uid
    def project_use(self):
        # 默认生产厂区
        out_source_url = "{}/hqScm/outsourceSupplier/getOutSourceSupplierList".format(self.SCM_URL)
        out_source_body = {"auditStatus": 3}
        out_source_res = self.rss.post(url=out_source_url, data=out_source_body, headers=self.headers).json()

        # 根据华秋UID查询用户信息
        uid_search_url = "{}/hqScm/order/getCustomerInfos?unionid={}".format(self.SCM_URL, self.uid)
        uid_search_res = self.rss.get(url=uid_search_url, headers=self.headers).json()

        # 获取项目经理、订单销售、销售客服、项目接洽人、SMT报价工程师、SMT工艺工程师、BOM工程师
        # /hqScm/projectManage/queryEmps
        project_user_search_url = "{}/hqScm/projectManage/queryEmps".format(self.SCM_URL)
        project_user_search_body = {"name": "叶茂", "type": 7}


