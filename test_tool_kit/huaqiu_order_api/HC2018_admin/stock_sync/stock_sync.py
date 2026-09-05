import re
import requests
import yaml
from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_path import yaml_file



class StockSync:
    """库存定价数据同步接口"""
    def __init__(self):
        self.rss = requests.Session()
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.HC2018_ADMIN_URL = data['HC2018_ADMIN_URL']
        self.headers = {"Content-Type": "application/x-www-form-urlencoded"}

    def stock_sync(self):
        stock_sync_url = "{}/sync/test/goodsIcSalesStat?last_id={}&limit=3000&start_date=&end_date=".format(
            self.HC2018_ADMIN_URL, 2500368600) # 2500368600
        stock_sync_res = self.rss.get(url=stock_sync_url).text
        print(stock_sync_res)
        while True:
            i = 0
            # print(stock_sync_res)
            # 判断是否存在<hr>over，若存在，则同步完成，反之继续同步
            over_match = re.compile('(<hr>over)').search(stock_sync_res)
            if over_match:
                logger.info("库存定价同步接口已完成")
                break
            else:
                otu_goods_id = re.search('(window.location.href="/sync/test/goodsIcSalesStat\?last_id=)([0-9]*)',
                                         stock_sync_res).group(2)
                logger.info(f"获取到下个执行的goods_id： {otu_goods_id}")
                stock_sync_url = "{}/sync/test/goodsIcSalesStat?last_id={}&limit=3000&start_date=&end_date=".format(self.HC2018_ADMIN_URL, otu_goods_id)
                stock_sync_res = self.rss.get(url=stock_sync_url).text
            i += 1
if __name__ == '__main__':
    StockSync().stock_sync()
