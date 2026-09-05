import json
import time
from datetime import datetime, timedelta

import jsonpath
import requests

import yaml
from faker import Faker

from huaqiu_order_api.HQCHIP_ERP.erp_smt_order_cancellation import ErpSmtOrderCancellation
from huaqiu_order_api.HQCHIP_SOO.login import SOOLogin
from huaqiu_order_api.HQSMT.HQMES_new.PCBA_mes_PDA_H5.newmes_smt_order_pda_cancenllation import \
    NewMesSmtOrderPdaCancenllation
from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_data import Data
from huaqiu_order_api.common.my_path import yaml_file, PCBAMES_file_dir


class NewMesSmtOrderCancellation:
    # 新的mes流程
    def __init__(self, rss=None, order_sn=None, order_no=None):
        """

        """
        self.newpcbames_rss = rss
        self.json_head = {"Content-Type": "application/json"}
        self.form_headers = {"Content-Type": "multipart/form-data"}
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.PCBA_MES_NEW_URL = data["PCBA_MES_NEW_URL"]
        self.PCBA_MES_NEW_UPLOAD_URL = data["PCBA_MES_NEW_UPLOAD_URL"]
        self.smt_order = getattr(Data, 'smt_order_sn', '')
        self.order_no = getattr(Data, 'order_no', '')
        if order_sn != None:
            self.smt_order = order_sn
        if order_no != None:
            self.order_no = order_no




    def choose_factory(self) :
        """切换工厂"""
        choose_factory_url = "{}/pcbames/web/permission/chooseFactory".format(self.PCBA_MES_NEW_URL)
        choose_factory_body = {"body": {"factoryCode": "CSHQ", "factoryName": "湖南华秋-望城厂区", "grade": 2, "id": 2, "shortName": "长沙华秋"}}
        choose_factory_res = self.newpcbames_rss.post(url=choose_factory_url, json=choose_factory_body, headers=self.json_head).json()
        logger.info(f"切换工厂")
        # logger.info(choose_factory_res.cookies)
        self.json_head["factoryCode"] = "CSHQ"
        return self
    def smt_order_list(self):
        """订单管理"""
        self.json_head["factoryCode"] = "CSHQ"
        order_list_url = "{}/pcbames/web/order/pageList".format(self.PCBA_MES_NEW_URL)
        order_list_body = {"body": {"customerOrderId": self.smt_order}, "header": {"pageNum": 1, "pageSize": 200}}
        order_list_res = self.newpcbames_rss.post(url=order_list_url, json=order_list_body,headers=self.json_head).json()
        self.order_no = order_list_res["body"][0]["orderNo"]
        self.order_id= order_list_res["body"][0]["id"]
        logger.info(f"获取到订单号：{self.smt_order}的生产单号：{self.order_no}")
        # 将获取的self.order_no往Data里面作虚拟存储以【order_no】命名以便后续提取
        setattr(Data, 'order_no', self.order_no)
        setattr(Data, 'order_id', self.order_id)
        return self

    def smt_order_detail(self):
        # 订单详情
        self.json_head["factoryCode"] = "CSHQ"
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
            # print(sett_process_circuit_res)
        logger.info(f"获取到订单号：{self.smt_order}的加工信息里面单/双面类型为：{self.boardFaceName}")
        setattr(Data, 'boardFaceName', self.boardFaceName)
        return self

    def trigger_produce_confirm_file(self):
        """手动触发生成文件确认----局限测试范畴适用"""
        trigger_produce_confirm_url = "{}/pcbames/web/order/dispatch/public".format(self.PCBA_MES_NEW_URL)
        trigger_produce_confirm_body = {"header": {"pafeNum": 1, "pagesize": 20}, "body": {"orderNo": self.order_no, "eventCode": "MATERIAL_COMPLETE"}}
        trigger_produce_confirm_res = self.newpcbames_rss.post(url=trigger_produce_confirm_url, json=trigger_produce_confirm_body, headers=self.json_head).json()
        logger.info(f"执行结果为：{trigger_produce_confirm_res}")
        return self

    def patch_plan(self, plan_type=None):
        """计划排产"""
        self.json_head["factoryCode"] = "CSHQ"
        self.order_no = getattr(Data, 'order_no')
        logger.info(f"生产单号：{self.order_no}")
        now_time = str((datetime.now()).strftime("%Y-%m-%d %H:%M:%S"))
        logger.info(f"获取当前时间：{now_time}")
        now_time_five_minutes = str((datetime.now() + timedelta(minutes=5)).strftime("%Y-%m-%d %H:%M:%S"))
        logger.info(f"获取当前时间5分钟后的时间：{now_time_five_minutes}")
        plan_list_url = "{}/pcbames/web/patchPlan/pageList".format(self.PCBA_MES_NEW_URL)
        plan_list_body = {"body": {
                                "keyword": self.order_no, "date": "", "lastStationCodes": [], "lineId": "", "materialStatus": "",
                                 "planEndTime": "", "planStartTime": "", "planStatus": "", "salesman": "", "schedulingStatus": 3},
                          "header": {"pageNum": 1, "pageSize": 500}}
        if plan_type != None:
            plan_list_url = "{}/pcbames/web/{}Plan/pageList".format(self.PCBA_MES_NEW_URL, plan_type)
            if plan_type == "weld":  # DIP计划
                plan_list_body = {"body": {
                                        "orderNo": self.order_no, "date": "", "lineId": "", "productSalesman": "", "planStatus": "",
                                        "schedulingStatus": "", "lastStationCodes": [], "smtWeldPlanStartTime": "", "smtWeldPlanEndTime": "",
                                        "oemList": [], "planSort": ""}, "header": {"pageNum": 1, "pageSize": 500}}
            elif plan_type == "packing":  # 出货计划
                plan_list_body = {"body": {
                                        "orderNo": self.order_no, "salesman": "", "fabricatedFactoryIds": "", "date": "", "lastStationCodes": [],
                                        "planStartTime": "", "planEndTime": "", "oemList": [], "planSort": ""},
                                  "header": {"pageNum": 1, "pageSize": 500}}
            elif plan_type == "abnormal":  # 异常计划
                plan_list_body = {"body": {
                                        "orderNo": self.order_no, "productSalesman": "", "oemList": []},

                                  "header": {"pageNum": 1, "pageSize": 500}}
        plan_list_res = self.newpcbames_rss.post(url=plan_list_url, json=plan_list_body, headers=self.json_head).json()
        print(plan_list_res)
        batchUpdate_body = plan_list_res["body"]
        # logger.info(batchUpdate_body)
        if plan_type == None:
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
        if plan_type != None:
            if plan_type == "weld":
                batch_update_url = "{}/pcbames/web/{}Plan/update".format(self.PCBA_MES_NEW_URL, plan_type)
                batchUpdate_body[0]["isEdit"] = True
                batchUpdate_body[0]["isWaveTool"] = ""
                batchUpdate_body[0]["lineId"] = 39
                batchUpdate_body[0]["sort"] = "1"
                batchUpdate_body[0]["smtWeldPlanStartTime"] = now_time
                batchUpdate_body[0]["smtWeldPlanEndTime"] = now_time_five_minutes
        batch_update_body = {"body": batchUpdate_body}
        print(json.dumps(batch_update_body, ensure_ascii=False).replace("'", '"'))
        batch_update_res = self.newpcbames_rss.post(url=batch_update_url, json=batch_update_body,headers=self.json_head).json()
        suc = batch_update_res["suc"]
        if suc == True:
            plan_name = "SMT"
            if plan_type != None:
                if plan_type == "weld":
                    plan_name = "DIP"
            logger.info(f"订单：{self.smt_order}的{plan_name}计划已排产")
        self.smt_order_detail()
        return self
    def first_inspect(self):
        """首件"""
        self.order_id = getattr(Data, 'order_id')
        self.order_no = getattr(Data, 'order_no')
        self.json_head["factoryCode"] = "CSHQ"
        # 送检
        search_add_first_inspect_url = "{}/pcbames/web/firstInspect/getOrderInfo".format(self.PCBA_MES_NEW_URL)
        search_add_first_inspect_body = {"body": {"orderNo": self.order_no}}
        search_add_first_inspect_res = self.newpcbames_rss.post(url=search_add_first_inspect_url, json=search_add_first_inspect_body, headers=self.json_head).json()
        oemName = search_add_first_inspect_res["body"]["oemName"]
        if "后焊" in oemName:
            logger.info("工序选择DIP")
            self.posiCodeKey = 1

        else:
            logger.info("工序选择SMT")
            self.posiCodeKey = 2
        setattr(Data, 'posiCodeKey', self.posiCodeKey)
        print(f"posiCodeKey: {self.posiCodeKey}")
        # 送检人员
        employee_info_url = "{}/pcbames/web/employee/info/public".format(self.PCBA_MES_NEW_URL)
        employee_info_body = {"body": {"name": "liaopeng"}}
        employee_info_res = self.newpcbames_rss.post(url=employee_info_url, json=employee_info_body, headers=self.json_head).json()
        self.employeeId = employee_info_res["body"]["id"]
        self.employeeName = employee_info_res["body"]["empName"]

        # 线体
        line_url = "{}/pcbames/web/line/enableListByProcedure/public".format(self.PCBA_MES_NEW_URL)
        line_body = {"body": 1}
        line_res = self.newpcbames_rss.post(url=line_url, json=line_body, headers=self.json_head).json()
        print(line_res)
        self.lineId = line_res["body"][0]["id"]
        print(f"lineId: {self.lineId}")

        # 首件送检-新增
        add_first_inspect_url = "{}/pcbames/web/firstInspect/add".format(self.PCBA_MES_NEW_URL)
        add_first_inspect_body = {"body": {
                                          "orderId": self.order_id,
                                          "posiCodeKey": self.posiCodeKey,
                                          "tbType": "",
                                          "lineId": self.lineId,
                                          "orderNo": self.order_no,
                                          "productName": self.smt_order,
                                          "isSmtEnd": False,
                                          "oemName": oemName,
                                          "sendUserName": self.employeeName,
                                          "sendUserId": self.employeeId}}
        # print(self.json_head)
        # print(json.dumps(add_first_inspect_body, ensure_ascii=False).replace("'", '"'))
        add_first_inspect_res = self.newpcbames_rss.post(url=add_first_inspect_url, json=add_first_inspect_body, headers=self.json_head).json()
        logger.info(f"首件送检新增结果：{add_first_inspect_res}")
        # 提交送检推送
        search_first_inspect_url = "{}/pcbames/web/firstInspect/pageList".format(self.PCBA_MES_NEW_URL)
        search_first_inspect_body = {"body": {
                                            "orderNo": self.order_no, "beginCTime": "", "checkNo": "",
                                            "lineId": "", "posiCodeKey": "", "checkResult": "", "checkState": "", "endCTime": "",
                                            "sendUserName": "", "productName": "", "status": ""},
                                     "header": {"pageNum": 1, "pageSize": 500}}
        search_first_inspect_res = self.newpcbames_rss.post(url=search_first_inspect_url, json=search_first_inspect_body, headers=self.json_head).json()
        first_inspect_id = jsonpath.jsonpath(search_first_inspect_res, "$..id")
        if first_inspect_id != False:
            for i in first_inspect_id:
                logger.info(f"首件送检id：{i}")
                first_inspect_url = "{}/pcbames/web/firstInspect/inspect".format(self.PCBA_MES_NEW_URL)
                first_inspect_body = {"body": i}
                first_inspect_res = self.newpcbames_rss.post(url=first_inspect_url, json=first_inspect_body, headers=self.json_head).json()
                logger.info(f"首件送检推送结果：{first_inspect_res}")
                # 首件检验--详情信息查找
                first_inspect_check_info_url = "{}/pcbames/web/firstInspect/checkInfo".format(self.PCBA_MES_NEW_URL)
                first_inspect_check_info_body = {"body": i}
                first_inspect_check_info_res = self.newpcbames_rss.post(url=first_inspect_check_info_url, json=first_inspect_check_info_body, headers=self.json_head).json()
                first_inspect_check_info_res_body = first_inspect_check_info_res["body"]
                first_inspect_check_info_res_body["checkResult"] = 1
                first_inspect_check_info_res_body["finishUserId"] = self.employeeId
                first_inspect_check_info_res_body["finishUserName"] = self.employeeName
                first_inspect_check_info_res_body["customerOrderId"] = ""
                first_inspect_check_info_res_body["inspectId"] = i
                file_body = self.pcbames_file_upload("first_inspect", PCBAMES_file_dir)
                first_inspect_check_info_res_body["sampleFiles"] = [file_body]
                for m in first_inspect_check_info_res_body["firstCheckItemVOs"]:
                    if m["itemProduction"] == "贴片表面点数":
                        m["checkTxt"] = "1"
                    elif m["itemProduction"] == "PCB板长度":
                        m["checkResult"] = 1
                    elif m["itemProduction"] == "电阻测值":
                        m["checkResult"] = 1
                logger.info(f"首件检验详情信息：{first_inspect_check_info_res_body}")
                # 检验
                saveCheck_url = "{}/pcbames/web/firstInspect/saveCheck".format(self.PCBA_MES_NEW_URL)
                saveCheck_body = {"body": first_inspect_check_info_res_body}
                saveCheck_res = self.newpcbames_rss.post(url=saveCheck_url, json=saveCheck_body, headers=self.json_head).json()
                logger.info(f"首件检验结果：{saveCheck_res}")
        return self
    def customers_sample_confirm(self):
        """客户样板确认"""
        self.json_head["factoryCode"] = "CSHQ"
        # self.order_id = getattr(Data, 'order_id')
        self.order_no = getattr(Data, 'order_no')
        customers_sample_confirm_search_url = "{}/pcbames/web/sample/orderPageList".format(self.PCBA_MES_NEW_URL)
        customers_sample_confirm_search_body = {"body": {
                                                      "orderNo": self.order_no, "auditState": "", "fabricatedFactoryIds": [],
                                                      "factoryId": "", "isFirstConfirm": "", "productName": "", "projectLeaderName": "",
                                                      "sampleStatus": 1, "sellerName": "", "startTime": "", "endTime": "", "projectName": "",},
                                                 "header": {"pageNum": 1, "pageSize": 500}}
        customers_sample_confirm_search_res = self.newpcbames_rss.post(url=customers_sample_confirm_search_url, json=customers_sample_confirm_search_body, headers=self.json_head).json()
        self.orderId = jsonpath.jsonpath(customers_sample_confirm_search_res, "$..orderId")
        self.fabricatedFactoryId = jsonpath.jsonpath(customers_sample_confirm_search_res, "$..fabricatedFactoryId")
        sample_confirm_info_url = "{}/pcbames/web/sample/infoPageList".format(self.PCBA_MES_NEW_URL)
        for i in range(len(self.orderId)):
            sample_confirm_info_body = {"body": {"orderId": self.orderId[i], "factoryId": self.fabricatedFactoryId[i]}, "header": {"pageNum": 1, "pageSize": 500}}
            sample_confirm_info_res = self.newpcbames_rss.post(url=sample_confirm_info_url, json=sample_confirm_info_body, headers=self.json_head).json()
            sample_confirm_id = jsonpath.jsonpath(sample_confirm_info_res, "$..id")
            stepState = jsonpath.jsonpath(sample_confirm_info_res, "$..stepState")
            for j in range(len(sample_confirm_id)):
                if stepState[j] == 1:
                    sample_confirm_url = "{}/pcbames/web/sample/querySample".format(self.PCBA_MES_NEW_URL)
                    sample_confirm_body = {"body": {"id": sample_confirm_id[j]}}
                    sample_confirm_res = self.newpcbames_rss.post(url=sample_confirm_url, json=sample_confirm_body, headers=self.json_head).json()
                    logger.info(f"客户样板确认：{sample_confirm_res}")

        return self



    def AOI_inspect(self):
        # AOI检验
        self.json_head["factoryCode"] = "CSHQ"
        self.boardFaceName = getattr(Data, 'boardFaceName')
        self.order_no = getattr(Data, 'order_no')
        boardFace_name_id_tbType_dict = {"T面": {"id": 47, "tbType": 1}, "B面": {"id": 48, "tbType": 2}, "TB面": {"id": 49, "tbType": 3}}
        for i in boardFace_name_id_tbType_dict:
            if i == self.boardFaceName:
                self.boardFace_id = boardFace_name_id_tbType_dict[i]["id"]
                self.tbType = boardFace_name_id_tbType_dict[i]["tbType"]
            top_eraTion_info_url = "{}/pcbames/web/topEraTion/info".format(self.PCBA_MES_NEW_URL)
            top_eraTion_info_body = {"body": {"id": self.boardFace_id}}
            top_eraTion_info_res = self.newpcbames_rss.post(url=top_eraTion_info_url, json=top_eraTion_info_body,headers=self.json_head).json()
            self.operCode = top_eraTion_info_res["body"]["operCode"]
            self.operName = top_eraTion_info_res["body"]["operName"]
            logger.info(f"获取到订单归属号：{self.smt_order}的加工信息里面单/双面类型为：{self.boardFaceName}的详情信息：operCode：{self.operCode}，operName：{self.operName}")
        employee_info_url = "{}/pcbames/web/employee/info/public".format(self.PCBA_MES_NEW_URL)
        employee_info_body = {"body": {"name": "liaopeng"}}
        employee_info_res = self.newpcbames_rss.post(url=employee_info_url, json=employee_info_body, headers=self.json_head).json()
        self.employeeId = employee_info_res["body"]["id"]
        self.employeeName = employee_info_res["body"]["empName"]
        aoi_order_info_url = "{}/pcbames/web/aoi/getOrderInfo".format(self.PCBA_MES_NEW_URL)
        aoi_order_info_body = {"body": {"orderNo": self.order_no, "tbType": self.tbType}}
        aoi_order_info_res = self.newpcbames_rss.post(url=aoi_order_info_url, json=aoi_order_info_body,headers=self.json_head).json()
        isTracedDesc = aoi_order_info_res["body"]["isTracedDesc"]
        lineId = aoi_order_info_res["body"]["lineId"]
        lineCode = aoi_order_info_res["body"]["lineCode"]
        lineName = aoi_order_info_res["body"]["lineName"]
        orderNum = aoi_order_info_res["body"]["orderNum"]
        logger.info(f"获取到isTracedDesc：{isTracedDesc}，orderNum：{orderNum}")
        now_time = str((datetime.now()).strftime("%Y-%m-%d %H:%M:%S"))
        logger.info(f"获取当前时间：{now_time}")
        now_time_one_minutes = str((datetime.now() + timedelta(minutes=1)).strftime("%Y-%m-%d %H:%M:%S"))
        logger.info(f"获取当前时间1分钟后的时间：{now_time_one_minutes}")
        aoi_add_url = "{}/pcbames/web/aoi/add".format(self.PCBA_MES_NEW_URL)
        aoi_add_body = {"body": {"aoiNgs": [], "isTracedDesc": isTracedDesc,"lineCode": lineCode,"proLineId": "", "procName": "", "productCode": "", "qualifiedNum": "","lineId": lineId,
                                  "lineName": lineName, "orderNo": self.order_no, "orderNum": orderNum,"orderStatus": 1, "productName": self.smt_order, "stationName": self.operName,
                                 "startTestTime": now_time, "startEndTime": now_time_one_minutes, "stationCode": self.operCode, "unqualifiedNum": 0, "testUnqualifiedNum": "",
                                 "tbType": 1, "testNum": orderNum, "testQualifiedNum": orderNum, "userName": self.employeeName,"employeeId": self.employeeId, "workHour": "1"
                                 }}
        aoi_add_res = self.newpcbames_rss.post(url=aoi_add_url, json=aoi_add_body,headers=self.json_head).json()
        logger.info(aoi_add_res)
        totalAoiNum = aoi_add_res["body"]["totalAoiNum"]
        logger.info(f"AOI检验通过总数为：{totalAoiNum}")
        return self

    def QA_inspect(self):
        # OA检验
        self.order_no = getattr(Data, 'order_no')
        self.json_head["factoryCode"] = "CSHQ"
        # 获取订单信息详情
        order_info_url = "{}/pcbames/web/qa/getOrderInfo".format(self.PCBA_MES_NEW_URL)
        order_info_body = {"body": self.order_no}
        order_info_res = self.newpcbames_rss.post(url=order_info_url, json=order_info_body, headers=self.json_head).json()
        logger.info(order_info_res)
        isTracedDesc = order_info_res["body"]["isTracedDesc"]
        orderNum = order_info_res["body"]["orderNum"]
        orderStatus = order_info_res["body"]["orderStatus"]
        productName = order_info_res["body"]["productName"]
        lineCode = order_info_res["body"]["lineCode"]
        lineId = order_info_res["body"]["lineId"]
        lineName = order_info_res["body"]["lineName"]
        now_time = str((datetime.now()).strftime("%Y-%m-%d %H:%M:%S"))
        logger.info(f"获取当前时间10分钟后的时间：{now_time}")
        now_time_ten_minutes = str((datetime.now() + timedelta(minutes=1)).strftime("%Y-%m-%d %H:%M:%S"))
        logger.info(f"获取当前时间10分钟后的时间：{now_time_ten_minutes}")
        employee_info_url = "{}/pcbames/web/employee/info/public".format(self.PCBA_MES_NEW_URL)
        employee_info_body = {"body": {"name": "liaopeng"}}
        employee_info_res = self.newpcbames_rss.post(url=employee_info_url, json=employee_info_body, headers=self.json_head).json()
        self.employeeId = employee_info_res["body"]["id"]
        self.employeeName = employee_info_res["body"]["empName"]
        # 确认提交
        QA_inspect_url = "{}/pcbames/web/qa/add".format(self.PCBA_MES_NEW_URL)
        QA_inspect_body = {"body": {
                            "isTracedDesc": isTracedDesc,"orderNo": self.order_no, "orderNum": orderNum, "productName": productName, "orderStatus": orderStatus, "overCountId": "",
                           "lineCode": lineCode, "lineId": lineId, "lineName": lineName, "proLineId": "", "proLineName": "", "procName": "", "productCode": "", "qaNgs": [], "qualifiedNum": "","tbType": "",
                            "testUnqualifiedNum": "", "unqualifiedNum": "","testNum": orderNum, "testQualifiedNum": orderNum,"startTestTime": now_time, "startEndTime": now_time_ten_minutes,
                            "stationCode": "QAJY", "stationName": "QA检验","userName": self.employeeName,"employeeId": self.employeeId
                            }}
        QA_inspect_res = self.newpcbames_rss.post(url=QA_inspect_url, json=QA_inspect_body,headers=self.json_head).json()
        logger.info(QA_inspect_res)
        return self
    def pack_scan(self):
        """包装扫描"""
        self.order_no = getattr(Data, 'order_no')
        self.json_head["factoryCode"] = "CSHQ"
        pack_order_info_url = "{}/pcbames/web/productPackage/packageOrderInfo/public".format(self.PCBA_MES_NEW_URL)
        pack_order_info_body = {"body": {"orderNo": self.order_no}}
        pack_order_info_res = self.newpcbames_rss.post(url=pack_order_info_url, json=pack_order_info_body,headers=self.json_head).json()
        logger.info(pack_order_info_res)
        hasOddment = pack_order_info_res["body"]["hasOddment"]
        orderNumber = pack_order_info_res["body"]["orderNumber"]
        orderId = pack_order_info_res["body"]["orderId"]
        logger.info(f"获取到hasOddment：{hasOddment}，orderNumber：{orderNumber}，orderId：{orderId}")
        # 获取物料编码
        search_goods_no_url = "{}/pcbames/web/packageMaterial/getProjectPackageMaterial/public".format(self.PCBA_MES_NEW_URL)
        search_goods_no_body = {"body": {"id": orderId}}
        search_goods_no_res = self.newpcbames_rss.post(url=search_goods_no_url, json=search_goods_no_body,headers=self.json_head).json()
        goods_no_list = jsonpath.jsonpath(search_goods_no_res, "$..partNumber")
        # # 判断包材里面是否有物料编码
        pack_id = ''
        packTypeKey = ''
        partNumber = ''
        for i in goods_no_list:
            pack_goods_no_search_url = "{}/pcbames/web/packageMaterial/pageList".format(self.PCBA_MES_NEW_URL)
            pack_goods_no_search_body = {"header": {"pageNum": 1, "pageSize": 500}, "body": {"partNumber": i, "partName":"", "packTypeKey":""}}
            pack_goods_no_search_res = self.newpcbames_rss.post(url=pack_goods_no_search_url, json=pack_goods_no_search_body,headers=self.json_head).json()
            if "body" in pack_goods_no_search_res:
                pack_id = jsonpath.jsonpath(pack_goods_no_search_res, "$..id")[0]
                packTypeKey = jsonpath.jsonpath(pack_goods_no_search_res, "$..packTypeKey")[0]
                partNumber  = jsonpath.jsonpath(pack_goods_no_search_res, "$..partNumber")[0]
                break
        if pack_id == '':
            logger.info("没有找到对应的包材")
            search_goods_no_url = "{}/pcbames/web/tpart/pageList/public".format(self.PCBA_MES_NEW_URL)
            search_goods_no_body = {"header": {"pageNum": 1, "pageSize": 500},
                                    "body": {"partNumber": goods_no_list[0], "partName": "", "partClass": "",  "partClassSmall": "",  "isFactoryMaterial": 1, "factoryId": 2}}
            search_goods_no_res = self.newpcbames_rss.post(url=search_goods_no_url, json=search_goods_no_body, headers=self.json_head).json()
            partId = jsonpath.jsonpath(search_goods_no_res, "$..id")[0]
            # 新增包材--纸箱
            pack_goods_no_add_url = "{}/pcbames/web/packageMaterial/add".format(self.PCBA_MES_NEW_URL)
            pack_goods_no_add_body = {"body": {"partIds": [partId], "packTypeKey": "1", "packType": "纸箱"}}
            pack_goods_no_add_res = self.newpcbames_rss.post(url=pack_goods_no_add_url, json=pack_goods_no_add_body, headers=self.json_head).json()
            logger.info(f"新增包材--纸箱结果：{pack_goods_no_add_res}")
            pack_goods_no_search_url = "{}/pcbames/web/packageMaterial/pageList".format(self.PCBA_MES_NEW_URL)
            pack_goods_no_search_body = {"header": {"pageNum": 1, "pageSize": 500}, "body": {"partNumber": goods_no_list[0], "partName":"", "packTypeKey":""}}
            pack_goods_no_search_res = self.newpcbames_rss.post(url=pack_goods_no_search_url, json=pack_goods_no_search_body,headers=self.json_head).json()
            if "body" in pack_goods_no_search_res:
                pack_id = jsonpath.jsonpath(pack_goods_no_search_res, "$..id")[0]
                packTypeKey = jsonpath.jsonpath(pack_goods_no_search_res, "$..packTypeKey")[0]
                partNumber  = jsonpath.jsonpath(pack_goods_no_search_res, "$..partNumber")[0]
        # lineId 获取
        line_list_url = "{}/pcbames/web/line/pageList".format(self.PCBA_MES_NEW_URL)
        line_list_body = {"body": {"lineCode": "", "lineName": "包装一线", "lineStatus": "", "posiCode": ""}, "header": {"pageNum": 1, "pageSize": 200}}
        line_list_res = self.newpcbames_rss.post(url=line_list_url, json=line_list_body,headers=self.json_head).json()
        logger.info(line_list_res)
        lineId = line_list_res["body"][0]["id"]
        lineName = line_list_res["body"][0]["lineName"]
        logger.info(f"获取到lineId：{lineId}")

        # 生成已包装采集信息
        pack_order_gather_add_url = "{}/pcbames/web/productPackage/add".format(self.PCBA_MES_NEW_URL)
        pack_order_gather_add_body = {"body": {"containerNum": orderNumber, "hasOddment": hasOddment, "lineId": lineId, "lineName": lineName,"oddmentNo": "", "packageNumber": 1,
                                      "operCode": "BZSM", "orderId": orderId, "orderNo": self.order_no, "orderNumber": orderNumber, "packageNum": orderNumber, "productName": self.smt_order,
                                      "materialList": [{"id": "", "materialId": pack_id, "num": orderNumber}], ",packageNum": "1"}}
        logger.info(pack_order_gather_add_body)
        pack_order_gather_add_res = self.newpcbames_rss.post(url=pack_order_gather_add_url, json=pack_order_gather_add_body, headers=self.json_head).json()
        logger.info(pack_order_gather_add_res)
        self.containerNo = pack_order_gather_add_res["body"][0]["containerNo"]
        # containerNo = []
        # for i in range(len(containerNoInfo)):
        #     containerNo.append(containerNoInfo[i]["containerNo"])
        logger.info(f"获取到containerNo：{self.containerNo}")
        # 将生成的self.containerNo往Data里面作虚拟存储以【containerNo】命名以便后续提取
        setattr(Data, 'containerNo', self.containerNo)
        return self

    def smt_order_delivery(self):
        self.order_no = getattr(Data, 'order_no')
        self.json_head["factoryCode"] = "CSHQ"
        product_list_url = "{}/pcbames/web/out/productList".format(self.PCBA_MES_NEW_URL)
        product_list_body = {"body": {"labelCode": "", "orderNo": self.order_no, "productName": ""}}
        product_list_res = self.newpcbames_rss.post(url=product_list_url, json=product_list_body, headers=self.json_head).json()
        orderId = product_list_res["body"][0]["orderId"]
        customerNo = product_list_res["body"][0]["customerNo"]
        num = product_list_res["body"][0]["inStockedNum"]
        logger.info(f"获取到orderId：{orderId}")

        # 确认发货结果
        check_deliver_url = "{}/pcbames/web/out/checkDeliver/public".format(self.PCBA_MES_NEW_URL)
        check_deliver_body = {"body": {"id": orderId}}
        product_list_res = self.newpcbames_rss.post(url=check_deliver_url, json=check_deliver_body, headers=self.json_head).json()

        # 获取发货详情
        out_info_url = "{}/pcbames/web/out/info".format(self.PCBA_MES_NEW_URL)
        out_info_body = {"body":{"customerNos": [customerNo],"orderIds": [orderId]}}
        out_info_res = self.newpcbames_rss.post(url=out_info_url, json=out_info_body, headers=self.json_head).json()
        items = out_info_res["body"]["items"]
        stockList = items[0]["stockList"]
        auditState = out_info_res["body"]["auditState"]
        customerName = out_info_res["body"]["customerName"]
        customerNo = out_info_res["body"]["customerNo"]
        expressPayType = out_info_res["body"]["expressPayType"]
        receivePhone = out_info_res["body"]["receivePhone"]
        receiveUser = out_info_res["body"]["receiveUser"]
        receiverAddress = out_info_res["body"]["receiverAddress"]
        # logger.info(stockList)
        stockList[0]["pickNum"] = num
        items[0]["selectedLabelList"] = stockList
        items[0]["sendNum"] = num
        items[0]["stockList"][0]["pickNum"] = num
        items[0]["memo"] = "测试发货"
        self.express_delivery_no = "SF" + datetime.now().strftime("%Y%m%d") + "001" + str(Faker("zh_CN").random_int(1, 10000))
        logger.info(f"生成的快递单号：{self.express_delivery_no}")
        # 添加发货明细
        out_add_url = "{}/pcbames/web/out/add".format(self.PCBA_MES_NEW_URL)
        out_add_body = {"body": {"auditState":auditState, "customerName": customerName, "customerNo": customerNo, "expressId": 1, "expressNo": "", "weightSelect": 0,
                                 "expressPayType": expressPayType, "items": items, "outNo": "", "receiveCountry": "", "receivePhone": receivePhone, "boxId": "", "boxNumber": 1,
                                 "receiveUser": receiveUser, "receiverAddress": receiverAddress, "remark": "测试", "lastBoxId": None, "lastWeight": "", "mainWeight": "",
                                 "realWeight": None, "recommendExpressCode": None, "recommendExpressItemName": None, "recommendExpressItemNo": None, "weightType": None,
                                 "recommendExpressName": None, "recommendExpressNo": None, "recommendExpressType": None, "recommendExpressWeight": None, "recommendExpressList": None
                                  }}
        logger.info(out_add_body)
        out_add_res = self.newpcbames_rss.post(url=out_add_url, json=out_add_body, headers=self.json_head).json()
        logger.info(out_add_res)

        # 获取发货订单id
        out_list_url = "{}/pcbames/web/out/pageList".format(self.PCBA_MES_NEW_URL)
        out_list_body = {"body": {"productName": self.smt_order}}
        out_list_res = self.newpcbames_rss.post(url=out_list_url, json=out_list_body, headers=self.json_head).json()
        logger.info(out_list_res)
        outId = out_list_res["body"][0]["id"]
        outNo = out_list_res["body"][0]["outNo"]
        logger.info(f"获取发货订单id: {outId}")

        # 发货审核
        out_audit_url = "{}/pcbames/web/out/audit".format(self.PCBA_MES_NEW_URL)
        out_audit_body = {"body": {"auditState": 2, "id": outId}}
        out_audit_res = self.newpcbames_rss.post(url=out_audit_url, json=out_audit_body, headers=self.json_head).json()
        logger.info(out_audit_res)

        # 发货修改
        out_info_update_url = "{}/pcbames/web/out/info".format(self.PCBA_MES_NEW_URL)
        out_info_update_body = {"body": {"outId": outId}}
        out_info_update_res = self.newpcbames_rss.post(url=out_info_update_url, json=out_info_update_body, headers=self.json_head).json()
        body = out_info_update_res["body"]
        body["expressNo"] = self.express_delivery_no
        out_update_url = "{}/pcbames/web/out/update".format(self.PCBA_MES_NEW_URL)
        out_update_body = {"body": body}
        out_update_res = self.newpcbames_rss.post(url=out_update_url, json=out_update_body, headers=self.json_head).json()
        logger.info(out_update_res)

        out_info_statement_url = "{}/pcbames/web/out/pageList".format(self.PCBA_MES_NEW_URL)
        out_info_statement_body = {"body": {"productName": self.smt_order}}
        out_info_statement_res = self.newpcbames_rss.post(url=out_info_statement_url, json=out_info_statement_body, headers=self.json_head).json()
        auditState = out_info_statement_res["body"][0]["auditState"]
        if auditState == 4:
            logger.info(f"订单号：{self.smt_order}已结案，SMT订单已完成")
        return self
    def pcbames_file_upload(self, file_type, file_path):
        """文件上传"""
        fileToken_url = "{}/pcbames/oss/client/token".format(self.PCBA_MES_NEW_URL)
        fileToken_res = self.newpcbames_rss.post(url=fileToken_url, headers=self.json_head).json()
        form_headers = {}
        form_headers["appKey"] = fileToken_res["body"]["appKey"]
        form_headers["fileToken"] = fileToken_res["body"]["fileToken"]
        form_headers["factoryCode"] = "CSHQ"
        mes_file_url = "{}/oss/file/upload".format(self.PCBA_MES_NEW_UPLOAD_URL)
        file_name = file_path.split("\\")[-1]
        file = [('file', (file_name, open(file_path, 'rb'), 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'))]
        mes_file_res = self.newpcbames_rss.post(url=mes_file_url, files=file, headers=form_headers).json()
        file_body = mes_file_res["body"]
        if file_type == "first_inspect":
            file_body["fileId"] = file_body["id"]
            file_body["fileType"] = file_body["fileSuffix"]
            file_body["filePath"] = file_body["url"]
            file_body["checkFileType"] = 1
            del file_body['id']
            del file_body['type']
            del file_body['url']
        return file_body

    def mian_smt_order(self):
        """运行"""
        self.choose_factory().smt_order_list()
        NewMesSmtOrderPdaCancenllation(self.newpcbames_rss).mian_smt_pda_h5_produce()
        self.patch_plan()
        NewMesSmtOrderPdaCancenllation(self.newpcbames_rss).mian_smt_pda_h5_patch()
        self.AOI_inspect().QA_inspect()
        self.pack_scan()
        cookies = self.newpcbames_rss.cookies.get_dict()
        self.pcbames_pda_token = cookies["orgauthUATToken"]
        # logger.info(self.pcbames_pda_token)
        NewMesSmtOrderPdaCancenllation(self.newpcbames_rss).product_storage()
        self.smt_order_delivery()
        return self
    def bug(self):
        pass

if __name__ == '__main__':
    order_sn = "TK24082646254"
    setattr(Data, 'smt_order_sn', order_sn)
    # erp_rss = SOOLogin(system_name="erp").target_login()
    # ErpSmtOrderCancellation(erp_rss).erp_smt_order_cancellation()
    pcbames_rss = SOOLogin(system_name="pcbames").target_login()
    # MES后台操作切换仓库、获取cookie
    NewMesSmtOrderCancellation(rss=pcbames_rss).choose_factory().smt_order_list()
    NewMesSmtOrderCancellation(rss=pcbames_rss).first_inspect().customers_sample_confirm().AOI_inspect()
    # NewMesSmtOrderCancellation(rss=pcbames_rss).patch_plan(plan_type="weld")