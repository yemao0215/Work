import yaml

from huaqiu_order_api.SSO_Reception.sso_reception import SSO_Reception
from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_data import Data
from huaqiu_order_api.common.my_path import yaml_file


class PayOrderAssets:
    def __init__(self, rss, order_sn):
        self.rss = rss
        self.order_sn = order_sn
        self.token = getattr(Data, "token")
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.HQCHIP_URL = data["HQCHIP_URL"]
        token = getattr(Data, 'token')
        self.headers = {"Content-Type": "application/x-www-form-urlencoded", "Authorization": token,
                        "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://www.huaqiu.com)"
                        }
        self.headers_json = {"Content-Type": "application/json;charset=utf-8", "Authorization": token,
                             "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://www.huaqiu.com)"
                             }

    def center_order_list(self):
        """元器件订单搜索"""
        center_order_list_url = self.HQCHIP_URL + f"/hqapi/usericorder/getlistinfoV2?page=1&order_keyword={self.order_sn}&order_goods_keyword=&otime=0&ostatus="
        center_order_list_res = self.rss.get(url=center_order_list_url, headers=self.headers_json).json()
        self.order_id = center_order_list_res["result"]["order_list"][0]["order_id"]
        logger.info(f"订单号：{self.order_sn}的order_id：{self.order_id}")


    def order_pay_type(self):
        pass

if __name__ == '__main__':
    rss = SSO_Reception('https://uat-www.hqchip.com', '13632951464', 'a123456').login()
    PayOrderAssets(rss, "S2025102365635").center_order_list()