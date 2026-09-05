import os

import yaml

from huaqiu_order_api.HQCHIP_Center.user_center import get_address, get_invoice, get_man
from huaqiu_order_api.SSO_Reception.sso_reception import SSO_Reception
from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_data import Data
from huaqiu_order_api.common.my_path import stockup_dir, smt_yansuo_dir, bom_dir, yaml_file, account_yaml


class StencilOrder:
    def __init__(self, rss, stencilFrame=None, stencilType=None, printingType=None, elec_tropolishing=None, stencil_size=None, stencil_side=None,
                 stencil_thickness=None, existing_fiducials=None, engineering_require=None):
        self.rss = rss
        self.headers = {"Content-Type": "application/json",
                        "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://www.huaqiu.com)"
                        }
        self.form_headers = {"Content-Type": "application/x-www-form-urlencoded",
                             "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://www.huaqiu.com)"
                             }
        self.data_headers = {"Content-Type": "multipart/form-data",
                             "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://www.huaqiu.com)"
                             }
        # self.phone = phone
        self.token = getattr(Data, "token")
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.HQCHIP_PC_ITEM_URL = data['HQCHIP_PC_ITEM_URL']
        self.HQPCB_URL = data['HQPCB_URL']
        with open(account_yaml, 'r', encoding='utf-8') as yamlfile:
            account = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.phone = account['PassPort']['phone']
        self.vat_type = account["HQCHIP_GOODS"]["vat_type"]
        self.vat_sub_type = account["HQCHIP_GOODS"]["vat_sub_type"]
        self.stencilNumber = account["HQCHIP_GOODS"]["number"]
        self.stencilFrame = stencilFrame
        self.stencilType = stencilType
        self.printingType = printingType
        self.elec_tropolishing = elec_tropolishing
        self.stencil_size = stencil_size
        self.stencil_side = stencil_side
        self.stencil_thickness = stencil_thickness
        self.existing_fiducials = existing_fiducials
        self.engineering_require = engineering_require


    def stencil_order_file(self, stencil_order_file_dir):
        """钢网文件上传"""
        stencil_order_file_url = "{}/upfile?type=pcbfile".format(self.HQPCB_URL)
        # return file_server_url
        head = {"User-Agent": "HQPCB Crawler DFM Push Tools"}
        data = {'type': 'iamges'}
        fp = open(stencil_order_file_dir, 'rb')
        files = {'file': (os.path.basename(stencil_order_file_dir), fp)}
        smt_order_file_url_res = self.rss.post(url=stencil_order_file_url, data=data, files=files,
                                               headers=head).json()
        logger.info(smt_order_file_url_res)
        file_server_url = smt_order_file_url_res["url"]
        return file_server_url



    def stencil_tmp_save(self):
        """钢网需求保存"""
        logger.info(self.stencil_side)
        logger.info(self.stencil_thickness)
        logger.info(self.existing_fiducials)
        save_order_url = "{}/stencil/quote_save".format(self.HQPCB_URL)
        save_order_body = {
            "stencil_frame": self.stencilFrame,
            "elec_tropolishing": self.elec_tropolishing,
            "stencil_size": self.stencil_size,
            "stencil_side": self.stencil_side,
            "stencil_thickness": self.stencil_thickness,
            "stencil_num": self.stencilNumber,
            "stencil_type": self.stencilType,
            "existing_fiducials": self.existing_fiducials,
            #"application_sphere": 1,
            "province": 6,
            "city": 77,
            "ship_name": "顺丰寄付",
            "invoice": "不需要",
            "printing_type": self.printingType,
            "engineering_require": self.engineering_require,
            "deltime": "24小时"
        }

        save_order_res = self.rss.post(url=save_order_url, data=save_order_body, headers=self.form_headers).json()
        logger.info(save_order_res)
        self.stencil_tmp_id = save_order_res["data"]["smd_quote_id"]
        self.smd_freight_fee = save_order_res["data"]["smd_freight_fee"]
        self.smd_total_amount = save_order_res["data"]["smd_freight_fee"]
        logger.info(f"获取到生成的需求id：{self.stencil_tmp_id}")
        return self

    def place_an_order(self):
        logger.info(f"开始检查收货地址")
        address_id = get_address(self.rss)
        logger.info(f"获取下单人信息id")
        orderMan_id, orderManName, orderManTel = get_man(self.rss)
        logger.info(f"拿到收货地址id: {address_id}")
        file_server_url = self.stencil_order_file(smt_yansuo_dir)
        add_user_email = str(self.phone) + "@163.com"
        invoice_type = None
        invoice = ''
        # if self.vat_type == '1' and self.vat_sub_type == '1':
        #     logger.info("选择发票类型为纸质增值税（专用）发票")
        #     invoice_type = 1
        if self.vat_type == '1' and self.vat_sub_type == '2':
            logger.info("选择发票类型为数电增值税（专用）发票")
            invoice = "增票全电"
            invoice_type = 1
        elif self.vat_type == '0' and self.vat_sub_type == '3':
            logger.info("选择发票类型为增值税（普通）电子发票")
            invoice_type = 2
            invoice = "普票"
        elif self.vat_type == '3' and self.vat_sub_type == '0':
            logger.info("选择发票类型为不开发票")
            invoice_type = 0
            invoice = "不需要"
        logger.info(f"对接用户中心的invoice_type：{invoice_type}")
        invoice_id = get_invoice(self.rss, invoice_type, 1)
        logger.info(f"拿到发票id: {invoice_id}")
        place_an_url = "{}/stencil/save".format(self.HQPCB_URL)
        place_an_body = {
            "smd_quote_id": self.stencil_tmp_id,
            "gerber_file": file_server_url,
            "address_id": address_id,
            "express": "顺丰寄付",
            "invoice": "不需要",
            "printing_type": 1,
            "engineering_require": 1,
            "bill_id": 0,
            "enginer_name": "test",
            "enginer_phone": self.phone,
            "enginer_email": add_user_email,
            "fhp": 0,
            "fhd_title": "",
            "deltime": "",
            "shipping_id": 30000000,
            "ship_name": "顺丰寄付",
            "contact": "",
            "stencil_note": "",
            "checked": True,
            "s_type": 1,
            "pcb_order_id": 0,
            "orderman_id": orderMan_id,
            "email": "",
            "fullname": ""

        }
        if invoice_id != None:
            place_an_body["bill_id"] = invoice_id
            place_an_body["invoice"] = invoice
        self.form_headers["Authorization"] = self.token
        save_order_res = self.rss.post(url=place_an_url, data=place_an_body, headers=self.form_headers).json()
        logger.info(save_order_res)
        msg = save_order_res["msg"]
        # order_sn = ""
        if msg == "提交订单成功":
            order_sn = save_order_res["data"]["smd_order_sn"]
            order_id = save_order_res["data"]["smd_order_id"]
            logger.info(f"订单生成成功，钢网订单编号: {order_sn}")
            logger.debug('=*' * 50)
            return order_sn



if __name__ == '__main__':
    rss= SSO_Reception('https://uat-www.hqpcb.com').login()
    StencilOrder(rss).stencil_tmp_save().place_an_order()