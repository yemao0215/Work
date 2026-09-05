import hashlib
import json
import math
import re
import time
import datetime

import pandas
import requests
import yaml

from huaqiu_order_api.HC2018_admin.login.login import Login
from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_path import yaml_file, goodsid_dir, supplier_dir, shieIdEccnYaml_dir


class EsRenew:
    def __init__(self, rss=None, goods_id=None, shieId_eccn=None):
        self.goods_id = goods_id
        self.shieId_eccn = shieId_eccn
        self.brand_id = 30546
        self.supplierNames ="supplier,digikey,mouser,future,element14,verical.chip1shop,arrow,master,tme.peigenesis,heillind,alliedelec,rocelec,americal" \
                            "rs,psg,icbase, "
        self.rss = requests.Session()
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.ES_SEARCH_URL = data['ES_SEARCH_URL']
        self.HQCHIP_ADMIN_URL = data['HQCHIP_ADMIN_URL']
        with open(supplier_dir, 'r', encoding='utf-8') as yamlfile:
            self.supplier_data = yaml.load(yamlfile, Loader=yaml.FullLoader)
            self.supplierNames = ','.join(self.supplier_data.keys()).replace('hqchip_self', 'self')
        self.headers_urlencoded = {"Content-Type": "application/x-www-form-urlencoded;charset=UTF-8"}
        self.headers_json = {"Content-Type": "application/json;charset=UTF-8"}
        self.hc2016_rss = rss
    def get_shieId_eccn_list(self):
        # 读取 YAML 文件
        with open(shieIdEccnYaml_dir, 'r', encoding='utf-8') as file:
            data = yaml.safe_load(file)
        shieId_eccn_list = None
        # 提取列表
        if 'ECCNList' in data:
            shieId_eccn_list = data['ECCNList']
            # print(partner_list)  # 输出: ['apple', 'banana', 'orange', 'grape']
        print(shieId_eccn_list)
        return shieId_eccn_list
    def hc2016_login(self):
        """HC2016后台登录"""
        login_url = "{}/Admin/Public/checkLogin/".format(self.HQCHIP_ADMIN_URL)
        self.body = {"user_name": "admin", "password": "HQ@uat@666"}
        logger.info(f"开始执行登录账号：{self.body}")
        res = self.rss.post(url=login_url, data=self.body, headers=self.headers_urlencoded)
        logger.info(f"登录完成")
        return self.rss
    def es_goods_all(self):
        """es数据维护操作全量导入更新"""
        logger.info(f"此时goods_id：{self.goods_id}")
        es_goods_all_url = "{}/v1/stock/batchUpdate?supplierNames={}&startId={}&batchNum=1000".format(self.ES_SEARCH_URL, self.supplierNames, 1)
        print(es_goods_all_url)
        res = self.rss.get(url=es_goods_all_url)
        print(res.json())
        print(res.text)
        return self
    def es_brand_update(self):
        """更新品牌主从"""

        es_brand_update_url = "{}/v1/brand/maintainByBrandId?brandId={}".format(self.ES_SEARCH_URL, self.brand_id)
        es_brand_update_res = self.rss.get(url=es_brand_update_url, headers=self.headers_json).json()
        # logger.info(es_dg_relevance_goods_res)
        msg = es_brand_update_res["body"]
        logger.info(f"执行结果：{msg}")
        return self
    def es_dg_relevance_goods(self):
        """指定goods_id更新es关联资料内容"""
        es_dg_relevance_goods_url = "{}/v1/goods/maintainByStockId?id={}".format(self.ES_SEARCH_URL, self.goods_id)
        print(es_dg_relevance_goods_url)
        es_dg_relevance_goods_res = self.rss.get(url=es_dg_relevance_goods_url, headers=self.headers_json).json()
        # logger.info(es_dg_relevance_goods_res)
        msg = es_dg_relevance_goods_res["body"]
        logger.info(f"执行结果：{msg}")
        return self

    def es_dg_relevance_supplier_goods(self):
        """供应商全量更新es关联资料内容"""
        self.supplierNames_lst = self.supplierNames.split(",")
        es_dg_relevance_supplier_goods_url = "{}/v1/goods/batchImport".format(self.ES_SEARCH_URL)
        es_dg_relevance_supplier_goods_body = {"supplierNames": self.supplierNames_lst, "brandNames": [], "pn2s": [], "startId": 0, "endId": 0}
        es_dg_relevance_supplier_goods_res = self.rss.post(url=es_dg_relevance_supplier_goods_url, json=es_dg_relevance_supplier_goods_body, headers=self.headers_json).json()
        # print(es_dg_relevance_supplier_goods_res)
        logger.info(f"执行结果：{es_dg_relevance_supplier_goods_res}")
        return self
    def es_update_goods(self):
        """更新es关内容"""
        es_update_goods_url = "{}/v1/stock/update?goodsIds={}".format(self.ES_SEARCH_URL, self.goods_id)
        logger.info(es_update_goods_url)
        es_update_goods_res = self.rss.get(url=es_update_goods_url, headers=self.headers_json).json()
        msg = es_update_goods_res["body"]
        logger.info(f"执行结果：{msg}")
        return self

    def es_participle_update(self):
        """更新es分词数据"""
        es_update_participle_url = "{}/v1/participle/update?goodsIds={}".format(self.ES_SEARCH_URL, self.goods_id)
        logger.info(es_update_participle_url)
        es_update_goods_res = self.rss.get(url=es_update_participle_url, headers=self.headers_json).json()
        msg = es_update_goods_res["body"]
        logger.info(f"执行结果：{msg}")
        return self
    def substitute_es_update(self):
        """更新替代料的es的数据  商品替代料按库存ID维护"""
        substitute_es_update_url = "{}/v1/goods/goodsSubstituteMainByStockId?stockId={}".format(self.ES_SEARCH_URL, self.goods_id)
        logger.info(substitute_es_update_url)
        substitute_es_update_res = self.rss.get(url=substitute_es_update_url, headers=self.headers_json).json()
        msg = substitute_es_update_res["body"]
        logger.info(f"执行结果：{msg}")
        return self

    def substitute_es_all_update(self):
        """更新替代料的es的数据  商品替代料全量维护"""
        substitute_es_update_url = "{}/v1/goods/goodsSubstituteImportEs?batchNum={}".format(self.ES_SEARCH_URL, 200)
        logger.info(substitute_es_update_url)
        substitute_es_update_res = self.rss.get(url=substitute_es_update_url, headers=self.headers_json).json()
        msg = substitute_es_update_res["body"]
        logger.info(f"执行结果：{msg}")
        return self
    def es_mongodb_overseas_goods_update(self, updater_goodsName=None, supplierName=None):
        """更新es海外仓库存数据"""
        if updater_goodsName == None:
            if self.hc2016_rss == None:
                self.hc2016_rss = self.hc2016_login()
            overseas_goods_search_url = "{}/Admin/SupplierGoodsStock/index".format(self.HQCHIP_ADMIN_URL)
            logger.info(overseas_goods_search_url)
            str_supplier_data = json.dumps(self.supplier_data, indent=4)
            json_supplier_data = json.loads(str_supplier_data)
            if supplierName == None:
                for key in json_supplier_data:
                    overseas_goods_search_body = {"pageNum": 1, "perpage": 20, "goods_id": self.goods_id, "supplier_id": json_supplier_data[key]}
                    overseas_goods_search_res = self.hc2016_rss.post(url=overseas_goods_search_url, data=overseas_goods_search_body, headers=self.headers_urlencoded)
                    try:
                        overseas_goods_search_res_text = overseas_goods_search_res.text
                        search_num = re.search(r'共(.*?)条', overseas_goods_search_res_text).group(1)
                        if int(search_num) >= 1:
                            goods_id = re.search('<tr target="id" rel="(.*?)">', overseas_goods_search_res_text).group(1)
                            goods_name = re.search(r'<a href="/Admin/SupplierGoodsStock/info/id/(.*?)" target="navTab" rel="SupplierGoodsStockInfo">(.*?)</a>', overseas_goods_search_res_text).group(2)
                            if int(goods_id) == int(self.goods_id):
                                supplierName = key
                                updater_goodsName = goods_name
                            break
                    except:
                        pass
        es_mongodb_overseas_goods_update_url = "{}/v1/testTool/updateAgencyStock".format(self.ES_SEARCH_URL)
        logger.info(es_mongodb_overseas_goods_update_url)
        es_mongodb_overseas_goods_update_body = {"stockDtoList": [{"stockId": self.goods_id, "goodsName": updater_goodsName}],
                                                 "supplierName": supplierName}
        es_mongodb_overseas_goods_update_res = self.rss.post(url=es_mongodb_overseas_goods_update_url, json=es_mongodb_overseas_goods_update_body,
                                                             headers=self.headers_json).json()
        if 'result' in es_mongodb_overseas_goods_update_res:
            msg = es_mongodb_overseas_goods_update_res["result"]
            logger.info(f"执行结果：{msg}")
        return self
    def es_shieId_eccn_removed(self, trigger_icon=None):
        """根据指定eccn下架屏蔽ES数据"""
        if self.shieId_eccn == None and trigger_icon =='IN':
            self.shieId_eccn = self.get_shieId_eccn_list()
        if not isinstance(self.shieId_eccn, list):
            self.shieId_eccn = [self.shieId_eccn]
        for eccn in self.shieId_eccn:
            logger.info(f"此时执行的eccn为：{eccn}")
            es_shieId_eccn_removed_url = "{}/v1/stock/unSale?eccns={}".format(self.ES_SEARCH_URL, eccn)
            es_shieId_eccn_removed_res = self.rss.get(url=es_shieId_eccn_removed_url, headers=self.headers_json).json()
            print(es_shieId_eccn_removed_res)
        return self

    def es_shieId_eccn_listed(self, trigger_icon=None):
        """根据屏蔽的指定eccn上架ES数据"""
        if self.shieId_eccn == None and trigger_icon =='IN':
            self.shieId_eccn = self.get_shieId_eccn_list()
        if not isinstance(self.shieId_eccn, list):
            self.shieId_eccn = [self.shieId_eccn]
        for eccn in self.shieId_eccn:
            logger.info(f"此时执行的eccn为：{eccn}")
            es_shieId_eccn_listed_url = "{}/v1/stock/doOnSale?eccns={}".format(self.ES_SEARCH_URL, eccn)
            es_shieId_eccn_listed_res = self.rss.get(url=es_shieId_eccn_listed_url, headers=self.headers_json).json()
            print(es_shieId_eccn_listed_res)
        return self
    def mian_es_goods_update(self):
        """更新es商品数据"""





if __name__ == '__main__':
    goods_id = 2500344404
    EsRenew(goods_id=goods_id).es_goods_all().es_brand_update().es_dg_relevance_goods().es_participle_update().es_update_goods().substitute_es_all_update().es_mongodb_overseas_goods_update()
    # EsRenew(goods_id=goods_id).es_goods_all()
