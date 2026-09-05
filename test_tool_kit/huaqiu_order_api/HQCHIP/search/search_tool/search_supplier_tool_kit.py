import multiprocessing
import sys
import urllib
from urllib import parse
from urllib.parse import quote

import jsonpath
import requests
import yaml

from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_path import yaml_file, account_yaml


class SearchSupplierToolKit:
    def __init__(self, keyword):
        self.rss = requests.Session()
        # 设置代理ip
        proxy_ip = "http://192.168.20.6:3128"
        # 设置代理
        self.proxies = {"http": proxy_ip, "https": proxy_ip}
        self.supplier_url = "https://api.mouser.com"
        self.appikey = "76f623be-ee57-4ae3-86b6-01e54048fd18"
        self.headers = {"Content-Type": "application/x-www-form-urlencoded",
                        "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://www.huaqiu.com)"
                        }
        self.headers_json = {"Content-Type": "application/json; charset=UTF-8",
                             "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://www.huaqiu.com)"
                             }
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.HQCHIP_URL = data['HQCHIP_URL']
        self.SEARCH_URL = data['SEARCH_URL']
        self.GO_SEARCH_URL = data['GO_SEARCH_URL']
        with open(account_yaml, 'r', encoding='utf-8') as yamlfile:
            account = yaml.load(yamlfile, Loader=yaml.FullLoader)
        # self.keyword = "0402 191KΩ 1安"
        self.keyword = keyword
        self.goods_id = [1017426139]

    def query_url_arguments(self, data):
        """将body参数转换成可拼接至url的参数"""
        lt = []
        for k, v in data.items():
            lt.append(k + '=' + quote(str(v)))
        # 这个是在for循环外面的，就是将列表的元素之间用用&符号连接起来
        query_string = '&'.join(lt)
        return query_string
    def supplier_search_data(self):
        search_v4_url = "https://uat-www.hqchip.com/betasearch"
        keyword_ud = parse.quote(self.keyword)
        logger.info(f"关键词编码为{keyword_ud}")
        search_goods_interior_port_url = "{}/{}.html?debug_self_search=1&showDsl=true&recordDsl=true".format(search_v4_url, keyword_ud)
        interior_port_res = self.rss.get(url=search_goods_interior_port_url, headers=self.headers).json()
        self.search_interior_url = interior_port_res["$url"]
        self.search_interior_params = interior_port_res["$params"]
        print(type(self.search_interior_params))
        # logger.info(f"执行结果为{interior_port_res}")
        return self
    def search_goods_log_push_v4(self):
        """hqchip_search日志实时推送"""
        # keyword_ud = parse.quote(self.keyword)
        keyword_ud = urllib.parse.quote(str(self.keyword).replace(' ', '+'), safe="+")
        logger.info(f"关键词编码为{keyword_ud}")
        # search_goods_url = "{}/search/v4/self?offset=0&limit=30&keyword={}&stockNum=-1&priceStart=0&priceEnd=0&orderType=0&sortType=1&userId=0&showDsl=true&onlySpotGoods=0".format(self.SEARCH_URL,keyword_ud)
        search_goods_url = "{}/search/v4/single?k=10&keyword={}&esKeyword={}&limit=20&debug_self_search=1&showDsl=true&recordDsl=true".format(self.SEARCH_URL, keyword_ud, keyword_ud)
        search_goods_res = self.rss.get(url=search_goods_url).json()
        # logger.info(search_goods_res)
        if "purchasingList" in search_goods_res["result"]:
            if search_goods_res["result"]["purchasingList"] != None:
                    logger.info("存在10开头的合作商库存的数据")
                    logger.info(search_goods_res["result"]["purchasingList"])
                    sys.exit(0)

        return self

    def mian(self):
        self.search_goods_log_push_v4()
if __name__ == '__main__':
    for i in range(2000):
        jobs = []
        for ii in range(5):
            p = multiprocessing.Process(target=SearchSupplierToolKit("searchV4.5.2").mian())
            jobs.append(p)
            p.start()

    # print(participlelist)