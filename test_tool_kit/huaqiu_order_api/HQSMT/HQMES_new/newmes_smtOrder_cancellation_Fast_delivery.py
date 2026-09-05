import json
import time
from datetime import datetime, timedelta

import yaml

from huaqiu_order_api.HQCHIP_ERP.erp_smt_order_cancellation import ErpSmtOrderCancellation
from huaqiu_order_api.HQCHIP_SOO.login import SOOLogin
from huaqiu_order_api.HQSMT.HQMES_new.PCBA_mes_PDA_H5.newmes_smt_order_pda_cancenllation import \
    NewMesSmtOrderPdaCancenllation
from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_data import Data
from huaqiu_order_api.common.my_path import yaml_file



class NewMesSmtOrderCancellationFastDelivery:
    # 新的mes流程---快速发货

    def __init__(self, rss):
        self.newpcbames_rss = rss
        self.json_head = {"Content-Type": "application/json"}
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.PCBA_MES_NEW_URL = data["PCBA_MES_NEW_URL"]
        self.smt_order = getattr(Data, 'smt_order_sn', '')



    def choose_factory(self):
        """切换工厂"""
        choose_factory_url = "{}/pcbames/web/permission/chooseFactory".format(self.PCBA_MES_NEW_URL)
        choose_factory_body = {"body": {"factoryCode": "CSHQ", "factoryName": "湖南华秋-望城厂区", "grade": 2, "id": 2, "shortName": "长沙华秋"}}
        choose_factory_res = self.newpcbames_rss.post(url=choose_factory_url, json=choose_factory_body, headers=self.json_head).json()
        # logger.info(choose_factory_res)
        self.json_head["factoryCode"] = "CSHQ"
        return self
    def smt_order_bom_list(self):
        """产品bom"""
        order_list_url = "{}/pcbames/web/stationProduct/pageList".format(self.PCBA_MES_NEW_URL)
        order_list_body = {"body": {"productName": self.smt_order}, "header": {"pageNum": 1, "pageSize": 200}}
        order_list_res = self.newpcbames_rss.post(url=order_list_url, json=order_list_body,headers=self.json_head).json()
        self.order_no = order_list_res["body"][0]["orderNo"]
        logger.info(f"获取到订单号：{self.smt_order}的生产单号：{self.order_no}")
        # 将获取的self.order_no往Data里面作虚拟存储以【order_no】命名以便后续提取
        setattr(Data, 'order_no', self.order_no)
        return self

    def smt_order_detail(self):
        # 订单详情
        order_list_url = "{}/pcbames/web/order/pageList".format(self.PCBA_MES_NEW_URL)
        order_list_body = {"body": {"customerOrderId": self.smt_order}, "header": {"pageNum": 1, "pageSize": 200}}
        order_list_res = self.newpcbames_rss.post(url=order_list_url, json=order_list_body,headers=self.json_head).json()
        self.order_id = order_list_res["body"][0]["id"]
        logger.info(f"获取到订单号：{self.smt_order}的订单ID：{self.order_id}")

        order_detail_url = "{}/pcbames/web/order/info".format(self.PCBA_MES_NEW_URL)
        order_detail_body = {"body": self.order_id}
        order_detail_res = self.newpcbames_rss.post(url=order_detail_url, json=order_detail_body,headers=self.json_head).json()
        self.boardFace = order_detail_res["body"]["orderProductVO"]["boardFace"]
        self.boardFaceName = order_detail_res["body"]["orderProductVO"]["boardFaceName"]
        if self.boardFace == 1:
            sett_process_circuit_url = "{}/pcbames/web/order/configLine".format(self.PCBA_MES_NEW_URL)
            sett_process_circuit_body = {"lineId": 32, "orderId": self.order_id, "orderBoardNum": ""}
            sett_process_circuit_res = self.newpcbames_rss.post(url=sett_process_circuit_url, json=sett_process_circuit_body, headers=self.json_head).json()
            print(sett_process_circuit_res)
        logger.info(f"获取到订单号：{self.smt_order}的加工信息里面单/双面类型为：{self.boardFaceName}")
        return self
    def patch_plan(self):
        """计划排产"""
        # self.json_head["factoryCode"] = "CSHQ"
        # self.order_no = "H20230714302938"
        now_time = str((datetime.now()).strftime("%Y-%m-%d %H:%M:%S"))
        logger.info(f"获取当前时间：{now_time}")
        now_time_five_minutes = str((datetime.now() + timedelta(minutes=5)).strftime("%Y-%m-%d %H:%M:%S"))
        logger.info(f"获取当前时间5分钟后的时间：{now_time_five_minutes}")
        # self.smt_order_list()

        patch_plan_list_url = "{}/pcbames/web/patchPlan/pageList".format(self.PCBA_MES_NEW_URL)
        patch_plan_list_body = {"body":
                                        {"keyword": self.order_no, "date": "", "lastStationCodes": [], "lineId": "", "materialStatus": "",
                                        "planEndTime": "", "planStartTime": "","planStatus": "", "salesman": "", "schedulingStatus": ""
                                        },
                                "header": {"pageNum": 1, "pageSize": 20}
                                }
        patch_plan_list_res = self.newpcbames_rss.post(url=patch_plan_list_url, json=patch_plan_list_body,headers=self.json_head).json()

        # logger.info(patch_plan_list_res)
        batchUpdate_body = patch_plan_list_res["body"]
        logger.info(batchUpdate_body)
        num = batchUpdate_body[0]["num"]
        batchUpdate_body[0]["schedulingStatusName"] = "可排产"
        batchUpdate_body[0]["lineId"] = "17"
        batchUpdate_body[0]["lineName"] = "SMT3-1"
        batchUpdate_body[0]["modelCode"] = "CP12PP&JTF+CP12PP"
        batchUpdate_body[0]["planSortName"] = "普通"
        batchUpdate_body[0]["patchPlanStartTime"] = now_time
        batchUpdate_body[0]["patchPlanEndTime"] = now_time_five_minutes
        batchUpdate_body[0]["sort"] = "1"
        batch_update_url = "{}/pcbames/web/patchPlan/batchUpdate".format(self.PCBA_MES_NEW_URL)
        logger.info(batchUpdate_body)
        batch_update_body = {"body": batchUpdate_body}
        batch_update_res1 = self.newpcbames_rss.post(url=batch_update_url, json=batch_update_body,headers=self.json_head).json()
        patch_plan_list1_url = "{}/pcbames/web/patchPlan/pageList".format(self.PCBA_MES_NEW_URL)
        patch_plan_list1_body = {"body":
                                        {"keyword": self.order_no, "date": "", "lastStationCodes": [], "lineId": "", "materialStatus": "",
                                        "planEndTime": "", "planStartTime": "","planStatus": "", "salesman": "", "schedulingStatus": 3
                                        },
                                "header": {"pageNum": 1, "pageSize": 20}
                                }
        patch_plan_list1_res = self.newpcbames_rss.post(url=patch_plan_list1_url, json=patch_plan_list1_body,headers=self.json_head).json()
        batchUpdate_body2 = patch_plan_list1_res["body"]
        batch_update_body2 = {"body": batchUpdate_body2}
        batch_update_res2 = self.newpcbames_rss.post(url=batch_update_url, json=batch_update_body2,headers=self.json_head).json()
        suc = batch_update_res2["suc"]
        if suc == True:
            logger.info(f"订单：{self.smt_order}已排产")
        return self