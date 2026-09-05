import random
from datetime import datetime

from huaqiu_order_api.HQCHIP.HQCHIP_OpenAPI.OpenAPI_Order.create_order import CreateOrder
from huaqiu_order_api.HQCHIP.HQCHIP_OpenAPI.OpenAPI_Order.pay_order import PayOrder
from huaqiu_order_api.common.loguru_logger import logger


class RunHqchipOpenApi:
    def __init__(self):
        self.url = "http://debugapi.hqchip.com"  # 预发布
        # self.url = "http://api.hqchip.com" # 线上
        self.app_key = "c11ff533617d2aa45ffd0e1994fb2cd7"
        self.app_sec = "7b0594651ce4ab534b3f941e5dc9fe63"


    def out_order_no_cearte(self):
        Overlying = random.randint(1, 100)
        date_obj = str(datetime.now().strftime('%Y%m%d'))
        if Overlying < 10:
            Overlying = "00000" + str(Overlying)
        else:
            Overlying = "0000" + str(Overlying)
        out_order_no_number = date_obj + str(Overlying)
        self.out_order_no = "YE" + out_order_no_number
        logger.info(f"生成out_order_no：{self.out_order_no}")
        return self
    def main_goods_list(self):
     pass
    def main_order_cearte(self):
        """订单生成"""
        self.out_order_no_cearte()
        CreateOrder(self.url, self.app_sec, self.app_key, self.out_order_no).openapi_goods_list()
        # self.order_sn, self.order_id = CreateOrder(self.url, self.app_sec, self.app_key, self.out_order_no).openapi_make()
        return self

    def main_order_pay(self, pay_type):
        """
        订单付款
        :param pay_type 1余额，2信用支付，3公司转账
        """
        # self.order_sn = "S2023062717536"
        # self.order_id = 297528
        PayOrder(self.url, self.app_sec, self.app_key, self.order_sn, self.order_id, pay_type).erp_confirm_order(self.out_order_no).order_pay()
        return self


    def mian(self, pay_type):
        self.main_order_cearte()
        self.main_order_pay(pay_type)




if __name__ == '__main__':
    RunHqchipOpenApi().main_order_cearte()