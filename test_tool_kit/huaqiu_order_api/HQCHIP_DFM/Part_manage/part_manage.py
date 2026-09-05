import hashlib
import math
import time
import datetime

import pandas
import requests
import yaml

from huaqiu_order_api.HC2018_admin.login.login import Login

from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_path import yaml_file, goodsid_dir


class PartManage:
    def __init__(self, rss):
        self.rss = rss
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.DFM_URL = data['DFM_URL']
        self.headers_urlencoded = {"Content-Type": "application/x-www-form-urlencoded"}
        self.headers_json = {"Content-Type": "application/json;charset=UTF-8"}


    def part_search(self):
        url = "{}/Chip/index".format(self.DFM_URL)
        body = {"pageNum": 1, "page_size": 15, "goods_type": 1, "is_first_pin": -1}
        search_res = self.rss.post(url=url, data=body, headers=self.headers_urlencoded).text
        logger.info(search_res)
        return self

if __name__ == '__main__':
    from huaqiu_order_api.HQCHIP_SOO.login import SOOLogin
    target_rss = SOOLogin("uat-dfm.elecfans.com","portal").target_login()
    PartManage(target_rss).part_search()