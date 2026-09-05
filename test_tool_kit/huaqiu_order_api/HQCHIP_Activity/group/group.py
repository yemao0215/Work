import json
import time
from datetime import datetime, timedelta

from HQCHIP_SOO.login import SOOLogin
from common.loguru_logger import logger
from common.my_path import poseter_img_dir, discount_dir


class Group:
    # 拼团活动
    def __init__(self, target_rss, activity_name):
        self.activity_rss = target_rss
        self.json_head = {"Content-Type": "application/json"}
        self.file_head = {"Content-Type": "multipart/form-source_data"}
        self.activity_name = activity_name



    def group_list(self):
        """拼团管理列表"""
        search_url = "https://uat-activity.hqchip.com/ecmc/group/groupList"
        search_body = {"timeStatus":"0", "pageNum": 1, "pageSize": 20}
        search_res = self.activity_rss.post(url=search_url, json=search_body, headers=self.json_head).json()
        # logger.info(search_res)
        activityInfo = search_res["result"]
        logger.info(len(activityInfo))
        # shopThematinfo = activityInfo.get("shopThematic")
        self.activity_id = []
        activity_name = []
        for i in range(len(activityInfo)):
            self.activity_id.append(activityInfo[i]["activityId"])
            activity_name.append(activityInfo[i]["activityName"])
        # logger.info(self.activity_id)
        # logger.info(activity_name)
        for q in range(len(activityInfo)):
            if self.activity_name == activity_name[q]:
                self.activity_id = self.activity_id[q]
                # self.activity_id.append(self.activity_id[q])
            continue
        logger.info(f"获取拼团活动名称为{self.activity_name}的活动id的list列表为{self.activity_id}")

        return self

    def group_add(self,price):
        """拼团活动"""
        now_time_ten_minutes = str((datetime.now() + timedelta(minutes=10)).strftime("%Y-%m-%d %H:%M:%S"))
        logger.info(f"获取当前时间10分钟后的时间：{now_time_ten_minutes}")
        now_time_one_day = str((datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"))
        logger.info(f"获取当前时间一天后的时间：{now_time_one_day}")
        add_url = "https://uat-activity.hqchip.com/ecmc/group/addGroup"
        oldPrice = self.savegoods_data[0]["tiered"][0][3]
        add_body = {"activityGroupId": 0, "activityName": self.activity_name, "activityStartTime": now_time_ten_minutes, "activityEndTime": now_time_one_day,
                    "timeDay": 2, "timeHour": 0, "timeMinute": 0, "groupUserNumber": 2, "goodsInfo": {
                "goodsId": self.savegoods_data[0]["goodsId"], "goodsImg": self.savegoods_data[0]["goodsImg"], "goodsName": self.savegoods_data[0]["goodsName"], "minBuynum": self.savegoods_data[0]["minBuynum"],
                "goodsNumber": self.savegoods_data[0]["goodsNumber"], "goodsSn": self.savegoods_data[0]["goodsSn"], "goodsType": self.savegoods_data[0]["goodsType"], "providerName": self.savegoods_data[0]["providerName"],
                "tiered": self.savegoods_data[0]["tiered"],"spotNumber":self.savegoods_data[0]["spotNumber"],"supplierId":self.savegoods_data[0]["supplierId"],"oldPrice": oldPrice,"price":price,
                "inGroupRole": -1, "maxInGroupNum": -1, "openGroupRole":-1,"useCoupon":0
            }}

        add_res = self.activity_rss.post(url=add_url, json=add_body, headers=self.json_head).json()
        logger.info(add_res)
        msg = add_res["result"]
        if msg == "新增成功":
            logger.info(f"拼团活动：{self.activity_name} 创建成功")
            return self

    def group_savegoods(self,goodsIds):
        """添加商品 按库存id搜索，生成绑定库存信息"""
        # cleartempgoods_url = "https://uat-activity.hqchip.com/ecmc/group/clearTempGoods"
        # cleartempgoods_body = {"actionName":"add", "activityId":"0"}
        # cleartempgoods_res = self.activity_rss.post(url=cleartempgoods_url, json=cleartempgoods_body, headers=self.json_head).json()
        # logger.info(cleartempgoods_res)
        getgoods_url = "https://uat-activity.hqchip.com/ecmc/group/getGoods"
        getgoods_body = {"goodsIds":goodsIds}
        getgoods_res = self.activity_rss.post(url=getgoods_url, json=getgoods_body, headers=self.json_head).json()
        # logger.info(getgoods_res)
        self.savegoods_data = getgoods_res["result"]
        return self

if __name__ == '__main__':
   target_rss = SOOLogin("admin", "12345678", "uat-activity.hqchip.com", "ecmc").target_login()
   # Discount(target_rss, "库存不限制单人购买限制").discount_savegoods("2500220268",80).discount_activity_add()
   Group(target_rss, "脚本测试0427").group_savegoods("2500314320").group_add(0.1).group_list()