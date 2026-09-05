import json
import re
import time
from pypinyin import lazy_pinyin
import jsonpath
# print("jsonpath模块路径：", jsonpath.__file__)
import yaml

from huaqiu_order_api.HC2018_admin.login.login import Login
from huaqiu_order_api.ShangHai_XinLing.menes import Means
# from xpinyin import Pinyin
from huaqiu_order_api.common.loguru_logger import logger
import requests

from huaqiu_order_api.common.my_path import stockup_dir, yaml_file, account_yaml

from huaqiu_order_api.common.my_data import Data
from huaqiu_order_api.common.yaml_handler import write_yaml


class GoodsMeans:
    def __init__(self, rss, goods_name=None, provider_name=None, pack_type=None, spq=None, cat_id_s=None):
        """
        :param goods_name:  型号名称
        :param provider_name:  品牌
        :param pack_type:  包装类型  1 卷装(TR)、2 剪切带(CT)、3 托盘(TRAY)、4 散装(BULK)、5 管装(TUBE)、6 袋装(BAG)、7 盒装(PACKAGE)
        :param spq 最小包装数量
        """
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.HC2018_ADMIN_URL = data['HC2018_ADMIN_URL']
        with open(account_yaml, 'r', encoding='utf-8') as yamlfile:
            account = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.user = account["Hc2018"]["user"]
        self.goods_name = goods_name
        self.rss = rss
        self.pack_type = pack_type
        self.auth_token = getattr(Data, 'dos_auth_token')
        self.provider_name = provider_name
        self.spq = spq
        self.cat_id_s = cat_id_s
        self.headers = {"Content-Type":"application/json;charset=UTF-8"}
        self.headers["Authorization"] = self.auth_token
        self.is_special_type_json = {1: "是", 0: "否"}
        self.user_pwd_json = {"yemao": "12345678", "taoting": "12345678", "admin": "HQ@uat@666", "zhangjin": "123456",
                              "qiufm@hqchip.com": "12345678", "liujiaowei": "12345678"}

    def goods_means_list(self, search_type=None, tag_type=None, goods_no=None):
        """商品资料列表"""
        goods_brand_search_url = "{}/v1/goods/DgkGoods/ajaxGetProviderName".format(self.HC2018_ADMIN_URL)
        goods_search_list_url = "{}/v1/goods/DgkGoods/findList".format(self.HC2018_ADMIN_URL)
        self.goods_id = None
        self.brand_id = None
        self.goods_no = None
        self.is_special_type = None
        self.special_key = None
        if goods_no==None:
            goods_brand_keyword_body = {"provider_name": self.provider_name, "src_type": 1, "brand_type": 1}
            goods_brand_search_res = self.rss.post(url=goods_brand_search_url, json=goods_brand_keyword_body, headers=self.headers).json()
            # print(goods_brand_search_res)
            goods_brand_id = jsonpath.jsonpath(goods_brand_search_res, '$..brand_id')
            # print(goods_brand_id)
            if goods_brand_id != False:
                for i in range(len(goods_brand_id)):
                    goods_search_list_body = {
                        "goods_name": self.goods_name,
                        "brand_id": goods_brand_id[i],
                        "search_type": "1",
                        "brand_type": "1",
                        "code_search_type": "1",
                        "complete_type": -1,
                        "has_stock": "-1",
                        "is_enabled": "-1",
                        "is_on_sale": "-1",
                        "self_status": "-1",
                        "type": "0",
                        "is_need_real_count": True
                    }
                    if search_type != None:
                        goods_search_list_body["search_type"] = search_type
                    if tag_type != None:
                        goods_search_list_body["type"] = tag_type
                    n = 0
                    while True:
                        try:
                            goods_search_list_res = self.rss.post(url=goods_search_list_url, json=goods_search_list_body, headers=self.headers).json()
                            time.sleep(3)
                            self.goods_id = jsonpath.jsonpath(goods_search_list_res, '$..goods_id')
                            self.goods_no = jsonpath.jsonpath(goods_search_list_res, '$..goods_no')
                            self.goods_encap = jsonpath.jsonpath(goods_search_list_res, '$..Encap')
                            self.is_special_type = jsonpath.jsonpath(goods_search_list_res, '$..is_special')
                            self.special_key = jsonpath.jsonpath(goods_search_list_res, '$..special_key')
                            self.recent_operate_user = jsonpath.jsonpath(goods_search_list_res, '$..recent_operate_user')
                            if len(self.goods_id) >= 1:
                                print(f"成功获取到goods_id:{self.goods_id}")
                                self.brand_id = goods_brand_id[i]
                                setattr(Data, 'recent_operate_user', self.recent_operate_user)
                                return self.goods_id, self.brand_id, self.goods_no, self.is_special_type, self.special_key, self.goods_encap
                        except Exception as e:
                            n += 1
                            if n < 6:
                                logger.warning(
                                    f"第 {n} 次,资料列表没有找到型号为:{self.goods_name},等待5秒后系统自动重试,错误信息:{e}")
                                time.sleep(5)
                            else:
                                # print(self.goods_id)
                                logger.error(f"资料列表查找型号为:{self.goods_name} 出错,请手动检查该型号是否存在")
                                break

            setattr(Data, 'recent_operate_user', self.recent_operate_user)
        else:
            goods_search_list_body = {
                "goods_name": "",
                "brand_id": "",
                "goods_no": goods_no,
                "search_type": "1",
                "brand_type": "1",
                "code_search_type": "1",
                "complete_type": -1,
                "has_stock": "-1",
                "is_enabled": "-1",
                "is_on_sale": "-1",
                "self_status": "-1",
                "type": "0",
                "is_need_real_count": True
            }
            n = 0
            while True:
                try:
                    goods_search_list_res = self.rss.post(url=goods_search_list_url, json=goods_search_list_body,
                                                          headers=self.headers).json()
                    time.sleep(3)
                    self.goods_id = jsonpath.jsonpath(goods_search_list_res, '$..goods_id')
                    brand_id = jsonpath.jsonpath(goods_search_list_res, '$..brand_id')
                    self.goods_encap = jsonpath.jsonpath(goods_search_list_res, '$..Encap')
                    self.is_special_type = jsonpath.jsonpath(goods_search_list_res, '$..is_special')
                    self.special_key = jsonpath.jsonpath(goods_search_list_res, '$..special_key')
                    self.recent_operate_user = jsonpath.jsonpath(goods_search_list_res, '$..recent_operate_user')
                    if len(self.goods_id) >= 1:
                        print(f"成功获取到goods_id:{self.goods_id}")
                        self.brand_id = brand_id[0]
                        setattr(Data, 'recent_operate_user', self.recent_operate_user)
                        return self.goods_id, self.brand_id, self.goods_no, self.is_special_type, self.special_key, self.goods_encap
                except Exception as e:
                    n += 1
                    if n < 6:
                        logger.warning(
                            f"第 {n} 次,资料列表没有找到型号为:{self.goods_name},等待5秒后系统自动重试,错误信息:{e}")
                        time.sleep(5)
                    else:
                        # print(self.goods_id)
                        logger.error(f"资料列表查找型号为:{self.goods_name} 出错,请手动检查该型号是否存在")
                        break

        return self.goods_id, self.brand_id, self.goods_no, self.is_special_type, self.special_key, self.goods_encap

    def goods_means_detil(self, special_type_attr_dict=None):
        """资料列表详情"""
        self.is_special = getattr(Data, 'is_special', "")
        is_special_type = ""
        for k, v in self.is_special_type_json.items():
            if self.is_special != "":
                if k == self.is_special:
                    is_special_type = v
            else:
                k = 0
                is_special_type = self.is_special_type_json[k]
        goods_means_detil_url = "{}/v1/goods/DgkGoods/viewOriginData".format(self.HC2018_ADMIN_URL)
        goods_means_detil_res = None
        if self.goods_id != None:
            for i in range(len(self.goods_id)):
                print(self.goods_id[i])
                if is_special_type == self.is_special_type[i]:
                    self.special_key_encap = self.special_key[i]
                    goods_means_detil_body = {"goods_id": self.goods_id[i], "origin": True}
                    goods_means_detil_res = self.rss.post(url=goods_means_detil_url, json=goods_means_detil_body, headers=self.headers).json()
                    if goods_means_detil_res["data"]["special_key"] != '' and "attr_value" in special_type_attr_dict:
                        if special_type_attr_dict["attr_value"] == goods_means_detil_res["data"]["special_key"].split(';;')[-1]:
                            self.special_key_encap = goods_means_detil_res["data"]["special_key"]
                            logger.info(f"特殊型号属性值:{self.special_key_encap}")
                            break
            goods_means_detil_erp_code_url = "{}/v1/goods/DgkGoods/getErpGoodsByGoodsNo".format(self.HC2018_ADMIN_URL)
            self.goods_name = goods_means_detil_res["data"]["goods_name"]
            self.goods_no = goods_means_detil_res["data"]["goods_no"]
            self.provider_name = goods_means_detil_res["data"]["provider_name"]
            self.cat_id = goods_means_detil_res["data"]["cat_id"]
            self.cat_cn = goods_means_detil_res["data"]["cat_cn"]
            packagelistInfo = goods_means_detil_res["data"].get("package_list")
            print(packagelistInfo)
            goods_means_detil_erp_code_body = {
                "goods_no": self.goods_no
            }
            self.pack_manner = ""
            if packagelistInfo != []:
                self.spq = packagelistInfo[0]["spq"]
                self.package_info = packagelistInfo[0]["package_info"]
                self.pack_manner = self.package_info.split('(')[0]
            goods_means_detil_erp_code_res = self.rss.post(url=goods_means_detil_erp_code_url, json=goods_means_detil_erp_code_body, headers=self.headers).json()
            erp_goods_sn = jsonpath.jsonpath(goods_means_detil_erp_code_res, "$..goods_sn")
            erp_goods_id = jsonpath.jsonpath(goods_means_detil_erp_code_res, "$..goods_id")
            logger.info(f"获取到型号信息【型号：{self.goods_name}，品牌：{self.provider_name}，包装方式：{self.pack_manner}，最小包装数量：{self.spq}，分类名称：{self.cat_cn}"
                            f"，芯城编码：{self.goods_no}，是否为特殊型号：{is_special_type}，特殊型号的属性值：{self.special_key_encap}】, 关联的ERP编码为：{erp_goods_sn}，ERP编码为：{erp_goods_id}")
            setattr(Data, 'erp_goods_sn', erp_goods_sn)
            return self.goods_name, self.provider_name, self.pack_manner, self.spq
    def goods_means_concrete_detil(self):
        """资料具体详情"""
        self.is_special = getattr(Data, 'is_special', "")
        is_special_type = ""
        for k, v in self.is_special_type_json.items():
            if self.is_special != "":
                if k == self.is_special:
                    is_special_type = v
            else:
                k = 0
                is_special_type = self.is_special_type_json[k]
        goods_means_concrete_detil_url = "{}/v1/goods/DgkGoods/goodsEdit".format(self.HC2018_ADMIN_URL)
        goods_means_concrete_detil_body = None
        if self.goods_id != None:
            for i in range(len(self.goods_id)):
                if is_special_type == self.is_special_type[i]:
                    goods_means_concrete_detil_body = {"goods_id": self.goods_id[i]}
            goods_means_concrete_detil_res = self.rss.post(url=goods_means_concrete_detil_url, json=goods_means_concrete_detil_body, headers=self.headers).json()
            # print(goods_means_concrete_detil_res)
            # logger.info(json.dumps(goods_means_concrete_detil_res, ensure_ascii=False).replace("'", '"'))
            self.goods_no = jsonpath.jsonpath(goods_means_concrete_detil_res, '$..goods_no')[0]
            self.goods_sn = jsonpath.jsonpath(goods_means_concrete_detil_res, '$..goods_sn')[0]
            self.cat_id = jsonpath.jsonpath(goods_means_concrete_detil_res, '$..cat_id')[0]
            self.is_shut_down = jsonpath.jsonpath(goods_means_concrete_detil_res, '$..is_shut_down')[0]
            self.is_special = jsonpath.jsonpath(goods_means_concrete_detil_res, '$..is_shut_down')[0]
            package_info = jsonpath.jsonpath(goods_means_concrete_detil_res, '$..package_list')[0]
            print(package_info)
            for item in package_info:
                if item.get('status') == '1':
                    self.packer = item.get('package_info').split('(')[0]
                    self.packer_number = item.get('spq')
                    break

        return self

    def goods_means_add(self, special_type_attr_dict=None):
        """资料创建"""
        # src_type 0资料添加页，1资料列表页
        # 创建的型号的品牌---只能查询到主品牌
        goods_brand_search_url = "{}/v1/goods/DgkGoods/ajaxGetProviderName".format(self.HC2018_ADMIN_URL)
        goods_brand_keyword_body = {"provider_name": self.provider_name, "src_type": 0}
        goods_brand_search_res = self.rss.post(url=goods_brand_search_url, json=goods_brand_keyword_body, headers=self.headers).json()
        # print(goods_brand_search_res)
        if goods_brand_search_res["data"] == []:
            print(f"在资料添加页没有查到信息﹔原因可能该品牌为非主品牌数据，转到资料列表页查询该品牌是否有效")
            goods_brand_keyword_body["src_type"] = 1
            goods_brand_search_res = self.rss.post(url=goods_brand_search_url, json=goods_brand_keyword_body, headers=self.headers).json()
        goods_brand_id = jsonpath.jsonpath(goods_brand_search_res, '$..brand_id')[0]
        logger.info(f"获取品牌id：{goods_brand_id}")
        goods_means_add_url = "{}/v1/goods/DgkGoods/addGoods".format(self.HC2018_ADMIN_URL)
        goods_means_add_body = {"ext": {"is_hqself":"0","is_shangjian": "0"},
                                "info": {"goods_sn_en": "test", "goods_other_name_en": "test", "brand_id": goods_brand_id, "cat_id": 2149,
                                         "goods_desc": "自动化测试型号", "goods_desc_en": "python-test-goods", "is_shut_down": "0",
                                        "goods_name": self.goods_name, "goods_weight": "0.100"},
                                "packArr": [{"is_default": "2", "spq": self.spq, "type_id": self.pack_type}]
                                }
        if self.cat_id_s != None:
            goods_means_add_body["info"]["cat_id"] = self.cat_id_s
        self.is_special = 0
        if special_type_attr_dict != None:
            if "special_type" in special_type_attr_dict:  # 特殊型号参数添加
                if special_type_attr_dict["special_type"] != None:
                    cat_attr_url = "{}/v1/goods/DgkGoods/ajaxCategoryAttrList".format(self.HC2018_ADMIN_URL)
                    cat_attr_body = {"cat_id": goods_means_add_body["info"]["cat_id"], "type": 0}
                    cat_attr_res = self.rss.post(url=cat_attr_url, json=cat_attr_body, headers=self.headers).json()
                    attr_id = jsonpath.jsonpath(cat_attr_res, '$..attr_id')
                    attr_name = jsonpath.jsonpath(cat_attr_res, '$..attr_name')
                    self.attr_first_value = ''  # 特殊型号参数的属性名称对应的第一个属性值
                    attr_first_name = ''  # 特殊型号参数的属性名称
                    attr_first_id = ''  # 特殊型号参数的属性名称id
                    attr_first_value_id = ''  # 特殊型号参数的属性名称对应的第一个属性值id
                    self.is_special = 1
                    if "封装/外壳" in attr_name:
                        for i in range(len(attr_id)):
                            if attr_name[i] == "封装/外壳":
                                special_attr_value_url = "{}/v1/goods/DgkGoods/ajaxAttrValueList".format(self.HC2018_ADMIN_URL)
                                special_attr_value_body = {"attr_id": attr_id[i], "attr_value": ""}
                                special_attr_value_res = self.rss.post(url=special_attr_value_url, json=special_attr_value_body, headers=self.headers).json()
                                if special_attr_value_res["data"]["value"] != []:
                                    first_key = ""
                                    if "attr_value" in special_type_attr_dict:
                                        attr_first_value = special_type_attr_dict["attr_value"]
                                        for a, b in special_attr_value_res["data"]["value"].items():
                                            if b == attr_first_value:
                                                first_key = a
                                                self.attr_first_value = attr_first_value
                                                print(f"存在属性名称：封装/外壳的指定属性值：{attr_first_value}，获取到对应属性值id：{first_key}")
                                                break
                                            else:
                                                pass
                                    else:
                                        first_key = next(iter(special_attr_value_res["data"]["value"]))
                                        self.attr_first_value = special_attr_value_res["data"]["value"][first_key]
                                    # attr_first_value此时为空或-时
                                    if self.attr_first_value in ["", "-"]:
                                        for k, v in special_attr_value_res["data"]["value"].items():
                                            if v in ["", "-"]:
                                                pass  # 跳过
                                            else:
                                                self.attr_first_value = v
                                                first_key = k
                                                break
                                    attr_first_name = attr_name[i]
                                    attr_first_id = attr_id[i]
                                    attr_first_value_id = first_key
                                    break
                        if self.attr_first_value == '':
                            for m in range(len(attr_id)):
                                special_attr_value_url = "{}/v1/goods/DgkGoods/ajaxAttrValueList".format(self.HC2018_ADMIN_URL)
                                special_attr_value_body = {"attr_id": attr_id[m], "attr_value": ""}
                                special_attr_value_res = self.rss.post(url=special_attr_value_url, json=special_attr_value_body, headers=self.headers).json()
                                if special_attr_value_res["data"]["value"] != []:
                                    first_key = next(iter(special_attr_value_res["data"]["value"]))
                                    self.attr_first_value = special_attr_value_res["data"]["value"][first_key]
                                    attr_first_name = attr_name[m]
                                    attr_first_id = attr_id[m]
                                    attr_first_value_id = first_key
                                    break
                    else:
                        for n in range(len(attr_id)):
                            special_attr_value_url = "{}/v1/goods/DgkGoods/ajaxAttrValueList".format(self.HC2018_ADMIN_URL)
                            special_attr_value_body = {"attr_id": attr_id[n], "attr_value": ""}
                            special_attr_value_res = self.rss.post(url=special_attr_value_url, json=special_attr_value_body,
                                                                   headers=self.headers).json()
                            if special_attr_value_res["data"]["value"] != []:
                                first_key = next(iter(special_attr_value_res["data"]["value"]))
                                self.attr_first_value = special_attr_value_res["data"]["value"][first_key]
                                attr_first_name = attr_name[n]
                                attr_first_id = attr_id[n]
                                attr_first_value_id = first_key
                                break
                    if attr_first_value_id != '':
                        # 当获取特殊型号属性值id不为空才能成为特殊型号
                        goods_means_add_body["info"]["is_special"] = 1
                        goods_means_add_body["info"]["special_key"] = str(attr_first_name) + ";;" + str(self.attr_first_value)
                        goods_means_add_body["attr"] = [{"attr_id": attr_first_id, "attr_value_id": attr_first_value_id}]
        goods_means_add_res = self.rss.post(url=goods_means_add_url, json=goods_means_add_body, headers=self.headers).json()
        logger.info(goods_means_add_res)
        goods_means_add_msg = goods_means_add_res["msg"]
        if goods_means_add_msg == "success":
            logger.info(f"品牌为{self.provider_name}的型号：{self.goods_name}创建成功")
        else:
            if goods_means_add_msg == "商品已存在":
                logger.info(f"品牌为{self.provider_name}的型号：{self.goods_name}已存在")
            elif goods_means_add_msg == "这个品牌没有关联芯灵品牌ID, 不能创建资料":
                logger.info(f"型号：{self.goods_name}的品牌为{self.provider_name}的这个品牌没有关联芯灵品牌ID, 不能创建资料")

            elif goods_means_add_msg == "调用芯灵接口创建资料失败":
                pass
            raise ValueError(goods_means_add_msg)
        time.sleep(3)
        setattr(Data, "is_special", self.is_special)
        return self

    def goods_means_giveaudit(self):
        """商品资料提审"""
        # 提审
        self.is_special = getattr(Data, 'is_special', "")
        self.recent_operate_user = getattr(Data, 'recent_operate_user', "")
        is_special_type = ""
        for k, v in self.is_special_type_json.items():
            if self.is_special != "":
                if k == self.is_special:
                    is_special_type = v
            else:
                k = 0
                is_special_type = self.is_special_type_json[k]
        goods_means_giveaudit_url = "{}/v1/goods/DgkGoods/giveAudit".format(self.HC2018_ADMIN_URL)
        # print('1111: {0}'.format(self.goods_id))
        if self.goods_id != None:
            for i in range(len(self.goods_id)):
                if is_special_type == self.is_special_type[i]:
                    giveaudit_user_name = self.recent_operate_user[i]
                    if giveaudit_user_name == "超级管理员":
                        giveaudit_user = "admin"
                    elif giveaudit_user_name == "仇芳梅":
                        giveaudit_user = "qiufm@hqchip.com"
                    else:
                        giveaudit_user = ''.join(lazy_pinyin(giveaudit_user_name))
                    if self.user == giveaudit_user:
                        pass
                    else:
                        if giveaudit_user in self.user_pwd_json:
                            user_pwd_params = {'admin_name': 'admin', "admin_pwd": 'HQ@uat@666', "user": giveaudit_user, "pwd": self.user_pwd_json[giveaudit_user]}
                            Hc2018_params = {"Hc2018": user_pwd_params}
                            write_yaml(account_yaml, Hc2018_params)
                            self.rss = Login().login()
                            self.auth_token = getattr(Data, 'dos_auth_token')
                            self.headers["Authorization"] = self.auth_token
                        else:
                            logger.error(f'提审人：{giveaudit_user} 不存在字典：self.user_pwd_json，请补充')
                            raise Exception
                    goods_means_giveaudit_body = {"goods_ids": self.goods_id[i]}
                    goods_means_giveaudit_res = self.rss.post(url=goods_means_giveaudit_url, json=goods_means_giveaudit_body, headers=self.headers).json()
                    logger.info(f"goods_id：{self.goods_id[i]}提审成功，提审结果：{goods_means_giveaudit_res}")
        return self

    def goods_means_audit(self):
        """商品资料审核"""
        n = 0
        k = 0
        while True:
            try:
                goods_audit_list_url = "{}/v1/goods/DgkGoods/goodsAuditList".format(self.HC2018_ADMIN_URL)
                goods_audit_list_body = {"page": 1, "per_page": 100, "status": 1, "goods_name": self.goods_name, "provider_name": self.provider_name}
                goods_audit_list_res = self.rss.post(url=goods_audit_list_url, json=goods_audit_list_body, headers=self.headers).json()
                total = jsonpath.jsonpath(goods_audit_list_res, "$..total")[0]
                found = False
                if int(total) >= 1:
                    audit_id_list = jsonpath.jsonpath(goods_audit_list_res, "$..id")
                    goods_id_list = jsonpath.jsonpath(goods_audit_list_res, "$..goods_id")
                    audit_id = ""
                    for i in range(len(goods_id_list)):
                        if goods_id_list[i] == self.goods_id[0]:
                            audit_id = audit_id_list[i]
                            logger.info(f"获取到审核id：{audit_id}")
                        break
                    goods_audit_url = "{}/v1/goods/DgkGoods/auditPass".format(self.HC2018_ADMIN_URL)
                    good_audit_body = {"ids": audit_id}
                    good_audit_res = self.rss.post(url=goods_audit_url, json=good_audit_body, headers=self.headers).json()
                    k += 1
                    if good_audit_res["msg"] == "success":
                        print(f"型号：{self.goods_name}，第{k}次审核成功")
                    if k > 4:
                        break
                elif int(total) < 1:
                    print("已审核")
                    found = True
                    break
                if found:  # 如果已通过，则跳出循环
                        logger.info("资料审核完成")
                        break
            except:
                n += 1
                print(f"{n}次循环")
                if n > 4:
                    break
        return self
    def goods_means_update(self):
        """资料修改"""
        goods_means_update_url = "{}/v1/goods/DgkGoods/updateGoods".format(self.HC2018_ADMIN_URL)
        goods_means_update_body = {"attr": [],"desc":{}, "desc_en": {}, "doc": [], "imageList": [], "tag": [],
                                   "ext": {"additive_country": "", "additive_tariffs": "","memo": "","tariff": "",
                                           "commodity_inspect": "0", "customs_inspect": "0", "customs_name": "",
                                           "is_hqself": "1", "is_shangjian": "0", "ladder_id": "1", "remind_number": "1",
                                           "min_picking_number": "1", "multi_package_goods_name": [], "origin_country": ""},
                                   "info": {"goods_id": self.goods_id[0], "goods_name": self.goods_name, "goods_desc": "测试型号",
                                            "goods_desc_en": "testGoods","provider_name": self.provider_name, "goods_weight": "0.1",
                                            "goods_eccn": "", "special_key": "", "goods_other_name": [], "goods_other_name_en": "",
                                            "customs_code": "", "goods_sn_en": "","brand_id": self.brand_id, "cat_id": self.cat_id,
                                            "goods_no": self.goods_no, "goods_sn": self.goods_sn, "is_shut_down": self.is_shut_down,
                                            "is_special": self.is_special},
                                   "packArr": [{"type_id": self.pack_type, "is_default": 2, "spq": 1000}]}
        goods_means_update_res = self.rss.post(url=goods_means_update_url, json=goods_means_update_body, headers=self.headers).json()
        if goods_means_update_res["msg"] == "success":
            logger.info(f"goods_id: {self.goods_id[0]}")
        return self
    def goods_means_forbidden(self):
        """商品资料禁用"""
        self.is_special = getattr(Data, 'is_special', "")
        if self.is_special == "":
            self.is_special = 0
        is_special_type = ""
        for k, v in self.is_special_type_json.items():
            if self.is_special != "":
                if k == self.is_special:
                    is_special_type = v
            else:
                k = 0
                is_special_type = self.is_special_type_json[k]

        goods_means_forbidden_url = "{}/v1/goods/DgkGoods/goodsInvalid".format(self.HC2018_ADMIN_URL)
        goods_id = []
        for i in range(len(self.goods_id)):
            if is_special_type == self.is_special_type[i]:
                goods_id.append(self.goods_id[i])
            else:
                is_special_type = "是"
                if self.special_key != self.is_special_type[i]:
                    goods_id.append(self.goods_id[i])
                    is_special_type = "否"
        goods_id_str = ','.join(goods_id)
        goods_means_forbidden_body = {"goods_id": goods_id_str, "memo": "自动化测试"}
        goods_means_forbidden_res = self.rss.post(url=goods_means_forbidden_url, json=goods_means_forbidden_body, headers=self.headers).json()
        print(f"goods_id：{goods_id_str}，禁用结果：{goods_means_forbidden_res}")
        return self
    def goods_means_enable(self):
        """商品资料启用"""
        self.is_special = getattr(Data, 'is_special', "")
        if self.is_special == "":
            self.is_special = 0
        is_special_type = ""
        for k, v in self.is_special_type_json.items():
            if self.is_special != "":
                if k == self.is_special:
                    is_special_type = v
            else:
                k = 0
                is_special_type = self.is_special_type_json[k]
        goods_means_enable_url = "{}/v1/goods/DgkGoods/restartGoods".format(self.HC2018_ADMIN_URL)
        for i in range(len(self.goods_id)):
            if is_special_type == self.is_special_type[i]:
                goods_means_enable_body = {"goods_id": self.goods_id[i]}
                goods_means_enable_res = self.rss.post(url=goods_means_enable_url, json=goods_means_enable_body, headers=self.headers).json()
                print(f"goods_id: {self.goods_id[i]}，启用结果：{goods_means_enable_res}")
            else:
                is_special_type = "是"
                if self.special_key != self.is_special_type[i]:
                    goods_means_enable_body = {"goods_id": self.goods_id[i]}
                    goods_means_enable_res = self.rss.post(url=goods_means_enable_url, json=goods_means_enable_body, headers=self.headers).json()
                    print(f"goods_id: {self.goods_id[i]}，启用结果：{goods_means_enable_res}")
                    is_special_type = "否"
        return self

    def mian_means_add(self, special_type_attr_dict=None):
        """商品资料新增→ →审核"""
        self.goods_means_add(special_type_attr_dict=special_type_attr_dict)
        erp_goods_sn = None
        self.goods_id, self.brand_id, self.goods_no, self.is_special_type, self.special_key, self.goods_encap = self.goods_means_list()
        if self.goods_id != []:
            self.goods_means_giveaudit()
            self.goods_means_audit()
            self.goods_means_detil(special_type_attr_dict=special_type_attr_dict)
            mpn, mfg, erp_goods_sn = Means().menes_search()
            # print(mpn, mfg, erp_goods_sn)
            if self.goods_name == mpn and self.provider_name == mfg:
                logger.info("商品资料: {}创建成功并且匹配芯灵".format(self.goods_name))
        return self.goods_id, self.brand_id, self.goods_no, erp_goods_sn

    def mian_means_stay_perfect(self):
        """待创建商品资料新增→ →审核"""
        self.goods_id, self.brand_id, self.goods_no, self.is_special_type, self.special_key, self.goods_encap = self.goods_means_list()
        if self.goods_id != []:
            self.goods_means_giveaudit()
            self.goods_means_audit()
            self.goods_means_detil()
        return self.goods_id, self.brand_id, self.goods_no
    def mian_means_update(self):
        """商品资料修改→ →审核"""
        self.goods_id, self.brand_id, self.goods_no, self.is_special_type, self.special_key, self.goods_encap = self.goods_means_list()
        if self.goods_id != []:
            self.goods_name, self.provider_name, self.pack_manner, self.spq = self.goods_means_detil()
            if self.spq == None:
                self.goods_means_concrete_detil()
                self.goods_means_update()
                self.goods_means_giveaudit()
                self.goods_means_audit()
                self.goods_means_detil()
        return self.goods_id, self.brand_id, self.goods_no
    def mian_goods_forbidden_enable(self):
        """商品资料禁用→ →启用"""
        self.goods_id, self.brand_id, self.goods_no, self.is_special_type, self.special_key, self.goods_encap = self.goods_means_list()
        if self.goods_id != []:
            self.goods_means_forbidden()
            self.goods_means_enable()
            self.goods_means_detil()
        return self.goods_id, self.brand_id, self.goods_no
    def mian_goods_enable(self):
        """商品资料启用"""
        self.goods_id, self.brand_id, self.goods_no, self.is_special_type, self.special_key, self.goods_encap = self.goods_means_list(tag_type="2")
        if self.goods_id != []:
            self.goods_means_enable()
            self.goods_means_detil()
        return self.goods_id, self.brand_id, self.goods_no
    def mian_goods_forbidden(self):
        """商品资料禁用"""
        self.goods_id, self.brand_id, self.goods_no, self.is_special_type, self.special_key, self.goods_encap = self.goods_means_list()
        if self.goods_id != []:
            self.goods_means_forbidden()
            self.goods_means_detil()
        return self.goods_id, self.brand_id, self.goods_no
    def mian_goods_giveaudit_audit(self):
        """商品资料提审→ → 审核"""
        self.goods_id, self.brand_id, self.goods_no, self.is_special_type, self.special_key, self.goods_encap = self.goods_means_list()
        if self.goods_id != []:
            self.goods_means_giveaudit()
            self.goods_means_audit()
            self.goods_means_detil()
        return self.goods_id, self.brand_id, self.goods_no

    def mian_goods_search(self, search_type=None, tag_type=None, goods_no=None):
        """型号查询"""
        self.goods_means_list(search_type=search_type, tag_type=tag_type, goods_no=goods_no)
        self.goods_means_concrete_detil()
        return self.packer, self.packer_number


