import re
import time
from datetime import datetime

import jsonpath
import requests
import yaml
from bs4 import BeautifulSoup

from huaqiu_order_api.HQCHIP_ERP.erp_order_stock import ErpOrderStock
from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_data import Data
from huaqiu_order_api.common.my_path import yaml_file, account_yaml
from huaqiu_order_api.common.yaml_handler import write_yaml


class ErpStockPurchase:

    def __init__(self, rss, goods_name=None, supplier_sn=None, order_sn=None, relevance_order_sn=None):
        """
        :param account:  登录ERP账号
        :param psw:  登录ERP密码
        :param order_sn:  前台商城生成订单编号
        :param uesr:    前台商城生成订单编号的用户名称
        """
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.ERP_URL = data['ERP_URL']
        self.goods_name = getattr(Data, 'stock_goods_name', '')
        self.supplier_sn = getattr(Data, 'stock_supplier_sn', '')
        self.relevance_order_sn = getattr(Data, 'stock_order_sn', '')
        self.dc = getattr(Data, 'dc', '')
        if self.goods_name == '' and goods_name!= None:
            self.goods_name = goods_name
        if self.supplier_sn == '' and supplier_sn != None:
            self.supplier_sn = supplier_sn
        keytype_json = {"备货单号": "plan_sn", "采购单号": "erp_picking_sn", "关联订单": "other_order_sn"}
        self.rss = rss
        self.headers = {'Content-Type': 'application/x-www-form-urlencoded',
                        "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://www.huaqiu.com)"
                        }
        self.json_head = {"Content-Type": "application/json",
                          "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://www.huaqiu.com)"
                          }
        self.warehouse_name_json = {"深圳华秋东莞仓": 2, "长沙华秋仓": 8}
        if order_sn != None and isinstance(order_sn, str):
           if order_sn[0:2] in ['SUP', 'SCM']:
               key = '备货单号'

           elif order_sn[0:1] in ['PO']:
               key = '采购单号'
           else:
               key = '关联订单'
           self.keytype = keytype_json[key]
        else:
            self.keytype = 'plan_sn'
            if self.relevance_order_sn != "":
                self.keytype = 'other_order_sn'
    def stock_up_plan(self):
        """
        备货计划任务操作
        """
        # 查询备货单号
        n = 0
        while True:
            try:
                search_plan_url = '{}/StockUpPlan/index'.format(self.ERP_URL)
                search_plan_body = {"goods_name": self.goods_name, "keytype": self.keytype, "keyword": self.relevance_order_sn, "supplier_sn": self.supplier_sn, "status": -1}
                search_plan_res = self.rss.post(url=search_plan_url, data=search_plan_body, headers=self.headers).text
                # logger.info(re.search('(<a  href="/StockUpPlan/detail/id/)([0-9]{5})', search_plan_res).group(2))
                plan_id = re.search('(<a  href="/StockUpPlan/detail/id/)([0-9]*)', search_plan_res).group(2)
                logger.info(f"第{n+1}次访问备货计划列表搜索完成,获取型号：{self.goods_name}的第一条待处理数据的plan_id: {plan_id}")

                keyword = re.split('(rel="StockUpPlanDetail" target="navTab" title=")', search_plan_res)[2].split('明细" >')[0]
                logger.info(f"搜索完成,获取型号：{self.goods_name}的第一条待处理数据的备货单号: {keyword}")
                search_plan_body_review = {"goods_name": self.goods_name, "keytype": "plan_sn", "keyword": keyword}
                search_plan_review_res = self.rss.post(url=search_plan_url, data=search_plan_body_review,headers=self.headers).text
                plan_id_review = re.search('(<a  href="/StockUpPlan/detail/id/)([0-9]*)',search_plan_review_res).group(2)
                if plan_id_review == plan_id:
                    logger.info(f"复验搜索成功，获取plan_id: {plan_id_review}")
                break
            except Exception as e:
                n += 1
                if n < 6:
                    logger.warning(f"第 {n} 次,备货计划列表没有找到获取型号：{self.goods_name}第一条待处理数据的,等待30秒后系统自动重试,错误信息:{e}")
                    time.sleep(30)
                else:
                    logger.error(f"备货计划列表没有找到获取型号：{self.goods_name} 出错,请手动检查备货计划列表是否存在")
                    raise ValueError
        time.sleep(2)



        # 生成采购单号
        stock_up_plan_audit_url = '{}/StockUpPlan/audit/navTabId/StockUpPlan'.format(self.ERP_URL)
        stock_up_plan_audit_body = {"id": plan_id_review}
        stock_up_plan_audit_res = self.rss.post(url=stock_up_plan_audit_url, data=stock_up_plan_audit_body,headers=self.headers).json()
        plan_audit_msg = stock_up_plan_audit_res["message"]
        if plan_audit_msg == '采购成功!':
            logger.info("生成采购单成功")
            search_plan_purchase_res = self.rss.post(url=search_plan_url, data=search_plan_body_review, headers=self.headers).text
            self.purchase_sn = search_plan_purchase_res.split('rel="PurchaseDetail" target="navTab"  title="')[1].split('明细" >')[0]
            self.purchase_id =  re.search('(<a  href="/Purchase/detail/id/)([0-9]*)', search_plan_purchase_res).group(2)
            logger.info(f"搜索成功。获取到采购单号：{self.purchase_sn}，采购单号id：{self.purchase_id}")
        return self


    def stock_up_purchase_affirm(self):
        """
        采购单号确认
        """
        # self.purchase_id = 146071
        # self.purchase_sn = "PO00438042"
        purchase_detail_url = "{}/purchase/detail?id={}&navTabId=PurchaseDetail".format(self.ERP_URL, self.purchase_id)
        purchase_detail_res = self.rss.get(url=purchase_detail_url).text
        currency_code = re.findall(r'币种：(\w+)', purchase_detail_res)[0]
        tax_rate = re.findall(r'税率：(\w+)', purchase_detail_res)[0] if re.findall(r'税率：(\w+)', purchase_detail_res) else None  # 没有就返回 None
        company_id = re.search('(<a class="blue company_name_text" href="/NewSupplier/detail/id/)([0-9]*)', purchase_detail_res).group(2)
        # print(company_id)
        warehouse_id = None
        warehouse_name = re.findall(r'交货仓库：(\w+)', purchase_detail_res)[0]
        for key in self.warehouse_name_json:
            if key == warehouse_name:
                warehouse_id = self.warehouse_name_json[key]
                ic_order_params = {'goods_id': '', "number": '', "warehouse_id": warehouse_id, "vat_type": "0"}
                inn_params = {"HQCHIP_GOODS": ic_order_params}
                write_yaml(account_yaml, inn_params)
        # 修改采购员
        update_purchaser_url = "{}/Purchase/click_set/navTabId/PurchaseDetail".format(self.ERP_URL)
        update_purchaser_body = {"picking_uid": 701, "id": self.purchase_id}
        update_purchaser_res = self.rss.post(url=update_purchaser_url, data=update_purchaser_body).json()
        # print(update_purchaser_res)
        warehouse_name_json = {"深圳华秋东莞仓": 2, "长沙华秋仓": 8}
        delivery_warehouse_id = None
        for key in warehouse_name_json:
            if key == warehouse_name:
                delivery_warehouse_id = warehouse_name_json[key]
                break
        # 修改基本信息
        plan_receive_date = str(datetime.now()).split(' ')[0]
        purchase_basic_information_update_url = '{}/Purchase/click_set'.format(self.ERP_URL)
        purchase_basic_information_update_body = {"id": self.purchase_id, "save": 1,
                                                  "purchasing_company_id": 1,
                                                  "delivery_warehouse_id": warehouse_id if warehouse_id != None else 2,
                                                  "purchasing_type": 5,
                                                  "second_type": 1,
                                                  "transaction_type": 1,
                                                  "seal_id": 1,
                                                  "plan_receive_date": plan_receive_date,
                                                  "supplier_pay_type": 2,
                                                  "account_cycle": 0,
                                                  "shipping_pay_type": 1,
                                                  "ajax": 1,
                                                  "is_iframe": 1
                                                  }
        if warehouse_name != None and delivery_warehouse_id != None:
            purchase_basic_information_update_body["delivery_warehouse_id"] = delivery_warehouse_id
        print(purchase_basic_information_update_body)
        purchase_basic_information_update_res = self.rss.post(url=purchase_basic_information_update_url, data=purchase_basic_information_update_body).json()
        logger.info("更新基本信息成功")
        if currency_code == "CNY" and (tax_rate == "-" or tax_rate == None):
            update_tax_rate_body = {
                        "id": self.purchase_id,
                        "save": 1,
                        "currency": 1,
                        "tax_id": 6,
                        "misc_fee": 0.0000,
                        "exchange_rate": 1,
                        "shipping_pay_type": 1,
                        "ajax": 1,
                        "is_iframe": 1
                    }
            update_tax_rate_res = self.rss.post(url=purchase_basic_information_update_url, data=update_tax_rate_body).json()
            # print(update_tax_rate_res)
        # 确认采购单
        purchase_affirm_url = '{}/Purchase/confirm/id/{}/navTabId/PurchaseDetail'.format(self.ERP_URL, self.purchase_id)
        purchase_affirm_res = self.rss.post(url=purchase_affirm_url).text
        # print(purchase_affirm_res)
        if "供应商银行信息未选择" in purchase_affirm_res:
            print("供应商银行信息未选择")
            company_blank_url = '{0}/Purchase/userbank/user_id/{1}/picking_id/{2}/navTabId/DeclarePayDetail'.format(self.ERP_URL, company_id, self.purchase_id)
            company_blank_res = self.rss.get(url=company_blank_url).text
            blank_id = re.findall(r'<td><input type="radio" name="bank_id" value="(\d+)"', company_blank_res)[0]
            update_company_blank_url = "{}/Purchase/userbank/".format(self.ERP_URL)
            update_company_blank_body = {
                                    "picking_id": self.purchase_id,
                                    "bank_id": blank_id,
                                    "user_id": company_id
                                }
            update_company_blank_res = self.rss.post(url=update_company_blank_url, data=update_company_blank_body).json()
            print(update_company_blank_res)
            if update_company_blank_res["info"] == '对应供应商银行信息更新失败':
                print(self.supplier_sn)
                from huaqiu_order_api.HQCHIP_SRM.partner_settle.partner_potential import PartnerPotential
                PartnerPotential(target_rss, supplierBackName=self.supplier_sn).mian_potential_partner_update("update_Brand")
                company_blank_url = '{0}/Purchase/userbank/user_id/{1}/picking_id/{2}/navTabId/DeclarePayDetail'.format(
                    self.ERP_URL, company_id, self.purchase_id)
                company_blank_res = self.rss.get(url=company_blank_url).text
                blank_id = re.findall(r'<td><input type="radio" name="bank_id" value="(\d+)"', company_blank_res)[0]
                update_company_blank_body["bank_id"] = blank_id
                update_company_blank_res = self.rss.post(url=update_company_blank_url,data=update_company_blank_body).json()
                print(update_company_blank_res)
            purchase_affirm_res = self.rss.post(url=purchase_affirm_url).text
            # print(purchase_affirm_res)
        elif "采购批次不能为空" in purchase_affirm_res:
            # 获取采购单里面存在明细id
            detail_compass_url = '{}/Purchase/detail_compass?id={}'.format(self.ERP_URL, self.purchase_id)
            detail_compass_res = self.rss.get(url=detail_compass_url).json()
            item_id = jsonpath.jsonpath(detail_compass_res, "$.data.wait_delivery")[0]
            # print(item_id)
            # 获取到的item_id是一个列表，里面有多个id，采取所有明细都为同一个采购批次，即要拼接传入的id，以逗号分隔
            # 确保所有元素为字符串类型
            str_list = list(map(str, item_id))
            # 使用 join() 方法拼接
            item_id_str = ",".join(str_list)
            if self.dc == "":
                # 根据当前日期去锁定生产周期 生产周期格式年份后两位+周 比如2024年的第39周   2439+
                # 获取当前日期
                current_date = datetime.now()
                # 计算当前日期是本年度的第几个周
                week_number = current_date.isocalendar()[1]
                # 获取本年度的最后两位数字，如果获取周数小于10，则前面补0
                year_last_two_digits = current_date.year % 100
                self.dc = str(year_last_two_digits) + f'0{week_number}+' if week_number < 10 else str(
                    week_number) + "+"
            else:
                if self.is_valid_year_week(self.dc) == True:
                    logger.info("生产周期格式正确，无需修改")
                    self.dc = str(self.dc) + "+"
                else:
                    self.dc = 'test+'
            update_purchase_item_batch_url = '{}/Purchase/batchPurchaseBatchNumSave'.format(self.ERP_URL)
            update_purchase_item_batch_body = {
                                    "id": self.purchase_id,
                                    "item_id": item_id_str,
                                    "offer_batch_number": self.dc,
                                    "ajax": 1,
                                    "is_iframe": 1
                                }
            # print(update_purchase_item_batch_body)
            update_purchase_item_batch_res = self.rss.post(url=update_purchase_item_batch_url, data=update_purchase_item_batch_body).text
            # print(update_purchase_item_batch_res)
            if "没有权限" in update_purchase_item_batch_res.encode('utf-8').decode('unicode_escape'):
                print("没有权限")
                # 退出登录，切换至超级管理员操作
                self.rss.get(url=self.ERP_URL + "/AuthLogin/ssoLogout")
                HQCHIP_SOO_update = {"admin_name": "admin", "admin_pwd": 'HQ@uat@666',
                                     "pro_pwd": "auth221313", "pro_user": "zhangbajun",
                                     "pwd": "HQ@uat@666", "user": "admin"}
                HQCHIP_SOO_update_params = {'HQCHIP_SOO': HQCHIP_SOO_update}
                write_yaml(account_yaml, HQCHIP_SOO_update_params)
                self.rss = SOOLogin("uat-e.hqchip.com", "AuthLogin").target_login()
                update_purchase_item_batch_res = self.rss.post(url=update_purchase_item_batch_url, data=update_purchase_item_batch_body).text
                # print(update_purchase_item_batch_res)
            purchase_affirm_res = self.rss.post(url=purchase_affirm_url).text
        elif "存在未通过毛利审核的明细" in purchase_affirm_res:
                logger.info("采购单审核失败")
                return self
            # print(purchase_affirm_res)

        logger.info("确认采购单成功")
        return self

    def stock_up_purchase_audit(self):
        """采购单审核"""
        #获取审核id
        try:
            stock_up_purchase_audit_list_url = "{}/PurchaseOrderAudit/index".format(self.ERP_URL)
            stock_up_purchase_audit_list_body = {"keyword": self.purchase_sn, "search_key": "order_sn"}
            stock_up_purchase_audit_list_res = self.rss.post(url=stock_up_purchase_audit_list_url, data=stock_up_purchase_audit_list_body).text
            audit_id = re.search('(<a href="/PurchaseOrderAudit/audit/id/)([0-9]*)', stock_up_purchase_audit_list_res).group(2)
            logger.info(f"搜索成功，获取到审核id为：{audit_id}")
            stock_up_purchase_audit_url = '{}/PurchaseOrderAudit/audit/navTabId/PurchaseOrderAuditAudit'.format(self.ERP_URL)
            stock_up_purchase_audit_body = {"id": audit_id, "checked": 1, "ajax": 1, "is_iframe": 1}
            stock_up_purchase_audit_res = self.rss.post(url=stock_up_purchase_audit_url, data= stock_up_purchase_audit_body).text
        except:
            pass

        return self

    def stock_up_purchase_negative_profit_audit(self):
        """IC整单毛利审核"""
        try:
            stock_up_purchase_negative_profit_audit_list_url = "{}/OrderGrossProfitAudit/index".format(self.ERP_URL)
            stock_up_purchase_negative_profit_audit_list_body = {"order_sn": self.relevance_order_sn}
        except:
            pass

        return self

    def stock_up_purchase_deliver_goods(self):
        """ 确认发货，生成出库单"""
        stock_up_purchase_deliver_goods_url = "{}/Purchase/confirmOrderPlaced/id/{}/navTabId/PurchaseDetail".format(self.ERP_URL, self.purchase_id)
        print(stock_up_purchase_deliver_goods_url)
        stock_up_purchase_deliver_goods_res = self.rss.post(url=stock_up_purchase_deliver_goods_url).text
        print(stock_up_purchase_deliver_goods_res)
        if "推送合作商下单失败" in stock_up_purchase_deliver_goods_res:
            logger.info("推送合作商下单失败")
            stock_up_purchase_deliver_goods_res = self.rss.post(url=stock_up_purchase_deliver_goods_url).text
            print(stock_up_purchase_deliver_goods_res)
        logger.info(f'采购单：{self.purchase_sn}确认已下单成功')
        purchase_detail_url = '{}/purchase/detail?id={}&navTabId=PurchaseDetail'.format(self.ERP_URL, self.purchase_id)
        purchase_detail_res = self.rss.get(url=purchase_detail_url).text
        inn_sn = re.search('(target="navTab" style="margin-left: 5px;" rel="addScan">)(IN[0-9]*)', purchase_detail_res).group(2)
        logger.info(f"搜索成功，获取到入库单为：{inn_sn}")
        setattr(Data, 'inn_sn', inn_sn)
        logger.debug('=*' * 50)
        return self

    def order_stock_purchase_affirm(self):
        """
        销售代采采购单号确认
        """
        self.purchase_sn = getattr(Data, 'purchase_sn', '')
        self.purchase_id = getattr(Data, 'purchase_id')
        #
        # self.purchase_sn = "PO00437213"
        # self.purchase_id = "68"
        # 修改基本信息
        plan_receive_date = str(datetime.now()).split(' ')[0]
        purchase_basic_information_update_url = '{}/Purchase/click_set'.format(self.ERP_URL)
        purchase_basic_information_update_body = {"id": self.purchase_id, "save": 1,
                                                  "purchasing_company_id": 1,
                                                  "delivery_warehouse_id": 2,
                                                  "purchasing_type": 1,
                                                  "second_type": 1,
                                                  "transaction_type": 1,
                                                  "seal_id": 1,
                                                  "plan_receive_date": plan_receive_date,
                                                  "supplier_pay_type": 2,
                                                  "account_cycle": 0,
                                                  "shipping_pay_type": 1,
                                                  "pr_contract_type": 3,
                                                  "ajax": 1,
                                                  "is_iframe": 1
                                                  }
        purchase_basic_information_update_res = self.rss.post(url=purchase_basic_information_update_url, data=purchase_basic_information_update_body).json()
        logger.info(f"更新基本信息成功,执行结果为：{purchase_basic_information_update_res}")

        #
        purchase_user_url = '{}/Purchase/click_set/navTabId/PurchaseDetail'.format(self.ERP_URL)
        purchase_user_body = {"picking_uid": 701, "id": self.purchase_id}
        purchase_user_res = self.rss.post(url=purchase_user_url, data=purchase_user_body, headers=self.headers).json()
        logger.info(f"执行结果为：{purchase_user_res}")

        # 币种修改为人民币
        purchase_update_url = '{}/Purchase/click_set'.format(self.ERP_URL)
        purchase_update_body ={"id": self.purchase_id, "save": 1, "currency": 1, "tax_id": 6,
                               "misc_fee": "0.0000", "exchange_rate": 1, "shipping_pay_type": 1,
                               "ajax": 1, "is_iframe": 1
                               }
        purchase_update_res = self.rss.post(url=purchase_update_url, data=purchase_update_body).json()
        logger.info(f"执行结果为：{purchase_update_res}")

        # 确认采购单
        purchase_affirm_url = '{}/Purchase/confirm/id/{}/navTabId/PurchaseDetail'.format(self.ERP_URL, self.purchase_id)
        purchase_affirm_res = self.rss.post(url=purchase_affirm_url).json()
        # 获取字典的键值（名称）并且以list汇总输出
        res_key = list(purchase_affirm_res.keys())
        logger.info(f"确认采购单成功,执行结果为{purchase_affirm_res}")
        if "confirmMsg" in res_key:
            if "采购价为0" in purchase_affirm_res["confirmMsg"]:
                affirm_audit_url = purchase_affirm_res["forwardUrl"]
                purchase_audit_url = self.ERP_URL + affirm_audit_url
                logger.info(purchase_audit_url)
                purchase_audit_body = {"id": self.purchase_id, "status": -1, "is_t_order": 2, "list_sort": ""}
                self.rss.post(url=purchase_audit_url, data=purchase_audit_body, headers=self.headers)
                logger.info(f"执行成功")
        else:
            logger.info("确认成功")
        return self

    def purchase_status_sync(self, purchase_id=None):
        purchase_status_sync_url = '{}/Service//Purchase/putPay'.format(self.ERP_URL)
        try:
            purchase_status_sync_body = {"picking_id": self.purchase_id}
            purchase_status_sync_res = self.rss.post(url=purchase_status_sync_url, data=purchase_status_sync_body, headers=self.headers).text
            # print(purchase_status_sync_res)
        except AttributeError as e:
            if e.args[0] == "'ErpStockPurchase' object has no attribute 'purchase_id'":
                if purchase_id !=None:
                    self.purchase_id = purchase_id
                    purchase_status_sync_body = {"picking_id": self.purchase_id}
                    # purchase_status_sync_body["picking_id"] = self.purchase_id
                    purchase_status_sync_res = self.rss.post(url=purchase_status_sync_url, data=purchase_status_sync_body,headers=self.headers).text
                    # print(purchase_status_sync_res)
                else:
                    print(f"请输入purchase_id")
        return self
    def mian_stock_up_purchase(self, IsPurchase=None):
        """补备货采购处理"""
        self.stock_up_plan()
        if IsPurchase == None:
            self.stock_up_purchase_affirm()
            self.stock_up_purchase_audit()
            self.stock_up_purchase_deliver_goods()
        return self

    def mian_order_stock_purchase(self):
        """销售补货采购处理"""
        self.order_stock_purchase_affirm()
        self.stock_up_purchase_deliver_goods()
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
    # 合作、海外库存代采流程
    from huaqiu_order_api.HQCHIP_SOO.login import SOOLogin
    target_rss = SOOLogin("uat-e.hqchip.com", "AuthLogin").target_login()
    ErpStockPurchase(target_rss).mian_stock_up_purchase()
