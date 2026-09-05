import time
from threading import Thread

import jsonpath
import requests

from huaqiu_order_api.common.loguru_logger import logger

login_url = 'https://uat-passport.elecfans.com/login/dologin.html?referer=https://uat-www.hqchip.com'
data = {"siteid": 12, "account": 13062032726, "password": "a123456", "aliscene": "login"}
headers = {"Content-Type": "application/x-www-form-urlencoded"}
res = requests.Session()
rsp = res.post(url=login_url, data=data, headers=headers).json()
print(rsp)
auth_url = jsonpath.jsonpath(rsp, '$..source_data.syncurl[2]')
res.get(url=auth_url[0])
lottery_url = 'https://uat-www.hqchip.com/activityapi/testLotter?model=test&key=6gRxaSK2kymSs&prize_type=1'


def lottery():
    for i in range(600):
        resp = res.get(url=lottery_url)
        json_res = resp.json()
        ret_code = jsonpath.jsonpath(json_res, '$.retCode') # 抽奖接口返回的code码
        if ret_code == [0]:
            product_name = jsonpath.jsonpath(json_res, '$..prize_name')
            logger.info(f"抽中的奖品为:{product_name}")
        else:
            product_msg = jsonpath.jsonpath(json_res, '$.retMsg')
            logger.info(f"抽奖接口返回错误，错误信息为:{product_msg}")


def main():
    start_time = time.time()
    ts = []
    for i in range(4):
        t1 = Thread(target=lottery)
        t1.start()
        ts.append(t1)
    for t in ts:
        t.join()
    end_time = time.time()
    print(end_time - start_time)


main()




