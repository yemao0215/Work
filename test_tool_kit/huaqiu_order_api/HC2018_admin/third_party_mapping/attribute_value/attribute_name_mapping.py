import json
import re

import jieba
import jsonpath
import requests
import simplejson as simplejson
import yaml

from huaqiu_order_api.HC2018_admin.dgk_goods_means.dgk_attr import DgkAttr
from huaqiu_order_api.HC2018_admin.dgk_goods_means.dgk_category import Category
from huaqiu_order_api.HC2018_admin.login.login import Login
# from huaqiu_order_api.HC2018_admin.login import Login
from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_data import Data
from huaqiu_order_api.common.my_path import yaml_file


class AttributeNameMapping:
    # 属性值映射
    def __init__(self, rss, cat_name=None, cat_id=None, supplier_id=None):
        """
        :param phone:  登录账号
        :param psw:  登录密码
        """
        # self.user = user
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.HC2018_ADMIN_URL = data['HC2018_ADMIN_URL']
        self.rss = rss
        self.auth_token = getattr(Data, 'dos_auth_token')
        self.headers = {"Content-Type":"application/json;charset=UTF-8"}
        self.headers["Authorization"] = self.auth_token
        self.cat_name = cat_name
        self.cat_id = cat_id
        self.supplier_id = supplier_id

    def string_split_assembly(self, str):
        """字符串拆词组合"""
        str = re.sub(r'[^\w\s]', '', str)
        # 中文分词
        result = []
        for i in range(len(str) - 1):
            sub = str[:i + 2]
            if sub[-1] != " ":
                sub_cut = jieba.lcut(sub)
                if len(sub_cut) > 1:
                    sub = "".join(sub_cut)
            result.append(sub)
        print(result)
        return result
    def attribute_name_mapping_list(self):
        """属性列表"""
        attribute_name_mapping_list_url = "{}/v1/third/CateRelation/getAttrList".format(self.HC2018_ADMIN_URL)
        attribute_name_mapping_list_body = {"attr_name": "", "state": "0", "page": 1, "cat_id": self.cat_id, "per_page": 100, "supplier_id": "1"}
        if self.supplier_id != None:
            attribute_name_mapping_list_body["supplier_id"] = self.supplier_id
        attribute_name_mapping_list_res = self.rss.post(url=attribute_name_mapping_list_url, json=attribute_name_mapping_list_body, headers=self.headers).json()
        dataInfo = attribute_name_mapping_list_res["data"]["data"]
        if dataInfo != []:
           self.other_cat_id = jsonpath.jsonpath(attribute_name_mapping_list_res, "$..other_cat_id")
           self.other_attr_name = jsonpath.jsonpath(attribute_name_mapping_list_res, "$..other_attr_name")
           self.other_attr_id = jsonpath.jsonpath(attribute_name_mapping_list_res, "$..id")
           self.dos_cat_id = attribute_name_mapping_list_res["data"]["dos_cat_id"]
           self.dos_attr_name = jsonpath.jsonpath(attribute_name_mapping_list_res, "$..dos_attr_name")
           self.dos_attr_id = jsonpath.jsonpath(attribute_name_mapping_list_res, "$..dos_attr_id")
           self.dos_cat_name = jsonpath.jsonpath(attribute_name_mapping_list_res, "$..dos_cat_name")[0]
           self.other_cat_name = jsonpath.jsonpath(attribute_name_mapping_list_res, "$..other_cat_name")[0]
           self.dos_top_cat_id = jsonpath.jsonpath(attribute_name_mapping_list_res, "$..dos_top_cat_id")[0]
           if '>' in self.dos_cat_name:
               self.dos_cat_name = self.dos_cat_name.split(">")[-1]
           if '>' in self.other_cat_name:
               self.other_cat_name = self.other_cat_name.split(">")[-1]
        return self
    def attribute_name_mappling(self):
        """属性映射"""
        for i in range(len(self.other_attr_name)):
            if self.dos_attr_id[i] == "--":
                dos_attr_id, dos_attr_name = self.dos_attr_name_search(self.other_attr_name[i], self.dos_cat_id)
                attribute_name_mappling_url = "{}/v1/third/CateRelation/insertAttrMap".format(self.HC2018_ADMIN_URL)
                attribute_name_mappling_body = {"dos_attr_id": dos_attr_id, "dos_attr_name": dos_attr_name,
                                                "dos_cat_id": self.dos_cat_id, "id": self.other_attr_id[i],
                                                "other_attr_name": self.other_attr_name[i], "other_cat_id": self.other_cat_id[i],
                                                "supplier_id": "1"}
                if self.supplier_id != None:
                    attribute_name_mappling_body["supplier_id"] = self.supplier_id
                attribute_name_mappling_res = self.rss.post(url=attribute_name_mappling_url, json=attribute_name_mappling_body, headers=self.headers).json()
                msg = attribute_name_mappling_res["msg"]
                logger.info(f"映射结果为：{msg}")
                supplier_id_name_json = {"1": "Digikey", "2": "立创", "5": "Future", "6": "Arrow", "7": "TI原厂"}
                if msg == "success":
                    if self.supplier_id == None:
                        self.supplier_id = "1"
                    for key in supplier_id_name_json:
                        if key == self.supplier_id:
                            self.supplier_name = supplier_id_name_json[key]
                    logger.info(f"第三方：{self.supplier_name}的类目：{self.cat_name}的属性名称：{self.other_cat_name[i]},"
                                f"映射的DOS类目id：{self.dos_cat_id}的属性名称：{dos_attr_name}")
        return self
    def dos_attr_name_search(self, attr_name, dos_cat_id):
        if self.cat_name != self.dos_cat_name:
            self.cat_name = self.dos_cat_name
        cat_top_json = Category(self.rss, cat_name=self.cat_name, parent_type=1).mian_cat_top_search()
        for key, value in cat_top_json.items():
            if len(value) >= 1:
                if dos_cat_id in value:
                    self.top_cat_id = key
            elif value == []:
                self.top_cat_id = key
        if self.top_cat_id != self.dos_top_cat_id:
            self.top_cat_id = self.dos_top_cat_id
        attr_id, attr_name = DgkAttr(self.rss, attr_name=attr_name, cat_id=self.top_cat_id).mian_dgk_attr(search_type="1")
        if self.cat_name != self.other_cat_name:
            self.cat_name = self.other_cat_name
        return attr_id, attr_name
    def main_attribute_name_mapping(self):
        self.attribute_name_mapping_list()
        self.attribute_name_mappling()

if __name__ == '__main__':
    rss = Login().login()
    a = "天线类型"
    AttributeNameMapping(rss, "驱动器", "224", "2").main_attribute_name_mapping()


