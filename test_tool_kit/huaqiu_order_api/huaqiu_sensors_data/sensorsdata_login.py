import json

import requests

from huaqiu_order_api.common.loguru_logger import logger


class SensorsData:
    def __init__(self):
        """
        :param phone:  登录账号
        :param psw:  登录密码
        :param goods_id:  购买的产品id
        """
        # self.phone = phone
        # self.goods_id = goods_id
        self.data_rss = requests.Session()
        self.url = 'https://uat-passport.elecfans.com/login/dologin.html'
        # self.body = {'siteid': 12, 'account': self.phone, 'password': psw}
        self.headers = {"Content-Type": "application/x-www-form-urlencoded"}

    def login_pro(self):
        pass

    def login_test(self):
        url = "https://data.hqchip.com/api/v2/sbp/secret/pubkey?algorithm=RSA"
        res = self.data_rss.get(url=url)
        logger.info(json.loads(res.text))
        login_url = "https://data.hqchip.com/api/v2/auth/login?project=default&is_global=false"
        source_data = json.loads(res.text)["public"]
        print(login_url + source_data)
        res1 = self.data_rss.post(url=login_url + source_data)
        print(res1)

if __name__ == '__main__':
    SensorsData().login_test()

