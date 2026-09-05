import json
import time

import jsonpath
import requests
import yaml

from huaqiu_order_api.HQCHIP_SOO.login import SOOLogin


from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_data import Data
from huaqiu_order_api.common.my_path import yaml_file



class NewMesSmtOrderPdaCancenllation:
    def __init__(self, rss):
        # 从Data里面提取 order_no
        self.containerNo = getattr(Data, 'containerNo', None)
        self.orderNo = getattr(Data, 'order_no', None)
        # self.num = num
        self.pcbames_pda_rss = rss
        self.json_head = {"factoryCode": "CSHQ", "Content-Type": "application/json"}
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.PCBA_MES_NEW_URL = data["PCBA_MES_NEW_URL"]

    def product_storage(self):
        logger.info("开始处理成品入库")
        # 从Data里面提取containerNo
        product_storage_url = "{}/pcbames/web/orderProdInStock/putProdInStock".format(self.PCBA_MES_NEW_URL)
        product_storage_body = {"body": {"labelCode": self.containerNo, "waCode": "C01", "warehouseCode": "CSCP"}}
        product_storage_res = self.pcbames_pda_rss.post(url=product_storage_url, data=json.dumps(product_storage_body), headers=self.json_head).json()
        logger.info(product_storage_res)
        labelCode = product_storage_res["body"]["labelCode"]
        if labelCode == self.containerNo:
            logger.info("成品入库操作成功")
        return self
    def produce_receipt(self):
        """生产收料"""
        logger.info("开始处理生产收料")
        produce_receipt_search_url = "{}/pcbames/web/issuance/getReceiveDataByOrderNo/public".format(self.PCBA_MES_NEW_URL)
        produce_receipt_search_body = {"body": {"orderNo": self.orderNo}}
        produce_receipt_search_res = self.pcbames_pda_rss.post(url=produce_receipt_search_url, json=produce_receipt_search_body, headers=self.json_head).json()
        productName = produce_receipt_search_res["body"]["productName"]
        materialList = produce_receipt_search_res["body"]["materialList"]

        produce_receipt_url = "{}/pcbames/web/issuance/receiveAll".format(self.PCBA_MES_NEW_URL)
        produce_receipt_body = {"body": {"orderNo": self.orderNo, "productName": productName, "remark": "", "materialList": materialList}}
        n = 0
        while True:
            try:
                produce_receipt_res = self.pcbames_pda_rss.post(url=produce_receipt_url, json=produce_receipt_body, headers=self.json_head).json()
                suc = produce_receipt_res["suc"]
                if suc == True:
                    logger.info(f"第{n + 1}次订单：{self.orderNo}生产收料成功")
                    break
            except Exception as e:
                n += 1
                if n < 6:
                    logger.info(f"第{n + 1}次订单：{self.orderNo}生产收料失败，等待30s后重试生产收料，报错信息为：{e}")
                    time.sleep(30)
                else:
                    logger.error(
                        f"订单：{self.orderNo}生产收料失败,请手动检查订单生产收料情况")
                    raise ValueError
        return self

    def produce_issuance(self):
        """生产发料"""
        logger.info("开始处理生产发料")
        produce_issuance_search_url = "{}/pcbames/web/issuance/getIssuanceDataByOrderNo/public".format(self.PCBA_MES_NEW_URL)
        produce_issuance_search_body = {"body": {"orderNo": self.orderNo}}
        produce_issuance_search_res = self.pcbames_pda_rss.post(url=produce_issuance_search_url, json=produce_issuance_search_body, headers=self.json_head).json()
        print(produce_issuance_search_res)
        productName = produce_issuance_search_res["body"]["productName"]
        materialList = produce_issuance_search_res["body"]["materialList"]
        produce_receipt_url = "{}/pcbames/web/issuance/issuanceAll".format(self.PCBA_MES_NEW_URL)
        produce_receipt_body = {"body": {"orderNo": self.orderNo, "productName": productName, "remark": "", "materialList": materialList}}
        produce_receipt_res = self.pcbames_pda_rss.post(url=produce_receipt_url, json=produce_receipt_body, headers=self.json_head).json()
        suc = produce_receipt_res["suc"]
        if suc == True:
            logger.info("生产发料成功")
        return self
    def materials_operate(self):
        """备料操作"""
        logger.info("开始处理备料操作")
        # 作业人员
        employee_info_url = "{}/pcbames/web/employee/info/public".format(self.PCBA_MES_NEW_URL)
        employee_info_body = {"body": {"name": "liaopeng"}}
        employee_info_res = self.pcbames_pda_rss.post(url=employee_info_url, json=employee_info_body, headers=self.json_head).json()
        self.employeeId = employee_info_res["body"]["id"]
        self.employeeName = employee_info_res["body"]["empName"]

        materials_operate_search_url = "{}/pcbames/web/product/getOrderInfo/public".format(self.PCBA_MES_NEW_URL)
        materials_operate_search_body = {"body": {"orderNo": self.orderNo}}
        materials_operate_search_res = self.pcbames_pda_rss.post(url=materials_operate_search_url, json=materials_operate_search_body, headers=self.json_head).json()

        # 开始备料
        materials_operate_url = "{}/pcbames/web/materialPrepare/operate/public".format(self.PCBA_MES_NEW_URL)
        materials_operate_start_body = {"body": {"employeeId": self.employeeId, "orderNo": self.orderNo, "userName": self.employeeName, "type": 1}}
        materials_operate_start_res = self.pcbames_pda_rss.post(url=materials_operate_url, json=materials_operate_start_body, headers=self.json_head).json()
        logger.info(f"执行开始备料已完成，返回结果：{materials_operate_start_res}")

        # 结束备料
        materials_operate_end_body = {"body": {"employeeId": self.employeeId, "orderNo": self.orderNo, "userName": self.employeeName, "type": 2}}
        materials_operate_end_res = self.pcbames_pda_rss.post(url=materials_operate_url, json=materials_operate_end_body, headers=self.json_head).json()
        logger.info(f"执行结束备料已完成，返回结果：{materials_operate_end_res}")
        return self

    def patch_operate(self):
        """贴片操作"""
        self.boardFaceName = getattr(Data, 'boardFaceName')
        logger.info("开始处理贴片操作")
        # 作业人员
        employee_info_url = "{}/pcbames/web/employee/info/public".format(self.PCBA_MES_NEW_URL)
        employee_info_body = {"body": {"name": "liaopeng"}}
        employee_info_res = self.pcbames_pda_rss.post(url=employee_info_url, json=employee_info_body, headers=self.json_head).json()
        self.employeeId = employee_info_res["body"]["id"]
        self.employeeName = employee_info_res["body"]["empName"]
        # 订单信息
        patch_operate_start_search_url = "{}/pcbames/web/product/getOrderInfo/public".format(self.PCBA_MES_NEW_URL)
        patch_operate_start_search_body = {"body": {"orderNo": self.orderNo}}
        patch_operate_start_search_res = self.pcbames_pda_rss.post(url=patch_operate_start_search_url, json=patch_operate_start_search_body, headers=self.json_head).json()
        self.orderId = patch_operate_start_search_res["body"]["orderId"]
        self.orderNumber = patch_operate_start_search_res["body"]["orderNumber"]
        # 排产信息
        patch_plan_serch_url = "{}/pcbames/web/patchPlan/getWaitPatchPlanByOrderId/public".format(self.PCBA_MES_NEW_URL)
        patch_plan_serch_body = {"body": self.orderId}
        patch_plan_serch_res = self.pcbames_pda_rss.post(url=patch_plan_serch_url, json=patch_plan_serch_body, headers=self.json_head).json()
        patch_plan_id = patch_plan_serch_res["body"][0]["id"]
        line_id_start = patch_plan_serch_res["body"][0]["lineId"]
        line_name_start = patch_plan_serch_res["body"][0]["lineName"]


        if self.boardFaceName == "T面" :
            # 开始贴片-T面
            patch_operate_start_url = "{}/pcbames/web/product/startPatch".format(self.PCBA_MES_NEW_URL)
            patch_operate_start_body = {"body": {"employeeId": self.employeeId, "orderId": self.orderId, "userName": self.employeeName, "operCode": "KSTP-T", "isChangeLine": 0,
                                                 "productNumber": self.orderNumber, "lineId": line_id_start, "lineName": line_name_start, "patchPlanId": patch_plan_id}}
            patch_operate_start_res = self.pcbames_pda_rss.post(url=patch_operate_start_url, json=patch_operate_start_body, headers=self.json_head).json()
            logger.info(f"执行开始贴片已完成，返回结果：{patch_operate_start_res}")

            # self.boardFaceName对应的面类型id
            patch_operate_end_search_url = "{}/pcbames/web/product/getOrderInfo/public".format(self.PCBA_MES_NEW_URL)
            patch_operate_end_search_body = {"body": {"orderNo": self.orderNo, "operCode": "WCTP"}}
            patch_operate_end_search_res = self.pcbames_pda_rss.post(url=patch_operate_end_search_url, json=patch_operate_end_search_body, headers=self.json_head).json()
            self.boardFace = patch_operate_end_search_res["body"]["boardFace"]

            # 选择工序查找
            lineId_end_url = "{}/pcbames/web/product/finishLineList/public".format(self.PCBA_MES_NEW_URL)
            lineId_end_body = {"body": {"orderId": self.orderId, "operCode": "WCTP-T", "planId": patch_plan_id}}
            lineId_end_res = self.pcbames_pda_rss.post(url=lineId_end_url, json=lineId_end_body, headers=self.json_head).json()
            self.lineId_end = lineId_end_res["body"][0]["lineId"]
            self.lineName_end = lineId_end_res["body"][0]["lineName"]
            # 结束贴片- T面
            patch_operate_end_url = "{}/pcbames/web/product/finishPatch".format(self.PCBA_MES_NEW_URL)
            patch_operate_end_body = {"body": {"employeeId": self.employeeId, "orderId": self.orderId, "userName": self.employeeName, "operCode": "WCTP-T", "logId": "",
                                                   "productNumber": self.orderNumber, "lineId": self.lineId_end, "boardFace": self.boardFace, "productPerson": 1,
                                               "patchPlanId": patch_plan_id, "workHour": "1", "remark": "自动化测试"
                                                   }}
            patch_operate_end_res = self.pcbames_pda_rss.post(url=patch_operate_end_url, json=patch_operate_end_body, headers=self.json_head).json()
            logger.info(f"执行结束贴片已完成，返回结果：{patch_operate_end_res}")
        elif self.boardFaceName == "B面":
            # 开始贴片-B面
            patch_operate_start_url = "{}/pcbames/web/product/startPatch".format(self.PCBA_MES_NEW_URL)
            patch_operate_start_body = {"body": {"employeeId": self.employeeId, "orderId": self.orderId, "userName": self.employeeName, "operCode": "KSTP-B", "isChangeLine": 0,
                                                 "productNumber": self.orderNumber, "lineId": line_id_start, "lineName": line_name_start, "patchPlanId": patch_plan_id}}
            patch_operate_start_res = self.pcbames_pda_rss.post(url=patch_operate_start_url, json=patch_operate_start_body, headers=self.json_head).json()
            logger.info(f"执行开始贴片已完成，返回结果：{patch_operate_start_res}")

            # self.boardFaceName对应的面类型id
            patch_operate_end_search_url = "{}/pcbames/web/product/getOrderInfo/public".format(self.PCBA_MES_NEW_URL)
            patch_operate_end_search_body = {"body": {"orderNo": self.orderNo, "operCode": "WCTP"}}
            patch_operate_end_search_res = self.pcbames_pda_rss.post(url=patch_operate_end_search_url, json=patch_operate_end_search_body, headers=self.json_head).json()
            self.boardFace = patch_operate_end_search_res["body"]["boardFace"]

            # 选择工序查找
            lineId_end_url = "{}/pcbames/web/product/finishLineList/public".format(self.PCBA_MES_NEW_URL)
            lineId_end_body = {"body": {"orderId": self.orderId, "operCode": "WCTP-B", "planId": patch_plan_id}}
            lineId_end_res = self.pcbames_pda_rss.post(url=lineId_end_url, json=lineId_end_body, headers=self.json_head).json()
            self.lineId_end = lineId_end_res["body"][0]["lineId"]
            self.lineName_end = lineId_end_res["body"][0]["lineName"]
            # 结束贴片- B面
            patch_operate_end_url = "{}/pcbames/web/product/finishPatch".format(self.PCBA_MES_NEW_URL)
            patch_operate_end_body = {"body": {"employeeId": self.employeeId, "orderId": self.orderId, "userName": self.employeeName, "operCode": "WCTP-B", "logId": "",
                                                   "productNumber": self.orderNumber, "lineId": self.lineId_end, "boardFace": self.boardFace, "productPerson": 1,
                                               "patchPlanId": patch_plan_id, "workHour": "1", "remark": "自动化测试"
                                                   }}
            patch_operate_end_res = self.pcbames_pda_rss.post(url=patch_operate_end_url, json=patch_operate_end_body, headers=self.json_head).json()
            logger.info(f"执行结束贴片已完成，返回结果：{patch_operate_end_res}")
        else:
            # 开始贴片-T面
            patch_operate_start_url = "{}/pcbames/web/product/startPatch".format(self.PCBA_MES_NEW_URL)
            patch_operate_start_body = {"body": {"employeeId": self.employeeId, "orderId": self.orderId, "userName": self.employeeName, "operCode": "KSTP-T", "isChangeLine": 0,
                                                 "productNumber": self.orderNumber, "lineId": line_id_start, "lineName": line_name_start, "patchPlanId": patch_plan_id}}
            patch_operate_start_res = self.pcbames_pda_rss.post(url=patch_operate_start_url, json=patch_operate_start_body, headers=self.json_head).json()
            logger.info(f"执行T面开始贴片已完成，返回结果：{patch_operate_start_res}")

            # self.boardFaceName对应的面类型id
            patch_operate_end_search_url = "{}/pcbames/web/product/getOrderInfo/public".format(self.PCBA_MES_NEW_URL)
            patch_operate_end_search_body = {"body": {"orderNo": self.orderNo, "operCode": "WCTP"}}
            patch_operate_end_search_res = self.pcbames_pda_rss.post(url=patch_operate_end_search_url, json=patch_operate_end_search_body, headers=self.json_head).json()
            self.boardFace = patch_operate_end_search_res["body"]["boardFace"]

            # 选择工序查找
            lineId_end_url = "{}/pcbames/web/product/finishLineList/public".format(self.PCBA_MES_NEW_URL)
            lineId_end_body = {"body": {"orderId": self.orderId, "operCode": "WCTP-T", "planId": patch_plan_id}}
            lineId_end_res = self.pcbames_pda_rss.post(url=lineId_end_url, json=lineId_end_body, headers=self.json_head).json()
            self.lineId_end = lineId_end_res["body"][0]["lineId"]
            self.lineName_end = lineId_end_res["body"][0]["lineName"]
            # 结束贴片- T面
            patch_operate_end_url = "{}/pcbames/web/product/finishPatch".format(self.PCBA_MES_NEW_URL)
            patch_operate_end_body = {"body": {"employeeId": self.employeeId, "orderId": self.orderId, "userName": self.employeeName, "operCode": "WCTP-T", "logId": "",
                                                   "productNumber": self.orderNumber, "lineId": self.lineId_end, "boardFace": self.boardFace, "productPerson": 1,
                                               "patchPlanId": patch_plan_id, "workHour": "1", "remark": "自动化测试"
                                                   }}
            patch_operate_end_res = self.pcbames_pda_rss.post(url=patch_operate_end_url, json=patch_operate_end_body, headers=self.json_head).json()
            logger.info(f"执行T面结束贴片已完成，返回结果：{patch_operate_end_res}")

            # 开始贴片-B面
            patch_operate_start_url = "{}/pcbames/web/product/startPatch".format(self.PCBA_MES_NEW_URL)
            patch_operate_start_body = {"body": {"employeeId": self.employeeId, "orderId": self.orderId, "userName": self.employeeName, "operCode": "KSTP-B", "isChangeLine": 0,
                                                 "productNumber": self.orderNumber, "lineId": line_id_start, "lineName": line_name_start, "patchPlanId": patch_plan_id}}
            patch_operate_start_res = self.pcbames_pda_rss.post(url=patch_operate_start_url, json=patch_operate_start_body, headers=self.json_head).json()
            logger.info(f"执行B面开始贴片已完成，返回结果：{patch_operate_start_res}")

            # self.boardFaceName对应的面类型id
            patch_operate_end_search_url = "{}/pcbames/web/product/getOrderInfo/public".format(self.PCBA_MES_NEW_URL)
            patch_operate_end_search_body = {"body": {"orderNo": self.orderNo, "operCode": "WCTP"}}
            patch_operate_end_search_res = self.pcbames_pda_rss.post(url=patch_operate_end_search_url, json=patch_operate_end_search_body, headers=self.json_head).json()
            self.boardFace = patch_operate_end_search_res["body"]["boardFace"]

            # 选择工序查找
            lineId_end_url = "{}/pcbames/web/product/finishLineList/public".format(self.PCBA_MES_NEW_URL)
            lineId_end_body = {"body": {"orderId": self.orderId, "operCode": "WCTP-B", "planId": patch_plan_id}}
            lineId_end_res = self.pcbames_pda_rss.post(url=lineId_end_url, json=lineId_end_body, headers=self.json_head).json()
            self.lineId_end = lineId_end_res["body"][0]["lineId"]
            self.lineName_end = lineId_end_res["body"][0]["lineName"]
            # 结束贴片- B面
            patch_operate_end_url = "{}/pcbames/web/product/finishPatch".format(self.PCBA_MES_NEW_URL)
            patch_operate_end_body = {"body": {"employeeId": self.employeeId, "orderId": self.orderId, "userName": self.employeeName, "operCode": "WCTP-B", "logId": "",
                                                   "productNumber": self.orderNumber, "lineId": self.lineId_end, "boardFace": self.boardFace, "productPerson": 1,
                                               "patchPlanId": patch_plan_id, "workHour": "1", "remark": "自动化测试"
                                                   }}
            patch_operate_end_res = self.pcbames_pda_rss.post(url=patch_operate_end_url, json=patch_operate_end_body, headers=self.json_head).json()
            logger.info(f"执行B结束贴片已完成，返回结果：{patch_operate_end_res}")
        return self
    def process_passing(self, process_type=None):
        """
        工序过站
        ：param process_type SMT-DIP：SMT过数DIP、DIP-QA:DIP过数QA、SMT-QA:SMT过数QA
        """
        process_type_name_dict = {"SMT-DIP": "SMT过数DIP", "DIP-QA": "DIP过数QA", "SMT-QA": "SMT过数QA"}
        # 作业人员
        employee_info_url = "{}/pcbames/web/employee/info/public".format(self.PCBA_MES_NEW_URL)
        employee_info_body = {"body": {"name": "liaopeng"}}
        employee_info_res = self.pcbames_pda_rss.post(url=employee_info_url, json=employee_info_body, headers=self.json_head).json()
        self.employeeId = employee_info_res["body"]["id"]
        self.employeeName = employee_info_res["body"]["empName"]
        # 订单信息
        search_order_url = "{}/pcbames/web/product/getOrderInfo/public".format(self.PCBA_MES_NEW_URL)
        search_order_body = {"body": {"orderNo": self.orderNo}}
        search_order_res = self.pcbames_pda_rss.post(url=search_order_url, json=search_order_body, headers=self.json_head).json()
        self.orderId = search_order_res["body"]["orderId"]
        self.orderNumber = search_order_res["body"]["orderNumber"]
        # 提交
        process_passing_url = "{}/pcbames/web/product/passStation".format(self.PCBA_MES_NEW_URL)
        process_passing_body = {"body": {
                                    "orderId": self.orderId, "productNumber": self.orderNumber,
                                    "employeeId": self.employeeId, "userName": self.employeeName, "operCode": process_type}}
        process_passing_res = self.pcbames_pda_rss.post(url=process_passing_url, json=process_passing_body, headers=self.json_head).json()
        for i in process_type_name_dict:
            if process_type == i:
                logger.info(f"{process_type_name_dict[i]}操作已完成，返回结果：{process_passing_res}")
                break
    def DIP_operate(self):
        """DIP操作"""
        # DIP开始生产
        # 作业人员
        employee_info_url = "{}/pcbames/web/employee/info/public".format(self.PCBA_MES_NEW_URL)
        employee_info_body = {"body": {"name": "liaopeng"}}
        employee_info_res = self.pcbames_pda_rss.post(url=employee_info_url, json=employee_info_body, headers=self.json_head).json()
        self.employeeId = employee_info_res["body"]["id"]
        self.employeeName = employee_info_res["body"]["empName"]
        # 订单信息
        search_order_url = "{}/pcbames/web/product/getOrderInfo/public".format(self.PCBA_MES_NEW_URL)
        search_order_body = {"body": {"orderNo": self.orderNo}}
        search_order_res = self.pcbames_pda_rss.post(url=search_order_url, json=search_order_body, headers=self.json_head).json()
        self.orderId = search_order_res["body"]["orderId"]
        self.orderNumber = search_order_res["body"]["orderNumber"]

        # 获取DIP计划id、lineId、lineName
        dip_plan_url = "{}/pcbames/web/weldPlan/getWaitWeldPlanByOrderId/public".format(self.PCBA_MES_NEW_URL)
        dip_plan_body = {"body": self.orderId}
        dip_plan_res = self.pcbames_pda_rss.post(url=dip_plan_url, json=dip_plan_body, headers=self.json_head).json()
        self.dip_plan_id = dip_plan_res["body"][0]["id"]
        # 线体
        line_url = "{}/pcbames/web/line/enableListByProcedure/public".format(self.PCBA_MES_NEW_URL)
        line_body = {"body": 1}
        line_res = self.pcbames_pda_rss.post(url=line_url, json=line_body, headers=self.json_head).json()
        self.lineId = line_res["body"][0]["id"]
        lineName = line_res["body"][0]["lineName"]
        print(f"lineId: {self.lineId}")



        # 开始生产
        dip_operate_start_url = "{}/pcbames/web/product/startDip".format(self.PCBA_MES_NEW_URL)
        dip_operate_start_body = {"body": {"orderId": self.orderId, "productNumber": self.orderNumber, "userNumber": "1",
                                           "lineId": self.lineId,"lineName": lineName, "weldPlanId": self.dip_plan_id}}
        print(dip_operate_start_body)
        dip_operate_start_res = self.pcbames_pda_rss.post(url=dip_operate_start_url, json=dip_operate_start_body, headers=self.json_head).json()
        logger.info(f"执行DIP开始生产已完成，返回结果：{dip_operate_start_res}")

        # 完成生产
        dip_operate_end_url = "{}/pcbames/web/product/finishDip".format(self.PCBA_MES_NEW_URL)
        dip_operate_end_body = {"body": {"orderId": self.orderId,"productNumber": self.orderNumber,"lineId": self.lineId,
                                         "weldPlanId": self.dip_plan_id, "productPerson": "1","workHour": "1","remark": "1"}}
        dip_operate_end_res = self.pcbames_pda_rss.post(url=dip_operate_end_url, json=dip_operate_end_body, headers=self.json_head).json()
        logger.info(f"执行DIP结束生产已完成，返回结果：{dip_operate_end_res}")
        return self




    def mian_smt_pda_h5_produce(self):
        self.produce_receipt()
        self.produce_issuance()
        self.materials_operate()
        return self
    def mian_smt_pda_h5_patch(self):
        self.patch_operate()
        return self
    def mian_smt_pda_h5_DIP(self):
        self.posiCodeKey = getattr(Data, 'posiCodeKey')
        if self.posiCodeKey == 1:
            # 含有后焊 需经历SMT过数DIP、DIP开始生产、DIP结束生产、DIP过数QA
            self.process_passing("SMT-DIP")
            self.DIP_operate()
            self.process_passing("DIP-QA")
        elif self.posiCodeKey == 2:
            # SMT过数QA
            self.process_passing("SMT-QA")
        return self


if __name__ == '__main__':
    from huaqiu_order_api.HQSMT.HQMES_new.newmes_smt_order_cancellation import NewMesSmtOrderCancellation
    pcbames_rss = SOOLogin(system_name="pcbames").target_login()
    # MES后台操作切换仓库、获取cookie
    NewMesSmtOrderCancellation(rss=pcbames_rss).choose_factory()
    orderNo = "H20240827966468"
    containerNo = "BCSHQ202408260005"
    posiCodeKey = 1
    setattr(Data, 'posiCodeKey', posiCodeKey)
    setattr(Data, 'order_no', orderNo)
    setattr(Data, 'containerNo', containerNo)
    NewMesSmtOrderPdaCancenllation(pcbames_rss).mian_smt_pda_h5_produce()