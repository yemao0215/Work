import math
import re

import jsonpath
import requests
import yaml

from huaqiu_order_api.HC2018_admin.login.login import Login
from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_data import Data
from huaqiu_order_api.common.my_path import yaml_file


class BrandMapping:
    # 品牌映射
    def __init__(self, rss, supplier_id=None):
        """
        :param phone:  登录账号
        :param psw:  登录密码
        """
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.HC2018_ADMIN_URL = data['HC2018_ADMIN_URL']
        self.rss = rss
        self.auth_token = getattr(Data, 'dos_auth_token')
        self.headers = {"Content-Type":"application/json;charset=UTF-8"}
        self.headers["Authorization"] = self.auth_token
        self.supplier_id = supplier_id
    def string_list_convert(self,str):
        result = None
        if "(" in str or ")" in str:
            print(123421)
            matches = re.search(r'\((.*?)\)', str)
            print(matches)
            # 如果匹配成功
            if matches:
                print(123422)
                # 第一个匹配组是括号外的部分
                part1 = str.split('(')[0].strip()

                # 第二个匹配组是括号内的部分
                part2 = matches.group(1).strip()

                # 放入列表
                result = [part1, part2]
                result = [s.strip('"') for s in result]
                result.append(str)
        elif " " in str:
            result = str.split()
            result.append(str)
        else:
            result = [str]
        print(result)
        return result

    def brand_mapping_list(self, brand_name):
        """品牌映射列表"""
        brand_mapping_list_url = "{}/v1/third/BrandRelation/brandList".format(self.HC2018_ADMIN_URL)
        brand_mapping_list_body = {"brand_name": brand_name, "state": "0", "supplier_id": "1", "page": 1,"per_page": 100}
        if self.supplier_id !=None:
            brand_mapping_list_body["supplier_id"] = self.supplier_id
        brand_mapping_list_res = self.rss.post(url=brand_mapping_list_url, json=brand_mapping_list_body, headers=self.headers).json()
        self.brand_id = []
        self.brand_name = []
        self.dos_cat_id = []
        self.dos_attr_id = []
        total = brand_mapping_list_res["data"]["total"]
        if int(total) /100 > 1:
            num = math.ceil(int(total)/100)
            for i in range(num):
                i = i + 1
                brand_mapping_list_body["page"] = i
                brand_mapping_list_res = self.rss.post(url=brand_mapping_list_url, json=brand_mapping_list_body,
                                                       headers=self.headers).json()
                brand_id = jsonpath.jsonpath(brand_mapping_list_res, "$..brand_id")
                brand_name = jsonpath.jsonpath(brand_mapping_list_res, "$..brand_name")
                self.brand_id = self.brand_id + brand_id
                self.brand_name = self.brand_name + brand_name
        else:
            brand_id = jsonpath.jsonpath(brand_mapping_list_res, "$..brand_id")
            brand_name = jsonpath.jsonpath(brand_mapping_list_res, "$..brand_name")
            self.brand_id = self.brand_id + brand_id
            self.brand_name = self.brand_name + brand_name
        # print(self.brand_name)
        # print(self.brand_id)
        return self

    def brand_mapping(self):
        """品牌映射"""
        # logger.info(f"当前品牌：{}")
        for i in range(len(self.brand_name)):
            try:
                brand_mapping_search_url = "{}/v1/goods/DgkGoods/ajaxGetProviderName".format(self.HC2018_ADMIN_URL)
                brand_mapping_search_body = {"provider_name": self.brand_name[i]}
                brand_mapping_search_res = self.rss.post(url=brand_mapping_search_url, json=brand_mapping_search_body, headers=self.headers).json()
                dataInfo = jsonpath.jsonpath(brand_mapping_search_res, "$..data")[0]
                if dataInfo == []:
                    self.dos_brand_id, self.brand_name_en =self.dos_brand_value(self.brand_name[i])
                else:
                    self.dos_brand_id = dataInfo[0]["brand_id"]
                    self.brand_name_en = dataInfo[0]["brand_name"]
                print(self.brand_name_en)
                brand_map_url = "{}/v1/third/BrandRelation/brandMap".format(self.HC2018_ADMIN_URL)
                brand_map_body = {"brand_id": self.brand_id[i], "brand_name": self.brand_name[i], "dos_brand_name": self.brand_name_en,
                                  "dos_brand_id": self.dos_brand_id, "supplier_id": "1"}
                if self.supplier_id != None:
                    brand_map_body["supplier_id"] = self.supplier_id
                logger.info(brand_map_body)
                brand_map_res = self.rss.post(url=brand_map_url, json=brand_map_body, headers=self.headers).json()
                msg = brand_map_res["msg"]
                logger.info(f"品牌映射结果：{msg}")
            except AttributeError as e:
                print(e)
                if "object has no attribute" in str(e):
                    pass
                else:
                    raise EOFError



    def dos_brand_value(self, brand_name):
        """获取资料管理里面的品牌信息"""
        logger.info(f"当前brand_name：{brand_name}")
        brand_name_list = self.string_list_convert(brand_name)
        print(brand_name_list)
        found_match = False
        for brand_name in brand_name_list:
            dos_brand_value_url = "{}/v1/goods/DgkBrand/brandList".format(self.HC2018_ADMIN_URL)
            dos_brand_value_body = {"brand_name": brand_name, "brand_type": "1", "is_exact": "0", "type": "0", "page": 1, "per_page": 100}
            dos_brand_value_res = self.rss.post(url=dos_brand_value_url, json=dos_brand_value_body, headers=self.headers).json()
            print(dos_brand_value_res)
            valuelistInfo = dos_brand_value_res["data"]["list"]
            if valuelistInfo != []:
                print(1111)
                self.brand_name_en = []
                self.brand_cn = []
                self.dos_brand_id = []
                self.brand_type = []
                self.pns_main_brand_id = []
                self.pns_main_brand_name = []
                for i in range(len(valuelistInfo)):
                    self.brand_name_en.append(valuelistInfo[i]["brand_name"])
                    self.brand_cn.append(valuelistInfo[i]["brand_cn"])
                    self.dos_brand_id.append(valuelistInfo[i]["brand_id"])
                    self.brand_type.append(valuelistInfo[i]["brand_type"])
                    self.pns_main_brand_id.append(valuelistInfo[i]["pns_main_brand_id"])
                    self.pns_main_brand_name.append(valuelistInfo[i]["pns_main_brand_name"])
                if found_match:
                    break
                for m in range(len(valuelistInfo)):
                    if self.brand_name_en[m] == brand_name:
                        if self.brand_type[m] == "1":
                            self.dos_brand_id_str = self.dos_brand_id[m]
                            self.brand_name_en_str = self.brand_name_en[m]
                            self.brand_cn_str = self.brand_cn[m]
                            self.pns_mian_brand_id_str = self.pns_main_brand_id[m]
                            self.pns_mian_brand_name_str = self.pns_main_brand_name[m]
                            if self.pns_mian_brand_id_str != "":
                                self.dos_brand_id_str = self.pns_mian_brand_id_str
                                self.brand_name_en_str = self.pns_mian_brand_name_str
                            logger.info(
                                f"获取{brand_name}的brand_id：{self.dos_brand_id_str}，brand_name：{self.brand_name_en_str}，brand_cn：{self.brand_cn_str}")
                            found_match = True
                            break
                    elif self.brand_name_en[m] in brand_name:
                        self.dos_brand_id_str = self.dos_brand_id[m]
                        self.brand_name_en_str = self.brand_name_en[m]
                        self.brand_cn_str = self.brand_cn[m]
                        self.pns_mian_brand_id_str = self.pns_main_brand_id[m]
                        self.pns_mian_brand_name_str = self.pns_main_brand_name[m]
                        if self.pns_mian_brand_id_str != "":
                            self.dos_brand_id_str = self.pns_mian_brand_id_str
                            self.brand_name_en_str = self.pns_mian_brand_name_str
                        logger.info(
                            f"获取{brand_name}的brand_id：{self.dos_brand_id_str}，brand_name：{self.brand_name_en_str}，brand_cn：{self.brand_cn_str}")
                        found_match = True
                        break
                    elif self.brand_name_en[m].lower() in brand_name.lower():
                        self.dos_brand_id_str = self.dos_brand_id[m]
                        self.brand_name_en_str = self.brand_name_en[m]
                        self.brand_cn_str = self.brand_cn[m]
                        self.pns_mian_brand_id_str = self.pns_main_brand_id[m]
                        self.pns_mian_brand_name_str = self.pns_main_brand_name[m]
                        if self.pns_mian_brand_id_str != "":
                            self.dos_brand_id_str = self.pns_mian_brand_id_str
                            self.brand_name_en_str = self.pns_mian_brand_name_str
                        logger.info(
                            f"获取{brand_name}的brand_id：{self.dos_brand_id_str}，brand_name：{self.brand_name_en_str}，brand_cn：{self.brand_cn_str}")
                        found_match = True
                        break
                    elif brand_name.lower() in self.brand_name_en[m].lower():
                        self.dos_brand_id_str = self.dos_brand_id[m]
                        self.brand_name_en_str = self.brand_name_en[m]
                        self.brand_cn_str = self.brand_cn[m]
                        self.pns_mian_brand_id_str = self.pns_main_brand_id[m]
                        self.pns_mian_brand_name_str = self.pns_main_brand_name[m]
                        if self.pns_mian_brand_id_str != "":
                            self.dos_brand_id_str = self.pns_mian_brand_id_str
                            self.brand_name_en_str = self.pns_mian_brand_name_str
                        logger.info(
                            f"获取{brand_name}的brand_id：{self.dos_brand_id_str}，brand_name：{self.brand_name_en_str}，brand_cn：{self.brand_cn_str}")
                        found_match = True
                        break
            else:
                print(112)
                check_brand_name_url = "{}/v1/goods/DgkBrand/checkBrandName".format(self.HC2018_ADMIN_URL)
                check_brand_name_body = {"brand_name": brand_name}
                check_brand_name_res = self.rss.post(url=check_brand_name_url, json=check_brand_name_body, headers=self.headers).json()
                msg = check_brand_name_res["msg"]
                print(msg)
                if msg == "名称可用":
                    add_brand_url = "{}/v1/goods/DgkBrand/brandInsert".format(self.HC2018_ADMIN_URL)
                    add_brand_body = {"brand": {"address": "", "auth_brand_append_img": "", "auth_brand_append_img_name": "", "auth_brand_img": "", "memo": "", "parent_id": "", "parent_name": "", "short_brand_desc_en": "",
                                "brand_cn_long": "", "brand_desc": "", "brand_desc_en": "", "brand_en_long": brand_name + "TEST", "brand_id": "", "brand_logo": "", "region": "","seo_brand": {}, "short_brand_desc": "",
                                "auth_brand_img_name": "授权证明", "brand_attr": "2", "brand_cn": brand_name, "brand_name": brand_name, "brand_other_name": [],"site_url" : "", "yingyonglingyu": "",
                                "is_hot": "0", "is_new": "0", "is_show": "1", "is_use": "0", "location_type": "0"
                                }}
                    add_brand_res = self.rss.post(url=add_brand_url, json=add_brand_body, headers=self.headers).json()
                    print(add_brand_body)
                    print(add_brand_res)
                    add_msg = add_brand_res["msg"]
                    logger.info(f"品牌新增结果：{add_msg}")
                    if '主品牌' in add_msg:
                        brand_name = re.search(r'【(.*?)】', add_msg).group(1)
                    dos_brand_value_url = "{}/v1/goods/DgkBrand/brandList".format(self.HC2018_ADMIN_URL)
                    dos_brand_value_body = {"brand_name": brand_name, "brand_type": "1", "is_exact": "0", "type": "0", "page": 1, "per_page": 100}
                    dos_brand_value_res = self.rss.post(url=dos_brand_value_url, json=dos_brand_value_body,headers=self.headers).json()
                    valuelistInfo = dos_brand_value_res["data"]["list"]
                    self.dos_brand_id_str = valuelistInfo[-1]["brand_id"]
                    self.brand_name_en_str = valuelistInfo[-1]["brand_name"]
                    self.brand_cn_str = valuelistInfo[-1]["brand_cn"]
                    self.is_use_str= valuelistInfo[-1]["is_use"]
                    if self.is_use_str != '1':
                        audit_brand_url = "{}/v1/goods/DgkBrand/giveAudit".format(self.HC2018_ADMIN_URL)
                        audit_brand_body = {"ids": self.dos_brand_id_str}
                        self.rss.post(url=audit_brand_url, json=audit_brand_body,headers=self.headers).json()
                        audit_brand_list_url = "{}/v1/goods/DgkBrand/brandAuditList".format(self.HC2018_ADMIN_URL)
                        audit_brand_list_body = {"brand_name": brand_name, "page": 1, "per_page": 100, "status": 1}
                        audit_brand_list_res = self.rss.post(url=audit_brand_list_url, json=audit_brand_list_body, headers=self.headers).json()
                        audit_id = audit_brand_list_res["data"]["list"][0]["id"]
                        for i in range(0, 3):
                            audit_brand_pass_url = "{}/v1/goods/DgkBrand/auditPass".format(self.HC2018_ADMIN_URL)
                            audit_brand_pass_body = {"ids": audit_id}
                            self.rss.post(url=audit_brand_pass_url, json=audit_brand_pass_body, headers=self.headers).json()
                        logger.info(f"品牌审核：{brand_name}通过")
                    logger.info(f"获取{brand_name}的brand_id：{self.dos_brand_id_str}，brand_name：{self.brand_name_en_str}，brand_cn：{self.brand_cn_str}")
                    break

        return self.dos_brand_id_str, self.brand_name_en_str
if __name__ == '__main__':
    brand_name = ""
    rss = Login().login()
    BrandMapping(rss, '6').brand_mapping_list(brand_name).brand_mapping()
    BrandMapping(rss, '4').string_list_convert("帝特(DTECH)")