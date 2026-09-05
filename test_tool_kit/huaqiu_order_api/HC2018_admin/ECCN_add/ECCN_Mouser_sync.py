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


class EccnMouserSync:
    def __init__(self, goods_name=None, brand_name=None, eccn=None):
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.HC2018_ADMIN_URL = data['HC2018_ADMIN_URL']
        self.headers = {"Content-Type": "application/x-www-form-urlencoded"}
        self.form_head = {'User-Agent': 'HQCHIP OpenAPI Python-SDK/1.0', "X-Request-Version": '1.0'}
        self.headers_json = {"Content-Type": "application/json"}
        self.goods_name = goods_name
        self.brand_name = brand_name
        self.eccn = eccn
        self.rss = requests.Session()


    def eccn_mouser_sync(self):
        """mousr的ECCN编码同步"""
        if "uat" in self.HC2018_ADMIN_URL:
            self.sign = "f9498bc27e3be5a0aed8c9401abca645"
        if "fat" in self.HC2018_ADMIN_URL:
            self.sign = "f9498bc27e3be5a0aed8c9401abca645"
        self.timestamp = int(time.time())
        params = {'timestamp': self.timestamp, "appid": "hqchip_erp_sync", "sign_type": "md5"}
        data = {"goods_name": self.goods_name, "brand_name": self.brand_name, "eccn": self.eccn}
        params['signature'] = OpenapiSignature(self.sign).hqchip_sign_main(params, data)

        eccn_mouser_sync_url = "{}/openapi/GoodsOpen/matchAndUpdateGoodsEccn".format(self.HC2018_ADMIN_URL)
        eccn_mouser_sync_res = self.rss.post(url=eccn_mouser_sync_url, params=params, data=data, headers=self.form_head,timeout=10).json()
        logger.info(eccn_mouser_sync_res)
        self.msg = eccn_mouser_sync_res["retMsg"]
        return self
    def eccn_mouser_sync_result_search(self):
        """mousr的ECCN编码同步以及命中规则"""
        result_eccn_sync = ''
        # self.msg = "操作成功"
        if self.msg == "操作成功":
            self.rss = Login().login()
            auth_token = getattr(Data, "dos_auth_token")
            self.headers["Authorization"] = auth_token
            self.headers_json["Authorization"] = auth_token
            goods_means_url = "{}/v1/goods/DgkGoods/findList".format(self.HC2018_ADMIN_URL)
            goods_means_body = {"page": 1, "per_page": 100, "is_on_sale": "-1", "has_stock": "-1", "self_status": "-1",
                                "complete_type": "-1","search_type": "2", "goods_name": self.goods_name}
            goods_means_res = self.rss.post(url=goods_means_url, json=goods_means_body, headers=self.headers_json).json()
            goods_eccn = jsonpath.jsonpath(goods_means_res, "$..goods_eccn")[0]
            brand_id_list = jsonpath.jsonpath(goods_means_res, "$..brand_id")
            brand_name_list = jsonpath.jsonpath(goods_means_res, "$..provider_name")
            brand_id = ""
            for a in range(len(brand_name_list)):
                if brand_name_list[a] == self.brand_name:
                    # logger.info(111)
                    brand_id = brand_id_list[a]
            if brand_id == "":
                brand_id = brand_id_list[0]
            brand_search_url = "{}/v1/goods/DgkBrand/brandList".format(self.HC2018_ADMIN_URL)
            brand_search_body = {"page": 1, "per_page": 100, "brand_id": brand_id, "brand_type": 1, "is_exact": "0", "type": "0"}
            brand_search_res = self.rss.post(url=brand_search_url, json=brand_search_body, headers=self.headers_json).json()
            brand_search_id = jsonpath.jsonpath(brand_search_res, "$..brand_id")
            pns_main_brand_name = jsonpath.jsonpath(brand_search_res, "$..pns_main_brand_name")
            pns_main_brand_id = jsonpath.jsonpath(brand_search_res, "$..pns_main_brand_id")
            brand_name = jsonpath.jsonpath(brand_search_res, "$..brand_name")
            for i in range(len(brand_name)):
                # logger.info(112)
                # 判断品牌名是否一致
                if brand_name[i] == self.brand_name:
                    result_eccn_sync = f"同步成功，此时ECCN: {goods_eccn}, 命中验证规则： 型号+品牌"
                    logger.info(result_eccn_sync)
                    break
                else:
                    # 判断品牌为主品牌
                    # logger.info(117)
                    if pns_main_brand_name[i] == self.brand_name:
                        result_eccn_sync = f"同步成功，此时ECCN: {goods_eccn}, 命中验证规则： 型号+主品牌"
                        logger.info(result_eccn_sync)
                        break
                    else:
                        # logger.info(113)
                        for m in brand_search_id:
                            # 判断品牌为从品牌
                            brand_zc_url = "{}/v1/goods/DgkBrand/getRelationList".format(self.HC2018_ADMIN_URL)
                            brand_zc_body = {"brand_id": m}
                            brand_zc_res = self.rss.post(url=brand_zc_url, json=brand_zc_body, headers=self.headers_json).json()
                            if brand_zc_res["data"] != []:
                                # logger.info(114)
                                brand_zc_name = jsonpath.jsonpath(brand_zc_res, "$..brand_name")
                                # logger.info(brand_zc_name)
                                for n in brand_zc_name:
                                    if n == self.brand_name:
                                        result_eccn_sync = f"同步成功，此时ECCN: {goods_eccn}, 命中验证规则： 型号+从品牌"
                                        logger.info(result_eccn_sync)
                                        break
                                    else:
                                        # logger.info(118)
                                        brand_search_detail_url = "{}/v1/goods/DgkBrand/brandEdit".format(
                                            self.HC2018_ADMIN_URL)
                                        brand_search_detail_body = {"id": m}
                                        brand_search_detail_res = self.rss.post(url=brand_search_detail_url,
                                                                                json=brand_search_detail_body,
                                                                                headers=self.headers_json).json()
                                        brand_other_name = jsonpath.jsonpath(brand_search_detail_res, "$..brand_other_name")[0]
                                        if self.brand_name in brand_other_name:
                                            result_eccn_sync = f"同步成功，此时ECCN: {goods_eccn}, 命中验证规则： 型号+品牌别名"
                                            logger.info(result_eccn_sync)
                                            break

                            elif brand_zc_res["data"] == [] and pns_main_brand_name[i] != '':
                                # logger.info(115)
                                brand_zc_body['brand_id'] = pns_main_brand_id[i]
                                brand_zc_res = self.rss.post(url=brand_zc_url, json=brand_zc_body, headers=self.headers_json).json()
                                if brand_zc_res["data"] != []:
                                    brand_zc_name = jsonpath.jsonpath(brand_zc_res, "$..brand_name")
                                    for n in brand_zc_name:
                                        if n == self.brand_name:
                                            result_eccn_sync = f"同步成功，此时ECCN: {goods_eccn}, 命中验证规则： 型号+从品牌"
                                            logger.info(result_eccn_sync)
                                            break
                                else:
                                    # logger.info(118)
                                    brand_search_detail_url = "{}/v1/goods/DgkBrand/brandEdit".format(
                                        self.HC2018_ADMIN_URL)
                                    brand_search_detail_body = {"id": m}
                                    brand_search_detail_res = self.rss.post(url=brand_search_detail_url,
                                                                            json=brand_search_detail_body,
                                                                            headers=self.headers_json).json()
                                    brand_other_name = jsonpath.jsonpath(brand_search_detail_res, "$..brand_other_name")[0]
                                    if self.brand_name in brand_other_name:
                                        result_eccn_sync = f"同步成功，此时ECCN: {goods_eccn}, 命中验证规则： 型号+品牌别名"
                                        logger.info(result_eccn_sync)
                                        break
                            else:
                                # 验证品牌别名
                                # logger.info(116)
                                brand_search_detail_url = "{}/v1/goods/DgkBrand/brandEdit".format(self.HC2018_ADMIN_URL)
                                brand_search_detail_body = {"id": m}
                                brand_search_detail_res = self.rss.post(url=brand_search_detail_url, json=brand_search_detail_body, headers=self.headers_json).json()
                                brand_other_name = jsonpath.jsonpath(brand_search_detail_res, "$..brand_other_name")[0]
                                if self.brand_name in brand_other_name:
                                    result_eccn_sync = f"同步成功，此时ECCN: {goods_eccn}, 命中验证规则： 型号+品牌别名"
                                    logger.info(result_eccn_sync)
                                    break
        else:
             logger.error(f"同步失败")
        return result_eccn_sync
if __name__ == '__main__':
    EccnMouserSync("SN74LVC04AD", "Texas Instruments", "EAR99").eccn_mouser_sync().eccn_mouser_sync_result_search()