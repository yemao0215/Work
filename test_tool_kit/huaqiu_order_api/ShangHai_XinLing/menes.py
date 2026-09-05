import json
import re
import time
from pipes import quote

import jsonpath
import requests
import yaml
from bs4 import BeautifulSoup

from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_data import Data
from huaqiu_order_api.common.my_path import yaml_file, account_yaml
class Means:

    def __init__(self):

        self.rss = requests.Session()
        self.json_head = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
            'Access-key': ''
        }
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.ShangHai_XinLing_reception_URL = data["ShangHai_XinLing_reception_URL"]
        self.HC2018_ADMIN_URL = data['HC2018_ADMIN_URL']
        self.erp_goods_sn = getattr(Data, 'erp_goods_sn')
        # self.erp_goods_sn = ['G50021345']

    def query_url_arguments(self, data):
        """将body参数转换成可拼接至url的参数"""
        lt = []
        for k, v in data.items():
            lt.append(k + '=' + quote(str(v)))
        # 这个是在for循环外面的，就是将列表的元素之间用用&符号连接起来
        query_string = '&'.join(lt)
        return query_string
    def menes_search(self):
        """商品查询"""
        if "uat" in self.HC2018_ADMIN_URL:
            self.json_head['Access-key'] = '904055d31de96b84b0c99f909cfc7f68'
        else:
            self.json_head['Access-key'] = ''
        xl_search_url = "{}/openapi/products/query/detail".format(self.ShangHai_XinLing_reception_URL)
        mpn = ''
        mfg = ''
        erp_goods_sn = ''
        if self.json_head['Access-key'] != '':
            if isinstance(self.erp_goods_sn, list):

                for i in self.erp_goods_sn:
                    data = {
                        "gCode": i
                    }
                    xl_search_body = self.query_url_arguments(data)
                    xl_search_new_url = "{}?{}".format(xl_search_url, xl_search_body)
                    # print(xl_search_new_url)
                    xl_search_res = self.rss.get(url=xl_search_new_url, headers=self.json_head).json()
                    # print(xl_search_res)
                    if xl_search_res['result']['detailInfoCn']!= None:
                        print("商品查询成功")
                        mpn = xl_search_res['result']['detailInfoCn']['mpn']
                        mfg = xl_search_res['result']['detailInfoCn']['mfg']
                        logger.info("芯灵前台【fdatasheets】商品查询成功，G编码为{}的型号名称为{}，品牌：{}".format(i, mpn, mfg))
                        erp_goods_sn = i
                        break
            else:
                data = {
                    "gCode": self.erp_goods_sn
                }
                xl_search_body = self.query_url_arguments(data)
                xl_search_new_url = "{}?{}".format(xl_search_url, xl_search_body)
                xl_search_res = self.rss.get(url=xl_search_new_url, headers=self.json_head).json()
                # print(xl_search_res)
                if xl_search_res['result']['detailInfoCn'] != None:
                    print("商品查询成功")
                    mpn = xl_search_res['result']['detailInfoCn']['mpn']
                    mfg = xl_search_res['result']['detailInfoCn']['mfg']
                    logger.info("芯灵前台【fdatasheets】商品查询成功，G编码为{}的型号名称为{}，品牌：{}".format(self.erp_goods_sn, mpn, mfg))
                    erp_goods_sn = self.erp_goods_sn
        return mpn, mfg, erp_goods_sn


if __name__ == '__main__':
    rss = Means().menes_search()
