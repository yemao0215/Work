import json
import re
import time

import jsonpath
from xpinyin import Pinyin
from huaqiu_order_api.common.loguru_logger import logger
import requests

from huaqiu_order_api.common.my_path import stockup_dir

from huaqiu_order_api.common.my_data import Data


class Es:
    def __init__(self, keyword,goodsId):
        """
        :param phone:  登录账号
        :param psw:  登录密码
        :param goods_id:  购买的产品id
        """
        self.keyword = keyword
        self.goodsId = goodsId

        self.rss = requests.Session()
        self.from_headers = {"Content-Type": "application/x-www-form-urlencoded"}

    def es_search_goodsId(self):
        """查询ES数据接口，根据库存ID 自营"""
        # search_url = f"https://uat-search.hqchip.com/searchSelf/v1/queryEsByStockId"
        search_url = f"https://uat-search.hqchip.com/searchSelf/v1/queryEsByStockId?stockId={self.goodsId}"
        # search_body = {"stockId": self.goodsId}
        # search_res = self.rss.get(url=search_url, source_data=search_body, headers=self.from_headers).json()
        search_res = self.rss.get(url=search_url).json()
        logger.info(search_res)
        return self

    def es_search_keyword(self):
        """关键词分词"""
        search_url = f"https://uat-search.hqchip.com/searchSelf/v1/getQueryDsl?keyword={self.keyword}"
        search_res = self.rss.get(url=search_url).json()
        logger.info(search_res)
        return self

if __name__ == '__main__':
    Es("ss8050", 2500367623).es_search_goodsId().es_search_keyword()