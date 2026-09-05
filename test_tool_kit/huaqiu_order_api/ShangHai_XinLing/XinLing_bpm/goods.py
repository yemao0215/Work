import json
import math
import re

from urllib.parse import quote

import jsonpath
import pandas
import pandas as pd
import requests
import yaml

from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_path import yaml_file, account_yaml, xl_brand_dir, xlsx_dos_brand_dir, xl_dos_brand_dir, \
    xl_create_goods_dir


class XLBpmGoods:

    def __init__(self, goods_name=None, provider_name=None, custom_cat_name=None, package=None, vendorId=None, xl_cat_name=None):

        self.rss = requests.Session()
        self.json_head = {
  'Accept': 'application/json, text/plain, */*',
  'Accept-Language': 'zh-CN,zh;q=0.9',
  'Authorization': 'Bearer eyJhbGciOiJIUzUxMiJ9.eyJqdGkiOiJhODZlNGU5OGZlNjM0NjhkOGM2ZTVjZjMzZTk3ZTFiYyIsInVzZXIiOiJhZG1pbiIsInN1YiI6ImFkbWluIn0.r9KWO9ZYAP7cGbusQaX7sDLf2OdO7-J0FRVa8jX25TspbnoXTZ9z-oSASiiDzslXWsUhCNW-8J891JWsBM7PNg',
  'Connection': 'keep-alive',
  'Referer': 'http://47.100.4.100/metadata/manufacturer',
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
}
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.ShangHai_XinLing_admin_URL = data["ShangHai_XinLing_admin_URL"]
        self.ShangHai_XinLing_reception_URL = data["ShangHai_XinLing_reception_URL"]
        self.ShangHai_XinLing_BPM_URL = data["ShangHai_XinLing_BPM_URL"]
        self.courier_number = data["courier_number"]
        with open(account_yaml, 'r', encoding='utf-8') as yamlfile:
            account = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.goods_name = goods_name
        self.provider_name = provider_name
        self.cat_name = custom_cat_name
        self.package = package
        self.vendorId = vendorId
        self.xl_cat_name = xl_cat_name
        self.token = account["ShangHai_XinLing"]["bpm_token"]
        self.json_head['Authorization'] = self.token
        self.files = [
            ('file', ('芯灵资料创建导入模板.xlsx', open(xl_create_goods_dir, 'rb'),
                      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'))]
        self.headers = {"Content-Type": "application/x-www-form-urlencoded",
                        "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://www.huaqiu.com)"
                        }

    def query_url_arguments(self, data):
        """将body参数转换成可拼接至url的参数"""
        lt = []
        for k, v in data.items():
            lt.append(k + '=' + quote(str(v), safe=''))
        # 这个是在for循环外面的，就是将列表的元素之间用用&符号连接起来
        query_string = '&'.join(lt)
        return query_string

    def scan_special_characters(self, input_string):
        # 定义特殊字符的正则表达式
        special_chars = r'[@_!#$%^&*()<>?/\|}{~:，。、-]'

        # 使用正则表达式匹配特殊字符并分割
        result = re.split(special_chars, input_string)

        # 移除空格、None和NULL等无效项
        cleaned_result = [item for item in result if item and item != "NULL" and item != "None"]

        return cleaned_result
    def excel_file_write(self):
        """更新文件里面型号、品牌、类目、封装"""
        data = {
            "mpn": [self.goods_name],
            "manufacturer": [self.provider_name],
            "category": [self.cat_name],
            "attr.package": [self.package],
        }
        logger.info(f"开始写入表格数据，表格数据为 {data}")
        df = pd.DataFrame(data)
        # 保存为Excel文件，不包含索引列
        df.to_excel(xl_create_goods_dir, index=False)
        logger.info(f"开始写入表格数据data成功")
        return self
    def xl_fdatasheets_goods_search(self):
        """芯灵前台型号查询"""
        xl_fdatasheets_goods_search_url_Header = "{}/api/chiplet/products/queryHeader".format(self.ShangHai_XinLing_reception_URL)
        xl_fdatasheets_goods_search_body_Header = {"desc": self.goods_name}
        xl_fdatasheets_goods_search_res_Header = self.rss.post(url=xl_fdatasheets_goods_search_url_Header,
                                                        json=xl_fdatasheets_goods_search_body_Header,
                                                        headers=self.json_head).json()
        if xl_fdatasheets_goods_search_res_Header['result']['matchCount'] == 0:
            logger.info("没有找到商品")
            return False
        else:
            xl_fdatasheets_goods_search_url_Page = "{}/api/chiplet/products/queryPage".format(self.ShangHai_XinLing_reception_URL)
            fdatasheets_goods_mfg_category_json_count = []

            if xl_fdatasheets_goods_search_res_Header['result']['matchCount'] > 50:
                num = math.ceil(int(xl_fdatasheets_goods_search_res_Header['result']['matchCount']) / 50)
                for i in range(num):
                    xl_fdatasheets_goods_search_body_Page = {"page": i + 1, "pageSize": 50, "desc": self.goods_name}
                    xl_fdatasheets_goods_search_res_Page = requests.post(xl_fdatasheets_goods_search_url_Page,
                                                                           json=xl_fdatasheets_goods_search_body_Page,
                                                                           headers=self.json_head).json()
                    xl_fdatasheets_goods_name = jsonpath.jsonpath(xl_fdatasheets_goods_search_res_Page, "$..mpn")
                    xl_fdatasheets_category = jsonpath.jsonpath(xl_fdatasheets_goods_search_res_Page, "$..category")
                    xl_fdatasheets_manufacturer = jsonpath.jsonpath(xl_fdatasheets_goods_search_res_Page, "$..manufacturer")
                    for a in range(len(xl_fdatasheets_goods_name)):
                        fdatasheets_goods_mfg_category_json = {xl_fdatasheets_goods_name[a]: (xl_fdatasheets_manufacturer[a], xl_fdatasheets_category[a])}
                        fdatasheets_goods_mfg_category_json_count.append(fdatasheets_goods_mfg_category_json)
            else:
                xl_fdatasheets_goods_search_body_Page = {"page": 1, "pageSize": 50, "desc": self.goods_name}
                xl_fdatasheets_goods_search_res_Page = requests.post(xl_fdatasheets_goods_search_url_Page,
                                                                     json=xl_fdatasheets_goods_search_body_Page,
                                                                     headers=self.json_head).json()
                xl_fdatasheets_goods_name = jsonpath.jsonpath(xl_fdatasheets_goods_search_res_Page, "$..mpn")
                xl_fdatasheets_category = jsonpath.jsonpath(xl_fdatasheets_goods_search_res_Page, "$..category")
                xl_fdatasheets_manufacturer = jsonpath.jsonpath(xl_fdatasheets_goods_search_res_Page, "$..manufacturer")
                for a in range(len(xl_fdatasheets_goods_name)):
                    fdatasheets_goods_mfg_category_json = {
                        xl_fdatasheets_goods_name[a]: (xl_fdatasheets_manufacturer[a], xl_fdatasheets_category[a])}
                    fdatasheets_goods_mfg_category_json_count.append(fdatasheets_goods_mfg_category_json)
            if self.xl_cat_name == None:

            for b in fdatasheets_goods_mfg_category_json_count:
                for k, v in b.items():
                    if k == self.goods_name and v[0] == self.provider_name and v[1] == self.xl_cat_name:
                        return True
                    break
            return False


    def xl_bpm_goods_elxcel_file(self):
        xl_bpm_goods_elxcel_file_url = "{}/dev-api/outside/upload/excel?vendorId={}".format(self.ShangHai_XinLing_BPM_URL, self.vendorId)
        xl_bpm_goods_elxcel_file_res = self.rss.post(url=xl_bpm_goods_elxcel_file_url, files=self.files).json()
        if xl_bpm_goods_elxcel_file_res["message"] == "sucess":
            logger.info(f"成功上传文件，上传文件结果为 {xl_bpm_goods_elxcel_file_res}")
            return True
        else:
            logger.error(f"上传文件失败，上传文件结果为 {xl_bpm_goods_elxcel_file_res}")
            return False
    def xl_bpm_goods_assetName(self):
        xl_bpm_goods_assetName_body = {"pageNum": 1, "pageSize": 50}
        xl_bpm_goods_assetName_body_conversion = self.query_url_arguments(xl_bpm_goods_assetName_body)
        xl_bpm_goods_assetName_url = "{}/dev-api/workflow/process/ownList?{}".format(self.ShangHai_XinLing_BPM_URL, xl_bpm_goods_assetName_body_conversion)

        xl_bpm_goods_assetName_res = self.rss.get(url=xl_bpm_goods_assetName_url,
                                                  headers=self.json_head,
                                                  ).json()
        assetName = jsonpath.jsonpath(xl_bpm_goods_assetName_res, "$..assetName")[0]
        taskName = jsonpath.jsonpath(xl_bpm_goods_assetName_res, "$..taskName")[0]
        proInstanceId = jsonpath.jsonpath(xl_bpm_goods_assetName_res, "$..proInstanceId")[0]
        print(taskName)
        if taskName == None:
            logger.info(f"创建成功，流程名称为 {assetName}")
        else:
            logger.info(f"存在待映射操作项，流程名称为 {taskName}")
        return proInstanceId

    def xl_bpm_goods_mfg_mapp(self, proInstance_id=None):
        """品牌映射-当前节点为mfg映射"""
        global positioning_mfg_name_list
        xl_bpm_goods_pipeline_positioning_url = "{}/dev-api/outside/errorAlias/todoList?aliasType=1".format(self.ShangHai_XinLing_BPM_URL)
        xl_bpm_goods_pipeline_positioning_res = self.rss.get(url=xl_bpm_goods_pipeline_positioning_url,
                                                  headers=self.json_head,
                                                  ).json()
        proInstanceId = jsonpath.jsonpath(xl_bpm_goods_pipeline_positioning_res, "$..proInstanceId")
        if proInstance_id in proInstanceId:
            xl_bpm_goods_mfg_mapp_search_original_url = "{}/dev-api/outside/errorAlias/page?page=0&pageSize=40&proInstanceId={}&aliasType=1".format(self.ShangHai_XinLing_BPM_URL, proInstance_id)
            xl_bpm_goods_mfg_mapp_search_original_res = self.rss.get(url=xl_bpm_goods_mfg_mapp_search_original_url,
                                                                 headers=self.json_head,
                                                                 ).json()
            total = jsonpath.jsonpath(xl_bpm_goods_mfg_mapp_search_original_res, "$..total")[0]
            num = math.ceil(int(total) / 40)
            positioning_mfg_name = []
            positioning_mfg_id = []
            positioning_mfg_name_json_list = []
            if num > 1:
                for i in range(num):
                    i = i - 1
                    xl_bpm_goods_mfg_mapp_search_original_url = "{}/dev-api/outside/errorAlias/page?page={}&pageSize=40&proInstanceId={}&aliasType=1".format(
                        self.ShangHai_XinLing_BPM_URL, i, proInstance_id)
                    xl_bpm_goods_mfg_mapp_search_original_res = self.rss.get(url=xl_bpm_goods_mfg_mapp_search_original_url,
                                                                    headers=self.json_head,
                                                                    ).json()
                    positioning_mfg_name_original = jsonpath.jsonpath(xl_bpm_goods_mfg_mapp_search_original_res, "$..alias")
                    positioning_mfg_id_original = jsonpath.jsonpath(xl_bpm_goods_mfg_mapp_search_original_res, "$..id")
                    positioning_mfg_name = positioning_mfg_name + positioning_mfg_name_original
                    positioning_mfg_id = positioning_mfg_id + positioning_mfg_id_original
            else:
                positioning_mfg_name = jsonpath.jsonpath(xl_bpm_goods_mfg_mapp_search_original_res, "$..alias")
                positioning_mfg_id = jsonpath.jsonpath(xl_bpm_goods_mfg_mapp_search_original_res, "$..id")
            for i in range(len(positioning_mfg_name)):
                positioning_mfg_name_list = self.scan_special_characters(positioning_mfg_name[i])
                positioning_mfg_name_json = {positioning_mfg_name[i]: (positioning_mfg_name_list, positioning_mfg_id[i])}
                positioning_mfg_name_json_list.append(positioning_mfg_name_json)
            print(positioning_mfg_name_json_list)
            brand_id = None
            brand_name = None
            brand_original_local_id = []
            for j in positioning_mfg_name_json_list:
                for k, v in j.items():
                    for v1 in v[0]:
                        logger.info(f"开始查找{k}映射品牌，用拆词：{v1}")
                        xl_bpm_goods_mfg_mapp_search_local_url = "{}/dev-api/outside/manufacturer/page?page=0&pageSize=40&name={}".format(self.ShangHai_XinLing_BPM_URL, v1)
                        xl_bpm_goods_mfg_mapp_search_local_res = self.rss.get(url=xl_bpm_goods_mfg_mapp_search_local_url,
                                                                            headers=self.json_head,
                                                                            ).json()
                        if int(jsonpath.jsonpath(xl_bpm_goods_mfg_mapp_search_local_res, "$..total")[0]) > 0:
                            displayName = jsonpath.jsonpath(xl_bpm_goods_mfg_mapp_search_local_res, "$..displayName")
                            shortName = jsonpath.jsonpath(xl_bpm_goods_mfg_mapp_search_local_res, "$..shortName")
                            id = jsonpath.jsonpath(xl_bpm_goods_mfg_mapp_search_local_res, "$..id")
                            for i in range(len(displayName)):
                                if re.match('^[a-zA-Z]+$', v1):  # 纯英文
                                    if v1 == displayName[i]:
                                        brand_id = id[i]
                                        brand_name = shortName[i]
                                        logger.info(f"{k}映射品牌为：{v1}，品牌id：{id[i]}, 简短名称为：{shortName[i]}")
                                    elif v1 == displayName[i].lower():
                                        brand_id = id[i]
                                        brand_name = shortName[i]
                                        logger.info(f"{k}映射品牌为：{v1}，品牌id：{id[i]}, 简短名称为：{shortName[i]}")
                                    elif v1 == displayName[i].upper():
                                        brand_id = id[i]
                                        brand_name = shortName[i]
                                        logger.info(f"{k}映射品牌为：{v1}，品牌id：{id[i]}, 简短名称为：{shortName[i]}")
                                    elif v1.lower() == displayName[i].lower():
                                        brand_id = id[i]
                                        brand_name = shortName[i]
                                        logger.info(f"{k}映射品牌为：{v1}，品牌id：{id[i]}, 简短名称为：{shortName[i]}")
                                    elif v1.upper() == displayName[i].upper():
                                        brand_id = id[i]
                                        brand_name = shortName[i]
                                        logger.info(f"{k}映射品牌为：{v1}，品牌id：{id[i]}, 简短名称为：{shortName[i]}")
                                else:
                                    if v1 == displayName[i]:
                                        brand_id = id[i]
                                        brand_name = shortName[i]
                                        logger.info(f"{k}映射品牌为：{v1}，品牌id：{id[i]}, 简短名称为：{shortName[i]}")
                        if brand_id:
                            brand_original_local_id_json = {k: [v[1], brand_id, brand_name]}
                            brand_original_local_id.append(brand_original_local_id_json)
                            break
            if brand_original_local_id:
                for i in brand_original_local_id:
                    for k, v in i.items():
                        xl_bpm_goods_mfg_mapp_url = "{}/dev-api/outside/errorAlias/mapping".format(self.ShangHai_XinLing_BPM_URL)
                        xl_bpm_goods_mfg_mapp_body = {
                            "aliasType": k,
                            "ids": [v[0]],
                            "proInstanceId": proInstance_id,
                            "shortName": v[2],
                        }
                        xl_bpm_goods_mfg_mapp_res = self.rss.post(url=xl_bpm_goods_mfg_mapp_url,
                                                                headers=self.json_head,
                                                                json=xl_bpm_goods_mfg_mapp_body).json()
                        if xl_bpm_goods_mfg_mapp_res["message"] == "success":
                            logger.info(f"{k}映射{v[2]}成功")
                        else:
                            logger.info(f"{k}映射{v[2]}失败")
        return self

    def xl_bpm_goods_cate_mapp(self, proInstance_id=None):
        """分类映射-当前节点为cate映射"""
        global positioning_cate_name_list
        xl_bpm_goods_pipeline_positioning_url = "{}/dev-api/outside/errorAlias/todoList?aliasType=2".format(self.ShangHai_XinLing_BPM_URL)
        xl_bpm_goods_pipeline_positioning_res = self.rss.get(url=xl_bpm_goods_pipeline_positioning_url,
                                                  headers=self.json_head,
                                                  ).json()
        proInstanceId = jsonpath.jsonpath(xl_bpm_goods_pipeline_positioning_res, "$..proInstanceId")
        if proInstance_id in proInstanceId:
            xl_bpm_goods_cate_mapp_search_original_url = "{}/dev-api/outside/errorAlias/page?page=0&pageSize=40&proInstanceId={}&aliasType=2".format(
                self.ShangHai_XinLing_BPM_URL, proInstance_id)
            xl_bpm_goods_cate_mapp_search_original_res = self.rss.get(url=xl_bpm_goods_cate_mapp_search_original_url,
                                                                     headers=self.json_head,
                                                                     ).json()
            total = jsonpath.jsonpath(xl_bpm_goods_cate_mapp_search_original_res, "$..total")[0]
            num = math.ceil(int(total) / 40)
            positioning_cate_name = []
            positioning_cate_id = []
            positioning_cate_name_json_list = []
            if num > 1:
                for i in range(num):
                    i = i - 1
                    xl_bpm_goods_cate_mapp_search_original_url = "{}/dev-api/outside/errorAlias/page?page={}&pageSize=40&proInstanceId={}&aliasType=2".format(
                        self.ShangHai_XinLing_BPM_URL, i, proInstance_id)
                    xl_bpm_goods_cate_mapp_search_original_res = self.rss.get(
                        url=xl_bpm_goods_cate_mapp_search_original_url,
                        headers=self.json_head,
                        ).json()
                    positioning_cate_name_original = jsonpath.jsonpath(xl_bpm_goods_cate_mapp_search_original_res,
                                                                      "$..alias")
                    positioning_cate_id_original = jsonpath.jsonpath(xl_bpm_goods_cate_mapp_search_original_res, "$..id")
                    positioning_cate_name = positioning_cate_name + positioning_cate_name_original
                    positioning_cate_id = positioning_cate_id + positioning_cate_id_original
            else:
                positioning_cate_name = jsonpath.jsonpath(xl_bpm_goods_cate_mapp_search_original_res, "$..alias")
                positioning_cate_id = jsonpath.jsonpath(xl_bpm_goods_cate_mapp_search_original_res, "$..id")
            for i in range(len(positioning_cate_name)):
                positioning_cate_name_list = self.scan_special_characters(positioning_cate_name[i])
                positioning_mfg_name_json = {positioning_cate_name[i]: (positioning_cate_name_list, positioning_cate_id[i])}
                positioning_cate_name_json_list.append(positioning_mfg_name_json)
            print(positioning_cate_name_json_list)
            cate_id = None
            cat_name = None
            cat_original_local_id = []
            for j in positioning_cate_name_json_list:
                for k, v in j.items():
                    for v1 in v[0]:
                        logger.info(f"开始查找{k}映射分类，用拆词：{v1}")
                        xl_bpm_goods_cate_mapp_search_local_body = {
                            "name": v1,
                            "page": 0,
                            "pageSize": 40
                        }
                        xl_bpm_goods_cate_mapp_search_local_body_arguments = self.query_url_arguments(xl_bpm_goods_cate_mapp_search_local_body)
                        xl_bpm_goods_cate_mapp_search_local_url = "{}/dev-api/outside/category/page?{}".format(self.ShangHai_XinLing_BPM_URL, xl_bpm_goods_cate_mapp_search_local_body_arguments)
                        xl_bpm_goods_mfg_mapp_search_local_res = self.rss.get(url=xl_bpm_goods_cate_mapp_search_local_url,
                                                                            headers=self.json_head,
                                                                            ).json()
                        if int(jsonpath.jsonpath(xl_bpm_goods_mfg_mapp_search_local_res, "$..total")[0]) > 0:
                            cat_name = jsonpath.jsonpath(xl_bpm_goods_mfg_mapp_search_local_res, "$..name")
                            cat_name_cn = jsonpath.jsonpath(xl_bpm_goods_mfg_mapp_search_local_res, "$..nameCn")
                            cat_id = jsonpath.jsonpath(xl_bpm_goods_mfg_mapp_search_local_res, "$..id")
                            for i in range(len(cat_name)):
                                if v1 == cat_name_cn[i]:
                                    cate_id = cat_id[i]
                                    cat_name = cat_name[i]
                                    logger.info(
                                        f"{k}映射类目为：{cat_name_cn}，类目id：{cate_id}, 英文名称为：{cat_name[i]}")
                        else:
                            if "电阻" in v1:
                                xl_bpm_goods_cate_mapp_search_local_body = {
                                    "name": "贴片电阻",
                                    "page": 0,
                                    "pageSize": 40
                                }
                                xl_bpm_goods_cate_mapp_search_local_body_arguments = self.query_url_arguments(xl_bpm_goods_cate_mapp_search_local_body)
                                xl_bpm_goods_cate_mapp_search_local_url = "{}/dev-api/outside/category/page?{}".format(
                                    self.ShangHai_XinLing_BPM_URL, xl_bpm_goods_cate_mapp_search_local_body_arguments)
                                xl_bpm_goods_mfg_mapp_search_local_res = self.rss.get(url=xl_bpm_goods_cate_mapp_search_local_url,headers=self.json_head,).json()
                                if int(jsonpath.jsonpath(xl_bpm_goods_mfg_mapp_search_local_res, "$..total")[0]) > 0:
                                    cat_name = jsonpath.jsonpath(xl_bpm_goods_mfg_mapp_search_local_res, "$..name")
                                    cat_name_cn = jsonpath.jsonpath(xl_bpm_goods_mfg_mapp_search_local_res, "$..nameCn")
                                    cat_id = jsonpath.jsonpath(xl_bpm_goods_mfg_mapp_search_local_res, "$..id")
                                    for i in range(len(cat_name)):
                                        if "贴片电阻" == cat_name_cn[i]:
                                            cate_id = cat_id[i]
                                            cat_name = cat_name[i]
                                            logger.info(f"{k}映射类目为：贴片电阻，类目id：{cate_id}, 英文名称为：{cat_name_cn[i]}")
                        if cate_id:
                            cat_original_local_id_json = {k: [v[1], cate_id, cat_name]}
                            cat_original_local_id.append(cat_original_local_id_json)
                            break
            if cat_original_local_id:
                for i in cat_original_local_id:
                    for k, v in i.items():
                        xl_bpm_goods_mfg_mapp_url = "{}/dev-api/outside/errorAlias/mapping".format(self.ShangHai_XinLing_BPM_URL)
                        xl_bpm_goods_mfg_mapp_body = {
                            "aliasType": k,
                            "ids": [v[0]],
                            "proInstanceId": proInstance_id,
                            "shortName": v[2],
                        }
                        xl_bpm_goods_mfg_mapp_res = self.rss.post(url=xl_bpm_goods_mfg_mapp_url,
                                                                headers=self.json_head,
                                                                json=xl_bpm_goods_mfg_mapp_body).json()
                        if xl_bpm_goods_mfg_mapp_res["message"] == "success":
                            logger.info(f"{k}映射{v[2]}成功")
                        else:
                            logger.info(f"{k}映射{v[2]}失败")
        return self

    def xl_bpm_goods_attr_mapp(self, proInstance_id=None):
        """分类映射-当前节点为attr映射"""
        global positioning_attr_name_list
        xl_bpm_goods_pipeline_positioning_url = "{}/dev-api/outside/errorAlias/todoList?aliasType=2".format(self.ShangHai_XinLing_BPM_URL)



if __name__ == '__main__':
    proInstance_id = "c40f0b5b-6e04-11f0-b514-a2feb16c8448"
    xl_bpm_goods = XLBpmGoods(goods_name="ERG25V330M8X12", provider_name="Yageo", custom_cat_name="陶瓷电容", package="0603", vendorId="74", xl_cat_name="Ceramic Capacitors")
    # xl_bpm_goods.excel_file_write()
    # xl_bpm_goods.xl_bpm_goods_cate_mapp(proInstance_id=proInstance_id)
    # a = xl_bpm_goods.scan_special_characters(proInstance_id)
    r = xl_bpm_goods.xl_fdatasheets_goods_search()
    print(r)
    # print(a)