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
from huaqiu_order_api.common.my_path import yaml_file, szlcsc_category_dir


class ParentCategoryRelevance:
    def __init__(self, rss=None):
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.HC2018_ADMIN_URL = data['HC2018_ADMIN_URL']
        token = getattr(Data, "dos_auth_token")
        self.headers = {"Content-Type": "application/x-www-form-urlencoded", "Authorization": token}
        self.headers_json = {"Content-Type": "application/json; charset=utf-8", "Authorization": token}
        self.rss =rss


    def parent_category_dict(self):
        search_url = "{}/v1/goods/DgkCategory/findList".format(self.HC2018_ADMIN_URL)
        search_body = {"cat_name": "", "search_type": 1, "is_enabled": "-1", "is_self": "-1", "is_show": "-1",
                       "type": "all", "page": 1, "per_page": 15}
        search_res = self.rss.post(url=search_url, json=search_body, headers=self.headers_json).json()
        data = search_res["data"]
        total = len(data)
        page_num = math.ceil(int(total) / 15)
        cat_id = []
        cat_name = []
        for i in range(page_num):
            i = i + 1
            search_url = "{}/v1/goods/DgkCategory/findList".format(self.HC2018_ADMIN_URL)
            search_body = {"cat_name": "", "search_type": 1, "is_enabled": "-1", "is_self": "-1", "is_show": "-1",
                           "type": "all", "page": i, "per_page": 15}
            search_res = self.rss.post(url=search_url, json=search_body, headers=self.headers_json).json()
            res_cat_id = jsonpath.jsonpath(search_res, '$..cat_id')
            res_cat_name = jsonpath.jsonpath(search_res, '$..cat_name')
            cat_name = cat_name + res_cat_name
            cat_id = cat_id + res_cat_id
        combined = zip(cat_name, cat_id)
        self.cat_name_id_dict = dict(combined)
        return self
    def read_data(self):
        logger.info("开始读取表格内容")
        data = pandas.read_excel(szlcsc_category_dir)
        self.szlcsc_category_en = data["芯灵类目name"]
        self.category_en = data["DOS类目"]
        self.dos_cat_id = data["uat_cat_id"]
        self.formal_brand_id = data["芯灵id"]
        self.row_count = len(data)
        self.column_count = data.shape[1]
        return self
    def category_update(self):
        pass
    def parent_relevance(self):
        pass




if __name__ == '__main__':
    from huaqiu_order_api.HC2018_admin.login.login import Login
    rss = Login().login()
    ParentCategoryRelevance(rss).parent_category_dict()