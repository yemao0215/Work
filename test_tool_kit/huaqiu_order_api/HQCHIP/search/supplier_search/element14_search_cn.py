import json
import math
import re
from urllib.parse import quote

import jsonpath
import requests
import yaml

from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_path import yaml_file, account_yaml


class Element14Search:
    def __init__(self, keyword):
        self.rss = requests.Session()
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.HQCHIP_URL = data['HQCHIP_URL']
        self.HQCHIP_ADMIN_URL = data['HQCHIP_ADMIN_URL']
        self.GO_SEARCH_URL = data['GO_SEARCH_URL']
        # 设置代理ip
        proxy_ip = data["supplier"]["proxy_ip"]
        # 设置代理
        self.proxies = {"http": proxy_ip, "https": proxy_ip}
        self.supplier_url = data["supplier"]["element14_url"]
        self.appikey = data["supplier"]["element14_appikey"]
        self.headers = {"Referer": "https://cn.element14.com/",
                        "Host": "api.element14.com",
                        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/apng,*/*;q=0.8",
                         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.26 Safari/537.36",
                        "upgrade-insecure-requests": "1"}
        self.keyword = keyword

    def query_url_arguments(self, data, type=None):
        """将body参数转换成可拼接至url的参数"""
        lt = []
        for k, v in data.items():
            if type != None:
                lt.append(f"{k}={v}")
            else:
                lt.append(k + '=' + quote(str(v)))
        # 这个是在for循环外面的，就是将列表的元素之间用用&符号连接起来
        query_string = '&'.join(lt)
        return query_string
    def element14_search_api(self):
        """Element14大陆接口"""
        supplier_keyword_url = "{}/catalog/products".format(self.supplier_url)
        supplier_keyword_body = {"term": f"any:{self.keyword}", "storeInfo.id": "cn.element14.com", "resultsSettings.offset": 0, "resultsSettings.numberOfResults": 20,
                                 "resultsSettings.filters": "rohsCompliat,2CinStock", "resultsSettings.responseGroup": "large",
                                 "callInfo.responseDataFormat": "json", "callinfo.apiKey": self.appikey
                                 }
        supplier_keyword_body_pin = self.query_url_arguments(supplier_keyword_body, 1)
        supplier_keyword_url_new = supplier_keyword_url + "?" + supplier_keyword_body_pin
        print(supplier_keyword_url_new)
        supplier_keyword_res = self.rss.get(url=supplier_keyword_url_new, headers=self.headers).json()
        # print(supplier_keyword_res)
        products = supplier_keyword_res["keywordSearchReturn"]['products']
        return products
if __name__ == '__main__':
    Element14Search('111').element14_search_api()