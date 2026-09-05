import re
from datetime import datetime

import requests

from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_data import Data


class OldMesSmtOrderCancellation:
    def __init__(self, smt_order):
        self.oldmes_rss = requests.Session()
        self.headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        self.smt_order = getattr(Data, 'smt_order_sn')


    def login(self):

        login_url = "https://uat-mes.hqchip.com/Portal/checkLogin.html"
        login_body = {'user_name': "icmall", 'password': "123456"}
        logger.info(f"开始执行登录账号:{login_body}")
        self.oldmes_rss.post(url=login_url, data=login_body, headers=self.headers)
        logger.info(f"登录完成")
        return self

    def smt_order_delivery(self):
        """发货"""
        # 切换至东莞华秋
        self.json_headers = {"Content-Type":  "application/json"}
        switch_factory_url = "https://uat-mes.hqchip.com/Portal/switchFactory.html?fid=1"
        self.oldmes_rss.get(url=switch_factory_url, headers=self.json_headers)

        # 获取out_id
        out_add_url = "https://uat-mes.hqchip.com/Out/add.html"
        out_add_res = self.oldmes_rss.get(url=out_add_url).text
        out_id = re.search('(name=\"out_id\" value=\")([0-9]{5})', out_add_res).group(2)
        logger.info(f"获取到out_id：{out_id}")

        # 获取 orderId
        product_list_url = "https://uat-mes.hqchip.com/Out/selectDetail/is_ajax/1.html"
        product_list_body = {"pageNum": 1, "act": "add", "customer_id": "", "order_no": "", "material_name": self.smt_order}
        product_list_res = self.oldmes_rss.post(url=product_list_url, json=product_list_body, headers=self.json_headers).text
        # logger.info(product_list_res)
        orderId = re.search('(<tr data-id=")([0-9]{5})', product_list_res).group(2)
        order_no = re.search('(<td>)(HDGHQ[0-9]{12})', product_list_res).group(2)
        custom_name = re.search('(<td>)(jf_[0-9]{8})', product_list_res).group(2)
        # over_status = re.search('(<td class="over_status">)', product_list_res).group(2)
        logger.info(f"获取到: {orderId},{order_no},{custom_name}")

        # 确认发货结果
        check_deliver_url = "https://uat-mes.hqchip.com/Out/addSelectDetail/navTabId/OutEdit.html"
        check_deliver_body = {"order_id": out_id, "ids[]": orderId, "act": "add", "ajax": 1}
        product_list_res = self.oldmes_rss.post(url=check_deliver_url, data=check_deliver_body).json()
        logger.info(product_list_res)
        forwardUrl = product_list_res["forwardUrl"]
        logger.info(forwardUrl)
        # out_id = forwardUrl.split("https://uat-mes.hqchip.com/Out/add.html?id=")[1].split("&action_id=0&navTabId=OutEdit&enter_save=1")[0]


        # 发货明细
        forward_url = f"https://uat-mes.hqchip.com{forwardUrl}"
        forward_res = self.oldmes_rss.get(url=forward_url).text
        customer_no = forward_res.split('name="out[customer_no]" size="23" value="')[1].split('"/>')[0]
        customer_id = forward_res.split('name="out[customer_id]"  value="')[1].split('">')[0]
        receiver_tel = forward_res.split('name="out[receiver_tel]" size="25" value="')[1].split('" onblur="sessionStorage.setItem')[0]
        detail_id = re.search('(<tr target="detail_id" rel=")([0-9]{5})', forward_res).group(2)
        biz_data = str(datetime.now().strftime('%Y-%m-%d'))
        #
        out_insert_url = "https://uat-mes.hqchip.com/Out/insert/navTabId/Out.html"
        out_insert_body = {"out_id": out_id,"out[express_company]": "顺丰快递","out[express_no]": "", "out[customer_no]": customer_no,
                            "out[receiver]": "测试订单", "out[receiver_tel]": receiver_tel, "out[customer_id]": customer_id, "out[customer_name]": custom_name,
                           "out[receiver_address]" : "中国广东省深圳福田区新一代产业园1栋5楼","out[memo]": "", f"detail[{detail_id}][num]": 4,
                           f"detail[{detail_id}][memo]": "测试订单", "out[biz_date]": biz_data, "ajax": 1
                           }
        # 保存发货明细
        out_insert_res = self.oldmes_rss.post(url=out_insert_url, data=out_insert_body).json()
        logger.info(out_insert_res)
        msg = out_insert_res["info"]
        if msg == "保存成功":
            logger.info(f"订单号：{self.smt_order}的发货明细保存成功")
            self.delivery_audit()

            edit_express_url = "https://uat-mes.hqchip.com/Out/editExpress/navTabId/OutEdit.html"
            edit_express_body = {"out_id": out_id, "express_company": "顺丰快递", "express_no": "SFTEST2023", "ajax": 1}
            edit_express_res = self.oldmes_rss.post(url=edit_express_url, data=edit_express_body).json()
            msg = edit_express_res["info"]
            if msg == "更新成功":
                logger.info(f"单据：{self.document_no}发货成功")

        return self
    def delivery_audit(self):
        out_info_url = "https://uat-mes.hqchip.com/Out/index"
        out_info_body = {"material_name": self.smt_order, "fabricated_factory_id": -1}
        out_info_res = self.oldmes_rss.post(url=out_info_url, data=out_info_body).text
        # logger.info(out_info_res)
        serial_no = re.search('(<td>)(NO.[0-9]{6})', out_info_res).group(2)
        self.document_no = re.search('(<td>)(PODGHQ-[0-9]{12})', out_info_res).group(2)
        customer_no = re.search('(<td>)(KH[0-9]{9})', out_info_res).group(2)
        out_id = re.search('(<tr target="id" rel=")([0-9]{5})', out_info_res).group(2)
        logger.info(f"获取到：serial_no：{serial_no}，document_no：{self.document_no}，customer_no：{customer_no}，out_id：{out_id}")

        out_info_edit_detail_url = f"https://uat-mes.hqchip.com/Out/edit.html?id={out_id}"
        out_info_edit_detail_res = self.oldmes_rss.get(url=out_info_edit_detail_url).text
        # logger.info(out_info_edit_detail_res)
        out_info_edit_url = "https://uat-mes.hqchip.com/Out/audit/navTabId/OutEdit.html"
        out_info_edit_body = {"order_id": out_id, "act": "{1$act}", "audit_remark": "测试订单", "ajax": 1}
        out_info_edit_res = self.oldmes_rss.post(url=out_info_edit_url, data=out_info_edit_body).json()
        msg = out_info_edit_res["info"]
        if msg == "审核成功":
            logger.info(f"单据：{self.document_no}审核成功")
        return self

    def main_old_mes_delivery(self):
        self.login()
        self.smt_order_delivery()


    def bug(self):
        # date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        date_obj = str(datetime.now().strftime('%Y%m%d'))
        logger.info(date_obj)

        logger.info(type(date_obj))



if __name__ == '__main__':
    # rss = SSO_Reception('15912757721', 'a123456', 'https://uat-smt.hqchip.com').login()
    # order_sn = SmtOrder(rss, 15912757721).smt_tmp_save().place_an_order()
    order_sn = "TK23062164655"
    # OldMesSmtOrderCancellation(order_sn).main_old_mes_delivery()
    OldMesSmtOrderCancellation(order_sn).bug()

