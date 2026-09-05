import json
import math
import re

import jsonpath
import requests
import yaml

from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_path import yaml_file, account_yaml


class MiDeSearch:
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
        self.supplier_url = data["supplier"]["midegaosi"]
        self.appikey = data["supplier"]["midegaosi_appikey"]
        self.headers = {"Content-Type": "application/x-www-form-urlencoded",
                        "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://www.huaqiu.com)"
                        }
        self.headers_json = {"Content-Type": "application/json; charset=UTF-8",
                             "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://www.huaqiu.com)"
                             }
        self.keyword = keyword

    def mide_search_api(self):
        """米德高斯接口"""
        supplier_keyword_url = "{}?token={}".format(self.supplier_url, self.appikey)
        supplier_keyword_body = {"page": 1, "pageSize": 20, "titleLike": self.keyword}
        supplier_keyword_res = self.rss.post(url=supplier_keyword_url, json=supplier_keyword_body, headers=self.headers_json)
        if supplier_keyword_res.status_code == 200:
            try:
                data = json.loads(supplier_keyword_res.text.encode('utf-8'))
                self.goods_name = jsonpath.jsonpath(data, '$..title')
                if self.goods_name == False:
                    logger.info(f"获取到关键词: {self.keyword}在米德高斯官网存在库存在售的goods_name列表:空数据")
                else:
                    logger.info(f"获取goods_name列表: {self.goods_name}")
            except ValueError as e:
                logger.error(f"解析JSON数据时发生错误：{e}")
        else:
            logger.error(f"请求失败，状态码为：{supplier_keyword_res.status_code}")
        return self

    def supplier_huaqiu_sync(self):
        """华秋同步合作库存信息"""
        if self.goods_name != False:
            for i in range(len(self.goods_name)):
                self.keyword = self.goods_name[i]
                sync_url = "{}/?supplier=supplier&limit=1000&keyword={}".format(self.GO_SEARCH_URL, self.keyword)
                logger.info(sync_url)
                sync_res = self.rss.get(url=sync_url).json()
                pn2 = jsonpath.jsonpath(sync_res, '$..pn2')
                logger.info(f"获取到同步供应商列表：{pn2}")
        return self


    def hc2016_login(self):
        """HC2016后台登录"""
        login_url= "{}/Admin/Public/checkLogin/".format(self.HQCHIP_ADMIN_URL)
        self.body = {"user_name": "admin", "password": "123456"}
        logger.info(f"开始执行登录账号：{self.body}")
        self.rss.post(url=login_url, data=self.body, headers=self.headers)
        logger.info(f"登录完成")
        return self

    def hc2016_cooperative_inventory(self):
        """hc2016合作库存查询"""

        search_url = "{}/Admin/GoodsSupp/index".format(self.HQCHIP_ADMIN_URL)
        search_body = {
                "pageNum": 1,
                "numPerPage": 20,
                "PN2": "HQCHIP-SHZQ",
                "provider_name": "",
                "goods_name": self.keyword}
        search_res = self.rss.post(url=search_url, data=search_body, headers=self.headers).text
        search_res_match = re.compile('(<tr target="id" rel=")([0-9]*)').search(search_res)
        goods_id = None
        if search_res_match:
                goods_id = re.search('(<tr target="id" rel=")([0-9]*)', search_res).group(2)
                logger.info(f"获取到goods_id：{goods_id }")
        elif search_res_match == None:
                logger.info("同步失败")

        return goods_id
if __name__ == '__main__':
    MiDeSearch('111').mide_search_api().supplier_huaqiu_sync().hc2016_login().hc2016_cooperative_inventory()