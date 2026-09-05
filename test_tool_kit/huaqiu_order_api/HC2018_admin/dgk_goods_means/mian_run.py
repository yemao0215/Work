from huaqiu_order_api.HQCHIP_ERP import erp_smt_order_cancellation
from huaqiu_order_api.HQCHIP_SCM.sorting import queryExpress
from huaqiu_order_api.HQPCBA.HQPCBA_Admin import HQPCBA_Admin_cancellation
from huaqiu_order_api.HQPCBA.HQPCBA_Reception import pcba_order
from huaqiu_order_api.HQSMT.SMT_Reception import SMT_order
from huaqiu_order_api.HQSMT.SMT_Reception.SMT_order import SmtOrder


class RunGoods:
    def __init__(self):
        pass


    @staticmethod
    def main(type, params=None):
        dict = {
                'goods_add': SMT_order.SmtOrder().mian_smt_order,  # 单独SMT下单
                'goods_giveaudit': pcba_order.PcbaOrder().run_pcba_order,  # PCBA下单
                'goods_add_giveaudit': erp_smt_order_cancellation.ErpSmtOrderCancellation().mian_erp_smtorder_run,
                'goods_audit': queryExpress.queryExpress().express_sort_run,
                'goods_giveaudit_audit': HQPCBA_Admin_cancellation.HQCPCBAdminCancellation().admin_cancellation_RCV_AOI_run,
                'goods_add_audit': HQPCBA_Admin_cancellation.HQCPCBAdminCancellation().admin_cancellation_RCV_DIP_run,

                }
        dict[type]() if params is None else dict[type](params)
if __name__ == '__main__':
    """
    'goods_add': 资料新建，只要改一下配置文件里面的Conf→account_conf_yaml.PassPort.name\phone\pwd
    'goods_giveaudit': 资料提审
    'goods_add_giveaudit': 资料新建到提审
    'goods_audit': 资料审核
    'goods_giveaudit_audit': 资料提审到审核
    'goods_add_audit': 新建资料到审核完成
    如需切换环境，打开pcb_config.yaml配置文件，修改域名即可
    """