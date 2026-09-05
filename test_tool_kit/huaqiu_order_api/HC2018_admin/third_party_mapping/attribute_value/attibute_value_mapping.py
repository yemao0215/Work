import json
import math

import jsonpath
import requests
import simplejson as simplejson
import yaml

from huaqiu_order_api.HC2018_admin.dgk_goods_means.dgk_attr import DgkAttr
from huaqiu_order_api.HC2018_admin.login.login import Login
# from huaqiu_order_api.HC2018_admin.login import Login
from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_data import Data
from huaqiu_order_api.common.my_path import yaml_file


class AttributeValueMapping:
    # 属性值映射
    def __init__(self, rss, cat_id, supplier_id=None):
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
        self.cat_id = cat_id
        self.supplier_id = supplier_id

    def attribute_value_mapping_list(self):
        """属性值列表"""
        attribute_value_mapping_list_url = "{}/v1/third/AttrValueRelation/getAttrRelationList".format(self.HC2018_ADMIN_URL)
        attribute_value_mapping_list_body = {"attr_name": "", "dos_cat_id": "", "is_value_finish": "-1", "other_cat_id": self.cat_id,
                                             "page": 1, "per_page": 100, "supplier_id": "1", "total": ""
                                             }
        if self.supplier_id !=None:
            attribute_value_mapping_list_body["supplier_id"] = self.supplier_id
        attribute_value_mapping_res = self.rss.post(url=attribute_value_mapping_list_url, json=attribute_value_mapping_list_body, headers=self.headers).json()
        self.other_attr_id = jsonpath.jsonpath(attribute_value_mapping_res, "$..id")
        self.attribute_name = jsonpath.jsonpath(attribute_value_mapping_res, "$..other_attr_name")
        self.dos_cat_id = jsonpath.jsonpath(attribute_value_mapping_res, "$..dos_cat_id")
        self.dos_attribute_name = jsonpath.jsonpath(attribute_value_mapping_res, "$..dos_attr_name")
        self.dos_attr_id = jsonpath.jsonpath(attribute_value_mapping_res, "$..dos_attr_id")

        return self


    def attribute_value_mapping(self):
        """属性值匹配"""
        for i in range(len(self.attribute_name)):
            logger.info(f"此时attribute_name为：{self.attribute_name[i]}")
            attribute_value_mapping_detail_url = "{}/v1/third/AttrValueRelation/getAttrValueByAttr".format(self.HC2018_ADMIN_URL)
            attribute_value_mapping_detail_body = {"attr_name": self.attribute_name[i], "attr_value": "", "cat_id": self.cat_id,
                                                   "page": 1, "per_page": 100, "supplier_id": "1", "state": "0"
                                                   }
            if self.supplier_id != None:
                attribute_value_mapping_detail_body["supplier_id"] = self.supplier_id
            attribute_value_mapping_total_res = self.rss.post(url=attribute_value_mapping_detail_url, json=attribute_value_mapping_detail_body, headers=self.headers).json()
            total = jsonpath.jsonpath(attribute_value_mapping_total_res, "$..total")[0]
            self.other_attr_value_id = []
            self.other_attr_value_name = []
            if int(total) / 100 > 1:
                num = math.ceil(int(total) / 100)
                for index in range(num):
                    index = index + 1
                    attribute_value_mapping_detail_body["page"] = index
                    attribute_value_mapping_detail_res = self.rss.post(url=attribute_value_mapping_detail_url, json=attribute_value_mapping_detail_body,
                                                           headers=self.headers).json()
                    other_attr_value_id = jsonpath.jsonpath(attribute_value_mapping_detail_res, "$..id")
                    other_attr_value_name = jsonpath.jsonpath(attribute_value_mapping_detail_res, "$..other_attr_value")
                    self.other_attr_value_id = self.other_attr_value_id + other_attr_value_id
                    self.other_attr_value_name = self.other_attr_value_name + other_attr_value_name
            else:
                self.other_attr_value_id = jsonpath.jsonpath(attribute_value_mapping_total_res, "$..id")
                self.other_attr_value_name = jsonpath.jsonpath(attribute_value_mapping_total_res, "$..other_attr_value")
            # print(self.other_attr_value_name)
            if self.other_attr_value_name != False:
                for m in range(len(self.other_attr_value_name)):

                    self.dos_attr_value(self.dos_attribute_name[i], self.dos_attr_id[i], self.other_attr_value_name[m])
                    attribute_value_mapping_url = "{}/v1/third/AttrValueRelation/attrValueMap".format(self.HC2018_ADMIN_URL)
                    attribute_value_mapping_body = {"dos_attr_id": self.dos_attr_id[i], "dos_attr_value": self.attr_value_name, "dos_attr_value_id": self.attr_value_id,
                                                    "dos_cat_id": self.dos_cat_id[i], "other_attr_name": self.attribute_name[i], "other_attr_value": self.other_attr_value_name[m],
                                                    "id": self.other_attr_value_id[m], "supplier_id": "1", "other_cat_id": self.cat_id}
                    if self.supplier_id != None:
                        attribute_value_mapping_body["supplier_id"] = self.supplier_id
                    attribute_value_mapping_res = self.rss.post(url=attribute_value_mapping_url, json=attribute_value_mapping_body,
                                                               headers=self.headers).json()
                    logger.info(f"属性值：{self.other_attr_value_name[m]}映射完成，执行结果为：{attribute_value_mapping_res}")
        return self




    def dos_attr_value(self, attr_name,attr_id, attr_value):
        """获取资料管理里面的属性值信息"""
        dos_top_cat_id = self.attribute_name_list()
        # print(dos_top_cat_id)
        logger.info(f"当前attr_id：{attr_id}, attr_name:{attr_name}, attr_value: {attr_value}")
        dos_attr_value_url = "{}/v1/goods/DgkCategoryAttr/findValueList".format(self.HC2018_ADMIN_URL)
        dos_attr_value_body = {"attr_id": attr_id, "status": "1", "per_page": 100, "page": 1}
        dos_attr_value_res = self.rss.post(url=dos_attr_value_url, json=dos_attr_value_body, headers=self.headers).json()
        # print(dos_attr_value_res)
        valuelistInfo = dos_attr_value_res["data"]["value_list"]["data"]
        valuelistNum = dos_attr_value_res["data"]["value_list"]["last_page"]
        if valuelistInfo != []:
            key_value_attr_value_id = jsonpath.jsonpath(dos_attr_value_res, "$..attr_value_id")
            key_value_attr_value_name = jsonpath.jsonpath(dos_attr_value_res, "$..attr_value")
            key_value_attr_value_name_en = jsonpath.jsonpath(dos_attr_value_res, "$..attr_value_en")
            if attr_value in key_value_attr_value_name:
                key_attr_value_name = key_value_attr_value_name.index(attr_value)
                value_attr_value_id = key_value_attr_value_id[key_attr_value_name]
                value_attr_value_name_en =key_value_attr_value_name_en[key_attr_value_name]
                value_attr_value_name = key_value_attr_value_name[key_attr_value_name]
                self.attr_value_id = value_attr_value_id
                self.attr_value_name_en = value_attr_value_name_en
                self.attr_value_name = value_attr_value_name
            else:
                self.attr_value_id = valuelistInfo[-1]["attr_value_id"]
                self.attr_value_name = valuelistInfo[-1]["attr_value"]
                self.attr_value_name_en = valuelistInfo[-1]["attr_value_en"]
                if self.attr_value_name != attr_value:
                    atrr_value_id_count = []
                    attr_value_name_count = []
                    attr_value_name_en_count = []
                    if valuelistNum > 1:
                        for i in range(int(valuelistNum)):
                            i = i + 1
                            dos_attr_value_body["page"] = i
                            dos_attr_value_res = self.rss.post(url=dos_attr_value_url, json=dos_attr_value_body, headers=self.headers).json()
                            attr_value_id = jsonpath.jsonpath(dos_attr_value_res, "$..attr_value_id")
                            attr_value_name = jsonpath.jsonpath(dos_attr_value_res, "$..attr_value")
                            attr_value_name_en = jsonpath.jsonpath(dos_attr_value_res, "$..attr_value_en")
                            atrr_value_id_count = atrr_value_id_count + attr_value_id
                            attr_value_name_count = attr_value_name_count + attr_value_name
                            attr_value_name_en_count = attr_value_name_en_count + attr_value_name_en
                    else:
                        attr_value_id = jsonpath.jsonpath(dos_attr_value_res, "$..attr_value_id")
                        attr_value_name = jsonpath.jsonpath(dos_attr_value_res, "$..attr_value")
                        attr_value_name_en = jsonpath.jsonpath(dos_attr_value_res, "$..attr_value_en")
                        atrr_value_id_count = atrr_value_id_count + attr_value_id
                        attr_value_name_count = attr_value_name_count + attr_value_name
                        attr_value_name_en_count = attr_value_name_en_count + attr_value_name_en
                    for m in range(len(attr_value_name_count)):
                        if attr_value_name_count[m] == attr_value:
                            self.attr_value_id = atrr_value_id_count[m]
                            self.attr_value_name = attr_value_name_count[m]
                            self.attr_value_name_en = attr_value_name_en_count[m]
                            break
                    if self.attr_value_name != attr_value:
                        self.attr_value_id = DgkAttr(rss, attr_name=attr_name, cat_id=dos_top_cat_id).mian_dgk_attr_value_add(attr_value, "1")
                        self.attr_value_name = attr_value
            logger.info(f"获取{attr_id}的attr_value_id：{self.attr_value_id}，attr_value_name：{self.attr_value_name}，attr_value_name_en：{self.attr_value_name_en}")
        else:
             self.attr_value_id = DgkAttr(rss, attr_name=attr_name, cat_id=dos_top_cat_id).mian_dgk_attr_value_add(attr_value, "1")
             self.attr_value_name = attr_value
        return self
    def attribute_name_list(self):
        """属性列表"""
        attribute_name_mapping_list_url = "{}/v1/third/CateRelation/getAttrList".format(self.HC2018_ADMIN_URL)
        attribute_name_mapping_list_body = {"attr_name": "", "state": "-1", "page": 1, "cat_id": self.cat_id, "per_page": 100, "supplier_id": "1"}
        if self.supplier_id != None:
            attribute_name_mapping_list_body["supplier_id"] = self.supplier_id
        # print(attribute_name_mapping_list_body)
        attribute_name_mapping_list_res = self.rss.post(url=attribute_name_mapping_list_url, json=attribute_name_mapping_list_body, headers=self.headers).json()
        # print(attribute_name_mapping_list_res)
        dataInfo = attribute_name_mapping_list_res["data"]["data"]
        if dataInfo != []:
           # print(1111)
           self.dos_top_cat_id = jsonpath.jsonpath(attribute_name_mapping_list_res, "$..dos_top_cat_id")[0]
        return self.dos_top_cat_id
    def mian_attribute_value_mapping(self):
        self.attribute_value_mapping_list()
        self.attribute_value_mapping()

if __name__ == '__main__':
    # cat_id 已完成属性映射的第三方类目的类目id
    cat_id = 224
    rss = Login().login()
    AttributeValueMapping(rss, cat_id, "2").mian_attribute_value_mapping()
    # AttributeValueMapping("admin","123456").double_quotation_mark_translation('0.598"（15.20mm）')
    # aa = {"aaa": 'bbb"kkk'}
    # print(json.dumps(aa))attr_id：19103, attr_name:类型, attr_value: DC-DC控制器
    # AttributeValueMapping(rss, cat_id, "2").dos_attr_value("类型", 19103, "DC-DC控制器")



