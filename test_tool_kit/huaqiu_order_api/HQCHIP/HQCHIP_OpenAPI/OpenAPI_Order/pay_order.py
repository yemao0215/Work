import json
import re
import time
from datetime import datetime
import datetime as dt

import yaml
from playwright.sync_api import Playwright, sync_playwright, expect
# import datetime

import requests

from huaqiu_order_api.HQCHIP.HQCHIP_OpenAPI.OpenAPI_Order.order_detail_search import OrderDetailSearch
from huaqiu_order_api.HQCHIP.HQCHIP_OpenAPI.Openapi_signature.signature import SignAture
from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_data import Data
from huaqiu_order_api.common.my_path import yaml_file, account_yaml


class PayOrder:

    def __init__(self, ic_order_id=None):
        self.openapi_rss = requests.Session()
        self.json_head = {"Content-Type": "application/json"}
        self.form_head = {'User-Agent': 'HQCHIP OpenAPI Python-SDK/1.0', "X-Request-Version": '1.0'}
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.app_key = data['APP_KEY']
        self.app_sec = data['APP_SEC']
        self.url = data['OPENAPI_UAT_URL']
        self.GoodsName = data['APIGoodsName']
        self.center_java_url = data['center_java_url']
        with open(account_yaml, 'r', encoding='utf-8') as yamlfile:
            account = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.phone = account["PassPort"]["phone"]
        self.goods_id = account["HQCHIP_GOODS"]["goods_id"]
        self.numder = account["HQCHIP_GOODS"]["number"]
        self.vat_type = account["HQCHIP_GOODS"]["vat_type"]
        self.vat_sub_type = account["HQCHIP_GOODS"]["vat_sub_type"]
        self.ic_order_id = getattr(Data, "ic_order_id", '')
        if self.ic_order_id == '' and ic_order_id != None:
            self.ic_order_id = ic_order_id
        self.pay_type = getattr(Data, "pay_type", 2)
        self.erp_rss = requests.Session()
        self.login_url = 'https://uat-e.hqchip.com/public/checkLogin/'
        self.body = {'account': "admin", 'password': "123456"}
        self.from_headers = {'Content-Type': 'multipart/form-data'}
        self.headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    # def erp_login(self):
    #     """
    #     登录ERP
    #     """

        # return self




    def erp_login(self):
        logger.info(f"开始执行登录账号:{self.body}")
        self.erp_rss.post(url=self.login_url, data=self.body, headers=self.headers)
        logger.info(f"ERP登录完成")
        return self

    def search_order(self):
        search_url = 'https://uat-e.hqchip.com/Orderinfo/index'
        search_body = {'keytype': 'order_sn', 'keyword': self.order_sn, 'start_time': '2022-08-01'}
        logger.info(f"搜索订单编号: {self.order_sn}")
        search_res = self.erp_rss.post(url=search_url, data=search_body, headers=self.headers).text  # 搜索订单，获取order_id
        self.order_id = re.search(r'(<a href="/Orderinfo/detail\?id=)([0-9]{6})', search_res).group(2)
        logger.info(f"搜索完成,获取到order_id: {self.order_id}")
        return self

    def is_lock(self):
        is_lock_url = f"https://uat-e.hqchip.com/Orderinfo/detail?id={self.order_id}&is_lock=-2"
        self.erp_rss.get(url=is_lock_url)
        return self
    def erp_confirm_order(self, custom_sn):

        # erp登录
        # time.sleep(60)
        logger.info(f"开始执行登录账号:{self.body}")
        self.erp_rss.post(url=self.login_url, data=self.body, headers=self.headers)
        logger.info(f"ERP登录完成")
        # 搜索订单号
        search_url = 'https://uat-e.hqchip.com/Orderinfo/index'
        search_body = {'keytype': 'order_sn', 'keyword': self.order_sn, 'start_time': '2022-08-01'}
        logger.info(f"搜索订单编号: {self.order_sn}")
        search_res = self.erp_rss.post(url=search_url, data=search_body, headers=self.headers).text  # 搜索订单，获取order_id
        order_id = re.search(r'(<a href="/Orderinfo/detail\?id=)([0-9]{6})', search_res).group(2)
        logger.info(f"搜索完成,获取到order_id: {order_id}")

        # 步骤1 分配订单销售
        ic_order_distribute_sale_url = f"https://uat-e.hqchip.com/Orderinfo/editFollowUserMore/navTabId/Orderinfo"
        ic_order_distribute_sale_body = {"id": order_id, f"sale_uid[{order_id}]": 706,"sale_list_all": 0,"ajax": 1, "is_iframe": 1}
        ic_order_distribute_sale_res = self.erp_rss.post(url=ic_order_distribute_sale_url, data=ic_order_distribute_sale_body).text
        logger.info("分配成功")
        # time.sleep(5)

        # 步骤2 修改明细里面货期备注、和承诺交货日期
        # 步骤2-1 驳回订单
        reject_order_url = f"https://uat-e.hqchip.com/Orderinfo/unconfirm/id/{order_id}/navTabId/SaleOrderDetail"
        self.erp_rss.post(url=reject_order_url)
        # time.sleep(15)

        # 步骤2-2 解除锁定状态
        # is_lock_url = f"https://uat-e.hqchip.com/Orderinfo/detail?id={order_id}&is_lock=-2"
        # self.erp_rss.get(url=is_lock_url)
        # # time.sleep(15)
        # self.erp_login().search_order().is_lock()


        # 步骤2-3 编辑订单
        edit_url = f"https://uat-e.hqchip.com/Orderinfo/edit/id/{order_id}"
        edit_res = self.erp_rss.get(url=edit_url).text

        goods_name = edit_res.split(r'<input name="goods_name[]" value="')[1].split(r'" />')[0]
        goods_id = re.search(r'(<a href="/goodsItem/add\?id=)([0-9]{5})', edit_res).group(2)
        rec_id = edit_res.split(r'<input name="rec_id[]" value="')[1].split(r'" type="hidden"/>')[0]
        self_stock = edit_res.split(r'<input name="self_stock[]" value="')[1].split(r'" type="hidden"/>')[0]
        # warehouse_id = edit_res.split(r'<input name="warehouse_id[]" value="')[1].split(r'" type="hidden"/>')[0]
        inv_desc = edit_res.split(r'<td><input name="inv_desc[]" value="')[1].split(r'" class="input_short inv_desc "/></td>')[0]
        unit = edit_res.split(r'<td><input name="unit[]" value="')[1].split(r'" class="input_short"></td>')[0]
        supplier_id = re.search(r'(<td class="mi" data-supplier_id=")([0-9]{3})', edit_res).group(2)
        sale_number = edit_res.split(r'<td><input name="sale_number[]" value="')[1].split(r'" class="input_short sale_number"/></td>')[0]
        old_sale_price = edit_res.split(r'<td><input name="old_sale_price[]" value="')[1].split(r'" class="input_short old_sale_price" readonly/></td>')[0]
        cost_price = edit_res.split(r'<input name="cost_price[]" class="cost_price" value="')[1].split(r'"/>')[0]
        front_cn_cost_price = edit_res.split(r'<input type="hidden" name="front_cn_cost_price[]" class="input_short front_cn_cost_price" value="')[1].split(r'"/>')[0]
        sale_price = edit_res.split(r'<td><input name="sale_price[]" value="')[1].split(r'" class="input_short sale_price" /></td>')[0]
        bonus_money = re.search(r'(<input name="bonus_money" value=")(0.[0-9]{2})', edit_res).group(2)
        delivery_time = edit_res.split(r'<td><input name="delivery_time[]" value="')[1].split(r'" class="w80 date " readonly/></td>')[0]
        logger.info(delivery_time)
        shipping_fee = edit_res.split(r'<input id="j_shipping_fee" name="shipping_fee" value="')[1].split(r'" class="input_short other_total" />')[0]
        estimate_gross_profit = edit_res.split(r'><input type="hidden" name="estimate_gross_profit" value="')[1].split(r'"/></li>')[0]
        commitment_time = self.weekday_create(7, str(datetime.now().strftime(r'%Y-%m-%d')))
        # logger.info(type(commitment_time))

        # 步骤2-4 保存编辑的内容
        updata_save_url = "https://uat-e.hqchip.com/orderinfo/update/navTabId/SaleOrderDetail"
        updata_save_body = {"smt_order_id": "",
                            "product_num": "1",
                            "order_id": order_id,
                            "company": "1",
                            "place_delivery": "1",
                            "shipping_strategy": "2",
                            "commitment_time": commitment_time,
                            "order_remark": "",
                            "custom_sn": custom_sn,
                            "event_remark": "",
                            "lable_type": 1,
                            "vat_type": "0",
                            "users_vat_id": "-1",
                            "inv_type": "1",
                            "invoice_mode_type": "2",
                            "recive_type": "2",
                            "vat_registration_sn": "",
                            "recive_consignee": "",
                            "recive_mobile": "",
                            "recive_province": "",
                            "recive_city": "",
                            "recive_district": "",
                            "recive_address": "",
                            "order_cert2": "",
                            "goods_name[]": goods_name,
                            "goods_id[]": goods_id,
                            "rec_id[]": rec_id,
                            "self_stock[]": self_stock,
                            "ic_goods_json[]": "",
                            "warehouse_id[]": "2",
                            "inv_desc[]": inv_desc,
                            "unit[]": unit,
                            "supplier_id[]": supplier_id,
                            "sale_number[]": sale_number,
                            "contact_delivery[]": "",
                            "spec[]": "1",
                            "removal_number[]": "0",
                            "old_sale_price[]": old_sale_price,
                            "cost_price[]": cost_price,
                            "front_cn_cost_price[]": front_cn_cost_price,
                            "sale_price[]": sale_price,
                            "bonus_money[]": bonus_money,
                            "tariff[]": "0.0000",
                            "commodity_price[]": "0.0000",
                            "delivery_time[]": delivery_time,
                            "delivery_msg[]": "现货",
                            "hqchip_remark[]": "",
                            "remark[]": "",
                            "bit_number[]": "",
                            "goods_sn[]": goods_name,
                            "picking_price": "0.00",
                            "shipping_fee[]": shipping_fee,
                            "estimate_gross_profit": estimate_gross_profit,
                            "pay_type": "3",
                            "advance_money": "0.00",
                            "ajax": "1",
                            "is_iframe": "1"
                            }
        updata_save_res = self.erp_rss.post(url=updata_save_url, data=json.dumps(updata_save_body), headers=self.from_headers).text
        logger.info(updata_save_res)
        # self.msg = updata_save_res.split(r'<title>')[1].split(r'</title>')[0]
        # logger.info(self.msg)
        #
        return self







    def order_pay(self, data_amount=None):
        # openapi_pay_url = '{}/order/pay/'.format(self.url)
        openapi_pay_url = '{}/order/pay/'.format(self.url)
        params = {
            'app_key': self.app_key,
            'timestamp': int(time.time())
        }
        data = {
            'order_id': int(self.ic_order_id),
            'pay_type': int(self.pay_type)
        }
        if data_amount is not None and data_amount != '':
            data['amount'] = data_amount
        # 统一封装 签名sign生成方法
        params['sign'] = SignAture(self.app_sec).hqchip_sign_main(params, data)
        openapi_pay_res = self.openapi_rss.post(url=openapi_pay_url, params=params, data=data, headers=self.form_head, timeout=10).json()

        data = None
        error_message = openapi_pay_res["error_message"]
        if openapi_pay_res["error_message"] == '':
            data = openapi_pay_res["data"]
            return data, error_message
        else:
            logger.info(r'错误信息：'f'{openapi_pay_res["error_message"]}')
            return data, error_message



    def is_lock_order(self):
        self.erp_login()
        self.search_order()
        self.is_lock()

    def mian_erp_order(self, custom_sn):
        self.erp_confirm_order(custom_sn)
        if self.msg == "系统发生错误":
            self.is_lock_order()
            # self.erp_confirm_order(custom_sn)


if __name__ == '__main__':
    out_order_no = ""
    ic_order_id = 300223
    data_amount = "1"
    OrderDetailSearch().order_detail_search(order_id=ic_order_id, out_order_no=out_order_no)
    PayOrder(ic_order_id).order_pay()
    # with sync_playwright() as playwright:
        # PayOrder(url, app_sec, app_key,order_sn,ic_order_id,pay_type).erp_confirm_order()