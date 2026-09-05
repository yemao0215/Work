from huaqiu_order_api.HQCHIP_ERP import erp_smt_order_cancellation
from huaqiu_order_api.HQCHIP_SCM.sorting import queryExpress
from huaqiu_order_api.HQPCBA.HQPCBA_Admin import HQPCBA_Admin_cancellation
from huaqiu_order_api.HQPCBA.HQPCBA_Reception import pcba_order
from huaqiu_order_api.HQSMT.SMT_Reception import SMT_order
from huaqiu_order_api.HQSMT.SMT_Reception.SMT_order import SmtOrder


class RunSMT:
    def __init__(self):
        pass


    @staticmethod
    def main(type, params=None):
        dict = {
                'smt_order': SMT_order.SmtOrder().mian_smt_order,  # 单独SMT下单
                'pcba_order': pcba_order.PcbaOrder().run_pcba_order,  # PCBA下单
                'erp_audit_pay': erp_smt_order_cancellation.ErpSmtOrderCancellation().mian_erp_smtorder_run,
                'scm_delivery': queryExpress.queryExpress().express_sort_run,
                'pcbames_RCV_AOI': HQPCBA_Admin_cancellation.HQCPCBAdminCancellation().admin_cancellation_RCV_AOI_run,
                'pcbames_RCV_DIP': HQPCBA_Admin_cancellation.HQCPCBAdminCancellation().admin_cancellation_RCV_DIP_run,
                'pcbames_RCV_QA': HQPCBA_Admin_cancellation.HQCPCBAdminCancellation().admin_cancellation_RCV_QA_run,
                'pcbames_RCV_INN': HQPCBA_Admin_cancellation.HQCPCBAdminCancellation().admin_cancellation_RCV_INN_run,
                'pcbames_RCV_DEL': HQPCBA_Admin_cancellation.HQCPCBAdminCancellation().admin_cancellation_RCV_DEL_run,
                'smt_erp_pcbames': HQPCBA_Admin_cancellation.HQCPCBAdminCancellation().smt_admin_pcbmes_run,
                # 'pcba_erp_pcbames': xnpb.Virtualpb().run_order_pb,

                }
        dict[type]() if params is None else dict[type](params)


if __name__ == '__main__':
    """
    'smt_order': 单独下SMT订单，只要改一下配置文件里面的Conf→account_conf_yaml.PassPort.name\phone\pwd
    'pcba_order': pcb_bom_smt_dict字典格式为{"pcb_bom_sn_dict": {"pcb_sn": "", "bom_sn": ""}, "smt_order_id": "", "dict_obj": ""} 下PCBA订单，字典字段非必传
    'erp_audit_pay': 自动审核 传入需审核的关联SMT订单号
    'scm_delivery': scm快递签收, 传入需签收的关联快递单号
    'pcbames_RCV_AOI': PCBAMES操作：工厂收料到AOI检验完成 传入SMT订单号
    'pcbames_RCV_DIP': PCBAMES操作：工厂收料到DIP生产完成 传入SMT订单号
    'pcbames_RCV_QA': PCBAMES操作：工厂收料到QA检验完成，传入SMT订单号
    'pcbames_RCV_INN': PCBAMES操作：工厂收料到成品入库完成，传入SMT订单号
    'pcbames_RCV_DEL': PCBAMES操作：工厂收料到发货完成，传入SMT订单号
    'smt_erp_pcbames': 全流程1：单独下SMT得到一个已发货订单
    'pcba_erp_pcbames': 全流程2：PCBA得到一个已发货订单
    如需切换环境，打开pcb_config.yaml配置文件，修改域名即可
    """
    # TK24082696777、TK24082699168、TK24082654128、TK24082645318、TK24082690730
    # RunSMT().main('pcba_order')
    RunSMT().main('erp_audit_pay', 'TK24112635428') # SF202408220006280
    # RunSMT().main('scm_delivery', 'SF202408260006893')
    # RunSMT().main('pcbames_RCV_DEL', 'TK24082646254')
    # RunSMT().main('smt_erp_pcbames')