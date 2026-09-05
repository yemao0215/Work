import json
import re
import time

import jsonpath
import pandas
import yaml

from huaqiu_order_api.HC2018_admin.login.login import Login
# from xpinyin import Pinyin
from huaqiu_order_api.common.loguru_logger import logger
import requests

from huaqiu_order_api.common.my_path import stockup_dir, yaml_file, xl_dos_category_dir_pro

from huaqiu_order_api.common.my_data import Data


class Category:
    # 分类
    def __init__(self, rss, cat_name=None, cat_name_en=None, invoice_cat_name=None, finance_cate_type=None, parent_type=None,parent_cat_name=None):
        """
        :param cat_name:  分类名称
        :param cat_name_en:  分类英文名称
        :param invoice_cat_name:  财务发票分类 字符串形式如：半导体
        :param finance_cate_type 财务统计归类 1半导体器件 2被动器件 3连接器 4其他
        :param parent_type:  是否存在上级分类
        :param parent_cat_name:  上级分类名称
        """
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.HC2018_ADMIN_URL = data['HC2018_ADMIN_URL']
        self.cat_name = cat_name
        self.rss = rss
        self.cat_name_en = cat_name_en
        self.auth_token = getattr(Data, 'dos_auth_token')
        self.invoice_cat_name = invoice_cat_name
        self.finance_cate_type = finance_cate_type
        self.parent_type = parent_type
        self.parent_cat_name = parent_cat_name
        self.headers = {"Content-Type":"application/json;charset=UTF-8"}
        self.headers_form = {"Content-Type":"application/x-www-form-urlencoded;charset=UTF-8"}
        self.headers["Authorization"] = self.auth_token
    def dict_json_level_split(self, dict, parent_id='0'):
        result = {}
        for key, value in dict.items():
            if value[0] == parent_id:
                children = self.dict_json_level_split(dict, key)
                if children:
                    result[key] = [value[1], children]
                else:
                    result[key] = value[1]
        return result

    def find_top_keys(self, data, target_value, top_key=None, result=None):
        if result is None:
            result = {}
        if top_key is None:
            # 初始化时，当前键就是顶层键
            top_key_mapping = {key: key for key in data.keys()}
        else:
            # 递归时继承父层的顶层键映射
            top_key_mapping = top_key

        for key, value in data.items():
            current_top_key = top_key_mapping[key]  # 当前键对应的顶层键
            if isinstance(value, list):
                # 检查第二个元素是否为字典
                if len(value) == 2 and isinstance(value[1], dict):
                    # 更新子键的顶层键映射（继承当前顶层键）
                    new_top_key_mapping = {**top_key_mapping, **{k: current_top_key for k in value[1].keys()}}
                    # 递归处理子字典
                    self.find_top_keys(value[1], target_value, new_top_key_mapping, result)
            elif value == target_value:
                # 找到目标值，记录其顶层键和当前键
                if current_top_key not in result:
                    result[current_top_key] = []
                result[current_top_key].append(key)
        return result

    def cat_search(self, cat_name=None, status=None):
        """分类查询"""
        if cat_name == None:
            cat_name = self.cat_name
        search_url = "{}/v1/goods/DgkCategory/findList".format(self.HC2018_ADMIN_URL)
        search_body = {"cat_name": cat_name, "search_type": "1", "is_enabled": "-1", "is_self": "-1",
                       "is_show": "-1", "type": "all", "page": 1, "per_page": 15}
        if status != None:
            search_body["is_enabled"] = status
        search_res = self.rss.post(url=search_url, json=search_body, headers=self.headers).json()
        dataInfo = search_res["data"]
        parent_id_count = []
        cat_id_count = []
        cat_name_count = []
        if dataInfo != []:
            for i in range(len(dataInfo)):
                parent_id_list = jsonpath.jsonpath(dataInfo[i], "$..parent_id")
                cat_id_list = jsonpath.jsonpath(dataInfo[i], "$..cat_id")
                cat_name_list = jsonpath.jsonpath(dataInfo[i], "$..cat_name")
                parent_id_count = parent_id_count + parent_id_list
                cat_id_count = cat_id_count + cat_id_list
                cat_name_count = cat_name_count + cat_name_list
        # 组成分类id、分类名称、上级id的字典
        cat_parent_name_id_dict = {cat_id_count: [parent_id_count, cat_name_count] for cat_id_count, parent_id_count, cat_name_count in zip(cat_id_count, parent_id_count, cat_name_count)}
        top_cat_parent_name_id_dict = self.dict_json_level_split(cat_parent_name_id_dict)
        cat_id = None
        parent_id = None
        for key, value in cat_parent_name_id_dict.items():
            if value[1] == cat_name:
                cat_id = key
                parent_id = value[0]
        return cat_id, parent_id, top_cat_parent_name_id_dict

    def cat_search_Temp(self, cat_name=None, status=None):
        """分类查询 search_type 查询类型"""
        data_list = []
        xl_data_pro = pandas.read_excel(xl_dos_category_dir_pro)
        self.pro_xl_category_name = xl_data_pro["dos_类目名称"].tolist()
        self.pro_xl_category_en = xl_data_pro["dos_英文类目名称"].tolist()
        search_url = "{}/v1/goods/DgkCategory/findList".format(self.HC2018_ADMIN_URL)
        search_body = {"cat_name": cat_name, "search_type": "1", "is_enabled": "-1", "is_self": "-1",
                       "is_show": "-1", "type": "all", "page": 1, "per_page": 15}
        for i in range(len(self.pro_xl_category_name)):
            parent_id_count = []
            cat_id_count = []
            cat_name_count = []
            try:
                print("此时搜索类目：{}".format(self.pro_xl_category_name[i]))
                search_body["cat_name"] = self.pro_xl_category_name[i]
                print(search_body)
                search_res = self.rss.post(url=search_url, json=search_body, headers=self.headers).json()
                dataInfo = search_res["data"]
                if dataInfo != []:
                    for i in range(len(dataInfo)):
                        parent_id_list = jsonpath.jsonpath(dataInfo[i], "$..parent_id")
                        cat_id_list = jsonpath.jsonpath(dataInfo[i], "$..cat_id")
                        cat_name_list = jsonpath.jsonpath(dataInfo[i], "$..cat_name")
                        parent_id_count = parent_id_count + parent_id_list
                        cat_id_count = cat_id_count + cat_id_list
                        cat_name_count = cat_name_count + cat_name_list
                        # 组成分类id、分类名称、上级id的字典
                        cat_parent_name_id_dict = {cat_id_count: [parent_id_count, cat_name_count] for
                                                   cat_id_count, parent_id_count, cat_name_count in
                                                   zip(cat_id_count, parent_id_count, cat_name_count)}
                        top_cat_parent_name_id_dict = self.dict_json_level_split(cat_parent_name_id_dict)
                        cat_id = None
                        parent_id = None
                        for key, value in cat_parent_name_id_dict.items():
                            if value[1] == cat_name:
                                cat_id = key
                                parent_id = value[0]
                            print(cat_id, parent_id, top_cat_parent_name_id_dict)
                        # return cat_id, parent_id, top_cat_parent_name_id_dict
                else:
                    print("此时搜索类目：{}没有搜索到".format(self.pro_xl_category_name[i]))

                    # 手动抛出异常来测试
                    raise ValueError("模拟异常")
            except:
                try:
                    print("此时搜索类目：{}没有搜索到，切换成英文名称搜索，此时英文名称：{}".format(self.pro_xl_category_name[i], self.pro_xl_category_en[i]))
                    search_body["search_type"] = 2 # 切换分类英文名称搜索
                    search_body["cat_name"] = self.pro_xl_category_en[i]
                    print(search_body)
                    search_res = self.rss.post(url=search_url, json=search_body, headers=self.headers).json()
                    dataInfo = search_res["data"]
                    if dataInfo != []:
                        for i in range(len(dataInfo)):
                            parent_id_list = jsonpath.jsonpath(dataInfo[i], "$..parent_id")
                            cat_id_list = jsonpath.jsonpath(dataInfo[i], "$..cat_id")
                            cat_name_list = jsonpath.jsonpath(dataInfo[i], "$..cat_name")
                            parent_id_count = parent_id_count + parent_id_list
                            cat_id_count = cat_id_count + cat_id_list
                            cat_name_count = cat_name_count + cat_name_list
                        # 组成分类id、分类名称、上级id的字典
                        cat_parent_name_id_dict = {cat_id_count: [parent_id_count, cat_name_count] for
                                                   cat_id_count, parent_id_count, cat_name_count in
                                                   zip(cat_id_count, parent_id_count, cat_name_count)}
                        top_cat_parent_name_id_dict = self.dict_json_level_split(cat_parent_name_id_dict)
                        cat_id = None
                        parent_id = None
                        for key, value in cat_parent_name_id_dict.items():
                            if value[1] == cat_name:
                                cat_id = key
                                parent_id = value[0]
                        print(cat_id, parent_id, top_cat_parent_name_id_dict)
                    else:
                        print("切换成英文名称搜索，此时英文名称：{}也没有搜索到".format(self.pro_xl_category_en[i]))

                        # 手动抛出异常来测试
                        raise ValueError("模拟异常")
                    # return cat_id, parent_id, top_cat_parent_name_id_dict

                except:
                    search_body["search_type"] = 1
                    print("此时搜索类目：{}没有搜索到，切换成英文名称搜索，此时英文名称：{}也没有搜索到".format(
                        self.pro_xl_category_name[i], self.pro_xl_category_en[i]))

    def cat_add(self):
        """分类新增"""
        cat_add_url = "{}/v1/goods/DgkCategory/insert".format(self.HC2018_ADMIN_URL)
        cat_add_body = {"cat_name": self.cat_name, "keywords": self.cat_name_en, "cat_letter": "MT", "is_show": "1", "is_describe": 0,
                        "is_required": 0, "sort_order": 1, "attr": [], "cat_desc": "自动化测试分类", "cat_desc_en": "automate-test-category",
                        "link_url": "", "seo_buy": {}, "tag_type": "", "seo_sn": {}, "seo_category": {"description": "", "keywords": "", "title": ""}}
        if self.parent_type == None and self.parent_cat_name == None:
            """self.cat_name为顶级分类"""
            cat_add_body["finance_cate_type"] = self.finance_cate_type
            cat_add_body["invoice_cat_name"] = self.invoice_cat_name
            cat_add_body["parent_id"] = ""
        elif self.parent_type != None and self.parent_cat_name != None:
            cat_id, parent_id, cat_parent_name_id_dict = self.cat_search(self.parent_cat_name)
            cat_add_body["parent_id"] = cat_id
            setattr(Data, "add_parent_id", cat_id)
        cat_add_body = {"cat": cat_add_body}
        # print(json.dumps(cat_add_body, ensure_ascii=False))
        cat_add_res = self.rss.post(url=cat_add_url, json=cat_add_body, headers=self.headers).json()
        print(cat_add_res)
        return self
    def cat_giveaudit(self):
        """分类提审"""
        cat_id, parent_id, cat_parent_name_id_dict = self.cat_search(status="0")
        # print(cat_id, parent_id)
        cat_giveaudit_url = "{}/v1/goods/DgkCategory/submitAudit".format(self.HC2018_ADMIN_URL)
        if cat_id != None:
            cat_giveaudit_body = {"cat_id": cat_id}
            cat_giveaudit_res = self.rss.post(url=cat_giveaudit_url, json=cat_giveaudit_body, headers=self.headers).json()
            print(cat_giveaudit_res)
        return self
    def cat_audit(self):
        """分类审核"""
        n = 0
        k = 0
        while True:
            try:
                audit_search_url = "{}/v1/goods/DgkCategory/findAuditList".format(self.HC2018_ADMIN_URL)
                audit_search_body = {"cat_name": self.cat_name, "global_audit_status": 1, "is_self": "-1", "page": 1, "per_page": 100}
                audit_search_res = self.rss.post(url=audit_search_url, json=audit_search_body, headers=self.headers).json()
                # print(audit_search_res)
                total = jsonpath.jsonpath(audit_search_res, "$..total")[0]
                found = False
                if int(total) >= 1:
                    cat_id_list = jsonpath.jsonpath(audit_search_res, "$..cat_id")
                    catIds = ",".join(cat_id_list)
                    cat_audit_url = "{}/v1/goods/DgkCategory/audit".format(self.HC2018_ADMIN_URL)
                    cat_audit_body = {"cat_id": catIds, "status": 1}
                    cat_audit_res = self.rss.post(url=cat_audit_url, json=cat_audit_body, headers=self.headers).json()
                    k += 1
                    if cat_audit_res["msg"] == "success":
                        print(f"分类：{self.cat_name}，第{k}次审核成功")
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
    def mian_cat_add(self):
        """创建流程"""
        self.cat_add()
        cat_id, parent_id, cat_parent_name_id_dict = self.cat_search()
        if cat_id != None:
            self.cat_giveaudit()
            self.cat_audit()
            cat_id, parent_id, cat_parent_name_id_dict = self.cat_search(status="1")
            add_parent_id = getattr(Data, "add_parent_id")
            if parent_id == add_parent_id:
                logger.info(f"获取到分类信息【分类：{self.cat_name}，分类id：{cat_id}，上级分类id：{parent_id}】")
        return self

    def mian_cat_top_search(self):
        """顶级类目查询"""
        cat_id, parent_id, top_cat_parent_name_id_dict = self.cat_search()
        print(cat_id, top_cat_parent_name_id_dict)
        cat_top_json = self.find_top_keys(top_cat_parent_name_id_dict, self.cat_name)
        print(cat_top_json)
        return cat_top_json


if __name__ == '__main__':
    rss = Login().login()
    # GoodsMeans(rss, "searchV4.9.7", "searchV4", "1").mian_means_stay_perfect()
    Category(rss, "电容", None, None, None, 1, None).mian_cat_top_search()