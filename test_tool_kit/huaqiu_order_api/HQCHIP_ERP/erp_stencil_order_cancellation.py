import json
import re

import requests
import yaml

from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_path import yaml_file


class ErpStencilOrdderCancellation:
    def __init__(self, account, psw, order_sn, uesr):
        """
        :param account:  登录ERP账号
        :param psw:  登录ERP密码
        :param order_sn:  前台商城生成订单编号
        :param uesr:    前台商城生成订单编号的用户名称
        """
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.ERP_URL = data['ERP_URL']
        self.account = account
        self.password = psw
        self.order_sn = order_sn
        self.uesr = uesr
        self.rss = requests.Session()
        self.login_url = '{}/public/checkLogin/'.format(self.ERP_URL)
        self.body = {'account': self.account, 'password': self.password}
        self.headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        self.form_headers = {'Content-Type': 'multipart/form-data', "Content-Length"
                             "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"}

    def login(self):
        """
        登录ERP
        """
        logger.info(f"开始执行登录账号:{self.body}")
        self.rss.post(url=self.login_url, data=self.body, headers=self.headers)
        logger.info(f"登录完成")
        return self

    def erp_stencil_order_cancellation(self, trade_out_no):
        """钢网订单订单处理"""
        search_url = '{}/SteelOrder'.format(self.ERP_URL)
        search_body = {'order_sn_value': self.order_sn, 's_time': '2023-01-01', "followup_group_id": -1, "search_order_type": 1}
        logger.info(f"搜索订单编号: {self.order_sn}")
        search_res = self.rss.post(url=search_url, data=search_body, headers=self.headers, timeout=1000).text  # 搜索订单，获取order_id
        # logger.info(search_res)
        self.order_id = re.search('(<a href="/SteelOrder/detail/id/)([0-9]{4})', search_res).group(2)
        logger.info(f"搜索完成,获取到order_id: {self.order_id}")

        # 设置销售员
        set_affi_url = '{}/SteelOrder/changeSaleUid/navTabId/SteelOrder'.format(self.ERP_URL)
        set_affi_body = {"id": self.order_id, "sale_uid": 705, "ajax": 1, "is_iframe": 1}
        logger.info(f"开始设置订单编号: {self.order_sn}的销售员为廖鹏")
        set_affi_res = self.rss.post(url=set_affi_url, data=set_affi_body, headers=self.form_headers, timeout=1000).text
        # logger.info(set_affi_res)

        # 设置销售客服
        set_cus_sale_url = '{}/SteelOrder/changeSaleCusUid/navTabId/SteelOrder'.format(self.ERP_URL)
        set_cus_sale_body = {"id": self.order_id, "sale_cus_uid": 705, "ajax": 1, "is_iframe": 1}
        logger.info(f"开始设置订单编号: {self.order_sn}的销售客服为廖鹏")
        set_cus_sale_res = self.rss.post(url=set_cus_sale_url, data=set_cus_sale_body, headers=self.form_headers,timeout=1000).text
        # logger.info(set_cus_sale_res)

        # 设置生产跟单
        set_produce_sale_url = '{}/SteelOrder/changeProduceUid/navTabId/SteelOrder'.format(self.ERP_URL)
        set_produce_sale_body = {"id": self.order_id, "smt_produce_uid": 705, "ajax": 1, "is_iframe": 1}
        logger.info(f"开始设置订单编号: {self.order_sn}的生产跟单为廖鹏")
        set_produce_sale_res = self.rss.post(url=set_produce_sale_url, data=set_produce_sale_body, headers=self.form_headers, timeout=1000).text

        # 审核
        confirm_url = "{}/SteelOrder/applicationConfirm/navTabId/SteelOrder".format(self.ERP_URL)
        confirm_body = {
            "id": self.order_id,
            "stencil_num": 1,
            "stencil_type": 1,
            "stencil_frame": 1,
            "stencil_side": 3,
            "stencil_size": "37*47",
            "blength": "0.0",
            "bwidth": "0.0",
            "spot_number": 0,
            "is_shaped": 1,
            "stencil_thickness": "0.12",
            "existing_fiducials": 1,
            "printing_type": 1,
            "elec_tropolishing": 2,
            "engineering_require": 1,
            "is_expedited": 1,
            "shipping_id": 1,
            "shipping_pay_type": 1,
            "other_fee": "0.00",
            "payment_method": 1,
            "remark": "",
            "check_remark": "按客户文件制作",
            "annex_file": "",
            "check_status": 1,
            "ajax": 1,
            "is_iframe": 1
        }
        # logger.info(confirm_body)
        confirm_res = self.rss.post(url=confirm_url, data=confirm_body, headers=self.headers, timeout=1000).text
        # logger.info(confirm__res)
        msg = confirm_res.split('"info":"')[1].split('",')[0]

        # Unicode字符串转换为中文字符
        msg_translation = msg.encode('ascii').decode('unicode-escape')
        logger.info(f"钢网订单审核操作结果为{msg_translation}")

        # 核销
        detail_url = self.ERP_URL + f"/SteelOrder/detailTab/id/{self.order_id}"
        detail_res = self.rss.get(url=detail_url).text
        self.erp_pay_sn = re.search('(<a href="/SteelReceiptPay/index\?erp_pay_sn=)(SG[0-9]{6})', detail_res).group(2)
        logger.info(f"搜索完成,获取到钢网的收款单号: {self.erp_pay_sn}")
        receipt_pay_url = "{}/SteelReceiptPay/index".format(self.ERP_URL)
        receipt_pay_body = {"erp_pay_sn": self.erp_pay_sn, "pageNum": 1, "numPerPage": 100}
        receipt_pay_res = self.rss.post(url=receipt_pay_url, data=receipt_pay_body, headers=self.headers, timeout=1000).text
        self.pay_amount = receipt_pay_res.split('<td text_type="right">')[1].split('</td>')[0]
        logger.info(f"获取到收款单号：{self.erp_pay_sn}的应收金额为{self.pay_amount}")

        self.bank_statement(trade_out_no)
        # 生成加工单
        steel_demand_url = '{}/SteelDemand'.format(self.ERP_URL)
        steel_demand_body = {"order_sn":  self.order_sn, "status": 2, "file_status": 2, "_search_likes": "*", "pageNum": 1}
        steel_demand_res = self.rss.post(url=steel_demand_url, data=steel_demand_body, headers=self.headers).text


    def bank_statement(self, trade_out_no):
        # 公司转账认领
        logger.info("开始执行公司转账")
        bank_statement_url = "{}/BankStatement".format(self.ERP_URL)
        bank_statement_body = {"trade_out_no": trade_out_no}
        bank_statement_res = self.rss.post(url=bank_statement_url, data=bank_statement_body).text
        trade_id = re.search('(<tr target="id" rel=")([0-9]{19})', bank_statement_res).group(2)

        trade_out_del_url = self.ERP_URL + f"/BankStatement/claim/navTabId/BankStatementClaim?id={trade_id}"
        trade_out_del_res = self.rss.get(url=trade_out_del_url).text
        total_remain_amount = trade_out_del_res.split('<td class="total_remain_amount_td">')[1].split('</td>')[0]
        if float(self.pay_amount) <= float(total_remain_amount):
            logger.info(f"银行流水单号：{trade_out_no}的剩余总金额大于等于应收单{self.erp_pay_sn}的应收金额")
            bank_statement_claim_url = "{}/BankStatement/saveClaim/navTabId/BankStatementClaim".format(self.ERP_URL)
            orderClaimList = [{"order_sn": self.order_sn, "steel_order_sn": self.order_sn, "checked": 1,
                               "order_type": "steel_0", "pay_log_type": 1, "pay_amount": self.pay_amount,
                               "recive_pay_sn": self.erp_pay_sn
                               }]
            bank_statement_claim_body = {"ids": trade_id, "order_type": 1, "orderCheck[]": 1, "order_sn[]": self.order_sn,
                                         "ajax": 1, "is_iframe": 1, "orderClaimList": json.dumps(orderClaimList)}

            # logger.info(bank_statement_claim_body)
            bank_statement_claim_res = self.rss.post(url=bank_statement_claim_url, data=bank_statement_claim_body,
                                                     headers=self.headers).json()
            # logger.info(bank_statement_claim_res)
            info = bank_statement_claim_res["info"]
            if info == "认领成功":
                logger.info(f"订单：{self.order_sn}公司转账认领成功")
        return self


if __name__ == '__main__':

    order_sn = "GW23072503187"
    ErpStencilOrdderCancellation("admin", "123456",order_sn,"uesr").login().erp_stencil_order_cancellation("G999999999")