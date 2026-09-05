import re
import time

import jsonpath
import requests
import yaml
from bs4 import BeautifulSoup
import websocket

from huaqiu_order_api.HQCHIP_SOO.login import SOOLogin
from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_data import Data
from huaqiu_order_api.common.my_path import yaml_file, account_yaml

from huaqiu_order_api.project_sqlreview.sql_user_resources import SqlUserResources


class MongodbHandleSqlTool:

    def __init__(self, db, mongodb_sql=None, gather_name=None):
            self.rss = db
            self.gather_name = gather_name
            self.mongodb_sql = mongodb_sql


    def db_sql_handle(self):
        # 选择集合（表）
        collection = self.rss[self.gather_name]
        results = collection.find(self.mongodb_sql)
        print("\n查询多条结果：")
        for item in results:
            print(item)

if __name__ == '__main__':
    from huaqiu_order_api.project_sqlreview.mongodb_login import MongodbLogin
    env = "fat"
    mongodb_sql = {"GoodsId": 1000000024}
    db = MongodbLogin(env=env).login()
    MongodbHandleSqlTool(db=db, gather_name='supplier').db_sql_handle()