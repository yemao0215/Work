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



class ProjectStockUp:
    #  项目备货
    def __init__(self, rss, goods_name=None, provider_name=None, packer=None, packer_number=None,
                 purchase_price=None, stock_number=None, stock_type=None, MTS_Rep=None, warehouse_name=None, goods_no=None):
        """
        :param goods_name:  型号
        :param provider_name:  品牌
        :param packer:  包装类型
        :param packer_number:  最小包装数量
        :param purchase_price:  采购单价
        :param stock_number:  补/备货货数量
        :param stock_type:  备货类型
        :param MTS_Rep:  补备货
        :param warehouse_name: 需求仓/交货仓
        """
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.HC2018_ADMIN_URL = data['HC2018_ADMIN_URL']
        self.goods_name = goods_name
        self.provider_name = provider_name
        self.packer = packer
        self.packer_number = packer_number
        self.purchase_price = purchase_price
        self.stock_number = stock_number
        self.stock_type = stock_type
        self.MTS_Rep = MTS_Rep
        self.warehouse_name = warehouse_name
        self.goods_no = goods_no
        self.rss = rss
        self.auth_token = getattr(Data, 'dos_auth_token')
        self.real_name = ''
        self.payload = {'origin': '1', 'content_unique': '1'}
        self.packer_type_json = {"卷装": 1, "剪切带": 2, "托盘": 3, "散装": 4, "管装": 5, "袋装": 6, "盒装": 7}
        self.files = [
  ('file', ('stockup.xlsx', open(stockup_dir, 'rb'),'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'))]
        self.headers = {"Content-Type": "application/x-www-form-urlencoded",
                        "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://www.huaqiu.com)"
                        }
        self.headers_json = {"Content-Type": "application/json; charset=UTF-8",
                             "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://www.huaqiu.com)"
                             }
        self.headers_json["Authorization"] = self.auth_token
        self.user_pwd_json = {"yemao": "12345678", "taoting": "12345678", "admin": "HQ@uat@666", "zhanngjin": "123456", "qiufm@hqchip.com": "12345678"}