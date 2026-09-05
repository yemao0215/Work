import json

import requests


from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_data import Data


class ReplacementShop:
    # 替代料清空缓存
    def __init__(self, phone, psw, goods_name):
        """
        :param phone:  登录账号
        :param psw:  登录密码
        :param goods_id:  购买的产品id
        """
        self.phone = phone
        self.goods_name = goods_name
        self.rss = requests.Session()
        self.url = 'https://uat-passport.elecfans.com/login/dologin.html'
        self.body = {'siteid': 12, 'account': self.phone, 'password': psw}
        self.headers = {"Content-Type": "application/x-www-form-urlencoded"}

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

    def replacementlist_clear(self):
        """替代料专题页清空"""
        logger.info(f"开始进行列表清空操作")
        replacementlist_clear_url = "https://uat-item.hqchip.com/api/v2/substitute/getSubstituteList"
        self.replacement_headers = {"Content-type":"application/json"}
        replacementlist_clear_body = {"pageNum": 1, "pagesize": 6}
        replacementlist_clear_res = self.rss.post(url=replacementlist_clear_url, data=json.dumps(replacementlist_clear_body), headers=self.replacement_headers).json()
        print(replacementlist_clear_res)
        return self

    def replacement_goods_clear(self):
        """替代料专题页具体型号清空"""
        logger.info(f"开始进行型号清空操作，清空型号为{self.goods_name}")
        replacement_goods_clear_url = "https://uat-item.hqchip.com/api/v2/substitute/matchingSubstitute"
        replacement_goods_clear_body = {"goodsName": self.goods_name, "disablecache": True}
        replacement_goods_clear_res = self.rss.post(url=replacement_goods_clear_url, data=json.dumps(replacement_goods_clear_body), headers=self.replacement_headers).json()
        print(replacement_goods_clear_res)
        return self

if __name__ == '__main__':
    # ReplacementShop("123", "123", "123").replacementlist_clear()
    goods_name = ["CC0603KRX7R9BB104"]
    for i in range(len(goods_name)):
        ReplacementShop("123","123",goods_name[i]).replacementlist_clear().replacement_goods_clear()
        continue