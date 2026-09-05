import re

import requests

from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_data import Data
from huaqiu_order_api.common.my_path import bom_dir


class BomOrder:
    bom_queryMatch_res_cookie = ""
    def __init__(self, phone, psw, goods_id):
        """
        :param phone:  登录账号
        :param psw:  登录密码
        :param goods_id:  购买的产品id
        """
        self.phone = phone
        self.goods_id = goods_id
        self.rss = requests.Session()
        self.url = 'https://uat-passport.elecfans.com/login/dologin.html'
        self.body = {'siteid': 12, 'account': self.phone, 'password': psw}
        self.headers = {"Content-Type": "application/x-www-form-urlencoded"}
        self.files = [('file', ('bom.xls', open(bom_dir, 'rb'), 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'))]

    def login(self):
        res = self.rss.post(url=self.url, data=self.body, headers={"Connection":"close"})
        logger.info(f"开始执行登录账号:{self.body}")
        json_res = res.json()
        token = json_res["source_data"]["token"]
        setattr(Data, 'token', token)
        cookie_url = json_res["source_data"]["syncurl"]
        for sso_url in cookie_url:
            if sso_url.find('https://uat-www.hqchip.com', 0, 26) != -1:
                self.rss.get(sso_url)  # 访问单点url生成cookie
                logger.info(f"登录成功")
                break
        else:
            logger.error(f"没有找到IC商城单点登录链接，获取单点cookie失败")
            raise IOError
        return self
    def bom_file(self):
        Select_file_url = f"https://uat-www.hqchip.com/ajax/upbatchcartgoods"
        res_Select_file_res = self.rss.post(url=Select_file_url, files=self.files).json()
        server_file = res_Select_file_res["img"]
        fileMD5 = res_Select_file_res["fileMD5"]
        bom_match_url = f"https://uat-www.hqchip.com/bom/match"
        bom_match_res = self.rss.post(url=bom_match_url, data={"file": server_file, "fileMD5": fileMD5}).json()
        bom_matchInfo = bom_match_res["source_data"]["list"][0]
        bom_id = bom_match_res["source_data"]["bom_id"]
        bom_matchInfo_list = bom_matchInfo["items_json"]
        bom_goods_name = bom_matchInfo_list[3]
        bom_brand_name = bom_matchInfo_list[2]
        setattr(Data, 'bom_goods_name', bom_goods_name)
        setattr(Data, 'bom_brand_name', bom_brand_name)
        bom_queryMatch_url = f"https://uat-www.hqchip.com//bom/queryMatch"
        bom_queryMatch_res = self.rss.post(url=bom_queryMatch_url, data={"bom_id": bom_id}).json()
        bom_queryMatchInfo = bom_queryMatch_res["source_data"]["result_list"][0]
        bom_queryMatchsourceInfo = bom_queryMatch_res["source_data"]["source_list"][0]
        match_type = bom_queryMatchInfo["match_type"]
        item_id = bom_queryMatchsourceInfo["item_id"]
        print(item_id)
        if match_type == "1":
            logger.info("bom文件完全匹配")
        elif match_type == "2":
            logger.info("bom文件待确认")
            confirmModel_url = f"https://uat-www.hqchip.com/bom/confirmModel"
            confirmModel_res = self.rss.post(url=confirmModel_url, data={"item_id": item_id}).json()
            if confirmModel_res["status"] =="1":
                logger.info("点击确认成功")
        elif match_type == "3":
            logger.info("bom文件无法匹配")

        bom_getUserInfo_url = "https://uat-www.hqchip.com/bom/getUserInfo"
        bom_getUserInfo_res = self.rss.get(url=bom_getUserInfo_url)
        company_name = bom_getUserInfo_res.json()["source_data"]["company_name"]
        mobile_phone = bom_getUserInfo_res.json()["source_data"]["mobile_phone"]
        # print(company_name, mobile_phone)
        bom_queryMatch_res_cookie = bom_getUserInfo_res.cookies
        # print(bom_queryMatch_res_cookie)
        if company_name == "":
            company_name = '测试'
        createServiceBom_url = "https://uat-www.hqchip.com/bom/createServiceBom"
        createServiceBom_res = self.rss.post(url=createServiceBom_url, data={
                                                                            "bom_title": "bom",
                                                                            "money_typy": 1,
                                                                            "bom_id": bom_id,
                                                                            "select_item_ids": '',
                                                                            "consignee": "测试",
                                                                            "mobile": mobile_phone,
                                                                            "company_name": company_name,
                                                                            "is_patch": 1
                                                                            })
        logger.info(f"开始提交订单，生成订单编号")
        submitordersuccess_url = createServiceBom_res.json()["url"]
        submitordersuccess_url_f, submitordersuccess_url_id = submitordersuccess_url.split("=")
        submitordersuccess_res = self.rss.get(f"https://uat-www.hqchip.com{submitordersuccess_url}").text
        order_sn = submitordersuccess_res.split(f'<a href="/mycenter/order/bom/detail?id={submitordersuccess_url_id}" target="_blank">')[1].split('</a></td><td>')[0]
        logger.info(f"订单生成成功，需求单号: {order_sn}")
        logger.debug('=*'*50)
        return order_sn





if __name__ == '__main__':
    BomOrder('15912757721', 'a123456', 2500323787).login().bom_file()