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


class SqlReviewLogin:
    def __init__(self):
        self.rss = requests.Session()
        self.json_head = {"Content-Type": "application/json"}
        self.form_head = {"Content-Type": "application/x-www-form-urlencoded"}
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.Sqlreview_URL = data['Sqlreview_URL']
        with open(account_yaml, 'r', encoding='utf-8') as yamlfile:
            account = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.s_username =account["SqlReview"]["s_username"]
        self.s_password = account["SqlReview"]["s_password"]
    def sqlReview_login(self):
        """sqlreview登录"""
        sqlreview_login_url = "{0}/ldap".format(self.Sqlreview_URL)
        sqlreview_login_body = {"username": self.s_username, "password": self.s_password, "is_ldap": True, "is_oidc": False}
        sqlreview_login_res = self.rss.post(url=sqlreview_login_url, json=sqlreview_login_body, headers=self.json_head).json()
        sqlreview_token = jsonpath.jsonpath(sqlreview_login_res, "$..token")[0]
        setattr(Data, "sqlreview_token", sqlreview_token)
        return self.rss