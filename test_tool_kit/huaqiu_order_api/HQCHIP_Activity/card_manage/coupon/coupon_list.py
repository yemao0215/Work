
import json
import time
from datetime import datetime, timedelta

import yaml
from huaqiu_order_api.HQCHIP_SOO.login import SOOLogin
from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_path import yaml_file


class Coupon:

    def __init__(self, target_rss, couponType=None, coupon_name=None, forbidType=None):
        self.coupon_rss = target_rss
        self.json_head = {"Content-Type": "application/json"}
        self.coupon_name = coupon_name
        self.couponType = couponType
        self.forbidType = forbidType
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.Activity_Center_URL = data['Activity_Center_URL']



    def common_list(self):
        """
        优惠券列表
        """
        common_list_url = "{}/ecmc/coupon/couponList".format(self.Activity_Center_URL)
        common_list_body = {"pageNum": 1, "pageSize": 20, "couponName": self.coupon_name}
        common_list_res = self.coupon_rss.post(url=common_list_url, data=json.dumps(common_list_body), headers=self.json_head).json()
        common_list_data = common_list_res["result"]
        self.coupon_id = []
        self.couponShowStatus = []
        for i in range(len(common_list_data)):
            # coupon_id = common_list_data[i]["id"]
            # 组成生成一个list列表
            self.coupon_id.append(common_list_data[i]["id"])
            self.couponShowStatus.append(common_list_data[i]["couponShowStatus"])
        logger.info(f"获取优惠券名称为{self.coupon_name}的优惠券id的list列表为{self.coupon_id},和优惠券专题id的list列表为{self.couponShowStatus}")

        # logger.info(common_list_res)
        return self
    def common_add(self, effectiveType=None, couponExpireDays=None, useType=None, couponAmount=None, couponDiscount=None, orderAmountLimit=None):
        """优惠券新增--ic
        :param couponType:  优惠券类型，优惠券能用的订单类型(多个逗号隔开) 1.ic(元器件S2线上下单的订单，下单时使用) 2:pcb 3ismt 4.smd 5.bom(和SMT关联付款时使用)6. ic2(元器件后台生单,付款时使用)7.bom2(线下bom转换的销售订单)
        :param couponAmount: 优惠券券面金额
        :param canUseGoods：可用商品
        """
        common_add_url = "{}/ecmc/coupon/couponAdd".format(self.Activity_Center_URL)
        common_add_body = {"couponType": self.couponType, "name": self.coupon_name, "couponStatus": 2, "effectiveType": effectiveType, "orderAmountLimit": orderAmountLimit,
                           "useType": useType, "couponAmount": couponAmount, "couponDiscount": couponDiscount, "canUseGoods": 1, "couponKind":1,
                            "useWidthDiscount": 1
                           }
        if effectiveType == "1":
            now_time = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            logger.info(f"获取当前时间：{now_time}")
            now_time_one_day = str((datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"))
            logger.info(f"获取当前时间一天后的时间：{now_time_one_day}")
            couponEffectiveStartTime = [now_time, now_time_one_day]
            common_add_body["couponEffectiveStartTime"] = couponEffectiveStartTime
        elif effectiveType == "2":
            common_add_body["couponExpireDays"] = couponExpireDays
        starttime = str(datetime.now().strftime("%Y-%m-%d %X"))
        logger.info(f'开始创建优惠券时间是：{starttime}')
        common_add_res = self.coupon_rss.post(url=common_add_url, json=common_add_body, headers=self.json_head).json()
        print(common_add_res)
        time.sleep(5)
        endtime = str(datetime.now().strftime("%Y-%m-%d %X"))
        logger.info(f'结束创建优惠券时间是：{endtime}')
        # 检查创建优惠券是否存在
        common_list_url = "{}/ecmc/coupon/couponList".format(self.Activity_Center_URL)
        common_list_body = {"pageNum": 1, "pageSize": 20, "couponName": self.coupon_name}
        common_list_res = self.coupon_rss.post(url=common_list_url, json=common_list_body,
                                                 headers=self.json_head).json()
        common_list_data = common_list_res["result"]
        coupon_id = []
        cTime  = []
        for i in range(len(common_list_data)):
            coupon_id.append(common_list_data[i]["id"])
            cTime.append(common_list_data[i]["cTime"])
        logger.info(f"获取优惠券名称为{self.coupon_name}的优惠券id的list列表为{coupon_id},{cTime}")
        if cTime[0] >= starttime and cTime[0] <= endtime:
            logger.info(f"优惠券：{self.coupon_name}创建成功,生成的优惠券id为{coupon_id[0]}")
        else:
            logger.error(f"优惠券：{self.coupon_name}创建失败！！")
        return coupon_id[0]



    def common_copy(self):
        """优惠券复制"""

        if len(self.coupon_id) == 0:
            logger.info("不存在优惠券")
        elif len(self.coupon_id) >= 1:
            logger.info("存在优惠券")
            self.coupon_id = self.coupon_id[0]
            logger.info(f"获取的couponId为：{self.coupon_id}")
            common_detail_url = "https://uat-activity.hqchip.com/ecmc/coupon/couponDetail"
            common_detail_body = {"couponId": self.coupon_id}
            common_detail_res = self.coupon_rss.post(url=common_detail_url, json=common_detail_body, headers=self.json_head).json()
            logger.info("查询成功")
            couponType = common_detail_res["result"]["couponType"][0]
            name = common_detail_res["result"]["name"]
            couponStatus = common_detail_res["result"]["couponStatus"]
            effectiveType = common_detail_res["result"]["effectiveType"]
            couponExpireDays = common_detail_res["result"]["couponExpireDays"]
            useType = common_detail_res["result"]["useType"]
            couponAmount = common_detail_res["result"]["couponAmount"]
            couponDiscount = common_detail_res["result"]["couponDiscount"]
            canUseGoods = common_detail_res["result"]["canUseGoods"]
            couponKind = common_detail_res["result"]["couponKind"]
            useWidthDiscount = common_detail_res["result"]["useWidthDiscount"]
            common_copy_url = "https://uat-activity.hqchip.com/ecmc/coupon/couponAdd"
            common_copy_body = {"couponId": self.coupon_id, "couponType": couponType, "name": name, "couponStatus": couponStatus, "effectiveType": effectiveType,
                               "couponExpireDays": couponExpireDays, "useType": useType, "couponAmount": couponAmount, "couponDiscount": couponDiscount,
                               "canUseGoods": canUseGoods, "couponKind": couponKind, "useWidthDiscount": useWidthDiscount,
                               }
            common_add_res = self.coupon_rss.post(url=common_copy_url, json=common_copy_body, headers=self.json_head).json()
            logger.info(common_add_res)
            logger.info(f"优惠券复制保存成功!")
        else:
            logger.error("---")
        return self

    def common_forbidden(self, union_ids):
        """优惠券禁用"""
        if len(self.coupon_id) == 0:
            logger.info("不存在优惠券")
        elif len(self.coupon_id) >= 1:
            for i in range(len(self.coupon_id)):
                logger.info(self.coupon_id[i])
                common_detail_url = "https://uat-activity.hqchip.com/ecmc/coupon/couponDetail"
                common_detail_body = {"couponId": self.coupon_id[i]}
                common_detail_res = self.coupon_rss.post(url=common_detail_url, json=common_detail_body, headers=self.json_head).json()
                logger.info(f"查询成功,{common_detail_res}")
                if common_detail_res["result"]["couponStatus"] == 2 and self.couponShowStatus[i] != 3:
                    logger.info(f"优惠券id：{self.coupon_id[i]}的状态为生效中")
                    if self.forbidType == 1:
                        logger.info("此禁用为禁用整张优惠券，此禁用产生效果为该优惠券被禁用后，所有已领取该优惠券且还没有使用的账户，该优惠券会立即失效和不会显示在用户中心且该优惠券正在发放中，禁用后也将会停止发放")
                        common_forbidden_url = f"https://uat-activity.hqchip.com/ecmc/coupon/couponDisable"
                        common_forbidden_body = {"couponId": self.coupon_id[i],"forbidType": 1}
                        common_forbidden_res = self.coupon_rss.post(url=common_forbidden_url, json=common_forbidden_body, headers=self.json_head).json
                        logger.info(f"优惠券id：{self.coupon_id[i]}禁用成功")
                    elif self.forbidType == 2:
                        logger.info("此禁用为禁用指定华秋id归属该优惠券")
                        common_forbidden_url = f"https://uat-activity.hqchip.com/ecmc/coupon/couponDisable"
                        common_forbidden_body = {"couponId": self.coupon_id[i],"forbidType": 1, "uidStr": union_ids}
                        common_forbidden_res = self.coupon_rss.post(url=common_forbidden_url, json=common_forbidden_body, headers=self.json_head).json
                        logger.info(f"华秋id：{union_ids}的优惠券id：{self.coupon_id[i]}禁用成功")

                elif self.couponShowStatus[i] == 3:
                    logger.info(f"优惠券id：{self.coupon_id[i]}的状态为禁用，不可操作禁用")
                else:
                    logger.info(f"优惠券id：{self.coupon_id[i]}的状态为已过期")
                continue






if __name__ == '__main__':
   target_rss = SOOLogin("admin", "12345678", "uat-activity.hqchip.com", "ecmc").target_login()

   Coupon(target_rss, "验证获取代码运行时间7", 1).common_list().common_forbidden(0)

