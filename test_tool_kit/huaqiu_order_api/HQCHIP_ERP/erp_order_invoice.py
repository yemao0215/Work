import json
import re
import time
from datetime import datetime

import jsonpath
import numpy as np
import requests
import yaml
from faker import Faker

from huaqiu_order_api.HQCHIP_Activity.big_data.user_promotion import UserPromotion
from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_data import Data
from huaqiu_order_api.common.my_path import yaml_file

class ErpOrderInvoice:


    def __init__(self, rss):
        """
        :param account:  登录ERP账号
        :param psw:  登录ERP密码
        :param order_sn:  前台商城生成订单编号
        :param uesr:    前台商城生成订单编号的用户名称
        """
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.ERP_URL = data['ERP_URL']

        # self.order_sn = getattr(Data, 'ic_order_sn')
        self.order_sn = "S2023091544856"
        # self.uesr = getattr(Data, 'username')
        self.rss = rss
        self.headers = {'Content-Type': 'application/x-www-form-urlencoded',
                        "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://www.huaqiu.com)"
                        }
        self.json_head = {"Content-Type": "application/json",
                          "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://www.huaqiu.com)"
                          }
    def invoice_sync(self):
        """发票同步"""
        search_url = "{}/InvoicePrepare/loadOrder".format(self.ERP_URL)
        search_body = {"order_sn": self.order_sn}
        logger.info(f"搜索订单编号: {self.order_sn}")
        search_res = self.rss.post(url=search_url, data=search_body, headers=self.headers, timeout=1000).json()  # 搜索订单，获取order_id
        self.order_id = jsonpath.jsonpath(search_res, '$..order_id')[0]
        logger.info(f"搜索完成,获取到order_id: {self.order_id}")

        sync_create_url = "{}/InvoicePrepare/syncInvoiceCreate".format(self.ERP_URL)
        sync_create_body = {"order_id_array[]": self.order_id, "order_sn_array[]": self.order_sn}
        sync_create_res = self.rss.post(url=sync_create_url, data=sync_create_body, headers=self.headers, timeout=1000).json()
        if self.order_sn in sync_create_res["success"]:
            logger.info("同步成功")
        return self
    def invoice_update_recive(self):
        """修改发票信息的收货地址"""
        invoice_update_gain_url = "{}/InvoicePrepare/detail/id/{}/navTabId/InvoicePrepare".format(self.ERP_URL,
                                                                                             self.invoice_detail_id)
        invoice_update_res = self.rss.get(url=invoice_update_gain_url).text
        self.vat_type_name = re.search('(<label>发票类型：</label>)\s*(<label>)([\u4e00-\u9fa5]*)',
                                       invoice_update_res).group(3)
        # logger.info(self.vat_type_name)
        self.inv_type_name = re.search('(<label>抬头类型：</label>)\s*(<label>)([\u4e00-\u9fa5]*)',
                                       invoice_update_res).group(3)
        self.recive_type_name = re.search('(<label>发票配送方式：</label>)\s*(<label>)([\u4e00-\u9fa5]*)',
                                          invoice_update_res).group(3)
        vat_company = re.search('(<label>开票公司：</label>)\s*(<label>)([\u4e00-\u9fa5]*)',
                                invoice_update_res).group(3)
        vat_registration_sn = re.search('(<label>税务登记号：</label>)\s*(<label>)([\u4e00-\u9fa5]*)',
                                        invoice_update_res).group(3)
        vat_bank = re.search('(<label>公司开户行：</label>)\s*(<label>)([\u4e00-\u9fa5]*)',
                             invoice_update_res).group(3)
        vat_bank_sn = re.search('(<label>银行账号：</label>)\s*(<label>)([0-9]*)',
                                invoice_update_res).group(3)
        vat_address = re.search('(<label>注册地址：</label>)\s*(<label>)([\u4e00-\u9fa5]*)',
                                invoice_update_res).group(3)
        # 检索固定电话 带”-“，例如：0755-56418592
        vat_tel = re.search('(<label>注册电话：</label>)\s*(<label>)([0-9]*\-?[0-9]+)',
                            invoice_update_res).group(3)
        # logger.info(vat_tel)

        logger.info(
            f"获取到vat_type_name：{self.vat_type_name}，inv_type_name：{self.inv_type_name}，recive_type_name：{self.recive_type_name}，"
            f"vat_company：{vat_company}，vat_registration_sn：{vat_registration_sn}，vat_bank：{vat_bank}，vat_bank_sn：{vat_bank_sn}，"
            f"vat_address：{vat_address}，vat_tel：{vat_tel}")
        if self.vat_type_name == "增值税专用发票":
            self.vat_type = "1"
        elif self.vat_type_name == "普通电子发票":
            self.vat_type = "0"
        logger.info(f"vat_type为{self.vat_type}")
        if self.inv_type_name == "企业单位":
            self.inv_type = "2"
        elif self.inv_type_name in "个人":
            self.inv_type = "1"
        logger.info(f"inv_type为{self.inv_type}")
        if self.recive_type_name == "随货发":
            self.recive_type = "1"
        elif self.recive_type_name == "单独寄出":
            self.recive_type = "2"
        logger.info(f"recive_type为{self.recive_type}")
        province_url = "{}/ajax/region?type=getChild&region_type={}&parent_id={}".format(self.ERP_URL, 2, 6)
        self.rss.get(url=province_url)
        city_url = "{}/ajax/region?type=getChild&region_type={}&parent_id={}".format(self.ERP_URL, 3, 77)
        self.rss.get(url=city_url)
        recive_update_url = "{}/InvoicePrepare/detail/navTabId/InvoicePrepare".format(self.ERP_URL)
        recive_update_body = {"id": self.invoice_detail_id, "is_edit": 1, "users_vat_id": -1, "vat_type": self.vat_type, "inv_type": self.inv_type,
                              "recive_type": self.recive_type, "vat_company": vat_company, "vat_registration_sn": vat_registration_sn, "vat_bank": vat_bank,
                              "vat_bank_sn": vat_bank_sn, "vat_address": vat_address, "vat_tel": vat_tel, "recive_consignee": "自动化测试",
                              "recive_mobile": 15912757721, "recive_province": 6, "recive_city": 77, "recive_district": 705,
                              "recive_address": "新一代产业园1栋5楼", "ajax": 1, "is_iframe": 1
                              }
        recive_update_body = UserPromotion("sign").query_url_arguments(recive_update_body)
        logger.info(recive_update_body)
        recive_update_res = self.rss.post(url=recive_update_url, data=recive_update_body, headers=self.headers, timeout=1000).text
        rep_msg = recive_update_res.split('var response = ')[1].split(';')[0]
        rep_msg_json = json.loads(rep_msg)
        logger.info(f"执行结果为{rep_msg_json}")
        return self

    def invoice_search(self):
        """待开票管理查询"""
        search_url = "{}/InvoicePrepare/index".format(self.ERP_URL)
        search_body = {"search_key": "order_sn", "search_val": self.order_sn, "pageNum": 1, "numPerPage": 20,
                       "luopan_type": 1, "luopan_show": 1, "vat_type": -1, "system_type": 1}

        search_res = self.rss.post(url=search_url, data=search_body, headers=self.headers, timeout=1000).text
        invoice_method_excerpt = search_res.split('<tr target="id"')[1].split('<td text_type="right">')[0]
        self.invoice_method = re.search("[\u4e00-\u9fa5]+开票", invoice_method_excerpt).group(0)
        # self.invoice_type = re.search("[\u4e00-\u9fa5]+发票", invoice_method_excerpt).group(0)
        # logger.info(self.invoice_method)
        self.luopan_type = ""
        if self.invoice_method == "按订单开票":
            self.luopan_type = 2
        elif self.invoice_method == "累计开票":
            self.luopan_type = 3
        elif self.invoice_method == "无需开票":
            pass
        self.invoice_detail_id = re.search('(<td><a href="/InvoicePrepare/detail/id/)([0-9]{6})', search_res).group(2)
        # logger.info(self.invoice_detail_id)
        invoice_detail_url = "{}/InvoicePrepare/add_invoice/navTabId/InvoicePrepare/luopan_type/{}?id={}".format(self.ERP_URL, self.luopan_type, self.invoice_detail_id)
        invoice_detail_res = self.rss.get(url=invoice_detail_url).text
        # 匹配元素定位属性值rec_id[]，利用正则(.*?)
        self.rec_id = re.search('(<input type="checkbox" name="(.*?)" value=")([0-9]{7})', invoice_detail_res).group(3)
        # logger.info(self.rec_id)
        self.wait_invoice_number = re.search('(<td text_type="right"><input type="text" name="prepare_number(.*?)" value="(.*?)")', invoice_detail_res).group(3)
        # logger.info(self.wait_invoice_number)
        self.wait_invoice_amount_count = re.search('(<td text_type="right"><input type="text" name="prepare_amount(.*?)" value="(.*?)")',
                                  invoice_detail_res).group(3)
        # logger.info(self.wait_invoice_amount_count)
        logger.info(f"获取到invoice_detail_id: {self.invoice_detail_id}, rec_id:{self.rec_id}, wait_invoice_number: {self.wait_invoice_number}, "
                    f"wait_invoice_amount_count: {self.wait_invoice_amount_count}")
        self.invoice_update_recive()
        self.rss.post(url=search_url, data=search_body, headers=self.headers, timeout=1000)
        return self

    def invoicing_all(self):
        """全部开票"""
        invoicing_url = "{}/InvoicePrepare/insert_invoice/navTabId/InvoicePrepare".format(self.ERP_URL)
        invoicing_body = {"id": self.invoice_detail_id, "luopan_type": self.luopan_type, "order_id[]": self.order_id, "rec_id[]": self.rec_id,
                         f"prepare_number[{self.rec_id}]":  self.wait_invoice_number, f"prepare_amount[{self.rec_id}]": self.wait_invoice_amount_count,
                          "ajax": 1, "is_iframe": 1
                          }
        invoicing_res = self.rss.post(url=invoicing_url, data=invoicing_body, headers=self.headers, timeout=1000).text
        rep_msg = invoicing_res.split('var response = ')[1].split(';')[0]
        rep_msg_json = json.loads(rep_msg)
        logger.info(f"执行结果为{rep_msg_json}")
        if "收货人信息未填写完整" in rep_msg_json["info"]:
            # self.invoice_update_recive()
            invoicing_body["recive_consignee"] = "自动化测试"
            invoicing_body["recive_mobile"] = 15912757721
            invoicing_body["recive_province"] = 6
            invoicing_body["recive_city"] = 77
            invoicing_body["recive_district"] = 705
            invoicing_body["recive_address"] = "新一代产业园1栋5楼"
            invoicing_res = self.rss.post(url=invoicing_url, data=invoicing_body, headers=self.headers,timeout=1000).text
            rep_msg = invoicing_res.split('var response = ')[1].split(';')[0]
            rep_msg_json = json.loads(rep_msg)
            logger.info(f"执行结果为{rep_msg_json}")
            
        return self
    def invocing_part(self):
        """部分开票"""
        invoicing_url = "{}/InvoicePrepare/insert_invoice/navTabId/InvoicePrepare".format(self.ERP_URL)
        invoice_number = Faker("zh_CN").random_int(1, int(self.wait_invoice_number))
        if invoice_number != 0 and invoice_number <= int(self.wait_invoice_number):
            invoice_amount_count = round(np.random.uniform(0, float(self.wait_invoice_amount_count)), 2)
            invoicing_body = {"id": self.invoice_detail_id, "luopan_type": self.luopan_type, "order_id[]": self.order_id, "rec_id[]": self.rec_id,
                         f"prepare_number[{self.rec_id}]":  invoice_number, f"prepare_amount[{self.rec_id}]": invoice_amount_count,
                          "ajax": 1, "is_iframe": 1
                          }
            invoicing_res = self.rss.post(url=invoicing_url, data=invoicing_body, headers=self.headers, timeout=1000).text
            rep_msg = invoicing_res.split('var response = ')[1].split(';')[0]
            rep_msg_json = json.loads(rep_msg)
            logger.info(f"执行结果为{rep_msg_json}")
            # if "收货人信息未填写完整" in rep_msg_json["info"]:
            #     self.invoice_update_recive()
            #     invoicing_res = self.rss.post(url=invoicing_url, data=invoicing_body, headers=self.headers, timeout=1000).text
            #     rep_msg = invoicing_res.split('var response = ')[1].split(';')[0]
            #     rep_msg_json = json.loads(rep_msg)
            #     logger.info(f"执行结果为{rep_msg_json}")
        return self
    def invocing_in_batches(self):
        """分批开票"""
        invoicing_url = "{}/InvoicePrepare/insert_invoice/navTabId/InvoicePrepare".format(self.ERP_URL)
        invoice_number = Faker("zh_CN").random_int(1, int(self.wait_invoice_number))
        if invoice_number != 0 and invoice_number <= int(self.wait_invoice_number):
            invoice_amount_count = round(np.random.uniform(0, float(self.wait_invoice_amount_count)), 2)
            invoicing_body = {"id": self.invoice_detail_id, "luopan_type": self.luopan_type, "order_id[]": self.order_id, "rec_id[]": self.rec_id,
                         f"prepare_number[{self.rec_id}]":  invoice_number, f"prepare_amount[{self.rec_id}]": invoice_amount_count,
                          "ajax": 1, "is_iframe": 1
                          }
            invoicing_res = self.rss.post(url=invoicing_url, data=invoicing_body, headers=self.headers, timeout=1000).text
            rep_msg = invoicing_res.split('var response = ')[1].split(';')[0]
            rep_msg_json = json.loads(rep_msg)
            logger.info(f"执行结果为{rep_msg_json}")
            # if "收货人信息未填写完整" in rep_msg_json["info"]:
            #     self.invoice_update_recive()
            #     invoicing_res = self.rss.post(url=invoicing_url, data=invoicing_body, headers=self.headers, timeout=1000).text
            #     rep_msg = invoicing_res.split('var response = ')[1].split(';')[0]
            #     rep_msg_json = json.loads(rep_msg)
            #     logger.info(f"执行结果为{rep_msg_json}")
            invoice_number_residue = int(self.wait_invoice_number) - invoice_number
            invoice_amount_count_residue = float(self.wait_invoice_amount_count) - invoice_amount_count
            invoicing_body_residue = {"id": self.invoice_detail_id, "luopan_type": self.luopan_type, "order_id[]": self.order_id, "rec_id[]": self.rec_id,
                         f"prepare_number[{self.rec_id}]":  invoice_number_residue, f"prepare_amount[{self.rec_id}]": invoice_amount_count_residue,
                          "ajax": 1, "is_iframe": 1
                          }
            invoicing_res = self.rss.post(url=invoicing_url, data=invoicing_body_residue, headers=self.headers, timeout=1000).text
            rep_msg_residue = invoicing_res.split('var response = ')[1].split(';')[0]
            rep_msg_residue_json = json.loads(rep_msg_residue)
            logger.info(f"执行结果为{rep_msg_residue_json}")
            # if "收货人信息未填写完整" in rep_msg_json["info"]:
            #     self.invoice_update_recive()
            #     invoicing_res = self.rss.post(url=invoicing_url, data=invoicing_body_residue, headers=self.headers, timeout=1000).text
            #     rep_msg = invoicing_res.split('var response = ')[1].split(';')[0]
            #     rep_msg_json = json.loads(rep_msg)
            #     logger.info(f"执行结果为{rep_msg_json}")

        elif invoice_number == 0:
            invoice_number = int(self.wait_invoice_number)
            invoice_amount_count = self.wait_invoice_amount_count
            invoicing_body = {"id": self.invoice_detail_id, "luopan_type": self.luopan_type, "order_id[]": self.order_id, "rec_id[]": self.rec_id,
                         f"prepare_number[{self.rec_id}]":  invoice_number, f"prepare_amount[{self.rec_id}]": invoice_amount_count,
                          "ajax": 1, "is_iframe": 1
                          }
            invoicing_res = self.rss.post(url=invoicing_url, data=invoicing_body, headers=self.headers, timeout=1000).text
            rep_msg = invoicing_res.split('var response = ')[1].split(';')[0]
            rep_msg_json = json.loads(rep_msg)
            logger.info(f"执行结果为{rep_msg_json}")
        else:
            logger.error('执行失败')


    def invoicing_gain(self):
        """查询指定订单下存在的开票编号"""
        search_url = "{}/invoice".format(self.ERP_URL)
        search_body = {"keytype": "order_sn", "keyword": self.order_sn, "pageNum": 1}
        search_res = self.rss.post(url=search_url, data=search_body, headers=self.headers, timeout=1000).text
        # re.findall 匹配多个定位值并且打印出成一个list列表形式
        invocing_code_match = re.findall('(<a class="edit" href="/invoice/sf_order_all/id/)([0-9]{6})', search_res, re.DOTALL)
        # logger.info(invocing_code_match)
        invocing_code_list = []
        # 提取 开票编号
        for i in range(len(invocing_code_match)):
            invocing_code_list.append(invocing_code_match[i][1])
        logger.info(f"获取到开票编号列表为：{invocing_code_list}")
        return invocing_code_list
    def invoice_manage(self):
        """发票管理"""
        invocing_code_list = self.invoicing_gain()
        for i in range(len(invocing_code_list)):
            manage_search_url = "{}/invoice".format(self.ERP_URL)
            manage_search_body = {"keytype": "invoice_statistics_id", "keyword": invocing_code_list[i], "status": "", "pageNum": 1}
            manage_search_res = self.rss.post(url=manage_search_url, data=manage_search_body, headers=self.headers, timeout=1000).text
            # logger.info(manage_search_res)
            self.invoice_id = invocing_code_list[i]
            manage_search_excerpt = manage_search_res.split('<!--<td>普通电子发票</td>-->')[1]
            self.invoice_type = re.search("[\u4e00-\u9fa5]+发票", manage_search_excerpt).group(0)
            # logger.info(self.invoice_type)
            # 确认发票
            check_url = "{}/invoice/checkinvoice/id/{}".format(self.ERP_URL, self.invoice_id)
            check_res = self.rss.post(url=check_url, headers=self.json_head, timeout=1000).json()
            logger.info(f"执行结果为：{check_res}")
            # 填写发票号
            # 随机生成发票号
            invoice_number = Faker("zh_CN").random_int(1, 999999999)
            logger.info(f"随机生成发票号：{invoice_number}")
            # fill_invoice_number_url ="{}/invoice/submitopen/navTabId/Invoice".format(self.ERP_URL)
            if self.invoice_type == "增值税专用发票":
                self.open_type = 3
            elif self.invoice_type == "普通电子发票":
                self.open_type = 2
            fill_invoice_number_url = "{}/invoice/submitopen/navTabId/Invoice".format(self.ERP_URL)
            fill_invoice_number_body = {"id": self.invoice_id, "edit_invoice_sn": invoice_number, "open_type": self.open_type,"ajax": 1, "is_iframe": 1}
            fill_invoice_number_res = self.rss.post(url=fill_invoice_number_url, data=fill_invoice_number_body, timeout=1000).json()
            # 获取字典的键值（名称）并且以list汇总输出
            res_key = list(fill_invoice_number_res.keys())
            logger.info(f"手填发票号成功,执行结果为{fill_invoice_number_res}")
            if "confirmMsg" in res_key:
                if "是否继续开票" in fill_invoice_number_res["confirmMsg"]:
                    affirm_audit_url = fill_invoice_number_res["forwardUrl"]
                    invoice_audit_url = self.ERP_URL + affirm_audit_url
                    logger.info(invoice_audit_url)
                    purchase_audit_body = {"id": self.invoice_id, "status": -1, "is_t_order": 2, "list_sort": ""}
                    self.rss.post(url=invoice_audit_url, data=purchase_audit_body, headers=self.headers)
                    logger.info(f"执行成功")
            else:
                logger.info("确认成功")
            if self.invoice_type == "增值税专用发票":
                invoice_delivery_url = "{}/Invoice/sf_order_all?navTabId=Invoice".format(self.ERP_URL)
                invoice_delivery_body = {"id": self.invoice_id, "shipping_name": 1, "shipping_type": 102, "shipping_pay_type": 1, "remark": "发票", "ajax": 1, "is_iframe": 1}
                invoice_delivery_res = self.rss.post(url=invoice_delivery_url, data=invoice_delivery_body, timeout=1000).json()
                logger.info(f"执行结果：{invoice_delivery_res}")
        return self






if __name__ == '__main__':

    from huaqiu_order_api.HQCHIP_ERP.login import ErpLogin
    rss = ErpLogin().login()
    ErpOrderInvoice(rss).invoice_sync().invoice_search().invoicing_all().invoice_manage()
    # ErpOrderInvoice(rss).invoice_sync().invoice_search()