import json
import time
from datetime import datetime, timedelta

import jsonpath
import requests
import yaml

from huaqiu_order_api.HQCHIP_SOO.login import SOOLogin
from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_path import poseter_img_dir, discount_dir, yaml_file, account_yaml


class HotSearchWord:
    def __init__(self):
        self.rss = requests.Session()
        self.json_head = {"Content-Type": "application/json"}
        self.file_head = {"Content-Type": "multipart/form-source_data"}
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.PRODUCT_DETAIL_URL = data["PRODUCT_DETAIL_URL"]
        with open(account_yaml, 'r', encoding='utf-8') as yamlfile:
            account = yaml.load(yamlfile, Loader=yaml.FullLoader)
    def hot_word_external(self):
        """热搜词对接接口"""
        hot_word_external_url = "{}/api/v3/switch/getHotGoodsName".format(self.PRODUCT_DETAIL_URL)
        logger.info(hot_word_external_url)
        hot_word_external_body = {"flushCache": True, "position": 0, "size": 16}
        hot_word_external_res = self.rss.post(url=hot_word_external_url, json=hot_word_external_body, headers=self.json_head)

        if hot_word_external_res.status_code == 200:
            logger.info(hot_word_external_res.json())
            return hot_word_external_res.json()["result"]
        else:
            logger.info(hot_word_external_res.text)
            return 404
if __name__ == '__main__':
    HotSearchWord().hot_word_external()