if __name__ == '__main__':
    goods_name = "dzz888"
    provider_name = "TI"
    packer = "1"
    spq = 1000
    cat_id_s = None
    import pandas as pd
    file = ""
    rss = Login().login()
    if file:
        data = pd.read_excel(file)
        print(data)
        # if isinstance(data, pd.DataFrame):
        goods_name = data["型号(必填)"].tolist()
        # print(type(goods_name))
        # print(goods_name)
        provider_name = data["品牌(必填)"].tolist()
        # packer = data["包装"]
        spq = data["包装数量"].tolist()
        # if isinstance(goods_name, list):
        for i in range(44, len(goods_name)):
            # print(i)
            GoodsMeans(rss, goods_name[i], provider_name[i], packer, spq[i], cat_id_s).mian_means_add()
    else:
        # GoodsMeans(rss, "ERJ6ENF1153V", "Panasonic", "1", 1000).mian_goods_giveaudit_audit()
        # GoodsMeans(rss, "GRM0335C1H2R7BA01D", "TE", "1", 1000).mian_goods_search(goods_no="MS0000127")  # special_type_attr_dict={"special_type": 1, "attr_value": "SOD-323"}
        GoodsMeans(rss, goods_name, provider_name, packer, spq, cat_id_s).mian_means_add()
    # GoodsMeans(rss, "wuqi0001", "yageo", "1", 1000).goods_means_list()

