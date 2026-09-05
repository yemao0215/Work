import json
from urllib.parse import quote
import re
import time
from datetime import datetime
import datetime as dt

import jsonpath
import requests
import yaml


from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_data import Data
from huaqiu_order_api.common.my_path import yaml_file, account_yaml
from huaqiu_order_api.HQCHIP.HQCHIP_OpenAPI.OpenAPI_Order.pay_order import  PayOrder

# class DateEncoder(json.JSONEncoder):
#     def default(self, obj):
#         if isinstance(obj, datetime):
#             return obj.strftime(r'%Y-%m-%d %H:%M:%S')
#         elif isinstance(obj, date):
#             return obj.strftime("%Y-%m-%d")
#         else:
#             return json.JSONEncoder.default(self, obj)

class ErpOrderCancellation:


    def __init__(self, rss, order_sn=None):
        """
        :param account:  登录ERP账号
        :param psw:  登录ERP密码
        :param order_sn:  前台商城生成订单编号
        :param uesr:    前台商城生成订单编号的用户名称
        """
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.ERP_URL = data['ERP_URL']
        with open(account_yaml, 'r', encoding='utf-8') as yamlfile:
            account = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.warehouse_type = account["HQCHIP_GOODS"]["warehouse_id"]
        self.vat_type = account["HQCHIP_GOODS"]["vat_type"]
        self.number = account["HQCHIP_GOODS"]["number"]
        # self.password = psw
        self.order_sn = getattr(Data, 'ic_order_sn', 'S2025031403621')
        if order_sn != None:
            self.order_sn = order_sn
        self.rss = rss
        self.headers = {'Content-Type': 'application/x-www-form-urlencoded',
                        "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://www.huaqiu.com)"
                        }
        self.headers_ = None
    def erp_ic_order_cancellation(self):
        """销售订单处理"""
        search_url = '{}/Orderinfo/index'.format(self.ERP_URL)
        search_body = {'keytype': 'order_sn', 'keyword': self.order_sn, 'start_time': '2023-01-01'}
        logger.info(f"搜索订单编号: {self.order_sn}")
        search_res = self.rss.post(url=search_url, data=search_body, headers=self.headers, timeout=1000).text  # 搜索订单，获取order_id
        # print(search_res)
        # logger.info(re.search(r'(<a href="/Orderinfo/detail\?id=)([0-9]{6})', search_res))
        search_res_excerpt = search_res.split(r'<tr target="id"')[1].split(r'<div class="pages">')[0]
        order_id = re.search(r'(<a href="/Orderinfo/detail\?id=)([0-9]*)', search_res).group(2)
        logger.info(f"搜索完成,获取到order_id: {order_id}")
        # 新增销售
        add_sale_url = "{}/Orderinfo/editFollowUserMore/navTabId/Orderinfo".format(self.ERP_URL)
        add_sale_body = {"id": order_id, f"sale_uid[{order_id}]": 704, "sale_list_all": 0}
        self.rss.post(url=add_sale_url, data=add_sale_body, timeout=1000)
        # logger.info(f"执行结果：{add_sale_res}")
        order_details_url = self.ERP_URL + f'/Orderinfo/detail?id={order_id}'
        logger.info(f"进入订单明细列表")
        order_detail_res = self.rss.get(url=order_details_url, headers=self.headers).text  # 获取订单明细id
        order_detail_match = re.compile(r'(<span><a href="/RecivePay/detail\?id=)([0-9]*)').search(order_detail_res)
        order_detail_id = ""
        if order_detail_match:
            order_detail_id = re.search(r'(<span><a href="/RecivePay/detail\?id=)([0-9]*)', order_detail_res).group(2)
        elif order_detail_match == None:
            logger.info("执行添加货期备注")
        logger.info(f"订单明细获取完成，拿到订单明细id: {order_detail_id}")
        if "待确认" in search_res_excerpt:
            logger.info(f"订单号：{self.order_sn}状态存在待确认状态")
            order_status_match = re.compile(r'(<li><a class="edit" href="/Orderinfo/confirm/id/{}/navTabId/SaleOrderDetail/ordertype/1\?type=org" target="dialog" title="选择部门"  width="450"><span>)([\u4e00-\u9fa5]*)(</span>)'.format(order_id)).search(
                order_detail_res)
            if order_status_match:
                order_status = re.search(r'(<li><a class="edit" href="/Orderinfo/confirm/id/{}/navTabId/SaleOrderDetail/ordertype/1\?type=org" target="dialog" title="选择部门"  width="450"><span>)([\u4e00-\u9fa5]*)(</span>)'.format(order_id), order_detail_res).group(2)
                if order_status == "确认订单":
                    logger.info(order_status)
                    sale_order_url = "{}/Orderinfo/confirm/id/{}/navTabId/SaleOrderDetail/ordertype/1?org_id={}".format(self.ERP_URL, order_id, 307)
                    sale_order_res = self.rss.post(url=sale_order_url, timeout=1000).json()
                    if self.order_sn in sale_order_res:
                        logger.info(f"确认订单成功，执行结果为{sale_order_res}")
            elif order_status_match == None:
                order_status = re.search(r'(<li><a class="edit" href="/Orderinfo/confirm/id/{}/navTabId/SaleOrderDetail/ordertype/2\?type=org" target="dialog" title="选择部门"  width="450"><span>)([\u4e00-\u9fa5]*)(</span>)'.format(order_id), order_detail_res).group(2)
                if order_status == "确认订单":
                    logger.info(order_status)
                    sale_order_url = "{}/Orderinfo/confirm/id/{}/navTabId/SaleOrderDetail/ordertype/2?org_id={}".format(self.ERP_URL, order_id, 307)
                    sale_order_res = self.rss.post(url=sale_order_url, timeout=1000).json()
                    if self.order_sn in sale_order_res:
                        logger.info(f"确认订单成功，执行结果为{sale_order_res}")
        goods_id = re.split(r'<a href="/Goods/detail/id/', order_detail_res)[1].split(r'/pass/1"')[0]
        order_details_goods_url = '{}/Goods/detail/id/{}/pass/1'.format(self.ERP_URL, goods_id)
        order_detail_goods_res = self.rss.get(url=order_details_goods_url, headers=self.headers).text  # 获取订单明细id
        erp_goods_sn = re.search(r'(<span class="ipt-tag">)(G[0-9]+)', order_detail_goods_res).group(2)
        logger.info(f"获取到订单：{self.order_sn}的型号的ERP编码：{erp_goods_sn}")
        # 将获取的ERP商品编码往Data里面作虚拟存储以【erp_goods_sn】命名以便后续提取
        setattr(Data, 'erp_goods_sn', erp_goods_sn)
        order_receipt_url = self.ERP_URL + f'/RecivePay/detail?id={order_detail_id}'
        time.sleep(15)
        logger.info(f"等待15s,获取收款单明细")
        order_verification_res = self.rss.get(url=order_receipt_url, headers=self.headers).text  # 获取核销金额
        order_money = re.search(r'(<label>合计：</label><span class="total">)([0-9]*\.?[0-9]+)',
                                order_verification_res).group(2)
        logger.info(f"收款单明细获取完成，成功拿到需要核销的金额: {order_money}")

        confirmation_writeOff_url = self.ERP_URL + f'/RecivePay/confirm/id/{order_detail_id}/navTabId/RecivePayDetail'
        logger.info(f"开始执行订单核销")
        confirmation_writeOff_body = {'money': order_money, 'remark': '测试订单'}
        self.rss.post(url=confirmation_writeOff_url, data=confirmation_writeOff_body, headers=self.headers)  # 执行核销
        logger.info(f"核销操作完成")

        time.sleep(10)
        order_detail = self.rss.get(url=order_details_url, headers=self.headers).text
        out_order = re.search(r'(rel="Removaledit">出库单)(OUT[0-9]+)', order_detail).group(2)
        otu_order_id = re.search(r'(href="/Removal/edit\?id=)([0-9]+)', order_detail).group(2)
        logger.info(f"出库单号: {out_order}")

        out_details_url = self.ERP_URL + f'/Removal/edit?id={otu_order_id}'
        out_order_status = None
        out_details_res = None
        n = 0
        while True:
            try:
                out_details_res = self.rss.get(url=out_details_url).text
                out_order_status = re.search(r'(<label>订单状态：</label>)\s*(<span>)([\u4e00-\u9fa5]*)', out_details_res).group(3)
                if out_order_status == '复核中':
                    logger.info(f"出库单复核中,可去wms操作出库")
                    # 将生成的IC出库单号往Data里面作虚拟存储以【out_order】命名以便后续提取
                    setattr(Data, 'out_order', out_order)
                    out_order_businessTypeName = re.search(r'(<td>)([\u4e00-\u9fa5]*)(</td>)', out_details_res).group(2)
                    logger.info(f"获取到出库单号商品定位的商品库存类型为：{out_order_businessTypeName}")
                    setattr(Data, 'businessTypeName', out_order_businessTypeName)
                    break
            except Exception as e:
                n += 1
                if n > 6:
                    out_details_res = self.rss.get(url=out_details_url).text
                    out_order_status = re.search(r'(<label>订单状态：</label>)\s*(<span>)([\u4e00-\u9fa5]*)', out_details_res).group(3)
                    logger.warning(f"第{n}次检查出库单状态，此时出库单状态为：{out_order_status}，等待10秒系统自动重试")
                    time.sleep(10)
                    break
        if out_order_status == '待确认' and out_order_status != None:
            # 将生成的IC出库单号往Data里面作虚拟存储以【out_order】命名以便后续提取
            setattr(Data, 'out_order', out_order)
            out_order_businessTypeName = re.search(r'(<td>)([\u4e00-\u9fa5]*)(</td>)', out_details_res).group(2)
            if out_order_businessTypeName == "代购储位":
                pass
            elif out_order_businessTypeName == "自营储位":
                out_order_stockStatus = re.search(r'(<td title="已生成补货需求，待自营PM确认">)([\u4e00-\u9fa5]*)(</td>)', out_details_res).group(2)
                logger.info(out_order_stockStatus)
                pass
            else:
                logger.error(f"出库单状态为:{out_order_status},无法进行出库")
                raise ValueError
        logger.debug(r'=*' * 50)
        setattr(Data, 'erp_order_json', {'order_sn': self.order_sn, "inner_sn": out_order})
        return self

    def erp_ic_order_update(self):
        """订单编辑保存"""
        self.order_id = 302018
        update_url = "{}/Orderinfo/edit/id/{}".format(self.ERP_URL, self.order_id)
        update_res = self.rss.get(url=update_url).text
        logger.info(update_res)
        # product_num = re.search(r'(<input type="hidden" name="product_num" value=")([0-9]*)', update_res).group(2)
        users_vat_id = re.search(r'(<input type="hidden" name="users_vat_id"  value=")([0-9]*)', update_res).group(2)
        inv_type = re.search(r'(<input type="hidden" name="inv_type" value=")([0-9]*)', update_res).group(2)
        vat_registration_sn = re.search(r'(<input  name="vat_registration_sn"   value=")([0-9]*)', update_res).group(2)
        goods_name = re.search(r'(<input  name="vat_registration_sn"   value="(.*?)")', update_res).group(2)
        goods_id = re.search(r'(<input name="goods_id(.*?)" value="(.*?)")([0-9]*)', update_res).group(2)
        rec_id = re.search(r'(<input name="rec_id(.*?)" value="(.*?)")([0-9]*)', update_res).group(2)
        self_stock = re.search(r'(<input name="self_stock(.*?)" value="(.*?)")([0-9]*)', update_res).group(2)
        inv_desc = re.search(r'(<input name="inv_desc(.*?)" value=")([\u4e00-\u9fa5]*)', update_res).group(2)
        unit = re.search(r'(class="input_short inv_desc "/></td>)\s*(<td><input name="unit(.*?)" value=")([\u4e00-\u9fa5]*)', update_res).group(4)
        supplier_id = re.search(r'(<td class="mi" data-supplier_id=")([0-9]*)', update_res).group(2)
        delivery_time = self.weekday_create(7, str(datetime.now().strftime(r'%Y-%m-%d')))
        logger.info(delivery_time)
        invoice_mode_type = ''
        if self.vat_type == 0:
            invoice_mode_type = 2
        elif self.vat_type == 1:
            invoice_mode_type = 1
        elif self.vat_type == 3:
            invoice_mode_type = 3
        # logger.info(product_num)
        p =  {
            "smt_order_id": "",
            "product_num": 0,
            "order_id": self.order_id,
            "company": "1",
            "place_delivery": "1",
            "shipping_strategy": "2",
            "order_remark": "",
            "other_type": 0,
            "custom_sn": "",
            "event_remark": "",
            "vat_type": self.vat_type,
            "users_vat_id": users_vat_id,
            "inv_type": inv_type,
            "invoice_mode_type": invoice_mode_type,
            "recive_type": 2,
            "vat_registration_sn": vat_registration_sn,
            "recive_consignee": "",
            "recive_mobile": "",
            "recive_province": "",
            "recive_city": "",
            "recive_district": "",
            "recive_address": "",
            "order_cert2": "(binary)",
            # "product_num": 0
            "goods_name[]": goods_name,
            "goods_id[]": goods_id,
            "rec_id[]": rec_id,
            "self_stock[]": self_stock,
            "ic_goods_json[]": "",
            "warehouse_id[]": self.warehouse_type,
            "inv_desc[]": inv_desc,
            "unit[]": "片",
            "supplier_id[]": supplier_id,
            "sale_number[]": self.number,
            "contact_delivery[]": "3-5工作日",
            "spec[]": 1,
            "removal_number[]": 0,
            "old_sale_price[]": 7.31311,
            "cost_price[]": 5.22370,
            "front_cn_cost_price[]": 5.22370,
            "sale_price[]": 7.31311,
            "bonus_money[]": 0.00,
            "tariff[]": 0.0000,
            "commodity_price[]": 0.0000,
            "delivery_time[]": "",
            "delivery_msg[]": "3-5工作日",
            "hqchip_remark[]": "",
            "remark[]": "",
            "bit_number[]": "",
            "goods_sn[]": "",
            # "goods_name[]":"",
            # "goods_id[]": "",
            # "rec_id[]": "",
            # "self_stock[]": 0,
            # "ic_goods_json[]": "",
            # "warehouse_id[]": 2,
            # "inv_desc[]": "电子元器件",
            # "unit[]": "片",
            # "supplier_id[]": "",
            # "sale_number[]": "",
            # "contact_delivery[]": "",
            # "spec[]": 1,
            # "old_sale_price[]": "",
            # "cost_price[]": 5.22370,
            # "sale_price[]": "",
            # "bonus_money[]": "",
            # "tariff[]": 0.00,
            # "commodity_price[]": 0.00,
            # "delivery_time[]": "2023-09-28",
            # "delivery_msg[]": 3-5工作日
            # "hqchip_remark[]": "",
            # "remark[]": "",
            # "bit_number[]": "",
            # "goods_sn[]": "",
            "picking_price": "0.00",
            "shipping_fee": 10.00,
            "estimate_gross_profit": 20.89,
            "pay_type": 3,
            # "advance_money": "",
            "advance_money": 0.00,
            "ajax": 1,
            "is_iframe": 1}

    def erp_bom_order_define(self):
        '''确定BOM需求+推送'''

        # login_url = 'https://uat-e.hqchip.com/public/checkLogin/'
        # login_body = {'account': 'admin', 'password': 123456}
        # logger.info(f"登录ERP系统,账号:{login_body}")
        # self.rss.post(url=login_url, source_data=login_body, headers=self.headers)  # 登录
        # logger.info(f"登录完成")

        search_url = '{}/DemandBusiness/index'.format(self.ERP_URL)
        search_body = {'bom_sn': self.order_sn, "picking_group_id": -1, "customer_type": 1, "is_patch": 0}
        logger.info(f"搜索需求单号: {self.order_sn}")
        n = 0
        while True:
            try:
                search_res = self.rss.post(url=search_url, data=search_body, headers=self.headers).text  # 搜索订单，获取order_id
                self.order_id = re.search(r'(<a href="/DemandBusiness/detail/id/)([0-9]+)', search_res).group(0).split("id/")[1]
                logger.info(f"第{n + 1}次访问需求管理列表搜索BOM订单号为：{self.order_sn}完成，获取到order_id: {self.order_id}")
                break
            except Exception as e:
                n += 1
                if n < 6:
                    logger.warning(f"第 {n} 次,访问需求管理列表搜索BOM订单号为：{self.order_sn},等待30秒后系统自动重试,错误信息:{e}")
                    time.sleep(30)
                else:
                    logger.error(f"访问需求管理列表搜索订单号为：{self.order_sn} 出错,请手动检查需求管理列表是否存在")
                    raise ValueError
        time.sleep(2)

        # 分配bom工程师
        divide_bom_url = "{}/DemandBusiness/setBomEngineerUid".format(self.ERP_URL)
        divide_bom_body = {"id": self.order_id, "bom_engineer_uid": 701}
        divide_bom_res = self.rss.post(url=divide_bom_url, data=divide_bom_body, headers=self.headers).json()
        logger.info(f"分配BOM工程师结果信息为：{divide_bom_res}")

        # 获取用户信息
        bom_order_details_uesr_url = self.ERP_URL + f"/DemandBusiness/suggest?type=user_name&callback_fn=demandBusinessDeatil_users&query={self.uesr}"
        bom_order_details_uesr_res = self.rss.get(url=bom_order_details_uesr_url).json()
        customer_id = bom_order_details_uesr_res["source_data"][0]["id"]
        name = bom_order_details_uesr_res["source_data"][0]["name"]
        old_user_id = bom_order_details_uesr_res["source_data"][0]["user_id"]
        logger.info(f"获取customer_id：{customer_id}和name：{name}")
        bom_order_details_contact_url = self.ERP_URL + f"/DemandBusiness/suggest?type=contact_name&customer_id={customer_id}"
        bom_order_details_contactr_res = self.rss.get(url=bom_order_details_contact_url).json()
        contact_id = bom_order_details_contactr_res["source_data"]["1"]["id"]
        logger.info(f"获取contact_id：{contact_id}")

        # 需求详情页
        bom_order_details_url = self.ERP_URL + f"/DemandBusiness/detail/id/{self.order_id}"
        bom_order_details_res = self.rss.get(url=bom_order_details_url).text
        # print(re.search(r'(<tr class="item_list" target="msgid" rel=")([0-9]{7})', bom_order_details_res).group(0).split(r'rel="'))
        item_id_old, item_id = re.search(r'(<tr class="item_list" target="msgid" rel=")([0-9]+)', bom_order_details_res).group(0).split(r'rel="')
        logger.info(f"搜索完成,获取到item_id: {item_id}")

        # 确定需求
        bom_order_details_define_url = self.ERP_URL + f"/DemandBusiness/operator_engineer/id/{self.order_id}/navTabId/DemandBusinessDetail"
        # list = [{
        #     "confirm_id": "{}".format(item_id),
        #     "is_ordered": "2",
        #     "client_goods_sn": "1",
        #     "cat_name": "贴片电容",
        #     "brand_name": "Walsin",
        #     "goods_name": "0603B104K500CT",
        #     "goods_desc": "100000pF ±10% DC50VX7R",
        #     "encap": "603",
        #     "bit_number": "C3,C4,C5,C6",
        #     "dosage": "100",
        #     "other": "",
        # }]
        predict_finish_time = str(datetime.now()).split(r' ')[0] + ' ' + str("23:59:59")
        # logger.info(f"最迟报价时间为：{predict_finish_time}")
        # bom_order_1 = {
        #     "status": -1,
        #     "excel": list,
        #     "old_user_id": old_user_id,
        #     "customer_id": customer_id,
        #     "contact_id": contact_id,
        #     "predict_finish_time": "2023-03-22%2023%3A59%3A59",
        #     "num": 5,
        #     "money_type": 1,
        #     "col_name[]": "client_goods_sn",
        #     "col_name[]": "cat_name",
        #     "col_name[]": "brand_name",
        #     "col_name[]": "goods_name",
        #     "col_name[]": "goods_desc",
        #     "col_name[]": "encap",
        #     "col_name[]": "bit_number",
        #     "col_name[]": "dosage",
        #     "col_name[]": "other",
        #     "is_ordered[" + item_id + "]": "2",
        #     "bom_category[" + item_id + "]": "",
        #     "ajax": "1",
        #     "is_iframe": "1",
        # }
        # bom_order_1 = json.dumps(bom_order_1, cls=DateEncoder)
        # print(bom_order_1)
        # bom_order_details_define_res = self.rss.post(url=bom_order_details_define_url, source_data=bom_order_1).text
        # logger.info(bom_order_details_define_res)
        now_date = str(datetime.now()).split(r' ')[0]
        payload = f'status=-1&excel=%5B%7B%22confirm_id%22%3A%22{item_id}%22%2C%22is_ordered%22%3A%222%22%2C%22client_goods_sn%22%3A%221%22%2C%22cat_name%22%3A%22%E8%B4%B4%E7%89%87%E7%94%B5%E5%AE%B9%22%2C%22brand_name%22%3A%22Walsin%22%2C%22goods_name%22%3A%220603B104K500CT%22%2C%22goods_desc%22%3A%22100000pF%20%C2%B110%25%20DC50VX7R%22%2C%22encap%22%3A%22603%22%2C%22bit_number%22%3A%22C3%2CC4%2CC5%2CC6%22%2C%22dosage%22%3A%224%22%2C%22other%22%3A%22%22%2C%22address%22%3A%22%E6%B7%B1%E5%9C%B3%22%2C%22delivery_time%22%3A%221-3%E5%B7%A5%E4%BD%9C%E6%97%A5%22%7D%5D&old_user_id={old_user_id}&passfield%5Bcustomer_name_cn%5D%5Ba=2%3A%7Bs%3A1%3A%2522m%2522%3Bs%3A20%3A%2522DemandBusinessDetail%2522%3Bs%3A1%3A%2522p%2522%3BN%3B%7D%5D%3Ajf_****3305&customer_id={customer_id}&contact_id={contact_id}&predict_finish_time={now_date}%2023%3A59%3A59&num=5&money_type=1&postscript=&col_name%5B%5D=client_goods_sn&col_name%5B%5D=cat_name&col_name%5B%5D=brand_name&col_name%5B%5D=goods_name&col_name%5B%5D=goods_desc&col_name%5B%5D=encap&col_name%5B%5D=bit_number&col_name%5B%5D=dosage&col_name%5B%5D=other&is_ordered%5B{item_id}%5D=2&bom_category%5B{item_id}%5D=&ajax=1&is_iframe=1'
        bom_order_details_define_res = self.rss.post(url=bom_order_details_define_url, data=payload, headers=self.headers).text
        # logger.info(bom_order_details_define_res)
        # title_1, title = re.search(r'(var response = )', bom_order_details_res).group(0).split(r';')
        # title = bom_order_details_define_res.split(r'<script type="text/javascript">')[0].split(r';')[0]
        # print(bom_order_details_define_res.split(r'<script type="text/javascript">')[0])

        # 获取明细id confirm_id
        bom_order_details_items_url = self.ERP_URL + f"/DemandBusiness/items?bom_id={self.order_id}"
        bom_order_details_items_res = self.rss.post(url=bom_order_details_items_url).text
        # logger.info(bom_order_details_items_res)
        self.confirm_id = re.search(r'(<tr source_data-id=")([0-9]+)', bom_order_details_items_res).group(0).split(r'"')[1]
        self.goods_name = re.split(r'<div class="tov" title="', bom_order_details_items_res)[1].split(r'">')[0]
        # picking_id_old, picking_id = re.search(r'(<tr click_id=")([0-9]{7})', bom_order_details_items_res).group(0).split(r'"')
        # logger.info(bom_order_details_items_res)
        logger.info(f"获取到confirm_id：{self.confirm_id}，goods_name：{self.goods_name}")

        # # 获取询价记录明细id picking_id
        # bom_order_details_poolinquirylist_url = f"https://uat-e.hqchip.com/DemandBusiness/poolinquirylist?confirm_id={confirm_id}"
        # bom_order_details_poolinquirylist_res = self.rss.get(url=bom_order_details_poolinquirylist_url).text
        # logger.info(re.search(r'(<tr click_id=")([0-9]{7})', bom_order_details_poolinquirylist_res))
        # picking_id_old, picking_id = re.search(r'(<tr click_id=")([0-9]{7})', bom_order_details_poolinquirylist_res).group(0).split(r'"')
        # logger.info(f"获取到picking_id：{picking_id}")
        #
        #
        logger.info("BOM自动匹配服务自动匹配时间，估计需要3分钟左右")
        time.sleep(180)
        logger.info("等待完成，开始推送BOM配单报价")
        #
        # bom_order_details_clickdata_url = f"https://uat-e.hqchip.com/DemandBusiness/click_data"
        # clickdata_body = {"action_type": "look_new", "confirm_id": {confirm_id}, "push_id": {picking_id}, "order_id": {order_id}}
        # bom_order_details_clickdata_res = self.rss.post(url=bom_order_details_clickdata_url, source_data=clickdata_body, headers=self.headers).json()
        #
        # 推送BOM配单报价
        bom_order_details_match_url = "{}/DemandBusiness/set_distribution".format(self.ERP_URL)
        bom_order_details_match_body = {"bom_id": self.order_id, "confirm_id": self.confirm_id, "is_early_locking": 1,"set_distribution_all":0,"distribution_time": predict_finish_time}
        bom_order_details_match_res = self.rss.post(url=bom_order_details_match_url, data=bom_order_details_match_body).text
        # logger.info(bom_order_details_match_res)
        match_push_msg = bom_order_details_match_res.split(r'<h3 class="ui-tipbox-title">')[1].split(r'</h3>')[0]
        logger.info(f"推送需求单{self.order_sn}的结果为：{match_push_msg}")
        return self

    def erp_bom_order_match(self):
        """BO配单"""

        bom_distribution_list_url = "{}/BomDistribution/index".format(self.ERP_URL)
        bom_distribution_list_res = self.rss.post(url=bom_distribution_list_url, data={"bom_sn": self.order_sn}, headers=self.headers).text
        distribution_list_id = re.search(r'(<tr target="id" rel=")([0-9]+)', bom_distribution_list_res).group(0).split(r'"')[3]
        logger.info(f"搜索成功，获取到配单列表记录id：{distribution_list_id}")

        # 确认报价
        bom_distribution_confirm_quote_url = self.ERP_URL + f"/BomDistribution/app_confirm/navTabId/BomDistributionDetail?id={distribution_list_id}"
        bom_distribution_confirm_quote_res = self.rss.post(url=bom_distribution_confirm_quote_url, data={"item_user_id":-1}).text
        # logger.info(bom_distribution_confirm_quote_res)
        # msg_info = re.search(r'("\u64cd\u4f5c\u5931\u8d25!\u542b\u6709\u672a\u5206\u914d\u660e\u7ec6\u914d\u5355\u5458!")', bom_distribution_confirm_quote_res).group(0)
        # msg_info = re.search(r'(<h3 class="ui-tipbox-title">)', bom_distribution_confirm_quote_res).group(1).split("</h3>")[0]
        msg_info = re.split(r'<h3 class="ui-tipbox-title">', bom_distribution_confirm_quote_res)[1].split("</h3>")[0]
        logger.info(msg_info)
        if msg_info == "操作失败!含有未分配明细配单员!":
            # 分配配单员
            push_url = "{}/BomDistribution/set_push_uid?navTabId=BomDistributionDetail".format(self.ERP_URL)
            push_body = {"id": distribution_list_id, "confirm_id": self.confirm_id, "push_uid": 1, "ajax": 1, "is_iframe":1}
            push_res = self.rss.post(url=push_url, data=push_body).text
            # print(push_res)
        elif msg_info == "操作失败!带星号必填项和未报价备注两者必须满足一项":
            logger.info("----")
            # 搜索库存
            bom_distribution_confirm_quote_goods_name_search_url = self.ERP_URL + f"/ajax/suggestBomDistribution?type=goods_name&bom_id={self.order_id}&query={self.goods_name}"
            bom_distribution_confirm_quote_goods_name_search_res = self.rss.get(url= bom_distribution_confirm_quote_goods_name_search_url).text
            # 获取信息


        logger.info("确认报价成功")
        # 审核
        bom_distribution_audit_url = "{}/BomDistribution/applicationAudit/navTabId/BomDistributionDetail".format(self.ERP_URL)
        bom_distribution_audit_body = {"last_bom_time": 3, "id":distribution_list_id, "is_iframe": 1, "ajax": 1}
        bom_order_details_match_res = self.rss.post(url=bom_distribution_audit_url, data=bom_distribution_audit_body).text
        logger.info("BOM配单审核完成")
        return self

        #
    def erp_bom_order_audit(self):
        """需求管理申请审核"""
        # login_url = 'https://uat-e.hqchip.com/public/checkLogin/'
        # login_body = {'account': 'admin', 'password': 123456}
        # logger.info(f"登录ERP系统,账号:{login_body}")
        # self.rss.post(url=login_url, source_data=login_body, headers=self.headers)  # 登录
        # logger.info(f"登录完成")
        search_url = '{}/DemandBusiness/index'.format(self.ERP_URL)
        search_body = {'bom_sn': self.order_sn, "picking_group_id": -1, "customer_type": 1, "is_patch": 0}
        logger.info(f"搜索需求单号: {self.order_sn}")
        search_res = self.rss.post(url=search_url, data=search_body, headers=self.headers).text
        # logger.info(re.search(r'(<tr target="id" rel=")([0-9]{5})', search_res).group(0).split(r'="')[2])# 搜索订单，获取order_id
        order_id = re.search(r'(<tr target="id" rel=")([0-9]+)', search_res).group(0).split(r'="')[2]
        # logger.info(re.search(r'(<tr class="item_list" target="msgid" rel=)([0-9]{7})', search_res))
        logger.info(f"搜索完成,获取到order_id: {order_id}")
        #

        # 申请审核
        bom_define_audit_url =self.ERP_URL + f"/DemandBusiness/applicationAudit?id={order_id}&navTabId=DemandBusiness/deploy"
        bom_define_audit_res = self.rss.post(url=bom_define_audit_url).text
        # logger.info(bom_define_audit_res)
        # audit_msg = bom_define_audit_res["info"]
        # logger.info(f"需求单{order_sn}的申请审核结果为：{audit_msg}")
        return self


    def erp_bom_order_Generate_sales_order(self):
        """生成SMT-IC销售单"""
        # 操作生成SMT-IC销售单
        # login_url = 'https://uat-e.hqchip.com/public/checkLogin/'
        # login_body = {'account': 'admin', 'password': 123456}
        # logger.info(f"登录ERP系统,账号:{login_body}")
        # self.rss.post(url=login_url, source_data=login_body, headers=self.headers)  # 登录
        # logger.info(f"登录完成")
        search_url = '{}/DemandBusiness/index'.format(self.ERP_URL)
        search_body = {'bom_sn': self.order_sn, "picking_group_id": -1, "customer_type": 1, "is_patch": 0}
        logger.info(f"搜索需求单号: {self.order_sn}")
        search_res = self.rss.post(url=search_url, data=search_body, headers=self.headers).text
        # logger.info(re.search(r'(<tr target="id" rel=")([0-9]{5})', search_res).group(0).split(r'="')[2])# 搜索订单，获取order_id
        order_id = re.search(r'(<tr target="id" rel=")([0-9]+)', search_res).group(0).split(r'="')[2]
        # logger.info(re.search(r'(<tr class="item_list" target="msgid" rel=)([0-9]{7})', search_res))
        logger.info(f"搜索完成,获取到order_id: {order_id}")

        # 获取明细id confirm_id
        bom_order_details_items_url = self.ERP_URL + f"/DemandBusiness/items?bom_id={order_id}"
        bom_order_details_items_res = self.rss.post(url=bom_order_details_items_url).text
        # logger.info(bom_order_details_items_res)
        confirm_id_old, confirm_id = re.search(r'(<tr source_data-id=")([0-9]+)', bom_order_details_items_res).group(0).split(r'"')
        # picking_id_old, picking_id = re.search(r'(<tr click_id=")([0-9]{7})', bom_order_details_items_res).group(0).split(r'"')
        # logger.info(bom_order_details_items_res)
        logger.info(f"获取到confirm_id：{confirm_id}")

        bom_order_details_transSale_url = self.ERP_URL + f"/DemandBusiness/transSale/id/{order_id}?navTabId=DemandBusiness/deploy&order_type=0"
        bom_order_details_transSale_body= {"confirm_id": confirm_id, "order_type": 0, "ajax": 1, "is_iframe": 1}
        bom_order_details_transSale_res = self.rss.post(url=bom_order_details_transSale_url,data=bom_order_details_transSale_body).text
        # logger.info(bom_order_details_transSale_res)
        logger.info("成功生成SMT-IC销售单")

        # 获取生成的SMT-IC销售单订单号
        bom_order_details_deploy_url = self.ERP_URL + f"/DemandBusiness/deploy/id/{order_id}"
        bom_order_details_res_IC = self.rss.get(url=bom_order_details_deploy_url).text
        SMT_IC_order_sn = bom_order_details_res_IC.split(f'style="line-height:22px;color: blue"><span>销售订单')[1].split(r'</span>')[0]
        logger.info(f"获取生成的SMT-IC销售单订单号为:{SMT_IC_order_sn}")
        return SMT_IC_order_sn

    def ic_order_distribute_sale(self,iC_order_sn):
        """分配订单销售"""
        self.iC_order_sn = iC_order_sn
        search_url = '{}/Orderinfo/index'.format(self.ERP_URL)
        search_body = {'keytype': 'order_sn', 'keyword': self.iC_order_sn, 'start_time': '2022-08-01'}
        logger.info(f"搜索订单编号: {self.iC_order_sn}")
        search_res = self.rss.post(url=search_url, data=search_body, headers=self.headers).text  # 搜索订单，获取order_id
        order_id = re.search(r'(<a href="/Orderinfo/detail\?id=)([0-9]+)', search_res).group(2)
        logger.info(f"搜索完成,获取到order_id: {order_id}")

        # 分配销售
        ic_order_distribute_sale_url = "{}/Orderinfo/editFollowUserMore/navTabId/Orderinfo".format(self.ERP_URL)
        ic_order_distribute_sale_body = {"id":order_id, f"sale_uid[{order_id}]": 706,"sale_list_all": 0,"ajax": 1, "is_iframe": 1}
        ic_order_distribute_sale_res = self.rss.post(url=ic_order_distribute_sale_url, data=ic_order_distribute_sale_body).text
        logger.info("分配成功")
        return self


    def ic_order_define(self):
        """确认订单"""

        search_url = 'https://uat-e.hqchip.com/Orderinfo/index'
        search_body = {'keytype': 'order_sn', 'keyword': self.iC_order_sn, 'start_time': '2022-08-01'}
        logger.info(f"搜索订单编号: {self.iC_order_sn}")
        search_res = self.rss.post(url=search_url, data=search_body, headers=self.headers).text  # 搜索订单，获取order_id
        order_id = re.search(r'(<a href="/Orderinfo/detail\?id=)([0-9]+)', search_res).group(2)
        logger.info(f"搜索完成,获取到order_id: {order_id}")

        # 确认订单
        order_define_url = self.ERP_URL + f"/Orderinfo/confirm/id/{order_id}/navTabId/SaleOrderDetail/ordertype/1?org_id=191"
        order_define_res = self.rss.post(url=order_define_url)
        logger.info(f"确认订单成功")
        return self


    def ic_order_change_price_audit(self):
        """改价审核"""
        # 获取审核id
        # self.iC_order_sn = "S0000000033474"
        change_price_audit_list_url = "{}/OrderPriceAudit/index".format(self.ERP_URL)
        change_price_audit_list_res = self.rss.post(url=change_price_audit_list_url, data={"order_sn": self.iC_order_sn, "pageNum": 1}).text
        OrderPriceAudit_match_msg = re.search(r'(<a href="/OrderPriceAudit/audit/id/)([0-9]+)', change_price_audit_list_res)
        if OrderPriceAudit_match_msg != None:
            logger.info("存在审核按钮")
            OrderPriceAudit_id = OrderPriceAudit_match_msg.group(2)
            logger.info(f"获取到审核id为:{OrderPriceAudit_id}")
            # 循环判断两次状态是否为审核中,若为审核中,则执行审核,反之跳出
            for i in range(2):
              # 获取审核状态

                # print(change_price_audit_list_res.split(f'<a href="/OrderPriceAudit/audit/id/{OrderPriceAudit_id}" rel="OrderPriceAuditAudit" target="dialog" width="580" height="600" title="'))
                audit_status = change_price_audit_list_res.split(f'<a href="/OrderPriceAudit/audit/id/{OrderPriceAudit_id}" rel="OrderPriceAuditAudit" target="dialog" width="580" height="600" title="')[1].split(r'">')[0]
                logger.info(f"获取的操作栏的可操作项为:{audit_status}")
                if audit_status == '审核': # 同意
                    logger.info("开始执行审核操作")
                    audit_url = "{}/OrderPriceAudit/audit/navTabId/OrderPriceAuditAudit".format(self.ERP_URL)
                    audit_body = {"id": OrderPriceAudit_id, "checked": 1, "ajax": 1, "is_iframe":1}
                    audit_res  = self.rss.post(url=audit_url,data=audit_body).text
                    logger.info(f"第{i+1}次审核成功")

                elif audit_status != '审核':
                    logger.info("该订单不要审核")
                    break
            logger.info("执行审核完成")
        else:
            logger.info("不存在审核按钮")
        return self
    def weekday_create(self, n, date):
        """指定日期生成指定日期的n个工作日的日期
        :param date 指定日期
        :param n 工作日数
        """
        j = n
        i = 0
        while i < j:
            # a=dt.date.today()
            a = datetime.strptime(date, '%Y-%m-%d').date()
            a = (a + dt.timedelta(days=i + 1)).strftime("%Y-%m-%d")
            list1 = a.split(r'-')
            list1 = list(int(x) for x in list1)
            tup = tuple(list1)
            b = dt.datetime(tup[0], tup[1], tup[2]).weekday()
            if b == 5 or b == 6:
                j = j + 1
            i = i + 1
        weekday_create = (dt.datetime.now() + dt.timedelta(days=i)).strftime("%Y-%m-%d")
        return weekday_create

    def erp_ic_order_transfer_claim(self, bank_statement_id=None):  # bank_statement_id 取值erp系统公司转账查询里面第一列
        # 订单核销-公司转账
        # 订单核销-公司转账查询
        search_res = None
        n = 0
        while True:
            try:
                search_url = '{}/BankStatement/searchOrder?orderSn={}'.format(self.ERP_URL, self.order_sn)
                search_res = self.rss.get(url=search_url, headers=self.headers).json()
                # print(json.dumps(search_res, ensure_ascii=False).replace("'", '"'))
                transfer_claim_url = "{}/BankStatement/saveClaim/navTabId/BankStatementClaim".format(self.ERP_URL)
                orderClaimList = [
                    {
                        "order_sn": self.order_sn,
                        "smt_order_sn": "",
                        "steel_order_sn": "undefined",
                        "checked": '1',
                        "order_type": "ic",
                        "pay_log_type": '1',
                        "pay_amount": float(
                            search_res.get(r'data', {}).get(r'lists', {}).get(r'lists', {}).get(r'ic', {}).get(
                                'order_amount')),
                        "recive_pay_sn": search_res.get(r'data', {}).get(r'lists', {}).get(r'lists', {}).get(r'ic', {}).get(
                            'recive_pay_sn'),
                    }
                ]
                transfer_claim_body = {"ids": bank_statement_id if bank_statement_id else 1895038187618742274,
                                       "orderClaimList": json.dumps(orderClaimList, indent=4),
                                       "billClaimList": "", "creditClaimList": "", "depositClaimList": "",
                                       "user_name": "", "orderCheck[]": '1',
                                       "order_type": '1', "order_sn[]": self.order_sn, "unionid": "", "ajax": 1,
                                       "is_iframe": 1,
                                       # "order_amount": search_res.get(r'data', {}).get(r'lists', {}).get(r'lists', {}).get(r'ic',{}).get(r'order_amount')
                                       "order_amount": '0.00'
                                       }
                transfer_claim_res = self.rss.post(url=transfer_claim_url, data=transfer_claim_body).json()
                print(transfer_claim_res)
                # 认领日志列表审核
                search_offline_transfer_log_url = '{}/OfflineTransferLog'.format(self.ERP_URL)
                search_offline_transfer_log_body = {
                    "order_no": self.order_sn,
                    "add_uid": 0,
                    "status": "-",
                    "log_from": "-",
                    "claim_type": "-",
                    "pageNum": 1
                }
                search_offline_transfer_log_res = self.rss.post(url=search_offline_transfer_log_url,
                                                                data=search_offline_transfer_log_body).text
                check_id = re.search(r'(<tr target="id" rel=")([0-9]+)', search_offline_transfer_log_res).group(2)
                logger.info(f"搜索完成,获取到订单:{self.order_sn}认领日志列表审核id: {check_id}")
                check_offline_transfer_url = '{}/OfflineTransferLog/writeoff/navTabId/OfflineTransferLog'.format(
                    self.ERP_URL)
                check_offline_transfer_body = {"id": check_id, "remark": "自动化测试", "ajax": 1, "is_iframe": 1}
                check_offline_transfer_res = self.rss.post(url=check_offline_transfer_url,
                                                           data=check_offline_transfer_body).json()
                logger.info(f"认领日志列表审核成功，执行结果为:{check_offline_transfer_res}")
                return check_offline_transfer_res
            except Exception as e:
                n += 1
                if n < 6:
                    logger.warning(f"第 {n} 次,访问IC销售订单号为：{self.order_sn},等待30秒后系统自动重试,错误信息:{e}")
                    time.sleep(30)
                else:
                    logger.error(f"访问需求管理列表搜索订单号为：{self.order_sn} 出错,请手动检查订单管理列表是否存在")
                    raise ValueError
        # print(search_res)







if __name__ == '__main__':
    from huaqiu_order_api.HQCHIP_ERP.login import ErpLogin
    # rss = ErpLogin().login()
    from huaqiu_order_api.HQCHIP_SOO.login import SOOLogin

    target_rss = SOOLogin("uat-e.hqchip.com", "AuthLogin").target_login()
    # ErpOrderCancellation(target_rss).erp_ic_order_cancellation()
    ErpOrderCancellation(target_rss).erp_ic_order_transfer_claim()

