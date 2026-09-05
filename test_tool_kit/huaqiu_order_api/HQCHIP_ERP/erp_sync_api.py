import re

import requests
import yaml
from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_data import Data
from huaqiu_order_api.common.my_path import yaml_file, account_yaml


class ErpSyncAPI:


    def __init__(self):
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.ERP_URL = data['ERP_URL']
        self.erp_rss = requests.session()
        self.headers = {'Content-Type': 'application/x-www-form-urlencoded',
                        "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://www.huaqiu.com)"
                        }
    def final_statement_sync(self, pbill_id=None):
        """ERP采购付款审批单-合作商结算单对接同步"""
        final_statement_sync_url = "{}/Service/PurchaseBillPay/updateSettleBillStatus".format(self.ERP_URL)
        final_statement_sync_body = {"pbill_id": pbill_id}
        final_statement_sync_res = self.erp_rss.post(url=final_statement_sync_url, json=final_statement_sync_body,
                                                     headers=self.headers).json()
        # print(final_statement_sync_res)
        return final_statement_sync_res

    def purchase_putpay_sync(self, picking_id=None):
        purchase_putpay_sync_url = "{}/Service/Purchase/putPay".format(self.ERP_URL)
        purchase_putpay_sync_body = {"picking_id": picking_id}
        purchase_putpay_sync_res = self.erp_rss.post(url=purchase_putpay_sync_url, json=purchase_putpay_sync_body,
                                                     headers=self.headers).json()
        return purchase_putpay_sync_res
    def convert_subject_sync(self, order_id=None):
        convert_subject_sync_url = "{}/Service/ConvertSubject/putConvertRemovalWms".format(self.ERP_URL)
        convert_subject_sync_body = {"order_id": order_id}
        convert_subject_sync_res = self.erp_rss.post(url=convert_subject_sync_url, json=convert_subject_sync_body,
                                                     headers=self.headers).json()
        return convert_subject_sync_res
    def removal_stockOut_dingTalk_push(self):
        """出库单齐料不足钉钉通知"""
        removal_stockOut_dingTalk_push_url = "{}/service/msg/fullMaterialRemovalNotify".format(self.ERP_URL)
        removal_stockOut_dingTalk_push_res = self.erp_rss.get(url=removal_stockOut_dingTalk_push_url).json()
        return removal_stockOut_dingTalk_push_res

    def scm_invoice_sync(self, invoice_id=None):
        """ERP发票推送SCM"""
        scm_invoice_sync_url = "{}/service/invoice/scmInvoice".format(self.ERP_URL)
        scm_invoice_sync_body = {"event": "financial.invoice.ic.invoiced", "sn": invoice_id, "unPush": 1}
        scm_invoice_sync_res = self.erp_rss.post(url=scm_invoice_sync_url, json=scm_invoice_sync_body,
                                                     headers=self.headers).json()
        return scm_invoice_sync_res
    def final_receivable_note_sync(self):
        """ERP推送应收单执行任务"""
        final_receivable_note_sync_url = "{}/api/checkOrderReceivablesLog" .format(self.ERP_URL)
        final_receivable_note_sync_res = self.erp_rss.get(url=final_receivable_note_sync_url, headers=self.headers).json()
        print(final_receivable_note_sync_res)
        return final_receivable_note_sync_res
    def revenue_cost_sync(self):
        """ERP推送SCM应收单并生成收入成本任务"""
        revenue_cost_sync_url = "{}/api/timingWaitScmRequest?debug=1".format(self.ERP_URL)
        revenue_cost_sync_res = self.erp_rss.post(url=revenue_cost_sync_url).json()
        return revenue_cost_sync_res
    def final_revenue_cost_sync(self):
        """ERP执行收入成本任务"""
        final_revenue_cost_sync_url ="{}/api/timingScmItemRequest?debug=1" .format(self.ERP_URL)
        final_revenue_cost_sync_res = self.erp_rss.get(url=final_revenue_cost_sync_url, headers=self.headers).json()
        print(final_revenue_cost_sync_res)
        return final_revenue_cost_sync_res

if __name__ == '__main__':
    # ErpSyncAPI().final_statement_sync(pbill_id=13)
    ErpSyncAPI().final_receivable_note_sync()
    ErpSyncAPI().final_revenue_cost_sync()
    ErpSyncAPI().revenue_cost_sync()
