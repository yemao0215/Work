import json
from datetime import datetime

import jsonpath
import requests
import yaml
from faker import Faker
from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_path import yaml_file, account_yaml


class GoodsNameSearch:
    # 开放接口查询型号

    def __init__(self, environment_type=None, version_type=None):
        self.openapi_rss = requests.Session()
        self.json_head = {"Content-Type": "application/json"}
        self.form_head = {'User-Agent': 'HQCHIP OpenAPI Python-SDK/1.0', "X-Request-Version": '1.0'}
        self.out_order_no = datetime.now().strftime("%Y%m%d") + "000" + str(Faker("zh_CN").random_int(1, 10000))
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.app_key = data['APP_KEY']
        self.app_sec = data['APP_SEC']
        self.url = data['OPENAPI_UAT_URL']
        if environment_type == "pro":
            self.url = data['OPENAPI_PRO_URL']
        self.GoodsName = data['APIGoodsName']
        self.GoodsType = data['APIGoodsType']
        self.gcode = data['APIGcode']
        self.phone = data['APIPhone']
        self.center_java_url = data['center_java_url']
        with open(account_yaml, 'r', encoding='utf-8') as yamlfile:
            account = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.phone = account["PassPort"]["phone"]
        self.goods_id =account["HQCHIP_GOODS"]["goods_id"]
        self.numder = account["HQCHIP_GOODS"]["number"]
        self.vat_type = account["HQCHIP_GOODS"]["vat_type"]
        # self.vat_sub_type = account["HQCHIP_GOODS"]["vat_sub_type"]
        # self.GoodsName = "RC0603JR-074K7L"
        # self.goods_id = '2500015356'
        self.version_type = version_type
        self.version = '/v2' if int(self.version_type) == 2 else ''

    def goods_search(self):
        """型号search"""
        openapi_goods_search_url = '{}{}/goods/search/'.format(self.url, self.version)
        logger.info("请求url：{}".format(openapi_goods_search_url))
        openapi_goods_search_body = {"app_key": self.app_key, "keyword": self.GoodsName}
        logger.info("请求参数body：{}".format(openapi_goods_search_body))
        openapi_goods_search_res = self.openapi_rss.get(url=openapi_goods_search_url, params=openapi_goods_search_body,
                                                      headers=self.form_head).json()
        logger.info("请求响应结果：{}".format(openapi_goods_search_res))
        return openapi_goods_search_res

    def goods_query(self):
        """型号query"""
        openapi_goods_query_url = '{}{}/goods/query/'.format(self.url, self.version)
        logger.info("请求url：{}".format(openapi_goods_query_url))
        openapi_goods_query_body = {"app_key": self.app_key, "goods_name": self.GoodsName}
        logger.info("请求参数body：{}".format(openapi_goods_query_body))
        openapi_goods_query_res = self.openapi_rss.get(url=openapi_goods_query_url, params=openapi_goods_query_body,
                                                        headers=self.form_head).json()
        logger.info("请求响应结果：{}".format(openapi_goods_query_res))
        return openapi_goods_query_res
    def goods_querybygcode(self):
        """型号query"""
        openapi_goods_querybygcode_url = '{}{}/goods/querybygcode/'.format(self.url, self.version)
        logger.info("请求url：{}".format(openapi_goods_querybygcode_url))
        openapi_goods_querybygcode_body = {"app_key": self.app_key, "gcode": self.gcode}
        logger.info("请求参数body：{}".format(openapi_goods_querybygcode_body))
        openapi_goods_querybygcode_res = self.openapi_rss.get(url=openapi_goods_querybygcode_url, params=openapi_goods_querybygcode_body,
                                                        headers=self.form_head).json()
        logger.info("请求响应结果：{}".format(openapi_goods_querybygcode_res))
        return openapi_goods_querybygcode_res
    def goods_detail(self, goods_id=None):
        """型号detail"""
        if goods_id != None:
            self.goods_id = goods_id
        openapi_goods_detail_url = '{}{}/goods/detail/'.format(self.url, self.version)
        logger.info("请求url：{}".format(openapi_goods_detail_url))
        openapi_goods_detail_body = {"app_key": self.app_key, "goods_id": self.goods_id}
        logger.info("请求参数body：{}".format(openapi_goods_detail_body))
        openapi_goods_detail_res = self.openapi_rss.get(url=openapi_goods_detail_url, params=openapi_goods_detail_body,
                                                       headers=self.form_head).json()
        logger.info("请求响应结果：{}".format(openapi_goods_detail_res))
        return openapi_goods_detail_res
    def goods_stock_detail(self, goods_id=None):
        if goods_id != None:
            self.goods_id = [goods_id]
        else:
            self.goods_id = [self.goods_id]
        openapi_goods_stock_detail_url = "{}{}/goods/stock/query/?app_key={}".format(self.url, self.version, self.app_key)
        logger.info("请求url：{}".format(openapi_goods_stock_detail_url))
        openapi_goods_stock_detail_body = {
                # "app_key": self.app_key,
                "goods_id_list": self.goods_id
        }
        logger.info("请求参数body：{}".format(openapi_goods_stock_detail_body))
        openapi_goods_stock_detail_res = self.openapi_rss.post(url=openapi_goods_stock_detail_url, json=openapi_goods_stock_detail_body,
                                                       headers=self.json_head).json()
        logger.info("请求响应结果：{}".format(openapi_goods_stock_detail_res))
        return openapi_goods_stock_detail_res
    def goods_list(self):
        """型号list"""
        openapi_goods_list_url = '{}{}/goods/list/'.format(self.url, self.version)
        logger.info("请求url：{}".format(openapi_goods_list_url))
        openapi_goods_list_body = {"app_key": self.app_key, "keyword": self.GoodsName}
        logger.info("请求参数body：{}".format(openapi_goods_list_body))
        openapi_goods_list_res = self.openapi_rss.get(url=openapi_goods_list_url, params=openapi_goods_list_body,
                                                      headers=self.form_head).json()
        logger.info("请求响应结果：{}".format(openapi_goods_list_res))
        return openapi_goods_list_res

    def goods_mquery(self):
        """型号mquery"""
        openapi_goods_mquery_url = '{}{}/goods/mquery/?app_key={}'.format(self.url, self.version, self.app_key)
        logger.info("请求url：{}".format(openapi_goods_mquery_url))
        data = []
        goods_list = self.GoodsName.split(",")
        for i in range(len(goods_list)):
            data.append({"mpn": goods_list[i], "qty": 1})
        openapi_goods_mquery_body = data
        logger.info("请求参数body：{}".format(openapi_goods_mquery_body))
        openapi_goods_mquery_res = self.openapi_rss.post(url=openapi_goods_mquery_url,  json=openapi_goods_mquery_body, headers=self.form_head).json()
        logger.info("请求响应结果：{}".format(openapi_goods_mquery_res))
        return openapi_goods_mquery_res
    def goods_query_best(self):
        """型号query_best"""
        openapi_goods_query_best_url = '{}{}/goods/query/best'.format(self.url, self.version)
        logger.info("请求url：{}".format(openapi_goods_query_best_url))
        openapi_goods_query_best_body = {"app_key": self.app_key, "goods_name": self.GoodsName}
        logger.info("请求参数body：{}".format(openapi_goods_query_best_body))
        openapi_goods_query_best_res = self.openapi_rss.get(url=openapi_goods_query_best_url, params=openapi_goods_query_best_body,
                                                      headers=self.form_head).json()
        logger.info("请求响应结果：{}".format(openapi_goods_query_best_res))
        return openapi_goods_query_best_res
    def goods_product(self):
        openapi_goods_product_url = "{}{}/goods/product/info/?app_key={}".format(self.url, self.version, self.app_key)
        logger.info("请求url：{}".format(openapi_goods_product_url))
        if not isinstance(self.gcode, list):
            goods_gcode = [self.gcode]
        else:
            goods_gcode = self.gcode
        openapi_goods_product_body = {"gcode_list": goods_gcode}
        logger.info("请求参数body：{}".format(openapi_goods_product_body))
        openapi_goods_product_res = self.openapi_rss.post(url=openapi_goods_product_url, json=openapi_goods_product_body,
                                                        headers=self.json_head).json()
        logger.info("请求响应结果：{}".format(json.dumps(openapi_goods_product_res, ensure_ascii=False).replace("'", '"')))
        return openapi_goods_product_res
    def mian_goods_search(self):
        openapi_goods_search_res = self.goods_search()
        openapi_goods_query_res = self.goods_query()
        if self.gcode != '':
            openapi_goods_querybygcode_res = self.goods_querybygcode()
            openapi_goods_product_res = self.goods_product()
        else:
            openapi_goods_querybygcode_res = None
            openapi_goods_product_res = None
        goods_id_lst = jsonpath.jsonpath(openapi_goods_query_res, "$..goods_id")
        print(goods_id_lst)
        openapi_goods_detail_res = None
        openapi_goods_stock_detail_res = None
        if self.goods_id != '':
            openapi_goods_detail_res = self.goods_detail()
            openapi_goods_stock_detail_res = self.goods_stock_detail()
        if self.goods_id == '' and goods_id_lst != False:
            data_json = []
            for i in range(len(goods_id_lst)):
                openapi_goods_detail_res = self.goods_detail(goods_id=goods_id_lst[i])
                data = jsonpath.jsonpath(openapi_goods_detail_res, "$..data")
                data_goods_id_json = {goods_id_lst[i]: data}
                data_json.append(data_goods_id_json)
                openapi_goods_detail_res['data'] = data_json
            openapi_goods_detail_res["artificial_add_message"] = "当goods_id不传时，openapi_goods_detail_res里面的data为openapi_goods_query_res的goods_id集合信息，非实际接口请求的"
            openapi_goods_stock_detail_res["artificial_add_message"] = "当goods_id不传时，openapi_goods_stock_detail_res里面的data为openapi_goods_query_res的goods_id集合信息，非实际接口请求的"
        openapi_goods_list_res = self.goods_list()
        openapi_goods_mquery_res = self.goods_mquery()
        openapi_goods_query_best_res = self.goods_query_best()
        return (openapi_goods_search_res, openapi_goods_query_res, openapi_goods_detail_res, openapi_goods_list_res,
                openapi_goods_mquery_res, openapi_goods_query_best_res, openapi_goods_querybygcode_res, openapi_goods_product_res, openapi_goods_stock_detail_res)


if __name__ == '__main__':
    # url = "http://debugapi.hqchip.com"
    # app_key = "c11ff533617d2aa45ffd0e1994fb2cd7"
    # app_sec = "7b0594651ce4ab534b3f941e5dc9fe63"
    GoodsNameSearch(version_type=2).mian_goods_search()

