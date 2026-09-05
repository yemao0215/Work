import json
import time
from datetime import datetime, timedelta

import jsonpath
import yaml
from xpinyin import Pinyin

from huaqiu_order_api.HQCHIP_SOO.login import SOOLogin
from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_path import yaml_file, account_yaml
from huaqiu_order_api.common.yaml_handler import write_yaml


class PartnerAudit:
    # 审核中心操作

    def __init__(self, target_rss, subject_name, passtask_body_supplierCode, audit_users, procInstId=None):
        """
        :param subject_name 搜索主题名称
        :param passtask_body_supplierCode 审核方法里面请求参数boy的supplierCode参数，不一定是供应商编码
        """
        self.srm_rss = target_rss
        self.json_head = {"Content-Type": "application/json"}
        self.file_head = {"Content-Type": "multipart/form-source_data"}
        self.subject_name = subject_name
        self.passtask_body_supplierCode = passtask_body_supplierCode
        self.audit_users = audit_users
        self.procInstId = procInstId
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.SRM_URL = data['SRM_URL']
        self.check_user_pwd_json = {"admin": "HQ@uat@666", "taoting": "Aa123456*", "xujiangquan": "12345678", "yemao": "Ye12345678+"}

    def parther_audit_list(self):
        """审核中心-我的审批"""
        search_url = "{}/partnermanage/queryTodo".format(self.SRM_URL)
        search_body = {"subject": self.subject_name,
                       "procDefKey": [
                           "supplier_apply_into",
                           "supplier_update_data",
                           "supplier_ban_change",
                           "supplier_taka_data",
                           "replace_sale_goods",
                           "partner_channel_update",
                           "supplier_black_recover"
                       ]}
        search_res = self.srm_rss.post(url=search_url, json=search_body, headers=self.json_head).json()
        logger.info(search_res)
        potentialInfo = search_res["body"]["list"]
        self.procDefKey = []
        self.procInstId = []
        supplierCode = []
        self.subject_name_str = []
        self.busiId = []
        self.audit_subject_name = ""
        for i in range(len(potentialInfo)):
            supplierCode.append(potentialInfo[i]["supplierCode"])
            self.procDefKey.append(potentialInfo[i]["procDefKey"])
            self.procInstId.append(potentialInfo[i]["procInstId"])
            self.busiId.append(potentialInfo[i]["busiId"])
            self.subject_name_str.append(potentialInfo[i]["subject"])
        for q in range(len(potentialInfo)):
            if self.passtask_body_supplierCode == supplierCode[q]:
                self.procDefKey = self.procDefKey[q]
                self.procInstId = self.procInstId[q]
                self.busiId = self.busiId[q]
                self.audit_subject_name = self.subject_name_str[q]
            continue
        logger.info(f"获取审核主题名称为{self.audit_subject_name}的审核id的list列表为：{self.procInstId},审核任务类型为{self.procDefKey}")
        return self
    def parther_auditor_acquire(self):
        # # 获取审核人
        # procInstId  库存更新审核id
        approvalrecord_url = "{}/partnermanage/approvalRecord".format(self.SRM_URL)
        approvalrecord_body = {"procInstId": self.procInstId}
        approvalrecord_res = self.srm_rss.post(url=approvalrecord_url, json=approvalrecord_body, headers=self.json_head).json()
        logger.info(approvalrecord_res)
        if "msg" in approvalrecord_res:
            if "token无效" in approvalrecord_res["msg"]:
                target_rss = SOOLogin("uat-srm.huaqiu.com", "partnermanage").target_login()
                self.srm_rss = target_rss
                approvalrecord_res = self.srm_rss.post(url=approvalrecord_url, json=approvalrecord_body, headers=self.json_head).json()
                logger.info(approvalrecord_res)
        approvalInfo = approvalrecord_res["body"]["list"]
        self.uidCreator = None
        if approvalInfo != []:
            creatorDesc = jsonpath.jsonpath(approvalrecord_res, "$..creatorDesc")
            uidCreator = jsonpath.jsonpath(approvalrecord_res, "$..uidCreator")
            applyStatus = jsonpath.jsonpath(approvalrecord_res, "$..applyStatus")
            for i in range(len(creatorDesc)):
                if creatorDesc[i] != "发起人":
                    if applyStatus[i] != "已通过":
                        self.uidCreator = uidCreator[i]
        logger.info(f"审核主题名称为{self.audit_subject_name}的审核节点为{self.uidCreator}")
        logger.info("请转至审核人的审核中心进行操作审核中心")
        return self.uidCreator


    def audit_user_judge(self):
        """判断当前登录账号是否为审核人"""
        info_url = "{}/partnermanage/resource/info".format(self.SRM_URL)
        info_res = self.srm_rss.get(url=info_url, headers=self.json_head).json()
        if "msg" in info_res:
            if "当前登录态已失效" in info_res["msg"]:
                target_rss = SOOLogin("uat-srm.huaqiu.com", "partnermanage").target_login()
                self.srm_rss = target_rss
                info_res = self.srm_rss.get(url=info_url, headers=self.json_head).json()
                # logger.info(info_res)
        srm_login_current = info_res["body"]["username"]
        logger.info(f"获取当前登陆账号的用户名称：{srm_login_current}")
        if srm_login_current == self.audit_users:
            logger.info("当前系统登陆用户和需要审核的流程的审核人保持一致")
        else:
            logger.info("当前系统登陆用户和需要审核的流程的审核人不一致，需要重新登录")
            logout_url = "{}/partnermanage/sso/logout".format(self.SRM_URL)
            check_user =''
            pwd = ''
            self.srm_rss.get(url=logout_url, headers=self.json_head).json()
            if self.audit_users != "超级管理员":
                check_user = Pinyin().get_pinyin(self.audit_users, '')
            elif self.audit_users == "超级管理员":
                check_user = "admin"
            for k, v in self.check_user_pwd_json.items():
                if check_user == k:
                    pwd = v
            SOO_user_params = {'admin_name': check_user, "admin_pwd": pwd, "pro_pwd": "auth221313",
                               "pro_user": "zhangbajun", "pwd": '123456789', "user": "yemao"}

            user_params = {"HQCHIP_SOO": SOO_user_params}
            write_yaml(account_yaml, user_params)
            target_rss = SOOLogin("uat-srm.huaqiu.com", "partnermanage").target_login()
            self.srm_rss = target_rss
        return self



    def parther_audit(self, comment, operation):
        """审核中心操作流程
        # 通过传值
        comment = 通过，operation=‘pass’
        comment = 驳回，operation=‘reject’

        """
        logger.info("---")
        passtask_url = "{}/partnermanage/passTask".format(self.SRM_URL)
        #  "procDefKey": self.procDefKey[0], "procInstId": self.procInstId[0],
        passtask_body = {"comment": comment, "operation": operation, "supplierCode": self.passtask_body_supplierCode}
        if isinstance(self.procDefKey, list):
            passtask_body["procDefKey"] = self.procDefKey[0]
        else:
            passtask_body["procDefKey"] = self.procDefKey
        if isinstance(self.procInstId, list):
            passtask_body["procInstId"] = self.procInstId[0]
        else:
            passtask_body["procInstId"] = self.procInstId
        logger.info(passtask_body)
        passtask_res = self.srm_rss.post(url=passtask_url, json=passtask_body, headers=self.json_head).json()
        logger.info(passtask_res)
        if passtask_res["suc"] == True:
            logger.info("审核完成")

        return passtask_res["suc"], self.passtask_body_supplierCode
    def mian_parther_audit(self):
        # uidCreator = None
        # if self.procInstId != None:
        #     uidCreator = self.parther_auditor_acquire()
        # self.audit_users = uidCreator
        self.audit_user_judge()
        self.parther_audit_list()
        suc, self.passtask_body_supplierCode = self.parther_audit("通过", "pass")
        return suc, self.passtask_body_supplierCode

if __name__ == '__main__':
    pass