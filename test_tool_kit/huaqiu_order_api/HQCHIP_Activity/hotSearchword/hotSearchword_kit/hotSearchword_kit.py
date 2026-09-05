import json
import time
from datetime import datetime, timedelta

import jsonpath
import requests
import yaml

from huaqiu_order_api.HQCHIP_SOO.login import SOOLogin
from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_path import poseter_img_dir, discount_dir, yaml_file, account_yaml


class HotSearchWordKit:
    def __init__(self):
        self.activity_rss = requests.Session()
        self.json_head = {"Content-Type": "application/json"}
        self.file_head = {"Content-Type": "multipart/form-source_data"}
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.Activity_Center_URL = data["Activity_Center_URL"]
        with open(account_yaml, 'r', encoding='utf-8') as yamlfile:
            account = yaml.load(yamlfile, Loader=yaml.FullLoader)
    def hot_word_external(self):
        """热搜词对外接口"""
        hot_word_external_url = "{}/ecmc/activityapi/hotSearchWords/list".format(self.Activity_Center_URL)
        hot_word_external_body = {"appid": "ic", "position": 0, "size": 16}
        hot_word_external_res = self.activity_rss.post(url=hot_word_external_url, json=hot_word_external_body, headers=self.json_head).json()
        logger.info(hot_word_external_res)


if __name__ == '__main__':
    HotSearchWordKit().hot_word_external()