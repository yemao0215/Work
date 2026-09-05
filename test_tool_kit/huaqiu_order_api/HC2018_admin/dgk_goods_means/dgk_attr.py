import math
import re

import jsonpath
import pandas
import pandas as pd
import requests
import yaml
from openpyxl.reader.excel import load_workbook

from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_data import Data
from huaqiu_order_api.common.my_path import yaml_file, attr_dir
from huaqiu_order_api.common.my_tool import field_translate


class DgkAttr:
    def __init__(self, rss, attr_name=None, attr_name_en=None, cat_id=None):
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.HC2018_ADMIN_URL = data['HC2018_ADMIN_URL']
        token = getattr(Data, "dos_auth_token")
        self.headers = {"Content-Type": "application/x-www-form-urlencoded", "Authorization": token}
        self.headers_json = {"Content-Type": "application/json; charset=utf-8", "Authorization": token}
        self.rss = rss
        self.attr_name = attr_name
        self.attr_name_en = attr_name_en
        self.cat_id = cat_id

    def read_data(self):
        logger.info("开始读取表格内容")
        data = pandas.read_excel(attr_dir)
        self.attr_name = data["属性名称"]
        self.attr_name_en = data["属性英文"]
        self.row_count = len(data)
        self.column_count = data.shape[1]
        return self

    def category_attr_seatch(self):
        search_type = getattr(Data, "search_type")
        search_url = "{}/v1/goods/DgkCategoryAttr/findAttrList".format(self.HC2018_ADMIN_URL)
        search_body = {"attr_name": self.attr_name, "attr_type": "-1", "cat_id": self.cat_id,  "is_hqself": "-1", "is_show": "-1", "origin": "-1",
                       "status": "-1", "page": 1, "per_page": 100, "pageSize": 20, "delete": 0}
        self.attr_id = None
        while True:
            i = 0
            search_res = self.rss.post(url=search_url, json=search_body, headers=self.headers_json).json()
            total = jsonpath.jsonpath(search_res, '$..total')
            if int(total[0]) > 0:
                attr_id = jsonpath.jsonpath(search_res, '$..attr_id')
                res_attr_name = jsonpath.jsonpath(search_res, '$..attr_name')
                print(res_attr_name)
                for k in range(len(attr_id)):
                    # for v in res_attr_name:
                        if res_attr_name[k] == self.attr_name:
                            logger.info(111)
                            search_detaill_url = "{}/v1/goods/DgkCategoryAttr/findValueList".format(self.HC2018_ADMIN_URL)
                            search_detaill_body = {"attr_id": attr_id[k], "page": 1, "per_page": 10, "sort_order": 0, "status": "-1"}
                            search_detaill_res = self.rss.post(url=search_detaill_url, json=search_detaill_body, headers=self.headers_json).json()
                            res_attr_name_en = jsonpath.jsonpath(search_detaill_res, '$..attr_name_en')[0]
                            logger.info(res_attr_name_en)
                            if res_attr_name_en == "" and search_type ==None:
                                logger.info(113)
                                attr_update_url = "{}/v1/goods/DgkCategoryAttr/update".format(self.HC2018_ADMIN_URL)
                                attr_update_body = {"attr_id": attr_id[k], "attr_name": self.attr_name, "attr_name_en": self.attr_name_en, "cat_id": self.cat_id,
                                                    "is_show": "1", "is_use_unit": "0", "sort_order": 1, "status": "1"}
                                attr_update_res = self.rss.post(url=attr_update_url, json=attr_update_body, headers=self.headers_json)
                                if attr_update_res.status_code == 200:
                                    logger.info(f"属性：{self.attr_name}更新成功，执行结果：{attr_update_res.json()}")
                            else:
                                logger.info(f"属性：{self.attr_name}存在属性英文")
                                self.attr_id = attr_id[k]
                                self.attr_name = res_attr_name[k]
                                break
                        else:
                             logger.info(f"属性：{self.attr_name}不等于属性{res_attr_name[k]}")

                    # else:
                    #      logger.info(112)
                    #      self.category_attr_create(self.attr_name, self.attr_name_en, self.cat_id)
                if self.attr_id == None:
                    self.category_attr_create(self.attr_name, self.attr_name_en, self.cat_id)

            else:
                logger.info(114)
                self.category_attr_create(self.attr_name, self.attr_name_en, self.cat_id)
            i += 1
            logger.info(i)
            if i >= 1:
                if self.attr_id !=None:

                    break
        return self.attr_id, self.attr_name


    def category_attr_create(self, attr_name, attr_name_en, cat_id, type=None):

        create_url = "{}/v1/goods/DgkCategoryAttr/insert".format(self.HC2018_ADMIN_URL)
        create_body = {"attr_name": attr_name, "cat_id": cat_id, "is_show": "1", "status": 1,
                       "attr_name_en": field_translate(attr_name) if not attr_name_en else attr_name_en}
        create_res = self.rss.post(url=create_url, json=create_body, headers=self.headers_json)
        if create_res.status_code == 200:
            logger.info(f"属性：{attr_name}新增成功，执行结果：{create_res.json()}")
            if type == None:
                self.category_attr_seatch()
        return self
    def category_attr_value_create(self, attr_id, attr_value, order_by):
        """属性值新增"""
        category_attr_value_create_url = "{}/v1/goods/DgkCategoryAttr/insertValue".format(self.HC2018_ADMIN_URL)
        category_attr_value_create_body = {"attr_id": attr_id, "attr_value": attr_value, "attr_value_en": field_translate(attr_value), "sort": order_by}
        category_attr_value_create_res = self.rss.post(url=category_attr_value_create_url, json=category_attr_value_create_body, headers=self.headers_json).json()
        if category_attr_value_create_res["msg"] == "success":
            logger.info(f"属性id：{attr_id}的属性值：{attr_value}新增成功，执行结果：{category_attr_value_create_res}")
            return self

    def category_attr_value_search(self, attr_id, attr_value):
        """属性值查询"""
        category_attr_value_search_url = "{}/v1/goods/DgkCategoryAttr/findValueList".format(self.HC2018_ADMIN_URL)
        category_attr_value_search_body = {"attr_id": attr_id, "page": 1, "per_page": 100, "status": "1", "attr_value": attr_value}
        category_attr_value_search_res = self.rss.post(url=category_attr_value_search_url, json=category_attr_value_search_body, headers=self.headers_json).json()
        attr_value_id = jsonpath.jsonpath(category_attr_value_search_res, "$..attr_value_id")
        res_attr_value = jsonpath.jsonpath(category_attr_value_search_res, "$..attr_value")
        for i in range(len(res_attr_value)):
            if res_attr_value[i] == attr_value:
                self.attr_value_id = attr_value_id[i]
                break
        return self.attr_value_id

    def main_excel_dgk_attr(self):
        self.read_data()
        n = 1
        for i in range(self.row_count):
            n = n + 1
            self.category_attr_seatch()
        return self
    def mian_excel_dgk_attr_add(self, search_type=None):
        setattr(Data, "search_type", search_type)
        self.read_data()
        for i in range(len(self.attr_name)):
            self.category_attr_create(self.attr_name[i], self.attr_name_en[i], self.cat_id, type='1')
        return self

    def mian_dgk_attr(self, search_type):
        setattr(Data, "search_type", search_type)
        attr_id, attr_name = self.category_attr_seatch()
        return attr_id, attr_name
    def mian_dgk_attr_value_add(self, attr_value=None, search_type=None):
        setattr(Data, "search_type", search_type)
        self.attr_id, self.attr_name = self.category_attr_seatch()
        self.category_attr_value_create(self.attr_id, attr_value, 1)
        attr_value_id = self.category_attr_value_search(self.attr_id, attr_value)
        return attr_value_id






if __name__ == '__main__':
    from huaqiu_order_api.HC2018_admin.login.login import Login
    rss = Login().login()
    # DgkAttr(rss).category_attr_seatch("高度", "Maximum Installation Height", "1396")
    attr_value_id = DgkAttr(rss, attr_name="封装/外壳", cat_id="835").mian_dgk_attr_value_add()
    # print(attr_id, attr_name)


