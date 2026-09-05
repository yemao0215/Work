import json
import re
import time
from datetime import datetime, timedelta

import jsonpath
import requests
import yaml
from dateutil.relativedelta import relativedelta
from huaqiu_order_api.HQCHIP_Center.assets.withdraw_order import ativity_withdraw_order_create
from huaqiu_order_api.HQCHIP_ERP.erp_withdraw_manage import ErpWithdrawManage
from huaqiu_order_api.HQCHIP_PAY.withdraw.audit_withdraw import AuditWithdraw
from huaqiu_order_api.HQCHIP_SCM.audit_center.audit_center import AuditCenter
from huaqiu_order_api.HQCHIP_SCM.financial_manage.withdraw_order import ScmWithdrawManage
from huaqiu_order_api.HQCHIP_SOO.login import SOOLogin
from huaqiu_order_api.SSO_Reception.sso_reception import SSO_Reception
from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_data import Data
from huaqiu_order_api.common.my_path import yaml_file, account_yaml
from huaqiu_order_api.common.yaml_handler import write_yaml


class WithdrawPayStatusVerify:
    def __init__(self, rss):
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.PAY_URL = data['PAY_URL']
        with open(account_yaml, 'r', encoding='utf-8') as yamlfile:
            account = yaml.load(yamlfile, Loader=yaml.FullLoader)
        # self.recharge_order = "R23121410402690670"
        self.headers = {"Content-Type": "application/x-www-form-urlencoded",
                        "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://www.huaqiu.com)"
                        }
        self.headers_json = {"Content-Type": "application/json; charset=UTF-8",
                             "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://www.huaqiu.com)"
                             }
        self.pay_rss = rss

    def date_old_day(self):
        # 获取当前日期
        current_date = datetime.now()
        # 获取上个月同一天的日期
        last_month_same_day = (current_date - relativedelta(months=1)).strftime("%Y-%m-%d")
        return last_month_same_day

    def withdraw_order_verify(self):
        self.withdraw_order = getattr(Data, 'withdraw_order')
        # self.withdraw_order = "W24120316053123866"
        last_month_same_day_time = str(self.date_old_day()) + " 00:00:00"
        current_date = datetime.now().strftime("%Y-%m-%d")
        current_date_time = str(current_date) + " 23:59:59"
        withdraw_order_search_url = "{}/management/bill/query/fast".format(self.PAY_URL)
        withdraw_order_search_body = {
            "pageNum": 1,
            "pageSize": 50,
            "startTime": last_month_same_day_time,
            "endTime": current_date_time,
            "pushDate": [last_month_same_day_time, current_date_time],
            "mchBillNo": self.withdraw_order,
            "billMoney": 0,
            "symbol": "1"
        }
        withdraw_order_lst = []
        n = 0
        while True:
            try:
                withdraw_order_search_res = self.pay_rss.post(url=withdraw_order_search_url, json=withdraw_order_search_body, headers=self.headers_json).json()
                mchBillNo = jsonpath.jsonpath(withdraw_order_search_res, "$..mchBillNo")[0]
                tradeStatus = jsonpath.jsonpath(withdraw_order_search_res, "$..tradeStatus")[0]
                if tradeStatus in [0, 3, 5]:
                    logger.info(f"第{n + 1}次访问付/退款管理列表,mchBillNo:{mchBillNo}")
                    withdraw_order_lst = jsonpath.jsonpath(withdraw_order_search_res, "$..result")[0]
                break
            except Exception as e:
                n += 1
                if n < 6:
                    logger.warning(f"第 {n} 次,付/退款管理列表没有找到提现单:{self.withdraw_order},等待30秒后系统自动重试,错误信息:{e}")
                    time.sleep(30)
                else:
                    logger.error(f"付/退款管理列表查找提现单:{self.withdraw_order} 出错,请手动检查入库单是否存在")
                    raise ValueError

        withdraw_order_msg = None
        if withdraw_order_lst != []:
            for k in withdraw_order_lst:
                if k["mchBillNo"] == self.withdraw_order and k["tradeStatus"] in [0, 3, 5]:
                    withdraw_order_msg = k
                    break
            if withdraw_order_msg != None:
                centerBillNo = withdraw_order_msg["centerBillNo"]
                id = withdraw_order_msg["id"]
                verify_url = "{}/management/auto/bill/offlinePay".format(self.PAY_URL)
                verify_body = {"centerBillNo": centerBillNo, "id": id}
                verify_res = self.pay_rss.post(url=verify_url, json=verify_body, headers=self.headers_json).json()
                logger.info(f"执行结果为{verify_res}")
        return self
    def mian_withdraw_flow(self, recharge_order=None, paypassword=None, withdrawAmount=None):
        rss = SSO_Reception('https://uat-www.hqchip.com').login()
        msg = ativity_withdraw_order_create(rss, recharge_order, paypassword, withdrawAmount)
        # setattr(Data, "withdrawAmount", float(5000) / 100)
        # msg = None
        print(recharge_order)
        withdraw_order = None
        if msg != "不存在可操作提现的内容":
            SOO_user_params = {'admin_name': "admin", "admin_pwd": "HQ@uat@666", "pro_pwd": "auth221313",
                               "pro_user": "zhangbajun", "pwd": '123456789', "user": "yemao"}
            user_params = {"HQCHIP_SOO": SOO_user_params}
            write_yaml(account_yaml, user_params)
            erp_rss = SOOLogin("uat-e.hqchip.com", "AuthLogin").target_login()
            withdraw_order = ErpWithdrawManage(erp_rss).withdraw_order_submit()
            withdrawAmount, audit_withdraw_order_msg = AuditWithdraw().audit_withdraw_order()
            print(withdraw_order)
            if audit_withdraw_order_msg == "非ERP历史提现单，不可操作！":
                # 运用新流程
                scm_target_rss = SOOLogin("uat-scm.huaqiu.com", "hqScm").target_login()
                audit_user_name = ScmWithdrawManage(scm_target_rss).withdraw_order_submit()
                time.sleep(10)
                approval_target_rss = SOOLogin("uat-approval.huaqiu.com", "approval").target_login()
                AuditCenter(approval_target_rss, withdraw_order, audit_user_name).mian_center_audit()
            self.withdraw_order_verify()
            return withdraw_order, withdrawAmount
        else:
            logger.info(f"请检查页面！！！")
            return withdraw_order, withdrawAmount


if __name__ == '__main__':
    target_rss = SOOLogin("uat-pay.huaqiu.com", "management").target_login()
    WithdrawPayStatusVerify(target_rss).withdraw_order_verify()
    # WithdrawPayStatusVerify(target_rss).mian_withdraw_flow(recharge_order="R24120214004133224")