import json
import re
import time

import jsonpath
import yaml

from huaqiu_order_api.HQCHIP_Center.user_center import get_address, get_ic_userId
from huaqiu_order_api.HQPCB.PCB_Reception.PCB_order import PCBOrder
from huaqiu_order_api.HQSMT.SMT_Reception.SMT_order import SmtOrder
from huaqiu_order_api.SSO_Reception.sso_reception import SSO_Reception
from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_data import Data
from huaqiu_order_api.common.my_path import stockup_dir, smt_yansuo_dir, bom_dir, yaml_file, account_yaml


class PcbaOrder:
    def __init__(self, pcb_bom_smt_dict=None):
        if pcb_bom_smt_dict is not None and isinstance(pcb_bom_smt_dict, dict):
            if 'pcb_bom_sn_dict' in pcb_bom_smt_dict:
                self.pcb_bom_sn_dict = pcb_bom_smt_dict['pcb_bom_sn_dict']
            else:
                self.pcb_bom_sn_dict = None
            if 'smt_order_id' in pcb_bom_smt_dict:
                self.smt_order_id = pcb_bom_smt_dict['smt_order_id']
            else:
                self.smt_order_id = None
            if 'dict_obj' in pcb_bom_smt_dict:
                self.dict_obj = pcb_bom_smt_dict['dict_obj']
            else:
                self.dict_obj = None
        else:
            self.pcb_bom_sn_dict = None
            # self.smt_order_id = None
            self.dict_obj = None


    def run_pcba_order(self):
        print(self.pcb_bom_sn_dict)
        rss, smt_order_sn, bom_order_sn = SmtOrder(pcb_bom_sn_dict=self.pcb_bom_sn_dict).mian_smt_order()
        self.smt_order_id = getattr(Data, 'smt_order_id', '')
        pcborderId = PCBOrder(rss, self.smt_order_id, self.dict_obj).run_pcb_order()
        print({"smt_order_sn": smt_order_sn, "bom_order_sn": bom_order_sn, "pcborderId": pcborderId, "msg": "PCBA订单生成成功"})
        return {"smt_order_sn": smt_order_sn, "bom_order_sn": bom_order_sn, "pcborderId": pcborderId, "msg": "PCBA订单生成成功"}