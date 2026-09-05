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


class JenkinsLogin:
    def __init__(self):
        self.rss = requests.Session()
        self.json_head = {"Content-Type": "application/json"}
        self.form_head = {"Content-Type": "application/x-www-form-urlencoded"}
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.Jenkins_URL = data['Jenkins_URL']
        with open(account_yaml, 'r', encoding='utf-8') as yamlfile:
            account = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.j_username =account["Jenkins"]["j_username"]
        self.j_password = account["Jenkins"]["j_password"]
    def jenkins_login(self):
        """jenkins登录"""
        jenkins_login_url = "{0}/j_acegj_securty_check".format(self.Jenkins_URL)
        jenkins_login_body = {"j_username": self.j_username, "j_password": self.j_password, "form": "/", "Submit": "登录"}
        jenkins_login_res = self.rss.post(url=jenkins_login_url, data=jenkins_login_body, headers=self.form_head)
        if jenkins_login_res.status_code == 200:
            print(f"登录成功")
        return self.rss