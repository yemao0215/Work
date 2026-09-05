import time

import jsonpath
import requests

from huaqiu_order_api.HQCHIP_SOO.login import SOOLogin
from huaqiu_order_api.HQCHIP_SRM.SRM_gateway.login import GatewayUserLogin
from huaqiu_order_api.HQCHIP_SRM.partner_users.partner_users import PartnerUsers
from huaqiu_order_api.common.loguru_logger import logger


class GoodsManage:
    # 门户商品管理
    def __init__(self,gateway_rss, goods_name):
        self.gateway_rss = gateway_rss
        self.json_head = {"Content-Type": "application/json"}
        self.file_head = {"Content-Type": "multipart/form-source_data"}
        self.goods_name = goods_name

    def goods_list(self):
        """商品管理列表"""
        search_url = "https://uat-partner.huaqiu.com/partner/goods/page"
        search_body = {"goodsName": self.goods_name, "goodsSn": "", "brandName": "", "startDate": "", "endDate": "",
                       "current": 1, "size": 10, "offSale": "", "feature": False, "type": 1}
        search_res = self.gateway_rss.post(url=search_url, json=search_body, headers=self.json_head).json()
        logger.info(search_res)
        recordsInfo = search_res["body"]["records"]
        goodsName = []
        goodsId = []
        dominantStock = []
        brandName = []
        encap = []
        pn2 = []
        for i in range(len(recordsInfo)):
            goodsName.append(recordsInfo[i]["goodsName"])
            goodsId.append(recordsInfo[i]["goodsId"])
            dominantStock.append(recordsInfo[i]["dominantStock"])
            brandName.append(recordsInfo[i]["brandName"])
            encap.append(recordsInfo[i]["encap"])
            pn2.append(recordsInfo[i]["pn2"])
        for q in range(len(recordsInfo)):
            if self.goods_name == goodsName[q]:
                self.goods_name = goodsName[q]
                self.goodsId = goodsId[q]
                self.dominantStock = dominantStock[q]
                self.brandName = brandName[q]
                self.encap = encap[q]
                self.pn2 = pn2[q]
        logger.info(f"获取到{self.goods_name}的库存id：{self.goodsId}、优势库存标签：{self.dominantStock}、品牌：{self.brandName}、封装：{self.encap}、2016后台供应商代号为：{self.pn2}")
        return self

    def goods_dominant_emplace(self):
        """合作库存设置成优势库存"""

        dominant_emplace_url = "https://uat-partner.huaqiu.com/partner/goods/dominantStock"
        dominant_emplace_body = {"body": {"stocks":
                                              [{"goodsId": self.goodsId, "goodsName": self.goods_name, "brandName": self.brandName, "encap": self.encap, "pn2":self.pn2}],
                                          "validateDay": 7
                                          }}
        dominant_emplace_res = self.gateway_rss.post(url=dominant_emplace_url, json=dominant_emplace_body, headers=self.json_head).json()
        msg = dominant_emplace_res["msg"]
        if msg == "超出优势库存数额限制":
            search_url = "https://uat-partner.huaqiu.com/partner/goods/page"
            search_body = {"goodsName": "", "goodsSn": "", "brandName": "", "startDate": "", "endDate": "",
                           "current": 1, "size": 10, "offSale": "", "feature": False, "type": 3}
            search_res = self.gateway_rss.post(url=search_url, json=search_body, headers=self.json_head).json()
            logger.info(search_res)
            recordsInfo = search_res["body"]["records"]
            logger.info(f"打印：{recordsInfo[-1]}")
            goodsName = recordsInfo[-1]["goodsName"]
            goodsId = recordsInfo[-1]["goodsId"]
            dominantStock = recordsInfo[-1]["dominantStock"]
            brandName = recordsInfo[-1]["brandName"]
            encap = recordsInfo[-1]["encap"]
            pn2 = recordsInfo[-1]["pn2"]
            cancel_dominant_url = "https://uat-partner.huaqiu.com/partner/goods/cancelDominantStock"
            cancel_dominant_body = {"body": {"stocks": [{"goodsId": goodsId, "goodsName": goodsName, "brandName": brandName, "encap": encap, "pn2": pn2}]}}
            cancel_dominant_res = self.gateway_rss.post(url=cancel_dominant_url, json=cancel_dominant_body, headers=self.json_head).json()
            logger.info(cancel_dominant_res)
            dominant_emplace_url = "https://uat-partner.huaqiu.com/partner/goods/dominantStock"
            dominant_emplace_body = {"body": {"stocks":
                                                  [{"goodsId": self.goodsId, "goodsName": self.goods_name,"brandName": self.brandName, "encap": self.encap, "pn2": self.pn2}],
                                              "validateDay": 7
                                              }}
            dominant_emplace_res = self.gateway_rss.post(url=dominant_emplace_url, json=dominant_emplace_body,headers=self.json_head).json()
            logger.info(dominant_emplace_res)
        elif msg == "当前选择已是优势库存":
            pass


        return self

if __name__ == '__main__':
    target_rss = SOOLogin("caizhouyi", "12345678", "uat-srm.huaqiu.com", "partnermanage").target_login()
    supplier_name = ["旷天琪测试公司","蝶恋花","华秋注册测试预发布公司","11111华秋","定风波","tiantianceshi","124"]
    goods_name = ["YS007","YS008","YS009","YS010","YS011","YS012"]
    for i in range(len(supplier_name)):
        username = PartnerUsers(target_rss).partner_users_list_keyword(supplier_name[i])
        gateway_rss = GatewayUserLogin(username).gateway_login()
        for q in range(len(goods_name)):
            GoodsManage(gateway_rss,goods_name[q]).goods_list().goods_dominant_emplace()
