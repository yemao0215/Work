import json
import math
import re
import time

import jsonpath
import pandas as pd
import yaml

from huaqiu_order_api.HC2018_admin.login.login import Login
# from xpinyin import Pinyin
from huaqiu_order_api.common.loguru_logger import logger
import requests

from huaqiu_order_api.common.my_path import stockup_dir, yaml_file, xlsx_dos_brand_dir

from huaqiu_order_api.common.my_data import Data


class DgkBrand:
    # 分类
    def __init__(self, rss, brand_name=None, brand_name_cn=None, brand_name_en_long=None, brand_name_cn_long=None):
        """
        :param brand_name:  品牌英文简称
        :param brand_name_cn:  品牌中文简称
        :param brand_name_en_long:  品牌英文全称
        :param brand_name_cn_long 品牌中文全称
        """
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.HC2018_ADMIN_URL = data['HC2018_ADMIN_URL']
        self.brand_name = brand_name
        self.rss = rss
        self.brand_name_cn = brand_name_cn
        self.auth_token = getattr(Data, 'dos_auth_token')
        self.brand_name_en_long = brand_name_en_long
        self.brand_name_cn_long = brand_name_cn_long
        self.headers = {"Content-Type":"application/json;charset=UTF-8"}
        self.headers_form = {"Content-Type":"application/x-www-form-urlencoded;charset=UTF-8"}
        self.headers["Authorization"] = self.auth_token

    def brand_search(self, brand_name=None, status=None):
        """品牌查询"""
        if brand_name == None:
            brand_name = self.brand_name
        search_url = "{}/v1/goods/DgkBrand/brandList".format(self.HC2018_ADMIN_URL)
        search_body = {"brand_name": brand_name, "brand_type": "1", "is_exact": "0", "is_use": "",
                       "type": "0", "page": 1, "per_page": 100}
        if status != None:
            search_body["is_use"] = status
        search_res = self.rss.post(url=search_url, json=search_body, headers=self.headers).json()
        listInfo = jsonpath.jsonpath(search_res, "$..list")[0]
        if listInfo != []:
            brand_id = jsonpath.jsonpath(search_res, "$..brand_id")
            brand_name = jsonpath.jsonpath(search_res, "$..brand_name")
            for i in range(len(brand_name)):
                if brand_name[i] == self.brand_name:
                    self.brand_id = brand_id[i]

        return self.brand_id

    def brand_search_new(self, brand_name=None, status=None):
        """品牌查询"""
        if brand_name == None:
            brand_name = self.brand_name
        search_url = "{}/v1/goods/DgkBrand/brandList".format(self.HC2018_ADMIN_URL)
        search_body = {"brand_name": brand_name, "brand_type": "1", "is_exact": "0", "is_use": "",
                       "type": "0", "page": 1, "per_page": 100}
        if status != None:
            search_body["is_use"] = status
        search_res = self.rss.post(url=search_url, json=search_body, headers=self.headers).json()
        # print(search_res)
        total = jsonpath.jsonpath(search_res, "$..total")[0]
        self.brand_id_name_count = []
        if int(total) / 100 > 1:
            number = math.ceil(int(total) / 100)
            for i in range(number):
                search_body["page"] = i + 1
                search_res = self.rss.post(url=search_url, json=search_body, headers=self.headers).json()
                brand_id = jsonpath.jsonpath(search_res, "$..brand_id")
                brand_name = jsonpath.jsonpath(search_res, "$..brand_name")
                brand_name_cn = jsonpath.jsonpath(search_res, "$..brand_cn")
                pns_mian_id = jsonpath.jsonpath(search_res, "$..pns_main_brand_id")
                is_delete = jsonpath.jsonpath(search_res, "$..is_delete")
                global_operation_status = jsonpath.jsonpath(search_res, "$..global_operation_status")
                for a in range(len(brand_name)):
                    if pns_mian_id[a] == "" and global_operation_status[a] != "3" and is_delete[a] == "0":
                        data = {"brand_id": brand_id[a], "brand_name": brand_name[a], "brand_cn": brand_name_cn[a]}
                        self.brand_id_name_count.append(data)
        else:
            if len(search_res['data']["list"]) == 0:
                return None
            brand_id = jsonpath.jsonpath(search_res, "$..brand_id")
            brand_name = jsonpath.jsonpath(search_res, "$..brand_name")
            brand_name_cn = jsonpath.jsonpath(search_res, "$..brand_cn")
            pns_mian_id = jsonpath.jsonpath(search_res, "$..pns_main_brand_id")
            is_delete = jsonpath.jsonpath(search_res, "$..is_delete")
            global_operation_status = jsonpath.jsonpath(search_res, "$..global_operation_status")
            for a in range(len(brand_name)):
                if pns_mian_id[a] == "" and global_operation_status[a] != "3" and is_delete[a] == "0":
                    data = {"brand_id": brand_id[a], "brand_name": brand_name[a], "brand_cn": brand_name_cn[a]}
                    self.brand_id_name_count.append(data)
        print(self.brand_id_name_count)
        return self.brand_id_name_count

    def brand_add(self):
        """品牌新增"""
        # 检测brand_name是否可用
        checkBrandName_url = "{}/v1/goods/DgkBrand/checkBrandName".format(self.HC2018_ADMIN_URL)
        checkBrandName_body = {"brand_name": self.brand_name}
        print(f"品牌名称检测入参参数：{checkBrandName_body}")
        checkBrandName_res = self.rss.post(url=checkBrandName_url, json=checkBrandName_body, headers=self.headers).json()
        print(checkBrandName_res)
        msg = checkBrandName_res["msg"]
        if msg == "名称可用":
            brand_add_url = "{}/v1/goods/DgkBrand/brandInsert".format(self.HC2018_ADMIN_URL)
            brand_add_body = {"brand_name": self.brand_name, "brand_cn": self.brand_name_cn, "brand_en_long": self.brand_name_en_long,
                              "brand_cn_long": self.brand_name_cn_long, "is_hot": "0", "is_new": "0", "is_show": "0", "is_use": "0",
                              "location_type": "0", "brand_attr": "1", "brand_desc": "自动化测试品牌", "brand_desc_en": "autotestBrand",
                              "brand_id": "", "brand_logo": "", "brand_other_name": [], "memo": "", "parent_id": "", "parent_name": "",
                              "region": "", "seo_brand": {}, "short_brand_desc": "", "short_brand_desc_en": "", "site_url": "", "tag_type": "",
                              "yingyonglingyu": "", "address": "", "auth_brand_append_img": "", "auth_brand_append_img_name": "",
                              "auth_brand_img": "", "auth_brand_img_name": "授权证明"}
            print(f"创建入参参数：{brand_add_body}")
            brand_add_res = self.rss.post(url=brand_add_url, json=brand_add_body, headers=self.headers).json()
            print(brand_add_res)
            # msg = brand_add_res["msg"]
            # if msg == "新增成功":
            #     print()
        return self
    def brand_giveaudit(self):
        """品牌提审"""
        brand_id = self.brand_search(status="0")
        brand_giveaudit_url = "{}/v1/goods/DgkBrand/giveAudit".format(self.HC2018_ADMIN_URL)
        if  brand_id != None:
            brand_giveaudit_body = {"ids": brand_id}
            brand_giveaudit_res = self.rss.post(url=brand_giveaudit_url, json=brand_giveaudit_body, headers=self.headers).json()
            print(brand_giveaudit_res)
        return self

    def brand_audit(self):
        """品牌审核"""
        n = 0
        k = 0
        while True:
            try:
                audit_search_url = "{}/v1/goods/DgkBrand/brandAuditList".format(self.HC2018_ADMIN_URL)
                audit_search_body = {"brand_name": self.brand_name, "status": 1, "page": 1, "per_page": 100}
                audit_search_res = self.rss.post(url=audit_search_url, json=audit_search_body, headers=self.headers).json()
                # print(audit_search_res)
                total = jsonpath.jsonpath(audit_search_res, "$..total")[0]
                found = False
                if int(total) >= 1:
                    audit_id_list = jsonpath.jsonpath(audit_search_res, "$..id")
                    auditIds = ",".join(audit_id_list)
                    brand_audit_url = "{}/v1/goods/DgkBrand/auditPass".format(self.HC2018_ADMIN_URL)
                    brand_audit_body = {"ids": auditIds}
                    cat_audit_res = self.rss.post(url=brand_audit_url, json=brand_audit_body, headers=self.headers).json()
                    k += 1
                    if cat_audit_res["msg"] == "success":
                        print(f"分类：{self.brand_name}，第{k}次审核成功")
                elif int(total) < 1:
                    print("已审核")
                    found = True
                    break
                if found:  # 如果已通过，则跳出循环
                    break
            except:
                n += 1
                if n > 6:
                    break
        return self

    def main_brand_add(self):
        """创建流程"""
        self.brand_add()
        brand_id = self.brand_search()
        if brand_id != None:
            self.brand_giveaudit()
            self.brand_audit()
            brand_id = self.brand_search(status="1")
            if brand_id != None:
                logger.info(
                    f"获取到创建品牌信息【品牌英文简称：{self.brand_name}，品牌中文简称：{self.brand_name_cn}，品牌英文全称：{self.brand_name_en_long}，"
                    f"品牌中文全称：{self.brand_name_cn_long}生成的品牌id为{brand_id}】")
        return self
    def xlsx_brand_add(self, data):
        # 转换成DataFrame
        df = pd.DataFrame(data)
        # 重命名列
        df.rename(columns={"brand_id": "品牌id", "brand_name": "品牌简称", "brand_cn": "品牌中文简称"}, inplace=True)
        # 写入指定Excel文件，写到默认第一个sheet，覆盖原内容
        df.to_excel(xlsx_dos_brand_dir, index=False)
        return self
    def mian_xlsx_brand_add(self):
        brand_id_name_count = self.brand_search_new()
        self.xlsx_brand_add(brand_id_name_count)

if __name__ == '__main__':
    rss = Login().login()
    # GoodsMeans(rss, "searchV4.9.7", "searchV4", "1").mian_means_stay_perfect()
    DgkBrand(rss).mian_xlsx_brand_add()

