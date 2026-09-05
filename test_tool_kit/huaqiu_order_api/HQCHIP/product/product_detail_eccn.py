import hashlib
import math
import time
import datetime

import pandas
import requests
import yaml

from huaqiu_order_api.HC2018_admin.login.login import Login
from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_path import yaml_file, goodsid_dir


class ProductDetailEccn:
    def __init__(self):

        self.rss = requests.Session()
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.PRODUCT_DETAIL_URL = data['PRODUCT_DETAIL_URL']
        self.headers_urlencoded = {"Content-Type": "application/x-www-form-urlencoded"}
        self.headers_json = {"Content-Type": "application/json;charset=UTF-8"}

    def read_data(self):
        data = pandas.read_csv(goodsid_dir)
        self.goodsIds = data["goods_id"]
        return self


    def product_detail_eccn(self):
        goods_ids = ''
        for i in range(len(self.goodsIds)):
            product_detail_url = "{}/api/v3/product/detail".format(self.PRODUCT_DETAIL_URL)
            stockId = str(self.goodsIds[i])
            product_detail_body = {"stockId": stockId}
            product_detail_res = self.rss.post(url=product_detail_url, json=product_detail_body, headers=self.headers_json).json()
            supplierStockInfo = product_detail_res["result"]["supplierStock"]
            if supplierStockInfo != None:
                goods_ids = goods_ids + stockId + ','
        goods_ids = goods_ids[: -1].split(",")
        # # logger.info(goods_ids)
        # goods_ids = ["1100684620"]
        for m in range(len(goods_ids)):
            product_detail_url = "{}/api/v3/product/detail".format(self.PRODUCT_DETAIL_URL)
            product_detail_body = {"stockId": goods_ids[m]}
            product_detail_res = self.rss.post(url=product_detail_url, json=product_detail_body, headers=self.headers_json).json()
            supplierStockInfo = product_detail_res["result"]["supplierStock"]

            # 获取字典的键名称并且以list汇总输出
            supplierStockInfo_key = list(supplierStockInfo.keys())
            logger.info(f"获取库存id：{goods_ids[m]}的所有supplierStockInfo的字段列表为：{supplierStockInfo_key}")
            for n in range(len(supplierStockInfo_key)):
                # logger.info(type(supplierStockInfo_key[n]))
                if supplierStockInfo_key[n] != "hqchip_self":
                    goods_type = supplierStockInfo_key[n]
                    listInfo = supplierStockInfo[f"{supplierStockInfo_key[n]}"]["list"]
                    for j in range(len(listInfo)):
                        eccn_msg = listInfo[j]["eccn"]
                        P2= listInfo[j]["pn2"]
                        if eccn_msg != None:
                            # logger.info(eccn_msg)
                            eccnCode = eccn_msg["eccnCode"]
                            webDisplay = eccn_msg["webDisplay"]
                            if goods_type != "supplier":
                                logger.info(f"库存id：{goods_ids[m]}的库存类型为{goods_type},存在ECCN编码：{eccnCode},ECCN限制说明：{webDisplay}")
                            else:
                                logger.info(f"库存id：{goods_ids[m]}的库存类型为{goods_type}对应供应商：{P2}，存在ECCN编码：{eccnCode}，ECCN限制说明：{webDisplay}")
                            break
                    break

            continue




if __name__ == '__main__':
    ProductDetailEccn().read_data().product_detail_eccn()