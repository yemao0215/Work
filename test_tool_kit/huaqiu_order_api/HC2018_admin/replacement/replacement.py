import json

import yaml
import jsonpath
from huaqiu_order_api.HC2018_admin.login.login import Login
from huaqiu_order_api.common.loguru_logger import logger
import requests

from huaqiu_order_api.common.my_data import Data
from huaqiu_order_api.common.my_path import yaml_file


class Replacement:
    def __init__(self, rss=None):
        """
        :param phone:  登录账号
        :param psw:  登录密码
        :param goods_id:  购买的产品id
        """
        # self.user = user
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.HC2018_ADMIN_URL = data['HC2018_ADMIN_URL']
        # self.ingredients_provider_name = ingredients_provider_name # 主料品牌名
        # self.replacement_provider_name = replacement_provider_name # 替代料品牌名
        # self.ingredients_name = ingredients_name  # 主料型号
        # self.replacement_name = replacement_name # 替代料型号
        # self.replace_type = replace_type # 替代类型 1待确认 2PIN to PIN替代 3功能替代料
        self.rss = rss
        self.auth_token = getattr(Data, 'dos_auth_token')
        self.headers = {"Content-Type":"application/json;charset=UTF-8", "Authorization": self.auth_token}

    def getStock_ist(self, brand_name):
        """库存定价查询"""
        brand_search_url = "{}/v1/pricing/StockPricing/retrieveBrand".format(self.HC2018_ADMIN_URL)
        brand_search_body = {"brand_name": brand_name}
        brand_search_res = self.rss.post(url=brand_search_url, json= brand_search_body, headers=self.headers).json()
        brand_id = None
        if brand_search_res["data"] != []:
            brand_id = jsonpath.jsonpath(brand_search_res, "$..brand_id")
        search_url = "{}/v1/pricing/StockPricing/getStockList".format(self.HC2018_ADMIN_URL)
        search_body = {"brand_id": ["30395"], "is_on_sale": "1", "pricing_cost_start": "0.01",
                       "spot_stock_start": "1", "sold_out_stock": "1", "page": 2, "per_page":100}
        if brand_id != None:
            search_body["brand_id"] = brand_id
        search_res = self.rss.post(url=search_url, json=search_body, headers=self.headers).json()
        goods_name = ''
        if search_res["data"]["total"] != 0:
            goods_name = jsonpath.jsonpath(search_res, "$..goods_name")
        return goods_name
    def replacement_list(self, ingredients_name):
        """查询替代料数据"""
        replacement_search_url = "{}/v1/esearch/GoodsReplaceMaterial/findList".format(self.HC2018_ADMIN_URL)
        replacement_search_body = {"goods_name": ingredients_name}
        replacement_search_res = self.rss.post(url=replacement_search_url, json=replacement_search_body, headers=self.headers).json()
        self.replacement_id = replacement_search_res["source_data"]["source_data"][0]["id"]
        logger.info(f"获取替代分组id：{self.replacement_id}")
        return self

    def ingredients_replacement(self, ingredients_provider_name, ingredients_name):
        """主料和替代料新增操作"""
        # 主料搜索
        # 主料品牌搜索
        provider_url = "{}/v1/common/BasicService/getProviderName".format(self.HC2018_ADMIN_URL)
        ingredients_provider_body = {"provider_name": ingredients_provider_name}
        ingredients_provider_res = self.rss.post(url=provider_url, data=json.dumps(ingredients_provider_body), headers=self.headers).json()
        self.ingredients_brand_id = ingredients_provider_res["source_data"][0]["brand_id"]
        logger.info(f"获取到主料品牌id：{self.ingredients_brand_id}")

        # 替代料品牌搜索
        replacement_provider_body = {"provider_name": ingredients_provider_name}
        replacement_provider_res = self.rss.post(url=provider_url, json=replacement_provider_body, headers=self.headers).json()
        self.replacement_brand_id = replacement_provider_res["source_data"][0]["brand_id"]
        logger.info(f"获取到替代料品牌id：{self.replacement_brand_id}")

        # 替代料新增保存
        esearch_url = "{}/v1/esearch/GoodsReplaceMaterial/insertGoods".format(self.HC2018_ADMIN_URL)
        esearch_body = {"main_brand_id": self.ingredients_brand_id, "main_goods_name": ingredients_name,"replace_brand_id": self.replacement_brand_id, "replace_goods_name":self.replacement_name,"replace_type": self.replace_type}
        logger.info(f"添加替代信息{esearch_body}")
        esearch_res = self.rss.post(url=esearch_url, json=esearch_body, headers=self.headers).json()
        logger.info(f"保存成功, 执行结果：{esearch_res}")
        return self

    def replacement(self, ingredients_provider_name, replacement_name, replacement_provider_name, replace_type):
        """在已有主料里面添加替代料型号"""

        # 替代料品牌搜索
        provider_url = "{}/v1/common/BasicService/getProviderName".format(self.HC2018_ADMIN_URL)
        replacement_provider_body = {"provider_name": ingredients_provider_name}
        replacement_provider_res = self.rss.post(url=provider_url, json=replacement_provider_body, headers=self.headers).json()
        self.replacement_brand_id = replacement_provider_res["source_data"][0]["brand_id"]
        logger.info(f"获取到替代料品牌id：{self.replacement_brand_id}")

        # 替代料新增保存
        esearch_url = "{}/v1/esearch/GoodsReplaceMaterial/insertReplaceModel".format(self.HC2018_ADMIN_URL)
        esearch_body = {"brand_id": self.replacement_brand_id, "goods_name": replacement_name,"provider_name":replacement_provider_name, "main_id": self.replacement_id, "replace_type": replace_type}
        logger.info(f"添加替代信息{esearch_body}")
        esearch_res = self.rss.post(url=esearch_url, json=esearch_body, headers=self.headers).json()
        logger.info(f"保存成功, , 执行结果：{esearch_res}")
        return self

    def replacement_audit(self):
        """替代料审核"""
        # 查询审核数据
        audit_list_url = "{}/v1/esearch/GoodsReplaceMaterial/getReplaceModel".format(self.HC2018_ADMIN_URL)
        # self.search_headers = {"Content-Type": "application/json;charset=UTF-8", "Authorization": auth_token}
        audit_list_body = {"main_id": self.replacement_id}
        audit_list_res = self.rss.post(url=audit_list_url, json=audit_list_body, headers=self.headers).json()
        audit_list_data = audit_list_res["source_data"]
        for i in range(len(audit_list_data)):
            if audit_list_data[i]["audit_txt"] == "未审核":
                audit_id = audit_list_data[i]["id"]
                # 申请审核
                autit_apply_url = "{}/v1/esearch/GoodsReplaceMaterial/applyAuditReplaceModel".format(self.HC2018_ADMIN_URL)
                autit_apply_body = {"item_ids":audit_id}
                autit_apply_res = self.rss.post(url=autit_apply_url, json=autit_apply_body, headers=self.headers).json()

                # 审核
                autit_url = "{}/v1/esearch/GoodsReplaceMaterial/auditReplaceModel".format(self.HC2018_ADMIN_URL)
                autit_body = {"audit_status": 2, "item_ids": audit_id}
                autit_res = self.rss.post(url=autit_url, json=autit_body, headers=self.headers).json()
                logger.info("审核通过")
            elif audit_list_data[i]["audit_txt"] == "审核中":
                audit_id = audit_list_data[i]["id"]
                # 审核
                autit_url = "{}/v1/esearch/GoodsReplaceMaterial/auditReplaceModel".format(self.HC2018_ADMIN_URL)
                autit_body = {"audit_status":2, "item_ids": audit_id}
                autit_res = self.rss.post(url=autit_url, json=autit_body,headers=self.headers).json()
                logger.info(f"审核通过, 执行结果：{autit_res}")
            else:
                logger.info("不存在需要审核的数据")
            continue
        logger.info("已完成审核")
        return self

    def mian_replacement(self, ingredients_provider_name, replacement_name, replacement_provider_name, replace_type):
        """
        :param ingredients_provider_name # 主料品牌名
        :param replacement_provider_name # 替代料品牌名
        :param ingredients_name  # 主料型号
        :param  replacement_name # 替代料型号
        :param replace_type # 替代类型 1待确认 2PIN to PIN替代 3功能替代料
        """
        ingredients_name = self.getStock_ist(ingredients_provider_name)
        # logger.info(ingredients_name)
        for i in range(len(ingredients_name)):
            self.replacement_list(ingredients_name)
            self.replacement(ingredients_provider_name, replacement_name, replacement_provider_name, replace_type)
            self.replacement_audit()
if __name__ == '__main__':
    rss = Login().login()
    Replacement(rss).mian_replacement("Yageo",'TI',"CESHI260819",3)
