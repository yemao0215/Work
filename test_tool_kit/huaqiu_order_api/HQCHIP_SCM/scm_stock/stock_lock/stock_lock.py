import hashlib
import math
import time
from datetime import datetime, timedelta

import jsonpath
import requests
import yaml

from huaqiu_order_api.HC2018_admin.login.login import Login

from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_data import Data
from huaqiu_order_api.common.my_path import yaml_file, account_yaml


class StockLock:
    def __init__(self, rss):
        self.scm_rss = rss
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.SCM_URL = data['SCM_URL']


        # self.goods_no = "G5058257"
        with open(account_yaml, 'r', encoding='utf-8') as yamlfile:
            account = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.warehouse_type = int(account["HQCHIP_GOODS"]["warehouse_id"])
        self.number = account["HQCHIP_GOODS"]["number"]
        self.json_head = {"Content-Type": "application/json"}

    def stock_lock_search(self):
        """即时库存查询"""
        self.goods_no = getattr(Data, 'erp_goods_sn')
        stock_lock_select_url = "{}/scmstock/web/lockgoods/list".format(self.SCM_URL)
        stock_lock_select_body = {"goodsNo": self.goods_no,"pageNum": 1, "pageSize": 500, "counted": True}
        stock_lock_select_res = self.scm_rss.post(url=stock_lock_select_url, json=stock_lock_select_body,
                                                  headers=self.json_head).json()
        logger.info(stock_lock_select_res)
        id = jsonpath.jsonpath(stock_lock_select_res, '$..id')
        logger.info(id)

    def goods_lock_search(self):
        """锁定库存查询"""
        self.goods_name = getattr(Data, 'detail_goods_list')
        self.goods_id = getattr(Data, 'detail_goods_id')
        self.detail_id_list = getattr(Data, 'detail_id_list')
        for i in range(len(self.goods_name)):
            stock_lock_select_url = "{}/scmstock/web/lockgoods/list".format(self.SCM_URL)
            goods_lock_search_body = {"goodsName": self.goods_name[i],"pageNum": 1, "pageSize": 500, "counted": True}
            goods_lock_search_res = self.scm_rss.post(url=stock_lock_select_url, json=goods_lock_search_body,
                                                  headers=self.json_head).json()
            goods_id = jsonpath.jsonpath(goods_lock_search_res, "$..goodsId")
            id = jsonpath.jsonpath(goods_lock_search_res, "$..id")
            for m in range(len(goods_id)):
                if goods_id[i] == self.goods_id[i]:
                    goods_lock_info_url = "{}/scmstock/web/lockgoods/info".format(self.SCM_URL)
                    goods_lock_info_body = {"id": id[m]}
                    goods_lock_info_res = self.scm_rss.post(url=goods_lock_info_url, json=goods_lock_info_body,
                                                              headers=self.json_head).json()
                    order_item_id = jsonpath.jsonpath(goods_lock_info_res, "$..orderItemId")
                    order_queuingTime = jsonpath.jsonpath(goods_lock_info_res, "$..queuingTime")
                    now_time = str((datetime.now()).strftime("%Y-%m-%d %H:%M:%S"))
                    logger.info(f"获取当前时间的时间：{now_time}")
                    order_item_id_new = []
                    for n in range(len(order_queuingTime)):
                        order_queuingTime_day_timestamp  = time.mktime(time.strptime(order_queuingTime[n], '%Y-%m-%d %H:%M:%S')) + 86400
                        now_time_timestamp = time.mktime(time.strptime(now_time, '%Y-%m-%d %H:%M:%S'))
                        print(f"转换成时间戳： order_queuingTime_timestamp为{order_queuingTime_day_timestamp}，当前时间戳：{now_time_timestamp}")
                        if order_queuingTime_day_timestamp <= now_time_timestamp:
                            print(f"此时goods_id：{goods_id[i]}，将此时的order_item_id：{order_item_id[n]}写入order_item_id_new")
                            order_item_id_new.append(order_item_id[n])
                    if self.detail_id_list != order_item_id_new:
                        logger.info(f"order_item_id在SCM不等于ERP的，将把SCM的列表写入Data.detail_id_list")
                        setattr(Data, "detail_id_list", order_item_id_new)
        return self





    def stock_lock_select(self):
        """判断库存是否满足出库"""
        warehouse_name = ''
        if self.warehouse_type == 2:
            warehouse_name = "深圳华秋东莞仓"
        elif self.warehouse_type == 8:
            warehouse_name = "长沙仓"
        stock_lock_select_url = "{}/scmstock/web/lockgoods/list".format(self.SCM_URL)
        stock_lock_select_body = {"warehouseCode": self.warehouse_type, "goodsNo": self.goods_no,
                                  "pageNum": 1, "pageSize": 500, "counted": True}
        stock_lock_select_res = self.scm_rss.post(url=stock_lock_select_url, json=stock_lock_select_body,
                                                headers=self.json_head).json()
        logger.info(stock_lock_select_res)
        goods_stock_sale = jsonpath.jsonpath(stock_lock_select_res, '$..saleNum')
        logger.info(goods_stock_sale)
        stock_sale_count = 0
        for i in range(len(goods_stock_sale)):
            stock_sale_count = stock_sale_count + int(goods_stock_sale[i])
        if stock_sale_count >= int(self.number):
            scm_msg = f"商品编码：{self.goods_no}，符合scm出库要求，此时商品编码：{self.goods_no}的仓库：{warehouse_name}的可用库存为：{stock_sale_count}"
            logger.info(scm_msg)

        else:
            scm_msg = f"商品编码：{self.goods_no}，不符合scm出库要求，此时商品编码：{self.goods_no}的仓库：{warehouse_name}的可用库存为：{stock_sale_count}"
            logger.error(scm_msg)
        return scm_msg
if __name__ == '__main__':
    from huaqiu_order_api.HQCHIP_SOO.login import SOOLogin
    target_rss = SOOLogin("uat-scm.huaqiu.com", "hqScm").target_login()
    StockLock(target_rss).stock_lock_select()

