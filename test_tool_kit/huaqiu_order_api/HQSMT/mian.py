import yaml

from huaqiu_order_api.HQCHIP_ERP.erp_smt_order_cancellation import ErpSmtOrderCancellation
from huaqiu_order_api.HQCHIP_ERP.login import ErpLogin
from huaqiu_order_api.HQCHIP_SOO.login import SOOLogin
from huaqiu_order_api.HQSMT.HQMES_new.newmes_smt_order_cancellation import NewMesSmtOrderCancellation
from huaqiu_order_api.HQSMT.HQMES_old.oldmes_smt_order_cancellation import OldMesSmtOrderCancellation
from huaqiu_order_api.HQSMT.SMT_Reception.SMT_order import SmtOrder
from huaqiu_order_api.SSO_Reception.sso_reception import SSO_Reception
from huaqiu_order_api.common.my_path import account_yaml


class RunSmt:
    def main_new(self):
        # 前台单点登录
        SSO_rss = SSO_Reception('https://uat-smt.hqchip.com').login()
        # 前台提交SMT订单
        SmtOrder(SSO_rss).smt_tmp_save().place_an_order()
        # ERP-SMT订单处理
        erp_rss = ErpLogin().login()
        ErpSmtOrderCancellation(erp_rss).erp_smt_order_cancellation()
        # PCBA-MES系统登录
        SOO_target_rss = SOOLogin("uat-pcbames.hqchip.com", "pcbames").target_login()
        # PCBA - MES系统, SMT处理
        NewMesSmtOrderCancellation(SOO_target_rss).mian_smt_order()

    def main_old(self):
        # 前台单点登录
        SSO_rss, token = SSO_Reception('https://uat-smt.hqchip.com').login()
        # 前台提交SMT订单
        order_sn = SmtOrder(SSO_rss).smt_tmp_save().place_an_order()
        # ERP-SMT订单处理
        erp_rss = ErpLogin().login()
        ErpSmtOrderCancellation(erp_rss).erp_smt_order_cancellation()
        # 老PCBA-MES系统处理
        OldMesSmtOrderCancellation(order_sn).main_old_mes_delivery()


    def main(self):
        with open(account_yaml, 'r', encoding='utf-8') as yamlfile:
            account = yaml.load(yamlfile, Loader=yaml.FullLoader)
        factory_updata = account["HQCHIP_ERP"]["factory_updata"]

        # factory_updata = 1  流程走老mes流程
        if factory_updata != 1:
            self.main_new()
        else:
            self.main_old()

if __name__ == '__main__':
    RunSmt().main()