import json
import time

import jsonpath
import yaml


from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_data import Data
from huaqiu_order_api.common.my_path import yaml_file


class PdaTransAttrBill:
    # 移位单
    def __init__(self, pda_rss):
        """
        :param InventoryNo  盘点单号
        """
        self.pda_rss = pda_rss
        self.json_head = {"Content-Type": "application/json"}
        self.theupper_headers = {"Content-Type": "x-www-from-urlencodeed", "User-Agent":"okhttp/3.14.9", "Connection":"keep-alive"}
        self.pda_json_head = {"Content-Type": "application/json", "User-Agent": "okhttp/3.14.9","Connection": "keep-alive"}
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.WMS_URL = "http://wms-api.elecfans.net"
        # self.transform_no = getattr(Data, 'transform_no')
        self.transform_no = "PD240801000003"

