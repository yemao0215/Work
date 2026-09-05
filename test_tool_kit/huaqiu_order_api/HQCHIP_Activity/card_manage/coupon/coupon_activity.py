import json
import time
from datetime import datetime, timedelta

from huaqiu_order_api.HQCHIP_SOO.login import SOOLogin
from huaqiu_order_api.common.loguru_logger import logger



class CouponActivity:

    def __init__(self, target_rss, activity_name):
        self.activity_rss = target_rss
        self.json_head = {"Content-Type": "application/json"}
        self.activity_name = activity_name
        # self.forbidType = forbidType


    def coupon_activity_list(self):
        """优惠券活动查询"""
        coupon_activity_search_url = "https://uat-activity.hqchip.com/ecmc/coupon/activityList"
        coupon_activity_search_body = {"activityName": self.activity_name, "pageSize":20,"pageNum":1}
        coupon_activity_search_res = self.activity_rss.post(url=coupon_activity_search_url, json=coupon_activity_search_body, headers=self.json_head).json()
        coupon_activity_search_data = coupon_activity_search_res["result"]
        self.activity_id = []
        self.couponShowStatus = []
        for i in range(len(coupon_activity_search_data)):
            self.activity_id.append(coupon_activity_search_data[i]["id"])
        logger.info(f"获取优惠活动名称为{self.activity_name}的活动id的list列表为{self.activity_id}")


    def coupon_activity_add(self):
        now_time = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        logger.info(f"获取当前时间：{now_time}")
        now_time_one_day = str((datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"))
        logger.info(f"获取当前时间一天后的时间：{now_time_one_day}")
        now_time_one_hours = str((datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S"))
        logger.info(f"获取当前时间一小时后的时间：{now_time_one_hours}")
        now_time_one_minutes = str((datetime.now() + timedelta(minutes=1)).strftime("%Y-%m-%d %H:%M:%S"))
        logger.info(f"获取当前时间一分钟后的时间：{now_time_one_minutes}")
    def coupon_activity_copy(self):
        pass


    def coupon_activity_forbidden(self):
        pass

    def coupon_activity_uesr_provide(self):
        pass

    def coupon_activity_edit(self):
        pass

    def coupon_activity_finish(self):
        pass

if __name__ == '__main__':
   target_rss = SOOLogin( "uat-activity.hqchip.com", "ecmc").target_login()

   CouponActivity(target_rss, "产品验收12.2602").coupon_activity_add()