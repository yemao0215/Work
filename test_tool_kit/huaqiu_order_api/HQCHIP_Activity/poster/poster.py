
import json
import time
from datetime import datetime, timedelta

from HQCHIP_SOO.login import SOOLogin
from common.loguru_logger import logger
from common.my_path import poseter_img_dir


class Poseter:
    # 海报活动
    def __init__(self, target_rss, activity_name):
        self.activity_rss = target_rss
        self.json_head = {"Content-Type": "application/json"}
        self.activity_name = activity_name





    def poseter_list(self):
        """海报管理列表"""
        search_url = "https://uat-activity.hqchip.com/ecmc/poster/list"
        search_body = {"activityProcessStatus": 0, "pageNum": 1, "pageSize": 20}
        search_res = self.activity_rss.post(url=search_url, json=search_body, headers=self.json_head).json()
        # logger.info(search_res)
        activityInfo = search_res["result"]
        # shopThematinfo = activityInfo.get("shopThematic")
        self.activity_id = []
        activity_name = []
        for i in range(len(activityInfo)):
            self.activity_id.append(activityInfo[i]["id"])
            activity_name.append(activityInfo[i]["activityName"])
        for q in range(len(activityInfo)):
            if self.activity_name == activity_name[q]:
                self.activity_id = self.activity_id[q]
        logger.info(f"获取海报活动名称为{self.activity_name}的活动id的list列表为{self.activity_id}")

        return self

    def poseter_activity_add(self):
        """海报活动建立"""
        now_time_ten_minutes = str((datetime.now() + timedelta(minutes=10)).strftime("%Y-%m-%d %H:%M:%S"))
        logger.info(f"获取当前时间10分钟后的时间：{now_time_ten_minutes}")
        now_time_one_day = str((datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"))
        logger.info(f"获取当前时间一天后的时间：{now_time_one_day}")
        add_url = "https://uat-activity.hqchip.com/ecmc/poster/add"
        add_body = {"activityName": self.activity_name, "activityStartTime": now_time_ten_minutes, "activityEndTime": now_time_one_day,
                    "activityPoster": {
                        "imgUrl": self.poseter_img_url, "activityUrl":"https://uat-www.hqchip.com/act/poster&type=zidonghuatest.html","logicLine": 1}}
        add_res = self.activity_rss.post(url=add_url, json=add_body, headers=self.json_head).json()
        # logger.info(add_res)
        msg = add_res["result"]
        if msg == "创建成功":
            logger.info(f"海报活动：{self.activity_name} 创建成功")
            return self

    def poseter_img_file(self):
        """海拔图片上传"""
        assembly_file_url = "https://uat-activity.hqchip.com/ecmc/upload/uploadFile"
        file = [('file', ("poseter.png", open(poseter_img_dir, 'rb'), 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'))]
        assembly_file_res = self.activity_rss.post(url=assembly_file_url, files=file).json()
        self.poseter_img_url = assembly_file_res["result"]["url"]
        logger.info(f"上传图片生成服务器图片地址：{self.poseter_img_url}")

        return self



if __name__ == '__main__':
   target_rss = SOOLogin("admin", "12345678", "uat-activity.hqchip.com", "ecmc").target_login()

   # Poseter(target_rss, "自动化测试-海报").poseter_img_file().poseter_activity_add().poseter_list()
   Poseter(target_rss, "自动化测试-海报").poseter_list()