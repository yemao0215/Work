import jsonpath
import requests
import yaml


from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_data import Data
from huaqiu_order_api.common.my_path import yaml_file, account_yaml


class EngineerGoodsSync:
    """ 工程师专区商品数据初始化 """
    def __init__(self):
        self.rss = requests.Session()
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.HC2018_ADMIN_URL = data['HC2018_ADMIN_URL']
        with open(account_yaml, 'r', encoding='utf-8') as yamlfile:
            account = yaml.load(yamlfile, Loader=yaml.FullLoader)
        # self.goods_id = account["HQCHIP_GOODS"]["goods_id"]
        self.goods_id = 2500368449
        self.headers = {"Content-Type": "application/x-www-form-urlencoded",
                        "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://www.huaqiu.com)"
                        }
        self.headers_json = {"Content-Type": "application/json; charset=UTF-8",
                             "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://www.huaqiu.com)"
                             }
        # self.auth_token = getattr(Data, 'dos_auth_token')
        # self.order_sn = getattr(Data, 'ic_order_sn')
        # self.order_sn = "S2023112175423"
        # self.headers_json["Authorization"] = self.auth_token

    def engineer_goods_sync(self):
        goods_sync_url = "{}/sync/Test/initSyncTask".format(self.HC2018_ADMIN_URL)
        logger.info(goods_sync_url)
        goods_sync_res = self.rss.get(url=goods_sync_url)
        logger.info(goods_sync_res)


if __name__ == '__main__':
    EngineerGoodsSync().engineer_goods_sync()