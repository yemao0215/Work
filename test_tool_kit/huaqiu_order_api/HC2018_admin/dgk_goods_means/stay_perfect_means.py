import json
import math
import multiprocessing
import re
import threading
import time

import jsonpath
import pandas
import requests
import yaml

from huaqiu_order_api.HC2018_admin.dgk_goods_means.dgk_goods_means import GoodsMeans
from huaqiu_order_api.HC2018_admin.login.login import Login
from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_data import Data
from huaqiu_order_api.common.my_path import yaml_file, eccn_dir


class StayPerfectMeans:
    # 待完善资料
    def __init__(self, rss, goods_name=None, provider_name=None, source_type=None):
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.HC2018_ADMIN_URL = data['HC2018_ADMIN_URL']
        token = getattr(Data, "dos_auth_token")
        self.headers = {"Content-Type": "application/x-www-form-urlencoded", "Authorization": token,
                        "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://www.huaqiu.com)"
                        }
        self.headers_json = {"Content-Type": "application/json; charset=UTF-8", "Authorization": token,
                             "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://www.huaqiu.com)"
                             }
        self.rss = rss
        self.goods_name = goods_name
        self.provider_name = provider_name
        self.source_type = source_type
        self.source_type_json = {"partner": [('consign'), 11], "dos": [('备货'), 21], "erp": [('ERP'), 13]}
    def stock_up_means(self):
        """待完善资料-备货"""
        search_url = "{}/v1/goods/GoodsInfo/findXjJDList".format(self.HC2018_ADMIN_URL)
        search_body = {"page": 1, "per_page": 100, "type": 1, "laiyuan": "stockup", "category_id": None,
                       "brand_id": None, "aaaorder_sn": "", "provider_name": self.provider_name}
        search_res = self.rss.post(url=search_url, json=search_body, headers=self.headers_json).json()
        total = jsonpath.jsonpath(search_res, "$..total")[0]
        goods_name = jsonpath.jsonpath(search_res, "$..goods_name")
        print(goods_name)
        ids = jsonpath.jsonpath(search_res, "$..id")
        if math.ceil(int(total) / 100) > 1:
            page_num = math.ceil(int(total) / 100)
            for i in range(2, page_num):
                search_body["page"] = i
                search_res = self.rss.post(url=search_url, json=search_body, headers=self.headers_json).json()
                goods_name_page_num = jsonpath.jsonpath(search_res, "$..goods_name")
                id_page_num = jsonpath.jsonpath(search_res, "$..id")
                goods_name = goods_name_page_num + goods_name
                ids = ids + id_page_num
        goods_name_ids_dict = {}
        # 一个循环来遍历 goods_name 和 ids 列表，并对每个元素进行处理。如果 name 已经存在于 goods_name_ids_dict 中，
        # 那么将当前的 id 添加到对应的列表中；如果 name 不存在于 goods_name_ids_dict 中，则创建一个新的键值对，将 name 和包含当前 id 的列表存储进去。
        for name, id in zip(goods_name, ids):
            if name in goods_name_ids_dict:
                goods_name_ids_dict[name].append(id)
            else:
                goods_name_ids_dict[name] = [id]
        brand_id = ''
        brand_name = ''
        for key in goods_name_ids_dict:
            if key == self.goods_name:
                id = goods_name_ids_dict[key]
                for v in id:
                    # self.provider_name是否存在特殊字符，如(), 若存在以特殊字符切割点，组成 provider_name_list且将空格字符过滤掉
                    provider_name_list = [x for x in re.split(r"[@_!#$%^&*()<>?/\|}{~:，。、]", self.provider_name) if x.strip()]

                    for k in provider_name_list:
                        search_provider_url = "{}/v1/goods/DgkGoods/ajaxGetProviderName".format(self.HC2018_ADMIN_URL)
                        search_provider_body = {"provider_name": k, "src_type": 0}
                        search_provider_res = self.rss.post(url=search_provider_url, json=search_provider_body, headers=self.headers_json).json()
                        try:
                            brand_id = jsonpath.jsonpath(search_provider_res, "$..brand_id")[0]
                            brand_name = jsonpath.jsonpath(search_provider_res, "$..brand_name")[0]
                            break
                        except:
                            pass
                    if brand_id != '':
                        stock_up_means_add_url = "{}/v1/goods/GoodsInfo/addStoupToGoods".format(self.HC2018_ADMIN_URL)
                        stock_up_means_add_body = {"brand_id": brand_id, "cat_id": "2148", "category_id": "2148",
                                                   "min_picking_number": 1, "weiruku_id": v, "weiruku_laiyuan": "stockup"}
                        stock_up_means_add_res = self.rss.post(url=stock_up_means_add_url, json=stock_up_means_add_body, headers=self.headers_json).json()
                        msg = stock_up_means_add_res["msg"]
                        if msg == "success":
                            logger.info(f"型号：{self.goods_name}，品牌：{self.provider_name}创建成功，此时型号品牌被定义为{brand_name}")
                            setattr(Data, 'stock_provider_name', brand_name)
                    else:
                        logger.error(f"品牌：{self.provider_name}在品牌列表无数据，请核对")
        return self.goods_name, brand_name
    def stay_perfect_means_search(self):
        """待完善资料查询"""
        source = None
        src_type = []
        for k, v in self.source_type_json.items():
            if self.source_type in v[0]:
                source = k
                src_type.append(v[1])
        search_url = "{}/v1/goods/GoodsInfo/getBusinessGoodsList".format(self.HC2018_ADMIN_URL)
        search_body = {"page": 1, "per_page": 20, "status": 1, "goods_name": self.goods_name, "provider_name": self.provider_name, "source": source}
        search_res = self.rss.post(url=search_url, json=search_body, headers=self.headers_json).json()
        total = jsonpath.jsonpath(search_res, "$..total")[0]
        item_id_count = []
        goods_name_count = []
        provider_name_count = []
        encap_count = []
        if int(total) > 100:
            print(f"商品总数{total}，超过100条，需分页")
            total_num = math.ceil(int(total) / 100)
            for i in range(total_num):
                search_body['page'] = i + 1
                search_res = self.rss.post(url=search_url, json=search_body, headers=self.headers_json).json()
                item_id = jsonpath.jsonpath(search_res, "$..item_id")
                goods_name = jsonpath.jsonpath(search_res, "$..goods_name")
                provider_name = jsonpath.jsonpath(search_res, "$..provider_name")
                encap = jsonpath.jsonpath(search_res, "$..encap")
                item_id_count = item_id_count + item_id
                goods_name_count = goods_name_count + goods_name
                provider_name_count = provider_name_count + provider_name
                encap_count = encap_count + encap
        else:
            print(f"商品总数{total}，未超过100条，无需分页")
            item_id_count = jsonpath.jsonpath(search_res, "$..item_id")
            goods_name_count = jsonpath.jsonpath(search_res, "$..goods_name")
            provider_name_count = jsonpath.jsonpath(search_res, "$..provider_name")
            encap_count = jsonpath.jsonpath(search_res, "$..encap")
        print(f"item_id:{item_id_count}, goods_name:{goods_name_count}, provider_name:{provider_name_count}, encap:{encap_count}")
        return item_id_count, goods_name_count, provider_name_count, encap_count, src_type
    def means_presence_check(self, goods_name=None, provider_name=None):
        """检查以型号和品牌是否存在唯一有效资料"""
        presence_check = True
        presence_goods_no = None
        self.goods_id, self.brand_id, self.goods_no, self.is_special_type, self.special_key = GoodsMeans(self.rss, goods_name, provider_name).goods_means_list()
        print(f"goods_id:{self.goods_id}, brand_id:{self.brand_id}, goods_no:{self.goods_no}, is_special_type:{self.is_special_type}, special_key:{self.special_key}")
        if self.goods_no != False and self.goods_no != None:
            for goods_no, is_special_type in zip(self.goods_no, self.is_special_type):
                if self.goods_id != [] and len(self.goods_no) and is_special_type == "否":
                    presence_check = False
                    if is_special_type == "否":
                        presence_goods_no = goods_no
                    print("已存在该型号和品牌，请勿重复创建, 此时presence_check：{0}, goods_no: {1}".format(presence_check, goods_no))
                    break
                else:
                    if is_special_type == "否":
                        presence_check = False
                        presence_goods_no = goods_no
                        print("已存在该型号和品牌，请勿重复创建, 此时goods_no:{0}，presence_check：{1}".format(goods_no, presence_check))
                        break
        else:
            print("不存在该型号和品牌，可以创建, 此时presence_check：{0}".format(presence_check))
        print(presence_check)
        return presence_check, presence_goods_no
    def stay_perfect_means_create(self, presence_check=None, presence_goods_no=None, item_id=None, goods_name=None, provider_name=None, encap=None, src_type=None):
        if presence_check == False:
            print("已存在该型号和品牌，请勿重复创建,此时待完善资料走直接关联")
            map_means_url = "{}/v1/goods/GoodsInfo/mapBusinessGoods".format(self.HC2018_ADMIN_URL)
            map_means_body = {"erp_goods_id": 0, "erp_provider_name": provider_name,"erp_goods_name": goods_name, "goods_no": presence_goods_no,
                     "goods_sn": "undefined", "goods_weight": "undefined", "encap": encap, "item_id": item_id, "src_type": src_type}
            map_means_res = self.rss.post(url=map_means_url, json=map_means_body, headers=self.headers_json).json()
            print("执行结果为：{0}".format(map_means_res))
        else:
            print("不存在该型号和品牌，可以创建,此时待完善资料走创建")
            # self.provider_name是否存在特殊字符，如(), 若存在以特殊字符切割点，组成 provider_name_list且将空格字符过滤掉
            provider_name_list = [x for x in re.split(r"[@_!#$%^&*()<>?/\|}{~:，。、]", provider_name) if x.strip()]
            brand_id = ''
            brand_name = ''
            for k in provider_name_list:
                search_provider_url = "{}/v1/goods/DgkGoods/ajaxGetProviderName".format(self.HC2018_ADMIN_URL)
                search_provider_body = {"provider_name": k, "src_type": 0}
                search_provider_res = self.rss.post(url=search_provider_url, json=search_provider_body,
                                                    headers=self.headers_json).json()
                try:
                    brand_id = jsonpath.jsonpath(search_provider_res, "$..brand_id")[0]
                    brand_name = jsonpath.jsonpath(search_provider_res, "$..brand_name")[0]
                    break
                except:
                    pass
            if brand_id != '':
                add_means_url = "{}/v1/goods/GoodsInfo/addBusinessGoods".format(self.HC2018_ADMIN_URL)
                add_means_body = {"brand_id": brand_id, "cat_id": "2149", "encap": encap, "goods_name": goods_name, "is_special": "0",
                                           "erp_goods_id": "0", "erp_goods_name": goods_name, "erp_provider_name": provider_name,
                                           "item_id": item_id, "src_type": src_type, "web_source": 0}
                add_means_res = self.rss.post(url=add_means_url, json=add_means_body, headers=self.headers_json).json()
                msg = add_means_res["msg"]
                if msg == "success":
                    logger.info(
                        f"型号：{self.goods_name}，品牌：{self.provider_name}创建成功，此时型号品牌被定义为{brand_name}")
                    setattr(Data, 'stock_provider_name', brand_name)
            else:
                logger.error(f"品牌：{provider_name}在品牌列表无数据，请核对")
            GoodsMeans(self.rss, goods_name, provider_name, "1", 1000).mian_goods_giveaudit_audit()
        return self
    def mian_stay_perfect_means_new(self):
        item_id_count, goods_name_count, provider_name_count, encap_count, src_type = self.stay_perfect_means_search()
        if item_id_count != False:
            for i in range(len(item_id_count)):
                presence_check, presence_goods_no = self.means_presence_check(goods_name_count[i], provider_name_count[i])
                self.stay_perfect_means_create(presence_check, presence_goods_no, item_id_count[i], goods_name_count[i], provider_name_count[i], encap_count[i], src_type[i])

if __name__ == '__main__':
    goods_name = "searchV4.16.15"
    provider_name = "searchV4"
    from huaqiu_order_api.HC2018_admin.login.login import Login
    target_rss = Login().login()
    # StayPerfectMeans(target_rss, "searchV4.10.6", "searchV4").stock_up_means()
    StayPerfectMeans(target_rss, "searchV4.16.15", "searchV4", source_type='备货').mian_stay_perfect_means_new()
    # StayPerfectMeans(target_rss, "searchV4.16.15", "searchV4", source_type='备货').means_presence_check(goods_name, provider_name)
