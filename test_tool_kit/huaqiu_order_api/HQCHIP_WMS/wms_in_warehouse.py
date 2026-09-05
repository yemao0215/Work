import json
import time
from datetime import datetime

import jsonpath
import requests
import yaml

from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_data import Data
from huaqiu_order_api.common.my_path import yaml_file, account_yaml


class WmsInWarehouse:

    def __init__(self, target_rss):
        self.wms_rss = target_rss
        self.pda_rss = requests.Session()
        self.json_head = {"Content-Type": "application/json"}
        self.pda_json_head = {"Content-Type": "application/json", "User-Agent":"okhttp/3.14.9", "Connection":"keep-alive"}
        self.json_head = {"Content-Type": "application/json"}
        self.in_order = getattr(Data, 'inn_sn',  "")
        self.batchNum = getattr(Data, 'dc', "")
        # self.in_order = "IN00154535"
        # self.in_order = ""
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.WMS_URL = data["WMS_URL"]
        with open(account_yaml, 'r', encoding='utf-8') as yamlfile:
            account = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.warehouse_type = account["HQCHIP_GOODS"]["warehouse_id"]

    def wms_warehousing(self):
        select_store_url = '{}/wms/base/store/selectStore?storeCode={}'.format(self.WMS_URL, self.warehouse_type)
        logger.info(select_store_url)# 选择仓库 2：东莞仓，8：长沙仓
        select_store_res = self.wms_rss.get(url=select_store_url)
        logger.info(f"选择东莞仓 storeCode={self.warehouse_type}, {select_store_res}")

        order_warehousing_url = '{}/wms/business/receivedoc/selectreceivedoclist'.format(self.WMS_URL)  # 访问预入库列表
        order_warehousing_body = {"inboundNo": self.in_order, "type": self.warehouse_type}
        n = 0
        while True:
            try:
                order_warehousing_res = self.wms_rss.post(url=order_warehousing_url, json=order_warehousing_body, headers=self.json_head).json()
                warehousing_id = jsonpath.jsonpath(order_warehousing_res, '$..id')[0]
                planReceivenumber = jsonpath.jsonpath(order_warehousing_res, '$..planReceiveQty')[0]
                docCode = jsonpath.jsonpath(order_warehousing_res, '$..docCode')[0]
                self.planReceivenumber = planReceivenumber
                self.docCode = docCode
                logger.info(f"第{n + 1}次访问预入库单列表,获取到warehousing_id:{warehousing_id},planReceivenumber:{planReceivenumber},docCode:{self.docCode}")
                break
            except Exception as e:
                n += 1
                if n < 6:
                    logger.warning(f"第 {n} 次,预入库单列表没有找到入库单:{self.in_order},等待30秒后系统自动重试,错误信息:{e}")
                    time.sleep(30)
                else:
                    logger.error(f"预入库单列表查找入库单:{self.in_order} 出错,请手动检查入库单是否存在")
                    raise ValueError
        time.sleep(2)
        warehousing_goods_url = '{}/wms/business/receivedocdetail/selectgoodslabellist'.format(self.WMS_URL)  # 入库单型号明细
        warehousing_goods_body = {"id": warehousing_id}
        warehousing_goods_res = self.wms_rss.post(url=warehousing_goods_url, json=warehousing_goods_body, headers=self.json_head).json()
        erp_code = jsonpath.jsonpath(warehousing_goods_res, '$..code')
        receiveDocDetailId = jsonpath.jsonpath(warehousing_goods_res, '$..id')
        quantity = jsonpath.jsonpath(warehousing_goods_res, '$..unCreateLabelQtyBu')
        logger.info(f"访问预入库单明细,获取到erp_code列表:{erp_code},receiveDocDetailId列表:{receiveDocDetailId},quantity列表:{quantity}")
        time.sleep(2)
        print_label_url = "{}/wms/business/receivelabel/printlable".format(self.WMS_URL)
        for i in range(len(receiveDocDetailId)):
            # 生产周期自定义
            print_label_body = {"batchNum": "", "labelQty": "1", "packingUnit": 4, "printer": "GP-3120TL", "quantity": quantity[i],
                                "receiveDocDetailId": receiveDocDetailId[i], "receiveDocId": warehousing_id}
            if self.batchNum == "":
                # 根据当前日期去锁定生产周期 生产周期格式年份后两位+周 比如2024年的第39周   2439+
                # 获取当前日期
                current_date = datetime.now()
                # 计算当前日期是本年度的第几个周
                week_number = current_date.isocalendar()[1]
                # 获取本年度的最后两位数字，如果获取周数小于10，则前面补0
                year_last_two_digits = current_date.year % 100
                self.batchNum = str(year_last_two_digits) + (f'{week_number:02}+' if week_number < 10 else (str(week_number)) + "+")
            else:
                if self.is_valid_year_week(self.batchNum) == True:
                    logger.info("生产周期格式正确，无需修改")
                    self.batchNum = str(self.batchNum) + "+"
                else:
                    self.batchNum = 'test+'
            print("获取到批次号为：{}".format(self.batchNum))
            print_label_body["batchNum"] = self.batchNum
            print_label_res = self.wms_rss.put(url=print_label_url, json=print_label_body, headers=self.json_head).json()
            if print_label_res["retMsg"] is not None and '请维护商品重量再打印' in print_label_res["retMsg"]:
                self.wms_goods_update(erp_code[i])
                print_label_res = self.wms_rss.put(url=print_label_url, json=print_label_body, headers=self.json_head).json()
            logger.info(f"商品编号：{erp_code[i]}打印标签完成，执行结果为{print_label_res}")
            continue
        logger.info("操作打印标签完成，开始操作一键入库操作")
        warehousing_search_label_url = "{}/wms/business/receivebatch/getdocdetailbydocid?receiveDocId={}".format(self.WMS_URL, warehousing_id)
        warehousing_search_label_res = self.wms_rss.get(url=warehousing_search_label_url).json()
        resultInfo = warehousing_search_label_res["result"]
        warehousing_add_url = "{}/wms/business/receiverecord/add".format(self.WMS_URL)
        warehousing_add_body = resultInfo
        warehousing_add_res = self.wms_rss.put(url=warehousing_add_url, json=warehousing_add_body, headers=self.json_head).json()
        logger.info(warehousing_add_res)
        if warehousing_add_res["retMsg"] is not None and '已生成来料待检任务,请检验再入库' in warehousing_add_res["retMsg"]:
            if ',' in warehousing_add_res["retMsg"].split("已生成来料待检任务,请检验再入库")[0]:
                iqctask_labCodes = warehousing_add_res["retMsg"].split("已生成来料待检任务,请检验再入库")[0].split(',')
            else:
                iqctask_labCodes = [warehousing_add_res["retMsg"].split("已生成来料待检任务,请检验再入库")[0]]
            print(iqctask_labCodes)
            for i in range(len(iqctask_labCodes)):
                self.wms_iqctask(iqctask_labCode=iqctask_labCodes[i])
            warehousing_add_res = self.wms_rss.put(url=warehousing_add_url, json=warehousing_add_body, headers=self.json_head).json()
            logger.info(warehousing_add_res)
        logger.info("入库完成")

        return self

    def wms_iqctask(self, iqctask_labCode=None, template_name=None):
        """来料检验"""
        wms_iqctask_search_url = '{}/wms/business/iqctask/getiqctaskpage'.format(self.WMS_URL)
        wms_iqctask_search_body = {"labelCode": iqctask_labCode, "counted": True, "pageNum": 1, "pageSize": 100, "iqcStatus": 5}
        wms_iqctask_search_res = self.wms_rss.post(url=wms_iqctask_search_url, json=wms_iqctask_search_body, headers=self.json_head).json()
        iqcTaskId = jsonpath.jsonpath(wms_iqctask_search_res, '$..id')
        unIqcQty = jsonpath.jsonpath(wms_iqctask_search_res, '$..unIqcQty')
        supplierCode = jsonpath.jsonpath(wms_iqctask_search_res, '$..supplierCode')
        for i in range(len(iqcTaskId)):
            search_iqcTemplate_url = '{}/wms/base/iqcTemplate/chooseIqcTemplate'.format(self.WMS_URL)
            search_iqcTemplate_body = {"supplierCode": supplierCode[i], "counted": True, "pageNum": 1, "pageSize": 20}
            search_iqcTemplate_res = self.wms_rss.post(url=search_iqcTemplate_url, json=search_iqcTemplate_body, headers=self.json_head).json()
            template_id_count = jsonpath.jsonpath(search_iqcTemplate_res, '$..id')
            template_name_count = jsonpath.jsonpath(search_iqcTemplate_res, '$..name')
            if template_name != None:
                # 提取模板名称为template_name的检验模板id
                template_id = [i for i, j in zip(template_id_count, template_name_count) if j == template_name][0]
            else:
                template_id = template_id_count[0]
            Confirmation_template_url = '{}/wms/business/iqctask/getaddoqcbilldto?iqcTaskId={}&iqcTmplId={}'.format(self.WMS_URL, iqcTaskId[i], template_id)
            Confirmation_template_res = self.wms_rss.get(url=Confirmation_template_url, headers=self.json_head).json()
            Confirmation_template_resultInfo = Confirmation_template_res["result"]
            template_rule_url = '{}/wms/business/iqctask/getoqcbilltmpllist?iqcTmplId={}&qty={}'.format(self.WMS_URL, template_id, unIqcQty[i])
            template_rule_res = self.wms_rss.get(url=template_rule_url, headers=self.json_head).json()
            # print(json.dumps(template_rule_res, ensure_ascii=False).replace("'", '"'))
            template_rule_resultInfo_new = []
            template_rule_resultInfo = template_rule_res["result"]
            for m in range(len(template_rule_resultInfo)):
                if template_rule_resultInfo[m]["iqcQty"] != 0:
                    if template_rule_resultInfo[m]["testDescription"] == "元器件的性能参数":
                        template_rule_resultInfo[m]["testValue"] = '是'
                    elif template_rule_resultInfo[m]["testDescription"] == "特性":
                        template_rule_resultInfo[m]["testValue"] = '自动化测试'
                    elif template_rule_resultInfo[m]["testDescription"] == "检验数量是否正确":
                        template_rule_resultInfo[m]["testValue"] = '自动化测试1'
                    elif template_rule_resultInfo[m]["testDescription"] == "检验包装是否完整":
                        template_rule_resultInfo[m]["testValue"] = '是'
                    elif template_rule_resultInfo[m]["testDescription"] == "证书的种类":
                        template_rule_resultInfo[m]["testValue"] = '中文证书'
                template_rule_resultInfo[m]["iqcTmplDetailId"] = template_rule_resultInfo[m]["id"]
                template_rule_resultInfo_new = template_rule_resultInfo
            # print(json.dumps(template_rule_resultInfo_new, ensure_ascii=False).replace("'", '"'))
            addoqcbill_url = '{}/wms/business/iqctask/addoqcbill'.format(self.WMS_URL)
            Confirmation_template_resultInfo['okQty'] = unIqcQty[i]
            addoqcbill_body = {"addOqcBillBadDtoList": [], "addOqcBillDto": Confirmation_template_resultInfo, "addOqcBillTmplDtoList": template_rule_resultInfo_new}
            addoqcbill_res = self.wms_rss.post(url=addoqcbill_url, json=addoqcbill_body, headers=self.json_head).json()
            logger.info(f"执行结果：{addoqcbill_res}")
        return self
    def wms_goods_update(self, erp_code=None):
        """货品资料更新"""
        search_url = "{}/wms/base/goods/page".format(self.WMS_URL)
        search_body = {"code": erp_code, "pageNum": 1, "pageSize": 100, "counted": True}
        search_res = self.wms_rss.post(url=search_url, json=search_body, headers=self.json_head).json()
        id = jsonpath.jsonpath(search_res, '$..id')
        weight = jsonpath.jsonpath(search_res, '$..weight')
        for i in range(len(id)):
            if weight[i] == 0.0:
                search_img_url = '{}/wms/base/attachFile/list'.format(self.WMS_URL)
                search_img_body = {"docId": id[i]}
                search_img_res = self.wms_rss.post(url=search_img_url, json=search_img_body, headers=self.json_head).json()
                summary = {}
                if search_img_res["result"] != []:
                    for item in search_img_res["result"]:
                        t = item["type"]
                        url = item["path"]
                        if t in summary:
                            summary[t].append(url)  # 如果类型已经在汇总中，将当前url添加到对应的列表中
                        else:
                            summary[t] = [url]  # 如果类型不在汇总中，创建一个新的列表
                wms_goods_update_url = '{}/wms/base/goods/uploadGoodsAttach'.format(self.WMS_URL)
                wms_goods_update_body = {"id": id[i], "weight": 0.25, "beSet": 1, "encapsulationFilePaths": [], "filePaths": [], "goodsFilePaths": [],
                                         "labelNumberFilePaths": [], "packingFilePaths": [], "silkscreenFilePaths": []}
                if summary != {}:
                    img_type = {"filePaths": 1,"goodsFilePaths": 2, "silkscreenFilePaths": 3, "encapsulationFilePaths": 4, "labelNumberFilePaths": 5, "packingFilePaths": 6}
                    for key in img_type:
                        img_type_value = img_type[key]
                        if img_type_value in summary:
                            wms_goods_update_body[key] = summary[img_type_value]
                        else:
                            wms_goods_update_body[key] = []
                wms_goods_update_res = self.wms_rss.post(url=wms_goods_update_url, json=wms_goods_update_body, headers=self.json_head).json()
                if wms_goods_update_res["retMsg"] is None:
                    logger.info(f"id：{id[i]}更新资料成功")
            else:
                logger.info("无需更新")
        return self
    def wms_theupper_list(self, docCode=None, theupper_sn=None, status=None):
        """wms 上架列表"""
        if docCode !=None:
            self.docCode = docCode
        theupper_list_url = '{}/wms/warehouse/shelvesBill/getshelvesbillpage'.format(self.WMS_URL)  # 访问上架单列表
        theupper_list_body = {"sourceBillNumber": self.docCode, "status": status, "code": theupper_sn, "originalNumber": self.in_order, "pageNum": 1, "pageSize": 100}
        if self.docCode != '' or self.in_order != '' or theupper_sn != '':
            logger.info("___")
            n = 0
            while True:
                try:
                    order_warehousing_res = self.wms_rss.post(url=theupper_list_url, json=theupper_list_body, headers=self.json_head).json()
                    # print(order_warehousing_res)
                    theupper_id = jsonpath.jsonpath(order_warehousing_res, '$..id')
                    theupper_code = jsonpath.jsonpath(order_warehousing_res, '$..code')#
                    logger.info(f"第{n + 1}次访问上架单列表,获取到warehousing_id:{theupper_id[0]},theupper_code:{theupper_code[0]}")
                    break
                except Exception as e:
                    n += 1
                    if n < 6:
                        logger.warning(f"第 {n} 次,上架单列表没有找到上架单:{self.docCode},等待30秒后系统自动重试,错误信息:{e}")
                        time.sleep(30)
                    else:
                        logger.error(f"上架单列表查找上架单:{self.docCode} 出错,请手动检查上架单是否存在")
                        raise ValueError
        else:
            # theupper_list_body["status"] = 1
            order_warehousing_res = self.wms_rss.post(url=theupper_list_url, json=theupper_list_body, headers=self.json_head).json()
            theupper_id = jsonpath.jsonpath(order_warehousing_res, '$..id')
            theupper_code = jsonpath.jsonpath(order_warehousing_res, '$..code') #
            # logger.info(f"第{n + 1}次访问上架单列表,获取到warehousing_id:{theupper_id},theupper_code:{theupper_code}")
        time.sleep(2)
        self.labelNumber_sn = []
        self.targetLocationCode = []
        for i in range(len(theupper_id)):
            labelNumber_url="{}/wms/warehouse/shelvesBill/getshelvesbilldetailpage".format(self.WMS_URL)
            labelNumber_body = {"id": theupper_id[i]}
            labelNumber_res = self.wms_rss.post(url=labelNumber_url, json=labelNumber_body, headers=self.json_head).json()
            labelNumber_sn  = jsonpath.jsonpath(labelNumber_res, '$..labelNumber')
            targetLocationCode = jsonpath.jsonpath(labelNumber_res, '$..targetLocationCode')
            self.labelNumber_sn = self.labelNumber_sn + labelNumber_sn
            self.targetLocationCode = self.targetLocationCode + targetLocationCode
            logger.info(f"获取到上架商品的货品标签：{self.labelNumber_sn},库位：{self.targetLocationCode}")
        setattr(Data, 'labelNumber_sn', self.labelNumber_sn)
        setattr(Data, 'targetLocationCode', self.targetLocationCode)
        # logger.info(self.labelNumber_sn)
        logger.debug('=*' * 50)
        return self

    def is_valid_year_week(self, batch_number):
        # 检查字符串是否长度为4
        if len(batch_number) != 4:
            return False

        # 检查前两位是否是数字
        year_last_two_digits = batch_number[:2]
        week_number = batch_number[2:]

        if not (year_last_two_digits.isdigit() and week_number.isdigit()):
            return False

        # 检查周数是否在 01 到 53 之间
        week_number_int = int(week_number)
        if 1 <= week_number_int <= 53:
            return True

        return False



if __name__ == '__main__':
    from huaqiu_order_api.HQCHIP_SOO.login import SOOLogin
    from huaqiu_order_api.HQCHIP_WMS.HQCHIP_PDA_UAT.pda_theupper import PdaTheupper
    from huaqiu_order_api.HQCHIP_WMS.HQCHIP_PDA_UAT.pda_login import PdaLogin
    target_rss = SOOLogin("uat-wms.huaqiu.com", "wms/base").target_login()
    # WmsInWarehouse(target_rss).wms_theupper_list('', '')
    # # pda_rss = PdaLogin().pda_login()
    # # PdaTheupper(pda_rss).pda_theupper()   # 预出库单  商品标签
    WmsInWarehouse(target_rss).wms_warehousing().wms_theupper_list(docCode="ASN260819000001", theupper_sn='', status='')
    pda_rss = PdaLogin().pda_login()
    PdaTheupper(pda_rss).pda_theupper()
    # a = WmsInWarehouse(target_rss).is_valid_year_week("2401")
    # print(a)
    #
