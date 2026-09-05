from huaqiu_order_api.HQCHIP.ic_order import IcOrder
from huaqiu_order_api.HQCHIP_Center.user_center import get_ic_order_pay
from huaqiu_order_api.HQCHIP_ERP.erp_order_cancellation import ErpOrderCancellation
from huaqiu_order_api.HQCHIP_ERP.erp_order_stock import ErpOrderStock
from huaqiu_order_api.HQCHIP_ERP.erp_stock_purchase import ErpStockPurchase
from huaqiu_order_api.HQCHIP_ERP.login import ErpLogin
from huaqiu_order_api.HQCHIP_SOO.login import SOOLogin
from huaqiu_order_api.HQCHIP_WMS.HQCHIP_PDA_UAT.pda_login import PdaLogin
from huaqiu_order_api.HQCHIP_WMS.HQCHIP_PDA_UAT.pda_pick import PdaPick
from huaqiu_order_api.HQCHIP_WMS.HQCHIP_PDA_UAT.pda_theupper import PdaTheupper
from huaqiu_order_api.HQCHIP_WMS.wms_in_warehouse import WmsInWarehouse
from huaqiu_order_api.HQCHIP_WMS.wms_out_warehouse import WmsOutWarehouse
from huaqiu_order_api.SSO_Reception.sso_reception import SSO_Reception
from huaqiu_order_api.common.my_data import Data
from huaqiu_order_api.common.my_path import account_yaml
from huaqiu_order_api.common.yaml_handler import write_yaml
from huaqiu_order_api.mian_goods_stock_warehouse import MainGoodsStockWarehouse


class RunIC:
    def __init__(self, reception_rss=None):
        self.url = "https://uat-www.hqchip.com"
        self.reception_rss = reception_rss

    def mian_ic_order_create(self, order_dict=None):
        if isinstance(order_dict, dict):
            if "user" in order_dict:
                # user = {"phone": phone, "name": name, "pwd": password}
                user = order_dict["user"]
                user_msg = {'PassPort': user}
                write_yaml(account_yaml, user_msg)
            if "goods" in order_dict:
                # goods = {'goods_id': '', 'number': '1', 'warehouse_id': '2', 'vat_type': '1', 'vat_sub_type': '',  'shipping_method': '', 'relation_smt_order_sn': ''}
                goods = order_dict["goods"]
                order_params = {"HQCHIP_GOODS": goods}
                write_yaml(account_yaml, order_params)
        if self.reception_rss == None:
            rss = SSO_Reception(self.url).login()
            self.reception_rss = rss
        IcOrder(self.reception_rss).add_cart().place_an_order()
        print(getattr(Data, 'order_json'))
        order_json = getattr(Data, 'order_json')
        if order_json != {}:
            get_ic_order_pay(self.reception_rss, order_sn=order_json.get('order_sn'))
        return self
    def mian_ic_order_spots(self):
        """非代购储位--自营现货"""
        main_Warehouse_msg = MainGoodsStockWarehouse().main_Warehouse_decide()
        main_Warehouse_result = "不符合" in main_Warehouse_msg
        if main_Warehouse_result == False:
            rss = SSO_Reception(self.url).login()
            IcOrder(rss).add_cart().place_an_order()
            erp_rss = ErpLogin().login()
            ErpOrderCancellation(erp_rss).erp_ic_order_cancellation()
            target_rss = SOOLogin("uat-wms.huaqiu.com", "wms/base").target_login()
            WmsOutWarehouse(target_rss).wms_pick()
            pda_rss = PdaLogin().pda_login()
            PdaPick(pda_rss).pda_pick()
            WmsOutWarehouse(target_rss).wms_pack()
        return self

    def mian_ic_order_no_spots(self):
        """非代购储位--自营非现货"""
        rss = SSO_Reception(self.url).login()
        IcOrder(rss).add_cart().place_an_order()
        erp_rss = ErpLogin().login()
        ErpOrderCancellation(erp_rss).erp_ic_order_cancellation()
        target_rss = SOOLogin("uat-wms.huaqiu.com", "wms/base").target_login()
        WmsOutWarehouse(target_rss).wms_pick()
        pda_rss = PdaLogin().pda_login()
        PdaPick(pda_rss).pda_pick()
        WmsOutWarehouse(target_rss).wms_pack()
        return self
    def mian_ic_order_daigou(self):
        """代购储位商品出库流程（含销售代采流程）"""
        rss = SSO_Reception(self.url).login()
        IcOrder(rss).add_cart().place_an_order()
        erp_rss = ErpLogin().login()
        ErpOrderCancellation(erp_rss).erp_ic_order_cancellation()
        ErpOrderStock(erp_rss).need_order_cancellation()
        ErpStockPurchase(erp_rss).order_stock_purchase_affirm().stock_up_purchase_deliver_goods()
        target_rss = SOOLogin("uat-wms.huaqiu.com", "wms/base").target_login()
        WmsInWarehouse(target_rss).wms_warehousing().wms_theupper_list()
        pda_rss = PdaLogin().pda_login()
        PdaTheupper(pda_rss).pda_theupper()
        WmsOutWarehouse(target_rss).wms_pick()
        PdaPick(pda_rss).pda_pick()
        WmsOutWarehouse(target_rss).wms_pack().interface_log_search()
        return self

if __name__ == '__main__':
    RunIC().mian_ic_order_create()