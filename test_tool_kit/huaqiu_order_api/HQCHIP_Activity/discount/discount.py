import json
import time
from datetime import datetime, timedelta

from huaqiu_order_api.HQCHIP_SOO.login import SOOLogin
from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_path import poseter_img_dir, discount_dir


class Discount:
    # 折扣活动
    def __init__(self, target_rss, activity_name):
        self.activity_rss = target_rss
        self.json_head = {"Content-Type": "application/json"}
        self.file_head = {"Content-Type": "multipart/form-source_data"}
        self.activity_name = activity_name



    def discount_list(self,goodsId,goodsName):
        """折扣管理列表"""
        search_url = "https://uat-activity.hqchip.com/ecmc/discount/getList"
        search_body = {"goodsId": goodsId, "goodsName": goodsName, "timeStatus":"0", "pageNum": 1, "pageSize": 20,"activityIdList":None}
        search_res = self.activity_rss.post(url=search_url, json=search_body, headers=self.json_head).json()
        logger.info(search_res)
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
        logger.info(f"获取折扣活动名称为{self.activity_name}的活动id的list列表为{self.activity_id}")

        return self

    def discount_activity_add(self):
        """折扣活动建立"""
        now_time_ten_minutes = str((datetime.now() + timedelta(minutes=10)).strftime("%Y-%m-%d %H:%M:%S"))
        logger.info(f"获取当前时间10分钟后的时间：{now_time_ten_minutes}")
        now_time_one_day = str((datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"))
        logger.info(f"获取当前时间一天后的时间：{now_time_one_day}")
        add_url = "https://uat-activity.hqchip.com/ecmc/discount/save"
        add_body = {"activityName": self.activity_name, "activityStartTime": now_time_ten_minutes, "activityEndTime": now_time_one_day,
                    "openTask":0,"actionName":"add"
                    }

        add_res = self.activity_rss.post(url=add_url, json=add_body, headers=self.json_head).json()
        logger.info(add_res)
        msg = add_res["result"]
        if msg == "创建成功":
            logger.info(f"折扣活动：{self.activity_name} 创建成功")
            return self

    def discount_savegoods(self, goodsIds,discountRate):
        """添加商品 按库存id搜索，生成绑定库存信息"""
        cleartempgoods_url = "https://uat-activity.hqchip.com/ecmc/discount/clearTempGoods"
        cleartempgoods_body = {"actionName":"add", "activityId":"0"}
        cleartempgoods_res = self.activity_rss.post(url=cleartempgoods_url, json=cleartempgoods_body, headers=self.json_head).json()
        selectgoods_url = "https://uat-activity.hqchip.com/ecmc/discount/selectGoods"
        selectgoods_body = {"goodsIds": goodsIds}
        selectgoods_res = self.activity_rss.post(url=selectgoods_url, json=selectgoods_body, headers=self.json_head).json()
        # logger.info(selectgoods_res)
        selectgoods_data = selectgoods_res["result"]
        prices = selectgoods_data[0]["tiered"]
        price = prices[len(prices) - 1][3]
        savegoods_url = "https://uat-activity.hqchip.com/ecmc/discount/saveTempGoods"
        savegoods_body = {"actionName": "add", "activityId": "", "source_data":{
            "goodsId": selectgoods_data[0]["goodsId"], "goodsName": selectgoods_data[0]["goodsName"], "goodsType":selectgoods_data[0]["goodsType"], "goodsImg":selectgoods_data[0]["goodsImg"],
            "goodsNumber": selectgoods_data[0]["goodsNumber"], "goodsSn": selectgoods_data[0]["goodsSn"], "startNumber": selectgoods_data[0]["minBuynum"], "providerName":selectgoods_data[0]["providerName"],
            "priceGroup": selectgoods_data[0]["tiered"], "storeNumber": selectgoods_data[0]["spotNumber"], "price": price, "priceType": 2, "useCoupon": 0,
            "afterPrice": price*discountRate/10, "discountMark": 6, "discountRate": discountRate, "promoteSalesType": -1, "promoteSalesNumber": 0, "maxInDiscountType": -1, "maxInDiscountNumber": 0
        }}
        savegoods_res = self.activity_rss.post(url=savegoods_url, json=savegoods_body, headers=self.json_head).json()
        logger.info(savegoods_res)
        gettempgoods_url = "https://uat-activity.hqchip.com/ecmc/discount/getTempGoods"
        gettempgoods_body = {"actionName":"add", "activityId":"", "goodsId":"", "pageSize":1, "pageNum":20, "isInit": True}
        # print(gettempgoods_body)
        gettempgoods_res = self.activity_rss.post(url=gettempgoods_url, json=gettempgoods_body, headers=self.json_head).json()


        return self

    def discount_goodsfile(self):
        """添加商品 按上传文件"""
        cleartempgoods_url = "https://uat-activity.hqchip.com/ecmc/discount/clearTempGoods"
        cleartempgoods_body = {"actionName":"add", "activityId":"0"}
        cleartempgoods_res = self.activity_rss.post(url=cleartempgoods_url, json=cleartempgoods_body, headers=self.json_head).json()
        logger.info(cleartempgoods_res)

        goodsfile_url = "https://uat-activity.hqchip.com/ecmc/discount/importGoods?actionName=add&activityId=0&activityDiscountId=0"
        file = [('file', ("discount.csv", open(discount_dir, 'rb'),'multipart/form-source_data.openxmlformats-officedocument.spreadsheetml.sheet'))]
        # goodsfile_body = {"actionName":"add","activityId":""}
        goodsfile_res = self.activity_rss.post(url=goodsfile_url, files=file).json()
        logger.info(goodsfile_res)

        gettempgoods_url = "https://uat-activity.hqchip.com/ecmc/discount/getTempGoods"
        gettempgoods_body = {"actionName":"add", "activityId":"", "goodsId":"", "pageSize":1, "pageNum":20, "isInit": True}
        # print(gettempgoods_body)
        gettempgoods_res = self.activity_rss.post(url=gettempgoods_url, json=gettempgoods_body, headers=self.json_head).json()
        logger.info(gettempgoods_res)
        return self



if __name__ == '__main__':
   target_rss = SOOLogin("admin", "12345678", "uat-activity.hqchip.com", "ecmc").target_login()
   # Discount(target_rss, "库存不限制单人购买限制").discount_savegoods("2500220268",80).discount_activity_add()
   Discount(target_rss, "周版本测试").discount_goodsfile().discount_activity_add()