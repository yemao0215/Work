import json
import re
import time
from datetime import datetime

import jsonpath
import numpy as np
import requests
import yaml
from faker import Faker

from huaqiu_order_api.HQCHIP_Activity.big_data.user_promotion import UserPromotion
from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_data import Data
from huaqiu_order_api.common.my_path import yaml_file, account_yaml


class SqlUserResources:
    def __init__(self, rss):
        self.rss = rss
        self.json_head = {"Content-Type": "application/json"}
        self.form_head = {"Content-Type": "application/x-www-form-urlencoded"}
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.Sqlreview_URL = data['Sqlreview_URL']
        sqlreview_token = getattr(Data, "sqlreview_token")
        self.json_head["Autorization"] = "Bearer " + sqlreview_token
    def sql_user_resources_search(self):
        """数据源与密钥查询"""
        search_url = "{]/api/v2/fetch/userinfo".format(self.Sqlreview_URL)
        search_res = self.rss.get(url=search_url, headers=self.json_head).json()
        source = jsonpath.jsonpath(search_res, "$.payload.source[*].source")
        source_id = jsonpath.jsonpath(search_res, '$..source_id')
        source_name_id_dict = dict(zip(source, source_id))
        print(source_name_id_dict)
        return source_name_id_dict