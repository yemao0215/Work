import base64
import collections
import hashlib
import hmac
import json
import math
import re
from urllib.parse import quote, urlencode

import jsonpath
import requests
import yaml

from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_path import yaml_file, account_yaml


class TmeSearch:
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
        self.supplier_url = data["supplier"]["tme_url"]
        self.appikey = data["supplier"]["tme_appikey"]
        self.token = data["supplier"]["tme_token"]
        self.keyword = keyword
        self.headers = {
            "Referer": "https://www.tme.eu/en/",
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.26 Safari/537.36"
        }
    def query_url_arguments(self, data):
        """将body参数转换成可拼接至url的参数"""
        lt = []
        # Step 1: 对字典的键按字母顺序排序
        sorted_keys = sorted(data.keys())
        for k in sorted_keys:
            lt.append(k + '=' + quote(str(data[k])))
        # 这个是在for循环外面的，就是将列表的元素之间用用&符号连接起来
        query_string = '&'.join(lt)
        return query_string
    def query_url_arguments_array(self, data):
        """将body参数转换成可拼接至url的参数 含有数组的"""
        data = collections.OrderedDict(sorted(data.items()))
        return urlencode(data, '')

    def get_sign(self, mode, url, data):
        """加密"""
        # 字典 data 中以 'SymbolList[' 开头的键有多少个
        if sum(1 for key in data.keys() if key.count('SymbolList[')) >= 2:
            data['SymbolList'] = data['SymbolList'][0]
            query_string = self.query_url_arguments_array(data)
        else:
            query_string = self.query_url_arguments(data)
        sginStr = str(mode.upper()) + '&' + quote(url, safe='').replace(" ", "%20") + '&' + quote(query_string)
        ApiSignature = base64.b64encode(hmac.new(self.appikey.encode(), sginStr.encode(), hashlib.sha1).digest()).decode()
        print(ApiSignature)
        return ApiSignature
    def goods_search(self):
        """型号查询"""
        goods_search_url = "{}/Products/Search.json".format(self.supplier_url)
        goods_search_body = {
            "Token": self.token,
            "Country": "CN",
            "Language": "ZH",
            "SearchPlain": self.keyword
        }
        ApiSignature = self.get_sign('POST', goods_search_url, goods_search_body)
        goods_search_body['ApiSignature'] = ApiSignature
        res = self.rss.post(goods_search_url, data=goods_search_body, proxies=self.proxies, headers=self.headers).json()
        # res = self.rss.post(goods_search_url, data=goods_search_body, headers=self.headers).json()
        SymbolList = jsonpath.jsonpath(res, '$..SymbolList')
        return SymbolList
    def goods_price_search(self, SymbolList):
        """价格查询"""
        goods_price_search_url = "{}/Products/GetPricesAndStocks.json".format(self.supplier_url)
        goods_price_search_body = {
            "Token": self.token,
            "Country": "CN",
            "Language": "ZH"
        }
        # SymbolList列表以10个值进行切割组成新列表
        split_list = [SymbolList[i:i + 10] for i in range(0, len(SymbolList), 10)]
        for SymbolList in split_list:
            for index, value in enumerate(SymbolList):
                key_name = f'SymbolList[{index}]'
                goods_price_search_body[key_name] = value
            ApiSignature = self.get_sign('POST', goods_price_search_url, goods_price_search_body)
            goods_price_search_body['ApiSignature'] = ApiSignature
            res = self.rss.post(goods_price_search_url, data=goods_price_search_body, proxies=self.proxies, headers=self.headers)
            print(json.loads(res.content.decode(res.content.decode().replace("'", '"'))))
        return self
    def mian_tme_goods_price_search(self):
        """主函数"""
        SymbolList = self.goods_search()
        self.goods_price_search(SymbolList)
if __name__ == '__main__':
    TmeSearch("0603WAF2491T5E").mian_tme_goods_price_search()
