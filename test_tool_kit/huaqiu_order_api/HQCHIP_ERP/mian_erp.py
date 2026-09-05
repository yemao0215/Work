from huaqiu_order_api.HQCHIP_ERP.erp_order_cancellation import ErpOrderCancellation
from huaqiu_order_api.HQCHIP_ERP.erp_smt_order_cancellation import ErpSmtOrderCancellation
from huaqiu_order_api.HQCHIP_ERP.erp_stock_purchase import ErpStockPurchase
from huaqiu_order_api.HQCHIP_SOO.login import SOOLogin
from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_data import Data


class RunErp:

    def __init__(self):
        self.url = "https://uat-www.hqchip.com"

    def mian_ic_erp(self, order_sn=None):
        target_rss = SOOLogin(system_name="erp").target_login()
        ErpOrderCancellation(target_rss, order_sn).erp_ic_order_cancellation()
        print(getattr(Data, 'erp_order_json'))
        return self

    def mian_bom_erp(self, order_sn):
        target_rss = SOOLogin(system_name="erp").target_login()
        iC_order_sn = ErpOrderCancellation(target_rss).erp_bom_order_define().erp_bom_order_match().erp_bom_order_audit().erp_bom_order_Generate_sales_order()
        return self

    def mian_smt_erp(self, order_sn=None):
        target_rss = SOOLogin(system_name="erp").target_login()
        ErpSmtOrderCancellation(target_rss, order_sn).erp_smt_order_cancellation()
        return self
    def mian_stock_up_purchase(self, param_dict=None):
        # param_dict = {"goods_name": "GS8551-TR", "supplier_sn": "hqchip-llsjl", "order_sn": "HQCHIP-SOO-S-20230406-00000001"}
        target_rss = SOOLogin(system_name="erp").target_login()
        ErpStockPurchase(target_rss, **param_dict).mian_stock_up_purchase()

    def mian_erp(self, order_sn):
        result_smt = "TK" in order_sn
        if result_smt == True:
            logger.info(f"{order_sn}为SMT订单，将执行SMT的ERP处理流程")
            self.mian_smt_erp(order_sn)
        else:
            result_ic = "S" in order_sn
            if result_ic == True:
                logger.info(f"{order_sn}为ic订单，将执行IC的ERP处理流程")
                self.mian_ic_erp(order_sn)
        return self