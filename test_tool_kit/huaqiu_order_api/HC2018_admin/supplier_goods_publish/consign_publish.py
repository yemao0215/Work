import datetime
import json
import math
import re
import time

import jsonpath
import openpyxl
import pandas as pd
import yaml
from openpyxl.cell import cell
from xpinyin import Pinyin

from huaqiu_order_api.HC2018_admin.dgk_goods_means.dgk_goods_means import GoodsMeans
from huaqiu_order_api.HC2018_admin.dgk_goods_means.stay_perfect_means import StayPerfectMeans
from huaqiu_order_api.HC2018_admin.login.login import Login
from huaqiu_order_api.HC2018_admin.supplier_goods_publish.supplier_stock_aduit.stock_aduit import StockAudit
from huaqiu_order_api.HC2018_admin.work_sheet.work_sheet import WorkSheet
from huaqiu_order_api.HQCHIP_ERP.erp_order_putaway import ErpOrderPutaway
from huaqiu_order_api.HQCHIP_ERP.login import ErpLogin
from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_data import Data
from huaqiu_order_api.common.my_path import stockup_dir, yaml_file, account_yaml
from huaqiu_order_api.common.yaml_handler import write_yaml



class ConsignPublish:
    # 寄售发布
    def __init__(self, rss, consign_sn=None, goods_name=None, supplier_sn=None):
        """
        :param goods_name:  型号
        :param consign_sn:  寄售发布单号
        """
        self.rss = rss
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.HC2018_ADMIN_URL = data['HC2018_ADMIN_URL']
        self.auth_token = getattr(Data, 'dos_auth_token')
        self.goods_name = goods_name
        self.consign_sn = consign_sn
        self.supplier_sn = supplier_sn
        self.headers = {"Content-Type": "application/x-www-form-urlencoded",
                        "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://www.huaqiu.com)"
                        }
        self.headers_json = {"Content-Type": "application/json; charset=UTF-8",
                             "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://www.huaqiu.com)"
                             }
        self.supplier_name_json = {"hqchip-llsjl": "测试专用账号1"}
        self.headers_json["Authorization"] = self.auth_token

    def consign_publish_list(self, status=None):
        """寄售发布查询"""
        search_url = "{}/v1/supplier/SuppPublish/stockLog".format(self.HC2018_ADMIN_URL)
        search_body = {"change_sn": "", "end_add_time": "", "goods_name": self.goods_name, "is_audit": 0,
                       "page": 1, "per_page": 100, "start_add_time": "", "status": -10, "supplier_id": "", "type": 1}
        if status != None:
            search_body["status"] = status
        consign_publish = []
        order_id_count = []
        order_sn_count = []
        supplier_id_count = []
        if self.supplier_sn != None:
            supplier_id = StockAudit(self.rss, supplier_sn_name=self.supplier_sn).supplier_id_search()
            if supplier_id != []:
                for i in range(len(supplier_id)):
                    search_body["supplier_id"] = supplier_id[i]
                    search_res = self.rss.post(url=search_url, json=search_body, headers=self.headers_json).json()
                    total = jsonpath.jsonpath(search_res, "$..total")[0]
                    if int(total) >= 100:
                        total_num = math.ceil(int(total) / 100)
                        for a in range(total_num):
                            search_body['page'] = a + 1
                            search_res = self.rss.post(url=search_url, json=search_body, headers=self.headers_json).json()
                            order_id = jsonpath.jsonpath(search_res, "$..order_id")
                            order_sn = jsonpath.jsonpath(search_res, "$..order_sn")
                            supplier_id_list = jsonpath.jsonpath(search_res, "$..supplier_id")
                            order_sn_count = order_sn + order_sn_count
                            order_id_count = order_id + order_id_count
                            supplier_id_count = supplier_id_count + supplier_id_list
                    else:
                        order_id_count = jsonpath.jsonpath(search_res, "$..order_id")
                        order_sn_count = jsonpath.jsonpath(search_res, "$..order_sn")
                        supplier_id_count = jsonpath.jsonpath(search_res, "$..supplier_id")
                    for n in range(len(order_id_count)):
                        print(f"此时：订单号为{order_sn_count[n]}")
                        # 审核
                        StockAudit(self.rss, supplier_sn_name=self.supplier_sn, order_id=order_id_count[n]).mian_stock_aduit_consign()
                        # 获取订单内型号详情
                        order_detail_url = "{}/v1/supplier/SupplierOrder/getUploadStockItem".format(self.HC2018_ADMIN_URL)
                        order_detail_body = {"page": 1, "per_page": 100, "supplier_id": supplier_id_count[n], "order_id": order_id_count[n]}
                        order_detail_res = self.rss.post(url=order_detail_url, json=order_detail_body, headers=self.headers_json).json()
                        detail_total = jsonpath.jsonpath(order_detail_res, "$..total")[0]
                        goods_name_count = []
                        provider_name_count = []
                        to_be_add_goods_mark_count = []
                        if int(detail_total) >= 100:
                            total_num = math.ceil(int(detail_total) / 100)
                            for m in range(total_num):
                                order_detail_body['page'] = m + 1
                                order_detail_res = self.rss.post(url=order_detail_url, json=order_detail_body, headers=self.headers_json).json()
                                goods_name = jsonpath.jsonpath(order_detail_res, "$..goods_name")
                                provider_name = jsonpath.jsonpath(order_detail_res, "$..provider_name")
                                to_be_add_goods_mark = jsonpath.jsonpath(order_detail_res, "$..to_be_add_goods_mark")
                                goods_name_count = goods_name_count + goods_name
                                provider_name_count = provider_name_count + provider_name
                                to_be_add_goods_mark_count = to_be_add_goods_mark_count + to_be_add_goods_mark
                        else:
                            goods_name_count = jsonpath.jsonpath(order_detail_res, "$..goods_name")
                            provider_name_count = jsonpath.jsonpath(order_detail_res, "$..provider_name")
                            to_be_add_goods_mark_count = jsonpath.jsonpath(order_detail_res, "$..to_be_add_goods_mark")
                        print(f"goods_name:{goods_name_count}, provider_name:{provider_name_count}, to_be_add_goods_mark:{to_be_add_goods_mark_count}")
                        # 判断型号对应标识是否待创建资料
                        for k in range(len(goods_name_count)):
                            if to_be_add_goods_mark_count[k] == 1:
                                print(1112)
                                print(f"{goods_name_count[k], provider_name_count[k]}型号对应标识为待创建资料，开始创建")
                                StayPerfectMeans(self.rss, goods_name=goods_name_count[k], provider_name=provider_name_count[k], source_type='consign').mian_stay_perfect_means_new()
                        # 获取发货明细内容
                        consign_detail_url = "{}/v1/supplier/SuppPublish/getPurchaseOrderList".format(self.HC2018_ADMIN_URL)
                        consign_detail_body = {"order_id": order_id_count[n], "is_new_jishou": "1", "page": 1, "per_page": 100, "picking_id": "0", "supplier_id": supplier_id[i]}
                        consign_detail_res = self.rss.post(url=consign_detail_url, json=consign_detail_body, headers=self.headers_json).json()
                        detail_total = jsonpath.jsonpath(consign_detail_res, "$..total")[0]
                        if int(detail_total) > 100:
                            total_num = math.ceil(int(detail_total) / 100)
                            for e in range(total_num):
                                consign_detail_body['page'] = e + 1
                                consign_detail_res = self.rss.post(url=consign_detail_url, json=consign_detail_body, headers=self.headers_json).json()
                                stock_id = jsonpath.jsonpath(consign_detail_res, "$..id")
                                send_amount = jsonpath.jsonpath(consign_detail_res, "$..real_delivery_number")
                                is_new_jishou = jsonpath.jsonpath(consign_detail_res, "$..is_new_jishou")
                                # supplier_order_dict["supplier_id"] = supplier_id[i]
                                order_msg = {"order_id": order_id_count[n], "stock_id": stock_id, "send_amount": send_amount, "is_new_jishou": is_new_jishou}
                                supplier_order_dict = {"supplier_id": supplier_id_count[n], "order_msg": order_msg, "order_sn": order_sn_count[n]}
                                consign_publish.append(supplier_order_dict)
                        else:
                            stock_id = jsonpath.jsonpath(consign_detail_res, "$..id")
                            send_amount = jsonpath.jsonpath(consign_detail_res, "$..real_delivery_number")
                            is_new_jishou = jsonpath.jsonpath(consign_detail_res, "$..is_new_jishou")
                            # supplier_order_dict["supplier_id"] = supplier_id[i]
                            order_msg = {"order_id": order_id_count[n], "stock_id": stock_id, "send_amount": send_amount, "is_new_jishou": is_new_jishou}
                            supplier_order_dict = {"supplier_id": supplier_id_count[n], "order_msg": order_msg, "order_sn": order_sn_count[n]}
                            consign_publish.append(supplier_order_dict)
        else:
            print("未指定供应商，查询所有供应商")
            if self.consign_sn != None:
                search_body["change_sn"] = self.consign_sn
            search_res = self.rss.post(url=search_url, json=search_body, headers=self.headers_json).json()
            print(search_res)
            total = jsonpath.jsonpath(search_res, "$..total")[0]
            if int(total) >= 100:
                total_num = math.ceil(int(total) / 100)
                for b in range(total_num):
                    search_body['page'] = b + 1
                    search_res = self.rss.post(url=search_url, json=search_body, headers=self.headers_json).json()
                    order_id = jsonpath.jsonpath(search_res, "$..order_id")
                    order_sn = jsonpath.jsonpath(search_res, "$..order_sn")
                    supplier_id_list = jsonpath.jsonpath(search_res, "$..supplier_id")
                    order_sn_count = order_sn + order_sn_count
                    order_id_count = order_id + order_id_count
                    supplier_id_count = supplier_id_count + supplier_id_list
            else:
                order_id_count = jsonpath.jsonpath(search_res, "$..order_id")
                order_sn_count = jsonpath.jsonpath(search_res, "$..order_sn")
                supplier_id_count = jsonpath.jsonpath(search_res, "$..supplier_id")
            for n in range(len(order_id_count)):
                print(f"此时：订单号为{order_id_count[n]}")
                # 审核
                StockAudit(self.rss, supplier_sn_name=self.supplier_sn,
                           order_id=order_id_count[n]).mian_stock_aduit_consign()
                # 获取订单内型号详情
                order_detail_url = "{}/v1/supplier/SupplierOrder/getUploadStockItem".format(self.HC2018_ADMIN_URL)
                order_detail_body = {"page": 1, "per_page": 100, "supplier_id": supplier_id_count[n],
                                     "order_id": order_id_count[n]}
                order_detail_res = self.rss.post(url=order_detail_url, json=order_detail_body,
                                                 headers=self.headers_json).json()
                detail_total = jsonpath.jsonpath(order_detail_res, "$..total")[0]
                goods_name_count = []
                provider_name_count = []
                to_be_add_goods_mark_count = []
                if int(detail_total) >= 100:
                    total_num = math.ceil(int(detail_total) / 100)
                    for m in range(total_num):
                        order_detail_body['page'] = m + 1
                        order_detail_res = self.rss.post(url=order_detail_url, json=order_detail_body,
                                                         headers=self.headers_json).json()
                        goods_name = jsonpath.jsonpath(order_detail_res, "$..goods_name")
                        provider_name = jsonpath.jsonpath(order_detail_res, "$..provider_name")
                        to_be_add_goods_mark = jsonpath.jsonpath(order_detail_res, "$..to_be_add_goods_mark")
                        goods_name_count = goods_name_count + goods_name
                        provider_name_count = provider_name_count + provider_name
                        to_be_add_goods_mark_count = to_be_add_goods_mark_count + to_be_add_goods_mark
                else:
                    goods_name_count = jsonpath.jsonpath(order_detail_res, "$..goods_name")
                    provider_name_count = jsonpath.jsonpath(order_detail_res, "$..provider_name")
                    to_be_add_goods_mark_count = jsonpath.jsonpath(order_detail_res, "$..to_be_add_goods_mark")
                # 判断型号对应标识是否待创建资料
                for k in range(len(goods_name_count)):
                    if to_be_add_goods_mark_count[k] == 1:
                        StayPerfectMeans(self.rss, goods_name=goods_name_count[k], provider_name=provider_name_count[k],
                                         source_type='consign').mian_stay_perfect_means_new()
                # 获取发货明细内容
                consign_detail_url = "{}/v1/supplier/SuppPublish/getPurchaseOrderList".format(self.HC2018_ADMIN_URL)
                consign_detail_body = {"order_id": order_id_count[n], "is_new_jishou": "1", "page": 1, "per_page": 100,
                                       "picking_id": "0", "supplier_id": supplier_id_count[n]}
                consign_detail_res = self.rss.post(url=consign_detail_url, json=consign_detail_body,
                                                   headers=self.headers_json).json()
                detail_total = jsonpath.jsonpath(consign_detail_res, "$..total")[0]
                if int(detail_total) > 100:
                    total_num = math.ceil(int(detail_total) / 100)
                    for e in range(total_num):
                        consign_detail_body['page'] = e + 1
                        consign_detail_res = self.rss.post(url=consign_detail_url, json=consign_detail_body,
                                                           headers=self.headers_json).json()
                        stock_id = jsonpath.jsonpath(consign_detail_res, "$..id")
                        send_amount = jsonpath.jsonpath(consign_detail_res, "$..real_delivery_number")
                        is_new_jishou = jsonpath.jsonpath(consign_detail_res, "$..is_new_jishou")
                        # supplier_order_dict["supplier_id"] = supplier_id[i]
                        order_msg = {"order_id": order_id_count[n], "stock_id": stock_id, "send_amount": send_amount,
                                     "is_new_jishou": is_new_jishou}
                        supplier_order_dict = {"supplier_id": supplier_id_count[n], "order_msg": order_msg,
                                               "order_sn": order_sn_count[n]}
                        consign_publish.append(supplier_order_dict)
                else:
                    stock_id = jsonpath.jsonpath(consign_detail_res, "$..id")
                    send_amount = jsonpath.jsonpath(consign_detail_res, "$..real_delivery_number")
                    is_new_jishou = jsonpath.jsonpath(consign_detail_res, "$..is_new_jishou")
                    # supplier_order_dict["supplier_id"] = supplier_id[i]
                    order_msg = {"order_id": order_id_count[n], "stock_id": stock_id, "send_amount": send_amount,
                                 "is_new_jishou": is_new_jishou}
                    supplier_order_dict = {"supplier_id": supplier_id_count[n], "order_msg": order_msg,
                                           "order_sn": order_sn_count[n]}
                    consign_publish.append(supplier_order_dict)
        print(json.dumps(consign_publish, ensure_ascii=False).replace("'", '"'))
        return consign_publish
    def consign_publish_delivery_all(self, consign_publish):
        """寄售发货-整单"""
        order_sn = []
        inn_order_list = []
        for i in range(len(consign_publish)):
            supplier_id = consign_publish[i]["supplier_id"]
            change_sn = consign_publish[i]["order_sn"]
            order_id = ""
            stock_id = None
            is_new_jishou_count = None
            consign_publish_delivery_all_body = ""
            send_amount = None
            stock_info = []
            for key, v in consign_publish[i].items():
                if key == "order_msg":
                    for m, n in v.items():
                        if m == "order_id":
                            order_id = n
                        if m == "stock_id":
                            stock_id = n
                        if m == "send_amount":
                            send_amount = n
                        if m == "is_new_jishou":
                            is_new_jishou_count = n
            if stock_id != False:
                for a in range(len(stock_id)):
                    is_new_jishou = is_new_jishou_count[a]
                    stock_info.append({"stock_id": stock_id[a], "send_amount": send_amount[a]})
                    stock_info_str = str(stock_info).replace("'", "\"")
                    today_time = datetime.date.today().strftime("%Y-%m-%d")
                    consign_publish_delivery_all_body = {
                        "supplier_id": supplier_id,
                        "order_id": order_id,
                        "stock_info": stock_info_str,
                        "is_new_jishou": is_new_jishou,
                        "express_name": "顺丰速运",
                        "express_sn": "00",
                        "is_print": False,
                        "plan_date": today_time,
                        "remark": "自动化测试"
                    }

                consign_publish_delivery_all_url = "{}/v1/supplier/SuppPublish/deliverGoods".format(self.HC2018_ADMIN_URL)
                consign_publish_delivery_all_res = self.rss.post(url=consign_publish_delivery_all_url, json=consign_publish_delivery_all_body,
                                                                 headers=self.headers_json).json()

                if consign_publish_delivery_all_res["msg"] == "success":
                    print(f"寄售发货-整单成功, 执行结果：{consign_publish_delivery_all_res}")

                    obtain_inn_order_url = "{}/v1/supplier/SuppPublish/getDeliveryRecord".format(self.HC2018_ADMIN_URL)
                    obtain_inn_order_body = {"order_id": order_id, "is_new_jishou": 1, "page": 1, "per_page": 10,"picking_id": 0, "supplier_id": supplier_id}
                    obtain_inn_order_res = self.rss.post(url=obtain_inn_order_url, json=obtain_inn_order_body,headers=self.headers_json).json()
                    inn_order = jsonpath.jsonpath(obtain_inn_order_res, "$..erp_putaway_sn")
                    inn_order_list = inn_order_list + inn_order
                    print(inn_order_list)
                    order_sn.append(change_sn)
        return order_sn, inn_order_list
    def main_consign_publish_delivery(self, status=None):
        n = 0
        while True:
            try:
                consign_publish = self.consign_publish_list(status=status)
                if consign_publish != []:
                    print(consign_publish)
                    break
            except:
                n += 1
                if n < 6:
                    logger.warning(
                        f"第 {n} 次,寄售发货列表没有找到查询条件:{next((x for x in [self.consign_sn, self.goods_name, self.supplier_sn] if x), 'No value')},等待30秒后系统自动重试")
                    time.sleep(30)
                else:
                    logger.error(f"寄售发货列表查找查询条件：{next((x for x in [self.consign_sn, self.goods_name, self.supplier_sn] if x), 'No value')} 出错,请手动检查入库单是否存在")
                    raise ValueError

        if consign_publish != []:
            order_sn, inn_order_list = self.consign_publish_delivery_all(consign_publish)
            print(order_sn, inn_order_list)
            return order_sn, inn_order_list



if __name__ == '__main__':
    consign_sn = None
    goods_name = "searchV4.16.24"
    supplier_sn = None
    # data = [{'supplier_id': 3041, 'order_msg': {'order_id': 4627, 'stock_id': [5220], 'send_amount': [1], 'is_new_jishou': [1]}}]
    from huaqiu_order_api.HC2018_admin.login.login import Login
    target_rss = Login().login()
    # ConsignPublish(target_rss, consign_sn, goods_name, supplier_sn).consign_publish_list()
    # ConsignPublish(target_rss, consign_sn, goods_name, supplier_sn).consign_publish_delivery_all()
    ConsignPublish(target_rss, consign_sn, goods_name, supplier_sn).main_consign_publish_delivery()

                        









