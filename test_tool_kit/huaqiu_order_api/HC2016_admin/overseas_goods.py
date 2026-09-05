import ast
import json
import math
from urllib.parse import quote
import re

import jsonpath
import requests
import yaml

from huaqiu_order_api.HQCHIP.Es.es_renew import EsRenew
from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_data import Data
from huaqiu_order_api.common.my_path import yaml_file, account_yaml, supplier_dir


class OverseasGoods:
    # 海外库存
    def __init__(self, rss, goods_id=None, goods_name=None, supplier_name=None):
        self.rss = rss
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.HQCHIP_ADMIN_URL = data['HQCHIP_ADMIN_URL']
        self.headers = {"Content-Type": "application/x-www-form-urlencoded",
                        "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://www.huaqiu.com)"
                        }
        self.headers_form_data = {"Content-Type": "multipart/form-data",
                        "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://www.huaqiu.com)"
                        }
        self.headers_json = {"Content-Type": "application/json; charset=UTF-8",
                             "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://www.huaqiu.com)"
                             }
        with open(supplier_dir, 'r', encoding='utf-8') as yamlfile:
            self.supplier_data = yaml.load(yamlfile, Loader=yaml.FullLoader)
            self.overseas_supplier_data = {key: value for key, value in self.supplier_data.items() if key not in ('supplier', 'szlcsc', 'mouser')}
        self.goods_id = goods_id
        self.goods_name = goods_name
        self.supplier_name = supplier_name
    def goods_search(self):
        """海外库存查询"""
        search_url = "{}/Admin/SupplierGoodsStock/index".format(self.HQCHIP_ADMIN_URL)
        search_body = {"pageNum": 1, "goods_id": self.goods_id, "goods_name": self.goods_name, "supplier_id": "", "perpage": 1000}
        supplier_goods = []
        if self.supplier_name != None:
            for key, v in self.overseas_supplier_data.items():
                if key == self.supplier_name.lower():
                    self.supplier_id = v
                    self.supplier_name = key
                    break
            # print(self.supplier_id)
            search_body["supplier_id"] = self.supplier_id
            search_res = self.rss.post(url=search_url, data=search_body, headers=self.headers).text
            goods_id = re.findall('<tr target="id" rel="(.*?)"', search_res)
            if goods_id != []:
                supplier_goods_id_dict = {"supplier_name": self.supplier_name, "supplier_id": self.supplier_id, "goods_id": goods_id}
                supplier_goods.append(supplier_goods_id_dict)
            print(supplier_goods)
        else:
            for m, n in self.overseas_supplier_data.items():
                self.supplier_id = n
                search_body["supplier_id"] = self.supplier_id
                search_res = self.rss.post(url=search_url, data=search_body, headers=self.headers).text
                goods_id = re.findall('<tr target="id" rel="(.*?)"', search_res)
                # print(goods_id)
                if goods_id != []:
                    supplier_goods_id_dict = {"supplier_name": m, "supplier_id": self.supplier_id, "goods_id": goods_id}
                    supplier_goods.append(supplier_goods_id_dict)
        # print(supplier_goods)
        return supplier_goods

    def goods_update_putaway(self, supplier_goods):
        """库存更新上架"""
        goods_id_msg = []
        msg = ''
        for i in range(len(supplier_goods)):
            for v in supplier_goods[i]["goods_id"]:
                supplier_goods_detail_url = '{}/Admin/SupplierGoodsStock/edit_price/id/{}/navTabId/SupplierGoodsStockInfo'.format(self.HQCHIP_ADMIN_URL, v)
                supplier_goods_detail_res = self.rss.get(url=supplier_goods_detail_url, headers=self.headers)
                if re.search(r'name="goods_number" size="8" value="(.*?)"', supplier_goods_detail_res.text):
                    goods_number = re.search('name="goods_number" size="8" value="(.*?)"', supplier_goods_detail_res.text).group(1)
                    min_buynum = re.search('name="min_buynum" size="8" value="(.*?)"', supplier_goods_detail_res.text).group(1)
                    increment = re.search('name="increment" size="8" value="(.*?)"', supplier_goods_detail_res.text).group(1)
                    goods_tiered_number = re.findall('name="number\[\]" size="8" value="(.*?)"', supplier_goods_detail_res.text)
                    goods_tiered_pricing = re.findall('name="price\[\]" size="8" value="(.*?)"', supplier_goods_detail_res.text)
                    supplier_goods_update_url = '{}/Admin/SupplierGoodsStock/edit_price/navTabId/SupplierGoodsStockInfo'.format(self.HQCHIP_ADMIN_URL)
                    supplier_goods_update_body = {"id": v, "goods_number": goods_number, "min_buynum": min_buynum, "increment": increment, "status": 1, "ajax": 1}
                    # 生成字典存在相同键的算法
                    supplier_goods_update_body["number"] = goods_tiered_number
                    supplier_goods_update_body["price"] = goods_tiered_pricing
                    # 添加 number[] 和 price[] 参数
                    for m in range(len(supplier_goods_update_body["number"])):
                        supplier_goods_update_body[f"number[{m}]"] = supplier_goods_update_body["number"][m]
                        supplier_goods_update_body[f"price[{m}]"] = supplier_goods_update_body["price"][m]
                        # 移除原始的 number 和 price 键
                    del supplier_goods_update_body["number"]
                    del supplier_goods_update_body["price"]
                    supplier_goods_update_res = self.rss.post(url=supplier_goods_update_url, data=supplier_goods_update_body).json()
                    if supplier_goods_update_res["info"] == "更新价格成功":
                        msg = supplier_goods_update_res["info"]
                        print(f"good_id: {v}编辑成功, 成功信息：{msg}")
                    else:
                        msg = supplier_goods_update_res["info"]
                        print(f"good_id: {v}编辑失败， 失败信息：{msg}")
                else:
                    if supplier_goods_detail_res.json()["info"] == "该mongo数据不存在":
                        print(f"good_id: {v}在mongo数据不存在")
                    else:
                        print(f"good_id: {v},执行结果：{supplier_goods_detail_res.json()}")
                    msg = supplier_goods_detail_res.json()["info"]
            supplier_goods[i]["goods_id"] = [{'id': goods_id, 'msg': msg} for goods_id in supplier_goods[i]['goods_id']]
            goods_id_msg.append(supplier_goods[i])
        print(goods_id_msg)
        return goods_id_msg
    def mian_goods_putaway_mongodb_update(self):
        supplier_goods = self.goods_search()
        goods_id_msg = self.goods_update_putaway(supplier_goods)
        updated_goods = []
        for supplier in goods_id_msg:
            # 遍历每个商品的信息
            for goods in supplier['goods_id']:
                # 如果msg为更新价格成功，则将对应的id加入updated_goods
                if goods['msg'] == '更新价格成功':
                    updated_goods.append(goods['id'])

        # 打印结果
        print(updated_goods)
        for i in updated_goods:
            EsRenew(self.rss, i).es_goods_all().es_brand_update().es_dg_relevance_goods().es_participle_update().es_update_goods().substitute_es_all_update().es_mongodb_overseas_goods_update()
        return self






if __name__ == '__main__':
    goods_id = None
    goods_name = "LM358"
    supplier_name = None
    from huaqiu_order_api.HC2016_admin.login import HC2016Login
    rss = HC2016Login().hc2016_login()
    # supplier_goods = OverseasGoods(rss, goods_id, goods_name, supplier_name).goods_search()
    # OverseasGoods(rss, goods_id, goods_name, supplier_name).goods_update_putaway(supplier_goods)
    OverseasGoods(rss, goods_id, goods_name, supplier_name).mian_goods_putaway_mongodb_update()