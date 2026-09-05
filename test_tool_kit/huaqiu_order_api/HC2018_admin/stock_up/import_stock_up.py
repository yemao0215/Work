import json
import os
import re
import time
from datetime import datetime

import jsonpath
import openpyxl
import pandas as pd
import yaml
from openpyxl.cell import cell
from xpinyin import Pinyin

from huaqiu_order_api.HC2018_admin.dgk_goods_means.dgk_goods_means import GoodsMeans
from huaqiu_order_api.HC2018_admin.dgk_goods_means.stay_perfect_means import StayPerfectMeans
from huaqiu_order_api.HC2018_admin.login.login import Login
from huaqiu_order_api.HC2018_admin.work_sheet.work_sheet import WorkSheet
from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_data import Data
from huaqiu_order_api.common.my_path import stockup_dir, yaml_file, account_yaml, stockup_error_dir
from huaqiu_order_api.common.yaml_handler import write_yaml



class StockUp:
    def __init__(self, rss, goods_name=None, provider_name=None, encap=None, packer=None, packer_number=None,
                 purchase_price=None, stock_number=None, stock_type=None, MTS_Rep=None, warehouse_name=None, order_sn=None,
                 import_file_type=None, goods_no=None, goods_no_type=None,urgent_Type=None):
        """
        :param goods_name:  型号
        :param provider_name:  品牌
        :param encap 封装
        :param packer:  包装类型
        :param packer_number:  最小包装数量
        :param purchase_price:  采购单价
        :param stock_number:  补/备货货数量
        :param stock_type:  备货类型
        :param MTS_Rep:  补备货
        :param warehouse_name: 需求仓/交货仓
        :param order_sn 销售单号
        :param import_file_type 是否导入需求文件参数，不做接口传值
        :param goods_no 商品编码
        :param goods_no_type 是否请求资料接口去拿芯城编号，生效条件为：当goods_no为空且goods_no_type为是时请求资料接口
        """
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.HC2018_ADMIN_URL = data['HC2018_ADMIN_URL']
        self.goods_name = goods_name
        self.provider_name = provider_name
        self.encap = encap
        self.packer = packer
        self.packer_number = packer_number
        self.purchase_price = purchase_price
        self.stock_number = stock_number
        self.stock_type = stock_type
        self.MTS_Rep = MTS_Rep
        self.warehouse_name = warehouse_name
        self.goods_no = goods_no
        self.order_sn = order_sn if order_sn != None else ""
        self.import_file_type = import_file_type
        self.urgent_Type = urgent_Type
        self.rss = rss
        self.auth_token = getattr(Data, 'dos_auth_token', '')
        self.real_name = ''
        self.payload = {'origin': '1', 'content_unique': '1'}
        self.packer_type_json = {"卷装": 1, "剪切带": 2, "托盘": 3, "散装": 4, "管装": 5, "袋装": 6, "盒装": 7}
        self.files = [
  ('file', ('stockup.xlsx', open(stockup_dir, 'rb'),'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'))]
        self.headers = {"Content-Type": "application/x-www-form-urlencoded",
                        "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://www.huaqiu.com)"
                        }
        self.headers_json = {"Content-Type": "application/json; charset=UTF-8",
                             "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://www.huaqiu.com)"
                             }
        self.headers_json["Authorization"] = self.auth_token
        self.user_pwd_json = {"yemao": "12345678", "taoting": "12345678", "admin": "HQ@uat@666", "zhangjin": "123456",
                              "qiufm@hqchip.com": "12345678", "liujiaowei": "12345678", "hepeng": "12345678"}
        self.dc = getattr(Data, 'dc', '1.5年内')
        self.goods_no_type = goods_no_type

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
    def dc_create(self):
        if self.dc is None or self.dc.strip() == "":
            print(111)
            # 根据当前日期去锁定生产周期 生产周期格式年份后两位+周 比如2024年的第39周   2439+
            # 获取当前日期
            current_date = datetime.now()
            # 计算当前日期是本年度的第几个周
            week_number = current_date.isocalendar()[1]
            # 获取本年度的最后两位数字，如果获取周数小于10，则前面补0
            year_last_two_digits = current_date.year % 100
            dc_create_number = str(year_last_two_digits) + (
                f'{week_number:02}' if week_number < 10 else (str(week_number)))
        else:
            if self.dc in ["1.5年内", "2年内", "3年内", "5年内", "无法确认批次", "散料不能要求批次"]:
                logger.info(f"DC格式正确，无需修改,此时DC: {self.dc}")
                dc_create_number = self.dc
            else:
                if "+" in self.dc:
                    logger.info(f"DC格式正确，无需修改,格式为：年份+,此时DC: {self.dc}")
                    dc_create_number = self.dc
                elif self.is_valid_year_week(self.dc) == True:
                    logger.info(f"DC格式正确，无需修改格式为：年份+周数,此时DC: {self.dc}")
                    dc_create_number = self.dc
                else:
                    dc_create_number = 'test'
        return dc_create_number
    def excel_file_write(self, stockup_error_writefile_path=None):
        """更新文件里面型号、品牌、封装"""

        data = {
            "型号(必填)": [self.goods_name],
            "品牌(必填)": [self.provider_name],
            "封装(必填)": [self.encap],
            "包装类型": [self.packer],
            "包装数量": [self.packer_number],
             "采购价(含税,必填)": [self.purchase_price],
            "采购数量(必填)": [self.stock_number],
            "交期 (必填)": ['3-7'],
            "交货地(必填)": [self.warehouse_name],
            "需求仓(必填)": [self.warehouse_name],
            "DC": [str(self.dc_create())],
            "供应商(必填)": ['hqchip-llsjl'],
            "是否强制导入": ['是'],
            "备货类型(必填)": [self.stock_type],
            "补备货": [self.MTS_Rep],
            "客户ID(项目备货请前往SCM申请)": [''],
            "项目编号(项目备货请前往SCM申请)": [''],
            "备注": ['测试工具导入'],
            "供应商料号": [''],
            "芯城编码": [self.goods_no],
            "加急": [self.urgent_Type]

        }
        if self.dc != '':
            data["DC"] = [self.dc]
        # logger.info(f"开始写入表格数据，表格数据为 {data}")
        # df = pd.DataFrame(data)
        # # 保存为Excel文件，不包含索引列
        # df.to_excel(stockup_dir, index=False)
        # if stockup_error_writefile_path != None:
        #     df.to_excel(stockup_error_writefile_path, index=False)
        # logger.info(f"开始写入表格数据data成功")
        logger.info(f"开始写入表格数据，表格数据为 {data}")
        df = pd.DataFrame(data)
        # 保存为Excel文件，不包含索引列
        # df.to_excel(stockup_dir, index=False)
        # logger.info(f"开始写入表格数据data成功")
        abs_path = os.path.abspath(stockup_dir)

        # 使用 xlsxwriter 引擎，生成原生标准xlsx
        with pd.ExcelWriter(abs_path, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False)
        df_read = pd.read_excel(stockup_dir, engine="openpyxl")
        logger.info(f"读取excel shape:{df_read.shape}, 内容:{df_read.to_dict('records')}")
        return self
    def stock_up_file(self):
        """导入需求"""
        stock_up_file_url = "{}/v1/common/File/upload/?auth_token={}".format(self.HC2018_ADMIN_URL, self.auth_token)
        upload_file_url = "{}/v1/stockup/NewStockUp/import".format(self.HC2018_ADMIN_URL)
        error_msg = None
        try:
            # stock_up_file_url = "{}/v1/common/File/upload/?auth_token={}".format(self.HC2018_ADMIN_URL, self.auth_token)
            stock_up_file_res = self.rss.post(url=stock_up_file_url, files=self.files, data=self.payload).json()
            origin_url = jsonpath.jsonpath(stock_up_file_res, '$..origin_url')[0]
            logger.info(f"文件导入服务器的生成地址：{origin_url}")
            # upload_file_url = "{}/v1/stockup/NewStockUp/import".format(self.HC2018_ADMIN_URL)
            upload_file_res = self.rss.post(url=upload_file_url, params={"origin_url": origin_url}, headers=self.headers_json).json()
            # logger.info(json.dumps(upload_file_res, ensure_ascii=False).replace("'", '"'))
            print(upload_file_res)
            if upload_file_res["data"]["error_list"] != []:
                error_msg = jsonpath.jsonpath(upload_file_res, '$..error_msg')[0]
            if error_msg is None:
                logger.info(f"需求导入成功")
            else:
                # 手动抛出异常来测试
                raise ValueError("抛出异常：{}".format(error_msg))
        except Exception as e:
            logger.error(f"捕获到异常: {e}")
            try:
                if error_msg != None:
                    self.files_error = [
                        ('file', ('stockup_error.xlsx', open(stockup_error_dir, 'rb'),
                                  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'))]
                    for item in error_msg:
                        if "补备货与系统不一致" in item and self.MTS_Rep == "备货":
                            error_msg = None
                            self.MTS_Rep = "补货"
                            self.excel_file_write(stockup_error_writefile_path=stockup_error_dir)
                            stock_up_file_error_res = self.rss.post(url=stock_up_file_url, files=self.files_error, data=self.payload).json()
                            origin_url = jsonpath.jsonpath(stock_up_file_error_res, '$..origin_url')[0]
                            print(origin_url)
                            upload_file_error_res = self.rss.post(url=upload_file_url, params={"origin_url": origin_url},
                                                            headers=self.headers_json).json()
                            print(upload_file_error_res)
                            if upload_file_error_res["data"]["error_list"] != []:
                                error_msg = jsonpath.jsonpath(upload_file_error_res, '$..error_msg')[0]
                            if error_msg is None:
                                logger.info(f"需求导入成功")
                            break
                        elif "补备货与系统不一致" in item and self.MTS_Rep == "补货":
                            error_msg = None
                            self.MTS_Rep = "备货"
                            self.excel_file_write(stockup_error_writefile_path=stockup_error_dir)
                            stock_up_file_error_res = self.rss.post(url=stock_up_file_url, files=self.files_error, data=self.payload).json()
                            origin_url = jsonpath.jsonpath(stock_up_file_error_res, '$..origin_url')[0]
                            upload_file_error_res = self.rss.post(url=upload_file_url, params={"origin_url": origin_url},
                                                            headers=self.headers_json).json()
                            # logger.info(json.dumps(upload_file_res, ensure_ascii=False).replace("'", '"'))
                            if upload_file_error_res["data"]["error_list"] != []:
                                error_msg = jsonpath.jsonpath(upload_file_error_res, '$..error_msg')[0]
                            if error_msg is None:
                                logger.info(f"需求导入成功")
                            break
            except Exception as inner_e:
                print(f"在异常处理中又发生了新的异常: {inner_e}")
        print(error_msg)
        return error_msg
    def stockup_audit(self, audit_real_name=None):
        """备货审核"""
        self.worksheet_order_id = []
        msg = ''
        search_url = "{}/v1/audit/StockUpAudit/page".format(self.HC2018_ADMIN_URL)
        search_body = {"goods_name": self.goods_name, "brand_name": self.provider_name,  "audit_user": audit_real_name, "audit_status": "0"}
        search_res = self.rss.post(url=search_url, json=search_body, headers=self.headers_json).json()
        if len(search_res["data"]["data"]) != 0:
            self.worksheet_order_id = jsonpath.jsonpath(search_res, '$..worksheet_order_id')
            for i in range(len(self.worksheet_order_id)):
                stockup_audit_url = "{}/v1/audit/StockUpAudit/audit".format(self.HC2018_ADMIN_URL)
                stockup_audit_body = {"worksheet_order_id": self.worksheet_order_id[i], "audit_status": 2}
                stock_up_audit_res = self.rss.post(url=stockup_audit_url, json=stockup_audit_body,headers=self.headers_json).json()
                logger.info(f'审核后msg：{stock_up_audit_res["msg"]}')
                msg = stock_up_audit_res["msg"]
        if search_res["data"]["data"] ==  []:
            msg = "success"
        return msg
    def replenishment_audit(self, audit_real_name=None):
        """补货审核"""
        self.worksheet_order_id = []
        search_url = "{}/v1/audit/ReplenishmentAudit/page".format(self.HC2018_ADMIN_URL)
        search_body = {"goods_name": self.goods_name, "brand_name": self.provider_name, "audit_user": audit_real_name, "audit_status": "0"}
        logger.info(search_body)
        search_res = self.rss.post(url=search_url, json=search_body, headers=self.headers_json).json()
        logger.info(search_res)
        msg = ''
        if len(search_res["data"]["data"]) != 0:
            self.worksheet_order_id = jsonpath.jsonpath(search_res, '$..worksheet_order_id')
            for i in range(len(self.worksheet_order_id)):
                stockup_audit_url = "{}/v1/audit/ReplenishmentAudit/audit".format(self.HC2018_ADMIN_URL)
                stockup_audit_body = {"worksheet_order_id": self.worksheet_order_id[i], "audit_status": 2}
                stock_up_audit_res = self.rss.post(url=stockup_audit_url, json=stockup_audit_body,headers=self.headers_json).json()
                logger.info(f'审核后msg：{stock_up_audit_res["msg"]}')
                msg = stock_up_audit_res["msg"]
        if search_res["data"]["data"] ==  []:
            msg = "success"
        return msg
    def stockup_inquiry(self, stockup_id=None, goods_number=None):
        """询价"""
        stockup_inquiry_detail_url = "{}/v1/stockup/NewInquiry/findDetail".format(self.HC2018_ADMIN_URL)
        stockup_inquiry_detail_body = {"id": stockup_id}
        stockup_inquiry_detail_res = self.rss.post(url=stockup_inquiry_detail_url, json=stockup_inquiry_detail_body, headers=self.headers_json).json()
        goods_no = stockup_inquiry_detail_res["data"]["goods_no"]
        inquirer_user = stockup_inquiry_detail_res["data"]["inquirer_user"]
        login_real_name = getattr(Data, "login_real_name")
        stockup_inquiry_url = "{}/v1/stockup/NewInquiry/confirmInquiry".format(self.HC2018_ADMIN_URL)
        stockup_inquiry_body = {
            "id": stockup_id,
            "dc": stockup_inquiry_detail_res["data"]["dc"] if stockup_inquiry_detail_res["data"]["dc"] and stockup_inquiry_detail_res["data"]["dc"] != "--" else "1.5年内",
            "delivery": stockup_inquiry_detail_res["data"]["delivery"] if stockup_inquiry_detail_res["data"]["delivery"] and stockup_inquiry_detail_res["data"]["delivery"] not in ["0", "--"] else stockup_inquiry_detail_res["data"]["demand_type"] if stockup_inquiry_detail_res["data"]["demand_type"] and stockup_inquiry_detail_res["data"]["demand_type"] not in ["0", "--"] else "2",
            "demand_type": stockup_inquiry_detail_res["data"]["demand_type"] if stockup_inquiry_detail_res["data"]["demand_type"] and stockup_inquiry_detail_res["data"]["demand_type"] not in ["0", "--"] else stockup_inquiry_detail_res["data"]["delivery"] if stockup_inquiry_detail_res["data"]["delivery"] and stockup_inquiry_detail_res["data"]["delivery"] not in ["0", "--"] else "2",
            "jiaoqi": stockup_inquiry_detail_res["data"]["jiaoqi"] if stockup_inquiry_detail_res["data"]["jiaoqi"] and stockup_inquiry_detail_res["data"]["jiaoqi"] != "--" else "3-7",
            "number": stockup_inquiry_detail_res["data"]["require_number"] if stockup_inquiry_detail_res["data"]["require_number"] else goods_number,
            "package_number": stockup_inquiry_detail_res["data"]["package_number"],
            "package_type": stockup_inquiry_detail_res["data"]["package_type"],
            "remark": stockup_inquiry_detail_res["data"]["remark"] if stockup_inquiry_detail_res["data"]["remark"] else "测试工具导入",
            "supplier_sn": stockup_inquiry_detail_res["data"]["supplier_sn"] if stockup_inquiry_detail_res["data"]["supplier_sn"] and stockup_inquiry_detail_res["data"]["supplier_sn"] != "--" else "hqchip-llsjl",
            # "tax_price": stockup_inquiry_detail_res["data"]["cost_price"] if stockup_inquiry_detail_res["data"]["cost_price"] and stockup_inquiry_detail_res["data"]["cost_price"] not in ["--", "0.00000"] else "0.15",
            "tax_price": str(round(float(stockup_inquiry_detail_res["data"]["cost_price"]), 4)) if stockup_inquiry_detail_res["data"]["stock_type"] == "4" and stockup_inquiry_detail_res["data"]["cost_price"] and stockup_inquiry_detail_res["data"]["cost_price"] not in ["--", "0.00000"] else stockup_inquiry_detail_res["data"]["cost_price"] if stockup_inquiry_detail_res["data"]["cost_price"] and stockup_inquiry_detail_res["data"]["cost_price"] not in ["--", "0.00000"] else "0.15",
            "transfer_number": "",
            "warehouse_in": "",
            "supplier_uuid": stockup_inquiry_detail_res["data"]["supplier_uuid"],
            "urgent": stockup_inquiry_detail_res["data"]["urgent"],
            "is_special_channel": stockup_inquiry_detail_res["data"]["is_special_channel"],
            "attachment": stockup_inquiry_detail_res["data"]["attachment"],
            "attachment_name": stockup_inquiry_detail_res["data"]["attachment_name"],
            "pm_lc_price": stockup_inquiry_detail_res["data"]["competitor_price_info"]["sys_lc_price"] if stockup_inquiry_detail_res["data"]["competitor_price_info"]["sys_lc_price"] and stockup_inquiry_detail_res["data"]["competitor_price_info"]["sys_lc_price"] != "--" and float(stockup_inquiry_detail_res["data"]["competitor_price_info"]["sys_lc_price"]) >= float(stockup_inquiry_detail_res["data"]["cost_price"]) else (str(float(stockup_inquiry_detail_res["data"]["cost_price"]) + 0.003) if stockup_inquiry_detail_res["data"]["competitor_price_info"]["sys_lc_price"] and stockup_inquiry_detail_res["data"]["competitor_price_info"]["sys_lc_price"] != "--" else str(float(stockup_inquiry_detail_res["data"]["cost_price"]) + 0.003)),
            "pm_yh_price": stockup_inquiry_detail_res["data"]["competitor_price_info"]["sys_yh_price"] if stockup_inquiry_detail_res["data"]["competitor_price_info"]["sys_yh_price"] and stockup_inquiry_detail_res["data"]["competitor_price_info"]["sys_yh_price"] != "--" and float(stockup_inquiry_detail_res["data"]["competitor_price_info"]["sys_yh_price"]) >= float(stockup_inquiry_detail_res["data"]["cost_price"]) else (str(float(stockup_inquiry_detail_res["data"]["cost_price"]) + 0.003) if stockup_inquiry_detail_res["data"]["competitor_price_info"]["sys_lc_price"] and stockup_inquiry_detail_res["data"]["competitor_price_info"]["sys_lc_price"] != "--" else str(float(stockup_inquiry_detail_res["data"]["cost_price"]) + 0.003)),
            "inquiry_record": [
                {
                    # 上海恒权电子科技有限公司询价记录
                    "id": stockup_id,
                    "goods_name": stockup_inquiry_detail_res["data"]["goods_name"],
                    "provider_name": stockup_inquiry_detail_res["data"]["provider_name"],
                    "tax_price": str(float(stockup_inquiry_detail_res["data"]["cost_price"]
                                           if stockup_inquiry_detail_res["data"]["cost_price"] and
                                              stockup_inquiry_detail_res["data"]["cost_price"] not in ["--", "0.00000"] else "0.15")
                                     + 0.0600),
                    "number": stockup_inquiry_detail_res["data"]["require_number"] if
                    stockup_inquiry_detail_res["data"]["require_number"] else goods_number,
                    "supplier_sn": "HQCHIP-SHHQ",
                    "package_type": stockup_inquiry_detail_res["data"]["package_type"],
                    "package_number": stockup_inquiry_detail_res["data"]["package_number"],
                    "jiaoqi": "8-9",
                    "dc": "1.5年内",
                    "remark": "",
                    "attachment": "",
                    "attachment_name": ""
                },
                {
                    # 上海茗慧电子科技有限公司询价记录
                    "id": stockup_id,
                    "goods_name": stockup_inquiry_detail_res["data"]["goods_name"],
                    "provider_name": stockup_inquiry_detail_res["data"]["provider_name"],
                    "tax_price": str(float(stockup_inquiry_detail_res["data"]["cost_price"]
                                           if stockup_inquiry_detail_res["data"]["cost_price"] and
                                              stockup_inquiry_detail_res["data"]["cost_price"] not in ["--", "0.00000"] else "0.15")
                                     - 0.0300),
                    "number": stockup_inquiry_detail_res["data"]["require_number"] if
                    stockup_inquiry_detail_res["data"]["require_number"] else goods_number,
                    "supplier_sn": "HQCHIP-HHXX",
                    "package_type": stockup_inquiry_detail_res["data"]["package_type"],
                    "package_number": stockup_inquiry_detail_res["data"]["package_number"],
                    "jiaoqi": "3-7",
                    "dc": "1.5年内",
                    "remark": "",
                    "attachment": "",
                    "attachment_name": ""
                }
            ]
        }
        print("stockup_inquiry_body: ", stockup_inquiry_body)
        if login_real_name == inquirer_user:
            stockup_inquiry_res = self.rss.post(url=stockup_inquiry_url, json=stockup_inquiry_body, headers=self.headers_json).json()
            if stockup_inquiry_res['msg'] != "success":
                # 目前应该只剩下包装类型和包装数量对不上，得倒查请求资料接口
                goods_search_url = "{}/v1/goods/DgkGoods/findList".format(self.HC2018_ADMIN_URL)
                goods_search_body = {"goods_no": goods_no}
                goods_search_res = self.rss.post(url=goods_search_url, json=goods_search_body, headers=self.headers_json).json()
                goods_id = jsonpath.jsonpath(goods_search_res, "$..goods_id")[0]
                goods_detail_url = "{}/v1/goods/DgkGoods/viewOriginData".format(self.HC2018_ADMIN_URL)
                goods_detail_body = {"goods_id": goods_id, "origin": True}
                goods_detail_res = self.rss.post(url=goods_detail_url, json=goods_detail_body, headers=self.headers_json).json()
                goods_package_type = jsonpath.jsonpath(goods_detail_res, "$..package_info")[0].split("(")[0]
                goods_package_number = jsonpath.jsonpath(goods_detail_res, "$..spq")[0]
                stockup_inquiry_body["package_type"] = goods_package_type
                stockup_inquiry_body["package_number"] = goods_package_number
                for record in stockup_inquiry_body["inquiry_record"]:
                    record["package_type"] = goods_package_type
                    record["package_number"] = goods_package_number
                stockup_inquiry_res = self.rss.post(url=stockup_inquiry_url, json=stockup_inquiry_body, headers=self.headers_json).json()
                if "采购价不能高于填写的LC价格" in stockup_inquiry_res["msg"]:
                    stockup_inquiry_body["pm_lc_price"] = stockup_inquiry_body["tax_price"]
                    stockup_inquiry_res = self.rss.post(url=stockup_inquiry_url, json=stockup_inquiry_body, headers=self.headers_json).json()
            print("询价执行结果为{}".format(stockup_inquiry_res))
        else:
            logger.info("当前系统登录人不为所要记录询价记录的询价，不能提交询价，请检查!!")
        return self

    def stockup_list(self):
        """补备货列表"""
        n = 0
        while True:
            try:
                search_url = "{}/v1/stockup/NewStockUp/findList".format(self.HC2018_ADMIN_URL)
                # 查找待审核数据
                self.search_body = {"goods_name": self.goods_name, "provider_name": self.provider_name, "stock_type": "",  "stock_status": "20"}
                # 按优先级排列的状态列表
                status_list = ["20", "21", "1", "5", "11", "-100"]
                search_res = None

                for status in status_list:
                    self.search_body["stock_status"] = status
                    search_res = self.rss.post(url=search_url, json=self.search_body, headers=self.headers_json).json()
                    print("搜索状态 {}: {}".format(status, search_res))

                    # 如果找到了数据，跳出循环
                    if search_res["data"]["data"] != []:
                        break

                # 最终结果
                print("最终结果: {}".format(search_res))
                self.stockup_goods_name = jsonpath.jsonpath(search_res, '$..goods_name')
                self.stockup_provider_name = jsonpath.jsonpath(search_res, '$..provider_name')
                self.stockup_id = jsonpath.jsonpath(search_res, '$..id')
                self.cost_price = jsonpath.jsonpath(search_res, '$..cost_price')
                self.goods_number = jsonpath.jsonpath(search_res, '$..goods_number')
                self.origin = jsonpath.jsonpath(search_res, '$..origin')
                self.stock_status = jsonpath.jsonpath(search_res, '$..stock_status')
                self.stock_type = jsonpath.jsonpath(search_res, '$..stock_type')
                self.stock_order_type = jsonpath.jsonpath(search_res, '$..lable_type_cn')
                self.supplier_sn = jsonpath.jsonpath(search_res, '$..supplier_sn')
                # 检查数据路径是否存在
                data_list = search_res.get("data", {}).get("data", {})
                self.order_bool_flags = []
                exclude_statuses = ["-3"]
                # 是否存在订单号
                if isinstance(data_list, list):
                    for item in data_list:
                        order_sn = item.get("order_sn")
                        stock_status = item.get("stock_status")
                        # 检查是否stock_status在排除之外
                        # 检查是否order_sn有效
                        is_valid = order_sn is not None and order_sn != "" and stock_status not in exclude_statuses
                        if stock_status not in exclude_statuses:
                            self.order_bool_flags.append(is_valid)
                if self.stock_status[0] == "1":
                    StayPerfectMeans(self.rss, self.goods_name, self.provider_name, source_type='备货').mian_stay_perfect_means_new()
                    for key in self.packer_type_json:
                        if key == self.packer:
                            self.packer_type = self.packer_type_json[key]
                    GoodsMeans(self.rss, self.goods_name, self.provider_name, self.packer_type).mian_means_stay_perfect()
                    GoodsMeans(self.rss, self.goods_name, self.provider_name, self.packer_type).mian_means_update()
                    # 待完善资料完成后也需要走：询价
                    self.stockup_inquiry(self.stockup_id[0], self.goods_number[0])
                    self.search_body["stock_status"] = "20"
                    search_res = self.rss.post(url=search_url, json=self.search_body, headers=self.headers_json).json()
                    self.stockup_goods_name = jsonpath.jsonpath(search_res, '$..goods_name')
                    self.stockup_provider_name = jsonpath.jsonpath(search_res, '$..provider_name')
                    self.stockup_id = jsonpath.jsonpath(search_res, '$..id')
                    self.cost_price = jsonpath.jsonpath(search_res, '$..cost_price')
                    self.goods_number = jsonpath.jsonpath(search_res, '$..goods_number')
                    self.origin = jsonpath.jsonpath(search_res, '$..origin')
                    self.stock_status = jsonpath.jsonpath(search_res, '$..stock_status')
                    self.stock_type = jsonpath.jsonpath(search_res, '$..stock_type')
                    self.stock_order_type = jsonpath.jsonpath(search_res, '$..lable_type_cn')
                    self.supplier_sn = jsonpath.jsonpath(search_res, '$..supplier_sn')
                    # 检查数据路径是否存在
                    data_list = search_res.get("data", {}).get("data", {})
                    # 是否存在订单号
                    if isinstance(data_list, list):
                        for item in data_list:
                            order_sn = item.get("order_sn")
                            stock_status = item.get("stock_status")
                            # 检查是否stock_status在排除之外
                            # 检查是否order_sn有效
                            is_valid = order_sn is not None and order_sn != "" and stock_status not in exclude_statuses
                            if stock_status not in exclude_statuses:
                                self.order_bool_flags.append(is_valid)
                if self.stock_status[0] == "5":
                    # 待确认
                    #确认补货
                    confirm_stock_url = "{}/v1/stockup/NewStockUp/confirmStock".format(self.HC2018_ADMIN_URL)
                    confirm_stock_stock_body = {"id": self.stockup_id[0]}
                    confirm_stock_stock_res = self.rss.post(url=confirm_stock_url, json=confirm_stock_stock_body,headers=self.headers_json).json()
                    # print("执行结果为{}".format(confirm_stock_stock_res))
                    self.stockup_inquiry(self.stockup_id[0], self.goods_number[0])
                    self.search_body["stock_status"] = "20"
                    search_res = self.rss.post(url=search_url, json=self.search_body, headers=self.headers_json).json()
                    self.stockup_goods_name = jsonpath.jsonpath(search_res, '$..goods_name')
                    self.stockup_provider_name = jsonpath.jsonpath(search_res, '$..provider_name')
                    self.stockup_id = jsonpath.jsonpath(search_res, '$..id')
                    self.cost_price = jsonpath.jsonpath(search_res, '$..cost_price')
                    self.goods_number = jsonpath.jsonpath(search_res, '$..goods_number')
                    self.origin = jsonpath.jsonpath(search_res, '$..origin')
                    self.stock_status = jsonpath.jsonpath(search_res, '$..stock_status')
                    self.stock_type = jsonpath.jsonpath(search_res, '$..stock_type')
                    self.stock_order_type = jsonpath.jsonpath(search_res, '$..lable_type_cn')
                    self.supplier_sn = jsonpath.jsonpath(search_res, '$..supplier_sn')
                    # 检查数据路径是否存在
                    data_list = search_res.get("data", {}).get("data", {})
                    # 是否存在订单号
                    if isinstance(data_list, list):
                        for item in data_list:
                            order_sn = item.get("order_sn")
                            stock_status = item.get("stock_status")
                            # 检查是否stock_status在排除之外
                            # 检查是否order_sn有效
                            is_valid = order_sn is not None and order_sn != "" and stock_status not in exclude_statuses
                            if stock_status not in exclude_statuses:
                                self.order_bool_flags.append(is_valid)
                if self.stock_status[0] == "11":
                    # 待询价
                    self.stockup_inquiry(self.stockup_id[0], self.goods_number[0])
                    self.search_body["stock_status"] = "20"
                    search_res = self.rss.post(url=search_url, json=self.search_body, headers=self.headers_json).json()
                    self.stockup_goods_name = jsonpath.jsonpath(search_res, '$..goods_name')
                    self.stockup_provider_name = jsonpath.jsonpath(search_res, '$..provider_name')
                    self.stockup_id = jsonpath.jsonpath(search_res, '$..id')
                    self.cost_price = jsonpath.jsonpath(search_res, '$..cost_price')
                    self.goods_number = jsonpath.jsonpath(search_res, '$..goods_number')
                    self.origin = jsonpath.jsonpath(search_res, '$..origin')
                    self.stock_status = jsonpath.jsonpath(search_res, '$..stock_status')
                    self.stock_type = jsonpath.jsonpath(search_res, '$..stock_type')
                    self.stock_order_type = jsonpath.jsonpath(search_res, '$..lable_type_cn')
                    self.supplier_sn = jsonpath.jsonpath(search_res, '$..supplier_sn')
                    # 检查数据路径是否存在
                    data_list = search_res.get("data", {}).get("data", {})
                    # 是否存在订单号
                    if isinstance(data_list, list):
                        for item in data_list:
                            order_sn = item.get("order_sn")
                            stock_status = item.get("stock_status")
                            # 检查是否stock_status在排除之外
                            # 检查是否order_sn有效
                            is_valid = order_sn is not None and order_sn != "" and stock_status not in exclude_statuses
                            if stock_status not in exclude_statuses:
                                self.order_bool_flags.append(is_valid)
                break
            except Exception as e:
                n += 1
                if n < 6:
                   logger.warning(
                            f"第 {n} 次,补备货列表没有找到型号为:{self.goods_name},等待30秒后系统自动重试,错误信息:{e}")
                   time.sleep(30)
                else:
                   logger.error(f"补备货列表查找型号为:{self.goods_name} 出错,请手动检查该型号是否存在")
                   raise ValueError
        return self
    def mian_self_file_stockup(self, IsAudit=None):
        # 当goods_no_type为是时且goods_no为空先去拿资料接口得芯城编码，在进行对接统一接口------2024-12-25更新
        # and self.goods_no_type == '是'
        if self.goods_no == '':
            print("当goods_no_type为是时且goods_no为空先去拿资料接口得芯城编码")
            self.goods_no, self.packer, self.packer_number, self.goods_encap = self.goods_no_search()
        error_msg = None
        if self.import_file_type == "1":
            self.excel_file_write()
            error_msg = self.stock_up_file()
        # error_msg = None
        msg = None
        if error_msg == None and IsAudit== None:
            self.stockup_list()
            print("此时stock_status: {}".format(self.stock_status))
            if self.stock_status[0] == "1":
                self.stockup_list()
            # print(f"23: {self.stockup_id}")
            for i in range(len(self.stockup_id)):
                cost_price = [float(re.findall(r'\d+\.\d+', p)[0]) for p in self.cost_price][i]
                if self.origin[i] in ("1", "2", "3", "8", "9", "12", "13"):
                    logger.info(f"补备货id为：{self.stockup_id[i]}走备货审核流程")
                    WorkSheet(self.rss).work_sheet_search("备货审核", order_tag=self.stock_order_type[i], order_bool_flag=self.order_bool_flags[i])
                    self.user_name = getattr(Data, 'user_name')   # 流程配置里面审核人登陆用户名
                    self.start_amount = getattr(Data, 'start_amount')  # 流程配置里面审核人所处的节点生效最低金额
                    self.audit_real_name = getattr(Data, 'audit_real_name')  # 流程配置里面审核人的真实姓名
                    for m in range(len(self.user_name)):
                       logger.info(f"此时获取启动流程中心配置的审核人为：{self.user_name[m]}的生效金额为：{self.start_amount[m]}，而此时采购金额为：{float(cost_price) * float(self.goods_number[i])}")
                       if float(cost_price) * float(self.goods_number[i]) >= float(self.start_amount[m]):
                           if self.user_name[m] in self.user_pwd_json:
                                 user_pwd_params = {'admin_name': 'admin', "admin_pwd": 'HQ@uat@666', "user": self.user_name[m], "pwd": self.user_pwd_json[self.user_name[m]]}
                                 Hc2018_params = {"Hc2018": user_pwd_params}
                                 write_yaml(account_yaml, Hc2018_params)
                                 Login().login()
                                 self.auth_token = getattr(Data, 'dos_auth_token')
                                 self.headers_json["Authorization"] = self.auth_token
                                 msg = self.stockup_audit(self.audit_real_name[m])
                           else:
                                logger.error(f'审核人：{self.user_name[m]} 不存在字典：self.user_pwd_json，请补充')
                                break
                           # continue
                       else:
                           break
                    continue
                elif self.origin[i] in ("4", "5", "6", "7", "10", "11"):
                    WorkSheet(self.rss).work_sheet_search("补货审核", order_tag=self.stock_order_type[i], order_bool_flag=self.order_bool_flags[i])
                    logger.info(f"补备货id为：{self.stockup_id[i]}走补货审核流程")
                    self.user_name = getattr(Data, 'user_name')
                    self.start_amount = getattr(Data, 'start_amount')
                    self.audit_real_name = getattr(Data, 'audit_real_name')
                    for m in range(len(self.user_name)):
                       logger.info(f"此时获取启动流程中心配置的审核人为：{self.user_name[m]}的生效金额为：{self.start_amount[m]}，而此时采购金额为：{float(cost_price) * float(self.goods_number[i])}")
                       if  float(cost_price) * float(self.goods_number[i]) >= float(self.start_amount[m]):
                           if self.user_name[m] in self.user_pwd_json:
                                 user_pwd_params = {'admin_name': 'admin', "admin_pwd": 'HQ@uat@666', "user": self.user_name[m],
                                              "pwd": self.user_pwd_json[self.user_name[m]]}
                                 Hc2018_params = {"Hc2018": user_pwd_params}
                                 write_yaml(account_yaml, Hc2018_params)
                                 Login().login()
                                 self.auth_token = getattr(Data, 'dos_auth_token')
                                 self.headers_json["Authorization"] = self.auth_token
                                 msg = self.replenishment_audit(self.audit_real_name[m])
                           else:
                                logger.error(f'审核人：{self.user_name[m]} 不存在字典：self.user_pwd_json，请补充')
                                break
                           # continue
                       else:
                           break
                    continue
                else:
                    logger.error(f"补备货id为：{self.stockup_id[i]}为未知名补备货，请检查")
                    break
            setattr(Data, 'stock_goods_name', self.goods_name if self.goods_name != None  else self.stockup_goods_name[0])
            setattr(Data, 'stock_provider_name', self.provider_name if self.provider_name != None else self.stockup_provider_name[0])
            setattr(Data, 'stock_supplier_sn', self.supplier_sn[0])
            setattr(Data, 'stock_order_sn', self.order_sn if self.order_sn != None else "")
        else:
            if error_msg != None:
                msg = error_msg
                logger.error(f"上传文件报错，报错信息：{msg}")
            else:
                msg = error_msg
                logger.error(f"脚本不执行：审核")
            logger.info(f"111233423：{msg}")
        return msg, self.MTS_Rep, self.packer, self.packer_number
    def goods_no_search(self):
        """指定型号获取其芯城编码、包装方式、包装数量、封装"""
        (self.goods_id, self.brand_id, self.goods_no, self.is_special_type, self.special_key,
         self.goods_encap) = GoodsMeans(self.rss, self.goods_name, self.provider_name).goods_means_list()
        # print(self.goods_no)
        if self.goods_no == False:
            print("不存在, 走新增操作")
            for key in self.packer_type_json:
                self.packer_type = self.packer_type_json[key]
                self.goods_id, self.brand_id, self.goods_no = GoodsMeans(self.rss, self.goods_name, self.provider_name, self.packer_type,
                                            self.packer_number).mian_means_add()

                # print(self.goods_no)
                return self.goods_no, self.packer_type, self.packer_number, self.goods_encap
        else:
            packer = None
            packer_number = None
            for i in range(len(self.goods_no)):
                if self.goods_encap[i] == self.encap:
                    print("存在")
                    self.goods_no = self.goods_no[i]
                    packer, packer_number = GoodsMeans(self.rss).mian_goods_search(goods_no=self.goods_no)
                    break
            if packer != None and packer != self.packer:
                self.packer = packer
            if packer_number != None and packer_number != self.packer_number:
                self.packer_number = packer_number
            print(self.goods_no)
            return self.goods_no, self.packer, self.packer_number, self.goods_encap

    def mian_self_file_stockup1(self):
        if self.goods_no == None:
            self.goods_no = self.goods_no_search()
        self.excel_file_write()
        error_msg = self.stock_up_file()









if __name__ == '__main__':
    file = None
    goods_name = 'WQSE-2X20H01LDAKTR'
    provider_name = 'WORLDPO'
    encap = '-'
    packer = '卷装'
    packer_number = 1000
    purchase_price = '0.89533'
    stock_number = 1000
    stock_type = '常规备货'
    MTS_Rep = '补货'
    warehouse_name = '深圳华秋东莞仓'
    order_sn = ''
    import_file_type = '1'
    goods_no = ''
    goods_no_type = '是'
    from huaqiu_order_api.HC2018_admin.login.login import Login
    from huaqiu_order_api.HC2018_admin.supplier_goods_publish.consign_publish import ConsignPublish
    from huaqiu_order_api.HQCHIP_SOO.login import SOOLogin
    from huaqiu_order_api.HQCHIP_WMS.wms_in_warehouse import WmsInWarehouse
    import pandas as pd
    target_rss = Login().login()
    if file:
        data = pd.read_excel(r"{}".format(file))
        if isinstance(data, pd.DataFrame):
            goods_name = data["型号(必填)"].tolist()
    if isinstance(goods_name, list):
        for i in range(len(goods_name)):
            provider_name = ""
            StockUp(target_rss, goods_name[i], provider_name, encap, packer, packer_number, purchase_price, stock_number, stock_type,
                    MTS_Rep,  warehouse_name, order_sn, import_file_type, goods_no, goods_no_type).mian_self_file_stockup()
    else:
        StockUp(target_rss, goods_name, provider_name, encap, packer, packer_number, purchase_price, stock_number, stock_type,
                MTS_Rep,  warehouse_name, order_sn, import_file_type, goods_no, goods_no_type).mian_self_file_stockup()
    if stock_type == '寄售备货':
        order_sn, inn_order_list = ConsignPublish(target_rss, consign_sn=None, goods_name=goods_name,
                                                                              supplier_sn=None).main_consign_publish_delivery(status=5)
        setattr(Data, 'inn_sn', inn_order_list[0] if inn_order_list != [] else '')
        wms_target_rss = SOOLogin("uat-wms.huaqiu.com", "wms_base").target_login()
        WmsInWarehouse(wms_target_rss).wms_warehousing().wms_theupper_list()
    # r = StockUp("rdd").excel_file_write()
    # print(r)




    # StockUp(target_rss, goods_name, provider_name, encap, packer, packer_number, purchase_price, stock_number, stock_type,
    #         MTS_Rep,  warehouse_name, order_sn, import_file_type, goods_no, goods_no_type).goods_no_search()