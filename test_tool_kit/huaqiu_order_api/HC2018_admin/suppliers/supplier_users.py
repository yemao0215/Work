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
class SupplierUsers:
    # 合作商
    def __init__(self, rss, consign_sn=None, goods_name=None, supplier_sn=None):
        pass