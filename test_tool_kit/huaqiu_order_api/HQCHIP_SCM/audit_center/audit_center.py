import json
import time
from datetime import datetime, timedelta

import jsonpath
import yaml
from xpinyin import Pinyin

from huaqiu_order_api.HQCHIP_SOO.login import SOOLogin
from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_data import Data
from huaqiu_order_api.common.my_path import yaml_file, account_yaml
from huaqiu_order_api.common.yaml_handler import write_yaml


class AuditCenter:
    # 审核中心操作

    def __init__(self, target_rss, order_sn, audit_users):
        self.approval_rss = target_rss
        self.json_head = {"Content-Type": "application/json"}
        self.file_head = {"Content-Type": "multipart/form-source_data"}
        self.audit_users = audit_users
        self.login_name = getattr(Data, 'login_name', "")
        self.login_userId = getattr(Data, 'login_userId', "")
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.Approval_URL = data['Approval_URL']
        self.order_sn = order_sn
        self.check_user_pwd_json = {"admin": "HQ@uat@666", "taoting": "HQ@uat@666", "xujiangquan": "Xjq123456.", "yemao": "Ye12345678+",
                                    "zhangbajun": "12345678", "hepeng": "He123456*"}

    def center_audit_list(self):
        """审核中心-我的审批"""
        search_url = "{}/approval/process/getTodoProcessList".format(self.Approval_URL)
        search_body = {"processName": self.order_sn, "loginUserId": self.login_userId, "pageNum": 1, "pageSize": 500}
        print(search_body)
        search_res = self.approval_rss.post(url=search_url, json=search_body, headers=self.json_head).json()
        print(search_res)
        self.procInstId = ''
        if search_res["result"] != []:
            self.procInstId = jsonpath.jsonpath(search_res, "$..procInstId")[0]
            self.procDefKey = jsonpath.jsonpath(search_res, "$..procDefKey")[0]
            self.order_audit_id = jsonpath.jsonpath(search_res, "$..id")[0]
        logger.info(f"获取审核关联订单号为{self.order_sn}的审核id: {self.order_audit_id}的list列表为：{self.procInstId},审核任务类型为{self.procDefKey}")
        return self
    def center_auditor_acquire(self):
        """获取当前审核人员信息"""
        operaUserName = ''
        taskStatus = ''
        if self.procInstId != '':
            center_audit_details_url = "{}/approval/process/getApprovalRecordList".format(self.Approval_URL)
            center_audit_details_body = {"procInstId": self.procInstId}
            center_audit_details_res = self.approval_rss.post(url=center_audit_details_url, json=center_audit_details_body,
                                                               headers=self.json_head).json()
            # print(center_audit_details_res)
            operaUserName = jsonpath.jsonpath(center_audit_details_res, "$..operaUserName")
            taskStatus = jsonpath.jsonpath(center_audit_details_res, "$..taskStatus")
        taskStatus_list = []
        operaUserName_list = []
        if operaUserName != []:
            for i in range(len(operaUserName)):
                if taskStatus[i] in [-1, 1]:
                    pass
                else:
                    taskStatus_list.append(taskStatus[i])
                    operaUserName_list.append(operaUserName[i])
        return operaUserName_list, taskStatus_list


    def audit_user_judge(self, login_name, audit_users):
        """判断当前登录账号是否为审核人"""
        self.judge_login_name = login_name
        self.judge_audit_users = audit_users
        logger.info(f"获取当前登陆账号的用户名称：{self.judge_login_name}")
        if self.judge_login_name == self.judge_audit_users:
            logger.info("当前系统登陆用户和需要审核的流程的审核人保持一致")
        else:
            logger.info("当前系统登陆用户和需要审核的流程的审核人不一致，需要重新登录")
            logout_url = "{}/approval/sso/logout".format(self.Approval_URL)
            pwd = ''
            check_user = ''
            self.approval_rss.get(url=logout_url, headers=self.json_head).json()
            if self.judge_audit_users != "超级管理员":
                check_user = Pinyin().get_pinyin(self.judge_audit_users, '')
            elif self.judge_audit_users == "超级管理员":
                check_user = "admin"
            if check_user != '':
                for k, v in self.check_user_pwd_json.items():
                    if check_user == k:
                        pwd = v
            SOO_user_params = {'admin_name': check_user, "admin_pwd": pwd, "pro_pwd": "auth221313",
                               "pro_user": "zhangbajun", "pwd": '12345678', "user": "yemao"}

            user_params = {"HQCHIP_SOO": SOO_user_params}
            write_yaml(account_yaml, user_params)
            target_rss = SOOLogin("uat-approval.huaqiu.com", "approval").target_login()
            self.login_name = getattr(Data, 'login_name', "")
            self.login_userId = getattr(Data, 'login_userId', "")
            self.approval_rss = target_rss
        return self
    def parther_audit(self, login_userId, login_name):
        """审核中心操作流程
        # 通过传值
        comment = 通过，operation=‘pass’
        comment = 驳回，operation=‘reject’

        """
        logger.info("---")
        passtask_url = "{}/approval/process/passTask".format(self.Approval_URL)
        #  "procDefKey": self.procDefKey[0], "procInstId": self.procInstId[0],
        passtask_body = {"id": self.order_audit_id, "loginUserId": login_userId, "loginUserName": login_name}
        logger.info(passtask_body)
        passtask_res = self.approval_rss.post(url=passtask_url, json=passtask_body, headers=self.json_head).json()
        logger.info(passtask_res)
        if passtask_res["result"] == True:
            logger.info("审核完成")
        return self
    def mian_center_audit(self):
        i = 0
        while True:
            self.center_audit_list()
            self.operaUserName_list, taskStatus_list = self.center_auditor_acquire()
            # print(self.operaUserName_list, taskStatus_list)
            if self.operaUserName_list != []:
                for k in range(len(self.operaUserName_list)):
                    judge_audit_users = self.operaUserName_list[k]
                    self.audit_user_judge(self.login_name, judge_audit_users)
                    self.parther_audit(self.login_userId, self.login_name)
            else:
                i += 1
                if i >= 1:
                   SOO_user_params = {'admin_name': "admin", "admin_pwd": "HQ@uat@666", "pro_pwd": "auth221313",
                                           "pro_user": "zhangbajun", "pwd": '123456789', "user": "yemao"}
                   user_params = {"HQCHIP_SOO": SOO_user_params}
                   write_yaml(account_yaml, user_params)
                   break
        return self
if __name__ == '__main__':
    target_rss = SOOLogin("uat-approval.huaqiu.com", "approval").target_login()
    AuditCenter(target_rss, "W25121018033695208", "许江铨").mian_center_audit()