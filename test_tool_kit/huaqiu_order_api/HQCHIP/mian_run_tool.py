from huaqiu_order_api.HQCHIP import mian_ic
from huaqiu_order_api.HQCHIP_ERP import mian_erp


class RunICTool:
    def __init__(self):
        pass


    @staticmethod
    def main(type, params=None):
        dict = {
                'ic_order': mian_ic.RunIC().mian_ic_order_create,  # IC下单
                'erp_audit_pay': mian_erp.RunErp().mian_ic_erp,  # ic erp审核支付
                # 'wms_order': queryExpress.queryExpress().express_sort_run,
                # 'pcbames_RCV_AOI': HQPCBA_Admin_cancellation.HQCPCBAdminCancellation().admin_cancellation_RCV_AOI_run,
                # 'pcbames_RCV_DIP': HQPCBA_Admin_cancellation.HQCPCBAdminCancellation().admin_cancellation_RCV_DIP_run,
                # 'pcbames_RCV_QA': HQPCBA_Admin_cancellation.HQCPCBAdminCancellation().admin_cancellation_RCV_QA_run,
                # 'pcbames_RCV_INN': HQPCBA_Admin_cancellation.HQCPCBAdminCancellation().admin_cancellation_RCV_INN_run,
                # 'pcbames_RCV_DEL': HQPCBA_Admin_cancellation.HQCPCBAdminCancellation().admin_cancellation_RCV_DEL_run,
                # 'smt_erp_pcbames': HQPCBA_Admin_cancellation.HQCPCBAdminCancellation().smt_admin_pcbmes_run,
                # # 'pcba_erp_pcbames': xnpb.Virtualpb().run_order_pb,

                }
        dict[type]() if params is None else dict[type](params)


if __name__ == '__main__':
    RunICTool().main('ic_order', {"goods": {'goods_id': '2500368607', 'number': '10', 'warehouse_id': '2', 'vat_type': '0',
                                            'vat_sub_type': '3', 'shipping_method': '1', 'relation_smt_order_sn': ''},
                                               'user': {"phone": "13889222016 ", "name": "jf_71970789", "pwd": "ye123456"}})
    # RunICTool().main('erp_audit_pay', 'S0000000034564')