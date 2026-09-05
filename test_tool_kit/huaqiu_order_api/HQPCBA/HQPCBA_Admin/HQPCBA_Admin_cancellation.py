import json
import re
import time


import jsonpath
import yaml

from huaqiu_order_api.HQCHIP_ERP.erp_smt_order_cancellation import ErpSmtOrderCancellation
from huaqiu_order_api.HQCHIP_SCM.sorting.queryExpress import queryExpress
from huaqiu_order_api.HQCHIP_SOO.login import SOOLogin
from huaqiu_order_api.HQSMT.HQMES_new.PCBA_mes_PDA_H5.newmes_smt_order_pda_cancenllation import \
    NewMesSmtOrderPdaCancenllation
from huaqiu_order_api.HQSMT.HQMES_new.newmes_smt_order_cancellation import NewMesSmtOrderCancellation
from huaqiu_order_api.HQSMT.SMT_Reception.SMT_order import SmtOrder
from huaqiu_order_api.common.my_data import Data


class HQCPCBAdminCancellation:
    def __init__(self):
        """
        :param order_sn SMT—生产订单号字典， {"order_sn": "", "product_sn": ""} 字典字段非必填
        :param order_sn SMT订单号
        :param product_sn MES系统的生产单号
        """

    def order_sn_product_sn_dict(self, order_product_sn_dict=None):
        if order_product_sn_dict != None and isinstance(order_product_sn_dict, dict):
            if "order_sn" in order_product_sn_dict:
                self.order_sn = order_product_sn_dict["order_sn"]
            if "product_sn" in order_product_sn_dict:
                self.product_sn = order_product_sn_dict["product_sn"]
        elif order_product_sn_dict != None and isinstance(order_product_sn_dict, str):
            if "TK" in order_product_sn_dict:
                self.order_sn = order_product_sn_dict
                setattr(Data, 'smt_order_sn', self.order_sn)
            elif "H" in order_product_sn_dict:
                self.product_sn = order_product_sn_dict

    def admin_cancellation_RCV_AOI_run(self, order_product_sn_dict=None):
        """pcbames_RCV_AOI"""
        self.order_sn_product_sn_dict(order_product_sn_dict=order_product_sn_dict)
        pcbames_rss = SOOLogin(system_name="pcbames").target_login()
        # MES后台操作切换仓库、获取cookie
        NewMesSmtOrderCancellation(rss=pcbames_rss).choose_factory().smt_order_list()
        # PDA操作订单收料、生产发料、备料操作
        NewMesSmtOrderPdaCancenllation(pcbames_rss).mian_smt_pda_h5_produce()
        # MES后台操作计划排产
        NewMesSmtOrderCancellation(rss=pcbames_rss).patch_plan()
        # PDA操作贴片操作
        NewMesSmtOrderPdaCancenllation(pcbames_rss).mian_smt_pda_h5_patch()
        # MES后台操作首件送检、首件检验、样板确认、AOI检验
        NewMesSmtOrderCancellation(rss=pcbames_rss).first_inspect().customers_sample_confirm().AOI_inspect()
        return self

    def admin_cancellation_RCV_DIP_run(self, order_product_sn_dict=None):
        """pcbames_RCV_DIP"""
        self.order_sn_product_sn_dict(order_product_sn_dict=order_product_sn_dict)
        pcbames_rss = SOOLogin(system_name="pcbames").target_login()
        # MES后台操作切换仓库、获取cookie
        NewMesSmtOrderCancellation(rss=pcbames_rss).choose_factory().smt_order_list()
        # PDA操作订单收料、生产发料、备料操作
        NewMesSmtOrderPdaCancenllation(pcbames_rss).mian_smt_pda_h5_produce()
        # MES后台操作计划排产
        NewMesSmtOrderCancellation(rss=pcbames_rss).patch_plan()
        # PDA操作贴片操作
        NewMesSmtOrderPdaCancenllation(pcbames_rss).mian_smt_pda_h5_patch()
        # MES后台操作首件送检、首件检验、样板确认、AOI检验、DIP排产
        NewMesSmtOrderCancellation(rss=pcbames_rss).first_inspect().customers_sample_confirm().AOI_inspect().patch_plan(plan_type="weld")
        # PDA操作SMT过数DIP、DIP操作、DIP过数QA
        NewMesSmtOrderPdaCancenllation(pcbames_rss).mian_smt_pda_h5_DIP()
        return self
    def admin_cancellation_RCV_QA_run(self, order_product_sn_dict=None):
        """pcbames_RCV_QA"""
        self.order_sn_product_sn_dict(order_product_sn_dict=order_product_sn_dict)
        pcbames_rss = SOOLogin(system_name="pcbames").target_login()
        # MES后台操作切换仓库、获取cookie
        NewMesSmtOrderCancellation(rss=pcbames_rss).choose_factory().smt_order_list()
        # PDA操作订单收料、生产发料、备料操作
        NewMesSmtOrderPdaCancenllation(pcbames_rss).mian_smt_pda_h5_produce()
        # MES后台操作计划排产
        NewMesSmtOrderCancellation(rss=pcbames_rss).patch_plan()
        # PDA操作贴片操作
        NewMesSmtOrderPdaCancenllation(pcbames_rss).mian_smt_pda_h5_patch()
        # MES后台操作首件送检、首件检验、样板确认、AOI检验、DIP排产
        NewMesSmtOrderCancellation(rss=pcbames_rss).first_inspect().customers_sample_confirm().AOI_inspect().patch_plan(plan_type="weld")
        # PDA操作SMT过数DIP、DIP操作、DIP过数QA
        NewMesSmtOrderPdaCancenllation(pcbames_rss).mian_smt_pda_h5_DIP()
        # MES后台操作QA检验
        NewMesSmtOrderCancellation(rss=pcbames_rss).QA_inspect()
        return self
    def admin_cancellation_RCV_INN_run(self , order_product_sn_dict=None):
        """pcbames_RCV_INN"""
        self.order_sn_product_sn_dict(order_product_sn_dict=order_product_sn_dict)
        pcbames_rss = SOOLogin(system_name="pcbames").target_login()
        # MES后台操作切换仓库、获取cookie
        NewMesSmtOrderCancellation(rss=pcbames_rss).choose_factory().smt_order_list()
        # PDA操作订单收料、生产发料、备料操作
        NewMesSmtOrderPdaCancenllation(pcbames_rss).mian_smt_pda_h5_produce()
        # MES后台操作计划排产
        NewMesSmtOrderCancellation(rss=pcbames_rss).patch_plan()
        # PDA操作贴片操作
        NewMesSmtOrderPdaCancenllation(pcbames_rss).mian_smt_pda_h5_patch()
        # MES后台操作首件送检、首件检验、样板确认、AOI检验、DIP排产
        NewMesSmtOrderCancellation(rss=pcbames_rss).first_inspect().customers_sample_confirm().AOI_inspect().patch_plan(plan_type="weld")
        # PDA操作SMT过数DIP、DIP操作、DIP过数QA
        NewMesSmtOrderPdaCancenllation(pcbames_rss).mian_smt_pda_h5_DIP()
        # MES后台操作QA检验、包装扫描
        NewMesSmtOrderCancellation(rss=pcbames_rss).QA_inspect().pack_scan()
        # PDA操作成品入库
        NewMesSmtOrderPdaCancenllation(pcbames_rss).product_storage()

        return self

    def admin_cancellation_RCV_DEL_run(self, order_product_sn_dict=None):
        """pcbames_RCV_DEL"""
        self.order_sn_product_sn_dict(order_product_sn_dict=order_product_sn_dict)
        pcbames_rss = SOOLogin(system_name="pcbames").target_login()
        # MES后台操作切换仓库、获取cookie
        NewMesSmtOrderCancellation(rss=pcbames_rss).choose_factory().smt_order_list()
        # PDA操作订单收料、生产发料、备料操作
        NewMesSmtOrderPdaCancenllation(pcbames_rss).mian_smt_pda_h5_produce()
        # MES后台操作计划排产
        NewMesSmtOrderCancellation(rss=pcbames_rss).patch_plan()
        # PDA操作贴片操作
        NewMesSmtOrderPdaCancenllation(pcbames_rss).mian_smt_pda_h5_patch()
        # MES后台操作首件送检、首件检验、样板确认、AOI检验、DIP排产
        NewMesSmtOrderCancellation(rss=pcbames_rss).first_inspect().customers_sample_confirm().AOI_inspect().patch_plan(plan_type="weld")
        # PDA操作SMT过数DIP、DIP操作、DIP过数QA
        NewMesSmtOrderPdaCancenllation(pcbames_rss).mian_smt_pda_h5_DIP()
        # MES后台操作QA检验、包装扫描
        NewMesSmtOrderCancellation(rss=pcbames_rss).QA_inspect().pack_scan()
        # PDA操作成品入库
        NewMesSmtOrderPdaCancenllation(pcbames_rss).product_storage()
        # MES后台操作订单发货
        NewMesSmtOrderCancellation(rss=pcbames_rss).smt_order_delivery()
        return self
    def smt_admin_pcbmes_run(self, order_product_sn_dict=None):
        """smt_erp_pcbames"""
        rss, smt_order_sn, bom_order_sn = SmtOrder().mian_smt_order()
        express_delivery_no = ErpSmtOrderCancellation().mian_erp_smtorder_run(smt_order_sn)
        queryExpress().express_sort_run(express_delivery_no)
        HQCPCBAdminCancellation().admin_cancellation_RCV_DEL_run(smt_order_sn)


if __name__ == '__main__':
    HQCPCBAdminCancellation().smt_admin_pcbmes_run()


