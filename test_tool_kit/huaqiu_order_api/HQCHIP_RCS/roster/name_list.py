import json
import time
from datetime import datetime, timedelta

from huaqiu_order_api.HQCHIP_SOO.login import SOOLogin
from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_path import freight_goods_dir, freight_people_dir


class NameList:
    # 风控中台名单管理-名单列表
    def __init__(self, target_rss, rcs_name,projectName):
        self.rcs_rss = target_rss
        self.json_head = {"Content-Type": "application/json"}
        self.file_head = {"Content-Type": "multipart/form-source_data"}
        self.rcs_name = rcs_name
        self.projectName = projectName

    def name_project_list(self):
        """名单列表"""
        search_project_url = "https://uat-rcs.huaqiu.com/api/admin/list_project/list"
        search_project_body = {"projectName": self.projectName}
        search_project_res = self.rcs_rss.post(url=search_project_url, json=search_project_body, headers=self.json_head).json()
        projectIdInfo = search_project_res["body"]
        projectId = []
        for n in range(len(projectIdInfo)):
            projectId.append(projectIdInfo[n]["projectId"])
        # print(projectId)
        project_detail_id = []
        for m in range(len(projectId)):
            search_url = "https://uat-rcs.huaqiu.com/api/admin/list_project/detail_page"
            search_body = {"fieldValue": "", "listType": "0", "projectId": projectId[m], "pageNum": 1, "pageSize": 20}
            search_res = self.rcs_rss.post(url=search_url, json=search_body, headers=self.json_head).json()
            # logger.info(search_res)
            rcsInfo = search_res["body"]["list"]
            logger.info(len(rcsInfo))
            self.rcs_id = []
            project_name = []
            for i in range(len(rcsInfo)):
                self.rcs_id.append(rcsInfo[i]["projectId"])
                project_name.append(rcsInfo[i]["projectName"])
                project_detail_id.append(rcsInfo[i]["projectDetailId"])
            # print(self.rcs_id,project_name,project_detail_id)
            # for q in range(len(rcsInfo)):
            #     if self.projectName == project_name[q]:
            # #         self.rcs_id = self.rcs_id[q]
            # #         project_detail_id = project_detail_id[q]
            #         self.rcs_id.append(self.rcs_id[q])
            #         project_detail_id.append(project_detail_id[q])
            #     print(project_detail_id)
            #     continue
        logger.info(f"获取名单项目管理名称为{self.projectName}的名单id的list列表为{project_detail_id}")
        #
        return self
    def name_project_add(self, fieldValue,fieldType,listType,isMasking):
        """名单列表新增
        :param fieldValue 新增内容
        :param fieldType 类型 1手机号 2邮箱 3uid 4税号 5设备号 6收货地址 7微信 8QQ 9IP地址
        :param listType 名单类型 1黑名单 2白名单
        :param isMasking 是否脱敏 1是 0否
        """

        search_project_url = "https://uat-rcs.huaqiu.com/api/admin/list_project/list"
        search_project_body = {"projectName": self.projectName}
        search_project_res = self.rcs_rss.post(url=search_project_url, json=search_project_body, headers=self.json_head).json()
        projectIdInfo = search_project_res["body"]
        projectId = []
        for n in range(len(projectIdInfo)):
            projectId.append(projectIdInfo[n]["projectId"])
        add_detail_url ="https://uat-rcs.huaqiu.com/api/admin/list_project/add_detail"
        add_detail_body = {"projectId": projectId[0],"fieldValue": fieldValue, "fieldType": fieldType, "listType": listType, "isMasking": isMasking}
        add_detail_res = self.rcs_rss.post(url=add_detail_url, json=add_detail_body,headers=self.json_head).json()
        if add_detail_res["suc"] == True:
            logger.info(f"新增名单项目：{self.projectName}的名单值：{fieldValue}成功")
        return self


if __name__ == '__main__':
    target_rss = SOOLogin("admin", "12345678", "uat-rcs.huaqiu.com", "api").target_login()
    NameList(target_rss, "111", "积分兑换优惠券项目").name_project_add("192.168.14.94",9,1,0)