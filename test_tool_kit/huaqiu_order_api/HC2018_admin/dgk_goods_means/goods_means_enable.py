import math
import multiprocessing
import threading
import time

import jsonpath
import pandas
import requests
import yaml

from huaqiu_order_api.HC2018_admin.login.login import Login
from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_data import Data
from huaqiu_order_api.common.my_path import yaml_file, eccn_dir


class GoodsMeansEnable:
    def __init__(self, rss):
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.HC2018_ADMIN_URL = data['HC2018_ADMIN_URL']
        token = getattr(Data, "dos_auth_token")
        self.headers = {"Content-Type": "application/x-www-form-urlencoded", "Authorization": token,
                        "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://www.huaqiu.com)"
                        }
        self.headers_json = {"Content-Type": "application/json; charset=UTF-8", "Authorization": token,
                             "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://www.huaqiu.com)"
                             }
        self.rss = rss
    def goods_means_discard(self):
        """资料废弃数据查询"""
        search_url = "{}/v1/goods/DgkGoods/findList".format(self.HC2018_ADMIN_URL)
        search_body = {"brand_type": "2", "code_search_type": "1", "complete_type": -1, "has_stock": "-1", "is_enabled": "-1",
                       "is_need_real_count": True, "is_on_sale": "-1", "search_type": "1", "self_status": "-1", "src_type": "-1",
                       "type": "2", "page": 1, "per_page": 20}
        search_res = self.rss.post(url=search_url, json=search_body, headers=self.headers_json).json()
        total = jsonpath.jsonpath(search_res, "$..total")[0]
        page_number = math.ceil(int(total) / 100)
        self.new_goods_id_list = []
        for i in range(int(page_number)):
            i = i + 1
            search_body = {"brand_type": "2", "code_search_type": "1", "complete_type": -1, "has_stock": "-1","is_enabled": "-1",
                           "is_need_real_count": True, "is_on_sale": "-1", "search_type": "1", "self_status": "-1","src_type": "-1",
                           "type": "2", "page": i, "per_page": 100}
            search_res = self.rss.post(url=search_url, json=search_body, headers=self.headers_json).json()
            goods_id_list = jsonpath.jsonpath(search_res, "$..goods_id")
            self.new_goods_id_list = self.new_goods_id_list + goods_id_list
            self.goods_means_enable()

        # logger.info(f"goods_id列表为：{self.new_goods_id_list},一共：{len(self.new_goods_id_list)}个goods_id")
        return self
    def goods_means_enable(self):
        """废弃资料启用"""
        if self.new_goods_id_list != []:
            goods_means_enable_url = "{}/v1/goods/DgkGoods/restartGoods".format(self.HC2018_ADMIN_URL)
            for i in range(len(self.new_goods_id_list)):
                goods_means_enable_body = {"goods_id": self.new_goods_id_list[i]}
                search_res = self.rss.post(url=goods_means_enable_url, json=goods_means_enable_body, headers=self.headers_json)
                if search_res.status_code == 200:
                    logger.info(f"goods_id: {self.new_goods_id_list[i]} 启用成功")
        else:
            logger.info(f"页面上暂无资料废弃数据")
        return self
    # def mian_goods_enable(self):
    #     self.goods_means_discard()
    #
    # def main(self):
    #     threads = []
    #
    #     t = threading.Thread(target=self.mian_goods_enable())
    #     threads.append(t)
    #     t.start()
    #     for t in threads:
    #         t.join()
    #     print("All test cases executed.")


if __name__ == '__main__':
    from huaqiu_order_api.HC2018_admin.login.login import Login
    rss = Login().login()
    # GoodsMeansEnable(rss).mian_goods_enable()
    # jobs = []
    # for i in range(5):
    #     p = multiprocessing.Process(target=GoodsMeansEnable(rss).mian_goods_enable())
    #     jobs.append(p)
    #     p.start()
    # threads = []
    #
    # thread = threading.Thread(target=GoodsMeansEnable(rss).mian_goods_enable())
    # t2 = threading.Thread(target=GoodsMeansEnable(rss).mian_goods_enable())
    # t3 = threading.Thread(target=GoodsMeansEnable(rss).mian_goods_enable())
    # t4 = threading.Thread(target=GoodsMeansEnable(rss).mian_goods_enable())
    # t5 = threading.Thread(target=GoodsMeansEnable(rss).mian_goods_enable())
    # t6 = threading.Thread(target=GoodsMeansEnable(rss).mian_goods_enable())
    # t7 = threading.Thread(target=GoodsMeansEnable(rss).mian_goods_enable())
    # t8 = threading.Thread(target=GoodsMeansEnable(rss).mian_goods_enable())
    # t9 = threading.Thread(target=GoodsMeansEnable(rss).mian_goods_enable())
    # thread.start()
    # t2.start()
    # t3.start()
    # t4.start()
    # t5.start()
    # t6.start()
    # t7.start()
    # t8.start()
    # t9.start()
    #
    #
    # # 等待线程执行完成
    # thread.join()
    # t2.join()
    # t3.join()
    # t4.join()
    # t5.join()
    # t6.join()
    # t7.join()
    # t8.join()
    # t9.join()