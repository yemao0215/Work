import yaml

from huaqiu_order_api.HC2018_admin.login.login import Login
from huaqiu_order_api.HC2018_admin.stock_select import Hc2018StockMange
from huaqiu_order_api.HQCHIP_ERP.erp_stock_select import ErpStockSelect
from huaqiu_order_api.HQCHIP_ERP.login import ErpLogin
from huaqiu_order_api.HQCHIP_SCM.scm_stock.stock_lock.stock_lock import StockLock
from huaqiu_order_api.HQCHIP_SOO.login import SOOLogin
from huaqiu_order_api.HQCHIP_WMS.stock_manage.stock_select import StockMange
from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_path import account_yaml


class MainGoodsStockWarehouse:
    def __init__(self):
        with open(account_yaml, 'r', encoding='utf-8') as yamlfile:
            account = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.goods_id = account["HQCHIP_GOODS"]["goods_id"]

    def main_Warehouse_decide(self):
        main_Warehouse_msg = ''
        dos_target_rss = Login().login()
        dos_msg = Hc2018StockMange(dos_target_rss).dos_out_goods_decide()
        dos_result = "不符合" in dos_msg
        logger.info(dos_result)
        if dos_result == False:
            scm_target_rss = SOOLogin("uat-scm.huaqiu.com", "hqScm").target_login()
            scm_msg = StockLock(scm_target_rss).stock_lock_select()
            scm_result = "不符合" in scm_msg
            if scm_result == False:
                erp_rss = ErpLogin().login()
                erp_msg = ErpStockSelect(erp_rss).erp_out_goods_decide()
                erp_result = "不符合" in erp_msg
                if erp_result == False:
                    wms_target_rss = SOOLogin("uat-wms.huaqiu.com", "wms/base").target_login()
                    wms_msg = StockMange(wms_target_rss).wms_out_goods_decide()
                    wms_result = "不符合" in wms_msg
                    if wms_result == False:
                        main_Warehouse_msg = f"库存id：{self.goods_id}符合出库要求"
                        logger.info(main_Warehouse_msg)
        else:
            main_Warehouse_msg = f"库存id：{self.goods_id}不符合出库要求，请检查库存相关信息"
            logger.error(main_Warehouse_msg)
        return main_Warehouse_msg
if __name__ == '__main__':
        MainGoodsStockWarehouse().main_Warehouse_decide()


