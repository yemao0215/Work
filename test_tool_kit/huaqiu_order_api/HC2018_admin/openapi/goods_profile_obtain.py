import json
import time

import jsonpath
import pandas
import requests
import yaml

from huaqiu_order_api.HC2018_admin.login.login import Login
from huaqiu_order_api.HC2018_admin.signature.openapi_signature import OpenapiSignature
from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_data import Data
from huaqiu_order_api.common.my_path import yaml_file, eccn_dir


class GoodsProfileObtain:
    def __init__(self, goods_name=None, brand_name=None, goods_id=None, encap=None):
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.HC2018_ADMIN_URL = data['HC2018_ADMIN_URL']
        self.headers = {"Content-Type": "application/x-www-form-urlencoded"}
        self.form_head = {'User-Agent': 'HQCHIP OpenAPI Python-SDK/1.0', "X-Request-Version": '1.0'}
        self.headers_json = {"Content-Type": "application/json"}
        self.goods_name = goods_name
        self.brand_name = brand_name
        self.goods_id = goods_id
        self.encap = encap
        self.rss = requests.Session()
    def opapi_goods_profile_obtain(self):
        if "uat" in self.HC2018_ADMIN_URL:
            self.sign = "f9498bc27e3be5a0aed8c9401abca645"
        if "fat" in self.HC2018_ADMIN_URL:
            self.sign = "f9498bc27e3be5a0aed8c9401abca645"
        self.timestamp = int(time.time())
        params = {'timestamp': self.timestamp, "appid": "hqchip_erp_sync", "sign_type": "md5"}
        data = {"goods_name": self.goods_name, "provider_name": self.brand_name, "goods_id": self.goods_id}
        params['signature'] = OpenapiSignature(self.sign).hqchip_sign_main(params, data)

        goods_profile_obtain_url = "{}/openapi/GoodsOpen/findGoodsInfoList".format(self.HC2018_ADMIN_URL)
        goods_profile_obtain_res = self.rss.post(url=goods_profile_obtain_url, params=params, data=data, headers=self.form_head,timeout=10).json()
        logger.info(goods_profile_obtain_res)
        self.msg = goods_profile_obtain_res["retMsg"]
        print(self.msg)
        return self
    def hc2018_admin_goods_profile_obtain(self):
        rss = Login().login()
        self.rss = rss
        """商品资料列表"""
        self.auth_token = getattr(Data, 'dos_auth_token')
        goods_brand_search_url = "{}/v1/goods/DgkGoods/ajaxGetProviderName".format(self.HC2018_ADMIN_URL)
        goods_brand_keyword_body = {"provider_name": self.brand_name, "src_type": 0}
        self.goods_list_headers = {"Content-Type": "application/json;charset=UTF-8", "Authorization": self.auth_token}
        goods_brand_search_res = self.rss.post(url=goods_brand_search_url, json=goods_brand_keyword_body, headers=self.goods_list_headers).json()
        goods_brand_id = jsonpath.jsonpath(goods_brand_search_res, '$..brand_id')
        goods_brand_name = jsonpath.jsonpath(goods_brand_search_res, '$..brand_name')
        brand_id = []
        for m in range(len(goods_brand_name)):
            if goods_brand_name[m] == self.brand_name:
                brand_id.append(goods_brand_id[m])
        for i in range(len(brand_id)):
            goods_search_list_url = "{}/v1/goods/DgkGoods/findList".format(self.HC2018_ADMIN_URL)
            goods_search_list_body = {
                "goods_name": self.goods_name,
                "brand_id": brand_id[i],
                "search_type": "1",
                "brand_type": "",
                "code_search_type": "1",
                "complete_type": -1,
                "has_stock": "-1",
                "is_enabled": "-1",
                "is_on_sale": "-1",
                "self_status": "-1",
                "type": "0",
                "is_need_real_count": True
            }
            logger.info(goods_search_list_body)
            goods_search_list_res = self.rss.post(url=goods_search_list_url, json=goods_search_list_body, headers=self.goods_list_headers).json()
            goods_searchInfo = goods_search_list_res["data"]["data"]
            goods_info = []
            if goods_searchInfo != []:
                for k in goods_searchInfo:
                    for v in k:
                        if v == "pns_main_goods_id":
                            if k[v] == "0":
                                goods_info.append(k)
                return goods_info
            else:
                return None
    def opapi_map_goods(self):
        """业务匹配资料"""
        opapi_map_goods_url = "{}/openapi/GoodsApi/mapDosGoodsNew".format(self.HC2018_ADMIN_URL)
        goods_name_list = self.goods_name.split(",")
        brand_name_list = self.brand_name.split(",")
        encap_list = [self.encap.split(',')[i] if self.encap is not None and i < len(self.encap.split(',')) else '' for i in range(len(goods_name_list))]
        data_json = []
        opapi_map_goods_body = {}
        for i in range(len(goods_name_list)):
            data = {"goods_name": goods_name_list[i], "brand_name": brand_name_list[i], "encap": encap_list[i], "key": i+1}
            data_json.append(data)
        opapi_map_goods_body["data"] = json.dumps(data_json)
        data_llist = json.loads(opapi_map_goods_body["data"])
        data_loads_json = {}
        data_loads_json["data"] = data_llist
        print(f"此时入参：" + json.dumps(data_loads_json, indent=4, ensure_ascii=False).replace("'", '"'))
        opapi_map_goods_res = self.rss.post(url=opapi_map_goods_url, data=opapi_map_goods_body, headers=self.headers).json()
        print("此时匹配结果：" + json.dumps(opapi_map_goods_res, indent=4, ensure_ascii=False).replace("'", '"'))
        return data_loads_json, opapi_map_goods_res

if __name__ == '__main__':
    GoodsProfileObtain(goods_name="CRCW04024K70FKEDHP", brand_name="Vishay", goods_id="1111111", encap="0402").opapi_map_goods()
