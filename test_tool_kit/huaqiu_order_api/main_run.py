# from ic_order_delivery.erp_order_cancellation import ErpOrderCancellation
# from ic_order_delivery.ic_order import IcOrder
# from ic_order_delivery.wms_out_warehouse import WmsOutWarehouse

from HQCHIP_SOO.login import SOOLogin
# from HQCHIP_Activity.coupon.coupon_list import common
from HQCHIP_WMS.wms_out_warehouse import WmsOutWarehouse

# # ic订单购买下单--erp处理--wms出库
# rss = SSO_Reception('16000000003', 'a123456.', 'https://uat-www.hqchip.com').login()
# order_sn = IcOrder(rss, '16000000003', 2500216175, 5, 2).add_cart().place_an_order()  # 8=长沙仓  2=东莞仓
# out_sn = ErpOrderCancellation("admin", "123456", order_sn, "jf_15113305").login().erp_ic_order_cancellation()
target_rss = SOOLogin("admin", "12345678", "uat-wms.huaqiu.com", "wms/base").target_login()
WmsOutWarehouse(target_rss, 'OUT00263678', "2").wms_pick().pda_shipments().wms_pack()

# # bom订单下单
# order_sn = BomOrder('15912757721', 'a123456', 2500323787).login().bom_file()
# iC_order_sn = ErpOrderCancellation("admin", "123456", order_sn,
#                                    "jf_15113305").login().erp_bom_order_define().erp_bom_order_match().erp_bom_order_audit().erp_bom_order_Generate_sales_order()
# ErpOrderCancellation("admin", "123456", order_sn, "jf_15113305").login().ic_order_distribute_sale(
#     iC_order_sn).ic_order_define().logout_login_audit("qiufangmei", "123456").ic_order_change_price_audit()
# ErpOrderCancellation("admin", "123456", order_sn, "jf_15113305").logout_login_audit("qiufangmei","123456").ic_order_change_price_audit()

# 补备货流程-erp处理-wms入库
# StockUp('yemao', '123456', "CF1W-1KΩ±1%T1", "A Plus",1000).login().stock_up_file().stock_up_judge_type().stock_up_audit()
# inn_sn = ErpStockPurchase("admin", "123456", "CF1W-1KΩ±1%T1").login().stock_up_plan().stock_up_purchase_affirm().logout_login_audit("admin", "123456").stock_up_purchase_audit().stock_up_purchase_deliver_goods()
# target_rss = SOOLogin("admin", "12345678", "uat-wms.huaqiu.com", "wms/base").target_login()
# WmsInWarehouse(target_rss, 'IN00154117', "2").wms_warehousing().wms_theupper_list().pda_theupper()


# # # HC2018创建资料
# GoodsMeans("admin", "123456", "LM2596-ADJ5",
#            "A Plus", 2000).login().goods_means_add().goods_means_list().goods_means_giveaudit().goods_means_audit()
# StockUp('yemao', '123456', "LM2596-ADJ5","A Plus",2000).stockup_excel_add().login().stock_up_file().stock_up_judge_type().stock_up_audit()
# inn_sn = ErpStockPurchase("admin", "123456", "LM2596-ADJ5").login().stock_up_plan().stock_up_purchase_affirm().logout_login_audit("admin", "123456").stock_up_purchase_audit().stock_up_purchase_deliver_goods()
# target_rss = SOOLogin("admin", "12345678", "uat-wms.huaqiu.com", "wms/base").target_login()
# WmsInWarehouse(target_rss, inn_sn, "2").wms_warehousing().wms_theupper_list().pda_theupper()


# 营销中台
# cookie = SOOLogin("admin", "12345678", "uat-activity.hqchip.com", "ecmc").target_login()
# print(type(cookie))
# common(json.dumps(cookie)).common_list()
print(111)

