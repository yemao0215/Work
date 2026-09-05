import math
import re

import jsonpath
import requests
import yaml

from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_path import yaml_file, account_yaml


class MouserSearchCNY:
    def __init__(self):
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
        self.supplier_url = data["supplier"]["mouser"]
        self.appikey = data["supplier"]["mouser_appikey"]
        self.headers = {"Content-Type": "application/x-www-form-urlencoded",
                        "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://www.huaqiu.com)"
                        }
        self.headers_json = {"Content-Type": "application/json; charset=UTF-8",
                             "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://www.huaqiu.com)"
                             }
        self.keyword = "0603WAF2491T5E"

    def mouser_search_api(self):
        """mouser接口"""
        supplier_keyword_url = "{}/api/v1/search/keyword?apiKey={}".format(self.supplier_url, self.appikey)
        supplier_keyword_body = {"SearchByKeywordRequest": {
            "keyword": self.keyword,
            "records": 10,
            "startingRecord": 0,
            "searchOptions": "0",
            "searchWithYourSignUpLanguage": "ZH"}}

        supplier_keyword_res = self.rss.post(url=supplier_keyword_url, json=supplier_keyword_body, headers=self.headers_json).json()
        self.ManufacturerPartNumber = jsonpath.jsonpath(supplier_keyword_res, "$..ManufacturerPartNumber")
        self.AvailabilityInStock = jsonpath.jsonpath(supplier_keyword_res, "$..AvailabilityInStock")
        logger.info(f"返回型号列表：{self.ManufacturerPartNumber}")
        PartsInfo = supplier_keyword_res["SearchResults"]["Parts"]
        for i in range(len(PartsInfo)):
            Parts_json = PartsInfo[i]
            # 获取字典键值（名称）并且以list汇总输出
            json_key = list(Parts_json.keys())
            if "RestrictionMessage" in json_key:
                RestrictionMessage =  Parts_json["RestrictionMessage"]

        return self

    def mouser_huaqiu_sync(self):
        """华秋同步mouser库存信息"""
        sync_url = "{}/supplier=mouser&limit=1000&keyword={}".format(self.GO_SEARCH_URL, self.keyword)
        sync_res = self.rss.get(url=sync_url).json()
        logger.info(f"执行结果：{sync_res }")
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
        for i in range(len(self.ManufacturerPartNumber)):
            AvailabilityInStock = self.AvailabilityInStock
            search_url = "{}/Admin/GoodsSupp/index".format(self.HQCHIP_ADMIN_URL)
            search_body = {
                "pageNum": 1,
                "numPerPage": 20,
                "PN2": "HQCHIP-mouser",
                "provider_name": "",
                "goods_name": self.ManufacturerPartNumber[i]}
            search_res = self.rss.post(url=search_url, data=search_body, headers=self.headers).text
            search_res_match = re.compile('(<tr target="id" rel=")([0-9]*)').search(search_res)
            goods_id = ''
            if search_res_match:
                goods_id = re.search('(<tr target="id" rel=")([0-9]*)', search_res).group(2)
                logger.info(f"获取到goods_id：{goods_id }")
            elif search_res_match == None:
                logger.info("同步失败")
            mongo_info_url = "{}/Admin/GooSupp/mongoinfo/goods_id/{}".format(self.HQCHIP_ADMIN_URL, goods_id)
            mongo_info_res = self.rss.get(url=mongo_info_url).text
            status = mongo_info_res.split("[&quot;error&&quot;] =&gt; int(")[1].split(")")[0]
            if status == "0":
               logger.info(f"目前在您所在地址销售该商品：{self.ManufacturerPartNumber[i]}，此时库存id：{goods_id}")
               # 库存获取同步过来的库存量和第一阶梯的人民币成本价、美元销售价、人民币销售价
               stock_number = mongo_info_res.split("[&quot;Stock&&quot;] =&gt; array(")[1].split("[0] =&gt; int(")[1].split(")")[0]
               rmb_cost_price = mongo_info_res.split("[0] =&gt; array(")[1].split("[3] =&gt; float(")[1].split(")")[0]
               rmb_Selling_price = mongo_info_res.split("[0] =&gt; array(")[1].split("[2] =&gt; float(")[1].split(")")[0]
               us_Selling_price = mongo_info_res.split("[0] =&gt; array(")[1].split("[1] =&gt; float(")[1].split(")")[0]
               logger.info(f"获取同步过来的库存量: {stock_number}和第一阶梯的人民币成本价：{rmb_cost_price}、美元销售价：{us_Selling_price}、人民币销售价：{rmb_Selling_price}")
               # 价格系数：1.055，关税：1.007，增值税：1.13，汇率：查询sql-select value from ecs_shop_config where code = "usd_exchange_rate"
               rmb_Selling_price_compute = float(rmb_cost_price) * 1.055
               us_Selling_price_compute = (float(rmb_cost_price) * 1.055) / (1.007*1.13*6.170000)
               if int(stock_number) == int(AvailabilityInStock):
                   logger.info("库存获取同步正常")
                   if round(rmb_Selling_price_compute, 4) == float(rmb_Selling_price):
                       logger.info("人民币价格验算正常")
                       if math.ceil(us_Selling_price_compute * 10000) / 10000 == float(us_Selling_price):
                           logger.info("美元价格验算正常")
            elif status == "4003":
                logger.info(f"目前在您所在地址不销售该商品：{self.ManufacturerPartNumber[i]}，此时库存id：{goods_id}")
            continue
        return self
if __name__ == '__main__':
    MouserSearchCNY().mouser_search_api().mouser_huaqiu_sync()