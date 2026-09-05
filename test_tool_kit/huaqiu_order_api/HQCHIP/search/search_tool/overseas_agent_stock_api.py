import jsonpath
import requests
import yaml

from huaqiu_order_api.common.my_path import yaml_file


class OverseAgentStockApi:
    # 提供海外代购库存查询接口
    def __init__(self, goods_name=None, goods_no=None, brand_name=None, max_res_count=None, alias_brand_name_list=None):
        self.rss = requests.Session()
        self.headers = {"Content-Type": "application/x-www-form-urlencoded",
                        "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://www.huaqiu.com)"
                        }
        self.headers_json = {"Content-Type": "application/json; charset=UTF-8",
                             "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://www.huaqiu.com)"
                             }
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.SEARCH_URL = data['SEARCH_URL']
        self.goods_name = goods_name
        self.goods_no = goods_no
        self.brand_name = brand_name
        self.max_res_count = max_res_count
        self.alias_brand_name_list = alias_brand_name_list

    def  overse_agent_stock_search_php(self, data):
        # php接口
        pass
    def  overse_agent_stock_search_java(self):
        # java接口
        body = []
        overse_agent_stock_search_java_url = "{}/spi/search/stock/getOverseasAgentStockInfo".format(self.SEARCH_URL)
        overse_agent_stock_search_java_body = {
            "confirm_id": 0,
            "goods_name": self.goods_name,
            "goods_no": self.goods_no if self.goods_no else "",
            "brand_name": self.brand_name if self.brand_name else "",
            "number": 0,
            "alias_brand_name_list": []
        }
        if self.max_res_count not in (None,  "") and int(self.max_res_count) <= 30:
            overse_agent_stock_search_java_body["max_res_count"] = self.max_res_count
        if  self.alias_brand_name_list not in (None,  "") and "," in self.alias_brand_name_list:
            alias_brand_name_list = self.alias_brand_name_list.split(",")
            overse_agent_stock_search_java_body["alias_brand_name_list"] = alias_brand_name_list
        elif self.alias_brand_name_list not in (None,  "") and "," not in self.alias_brand_name_list:
            overse_agent_stock_search_java_body["alias_brand_name_list"] = [self.alias_brand_name_list]
        body.append(overse_agent_stock_search_java_body)
        print(body)
        overse_agent_stock_search_java_res = self.rss.post(url=overse_agent_stock_search_java_url,
                                                          json=body,
                                                          headers=self.headers_json,).json()
        # print(overse_agent_stock_search_java_res)
        stocks_info = []
        if overse_agent_stock_search_java_res['result'] != []:
            stocks_info = jsonpath.jsonpath(overse_agent_stock_search_java_res, '$..stockInfoDdo')
            print(stocks_info)
        return stocks_info
if __name__ == "__main__":
    goods_name = "CC0603KRX5R6BB106"
    goods_no = None
    brand_name = "YAGEO"
    max_res_count = 30
    alias_brand_name_list = ""
    OverseAgentStockApi(goods_name,  goods_no, brand_name, max_res_count, alias_brand_name_list).overse_agent_stock_search_java()
