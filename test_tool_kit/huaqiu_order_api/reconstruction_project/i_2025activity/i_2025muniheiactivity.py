import threading
import jsonpath
import pandas
import requests
import yaml


from threading import Thread
import time

from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_path import yaml_file, munihei_user_dir


class Muniheiactivity:
    def __init__(self, LOTTERY_TIMES_start, LOTTERY_TIMES_end, THREAD_COUNT):

        self.LOTTERY_TIMES_start = LOTTERY_TIMES_start  # 抽奖次数参数化
        self.LOTTERY_TIMES_end = LOTTERY_TIMES_end
        self.THREAD_COUNT = THREAD_COUNT     # 线程数参数化

        self.headers = {'Content-Type': 'application/x-www-form-urlencoded',
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36; +https://www.huaqiu.com)"
                        }
        # user_id = "1111"
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.HQCHIP = data['HQCHIP_URL']
        # self.ERP_URL = data['ERP_URL']


    def get_session(self):
        # 线程本地存储Session
        local = threading.local()
        if not hasattr(local, "session"):
            local.session = requests.Session()
        return local.session

    def lottery(self):
        logger.info(f"开始读取")
        data = pandas.read_excel(munihei_user_dir)
        user_id = data['user_id']
        session = self.get_session()
        self.prize_ai_num = 0
        self.prize_backpack_num = 0
        self.prize_coupon_num = 0
        self.prize_tumbler_num = 0
        self.prize_support_num = 0
        self.prize_data_cable_num = 0
        self.prize_error_num = 0
        self.prize_error_user = []
        for i in range(self.LOTTERY_TIMES_start, self.LOTTERY_TIMES_end):
            try:
                # 是否获取地理位置
                add_Geographic_url = "{}/activityapi/addUserGeographicLocationInfo".format(self.HQCHIP)
                add_Geographic_body = {"user_id": user_id[i], "place_click_yes": 1, "platform": "hqchip"}
                add_Geographic_res = session.post(url=add_Geographic_url, data=add_Geographic_body, headers=self.headers, timeout=10).json()
                self.lottery_url = "{}/activityapi/munichActivityLottery".format(self.HQCHIP)
                user_id_str = str(user_id[i])
                session.cookies.set('ICC_user_id', user_id_str, domain=".hqchip.com", path="/")
                resp = session.post(url=self.lottery_url, data={"user_id": user_id[i]}, headers=self.headers, timeout=10)
                resp.raise_for_status()
                json_res = resp.json()
                # print(json_res)
            except Exception as e:
                logger.error(f"[线程 {threading.get_ident()}] 第{i+1}次请求失败: {e}")
                continue

            ret_code = jsonpath.jsonpath(json_res, '$.retCode')
            if ret_code and ret_code[0] == 0:
                prize_names = jsonpath.jsonpath(json_res, '$..prize_name')
                if prize_names:
                    logger.info(f"[线程 {threading.get_ident()}] 第{i+1}次抽奖 - 用户：{user_id[i]}抽中奖品: {prize_names[0]}")
                    if prize_names[0] == "AI语音机器人":
                        self.prize_ai_num = self.prize_ai_num +1
                    elif prize_names[0] == "双肩背包":
                         self.prize_backpack_num = self.prize_backpack_num + 1
                    elif prize_names[0] == "满5000减300优惠券":
                        self.prize_coupon_num = self.prize_coupon_num + 1
                    elif prize_names[0] == "保温杯":
                        self.prize_tumbler_num = self.prize_tumbler_num + 1
                    elif prize_names[0] == "手机支架":
                        self.prize_support_num = self.prize_support_num + 1
                    elif prize_names[0] == "三充数据线":
                        self.prize_data_cable_num = self.prize_data_cable_num + 1
                else:
                    logger.warning(f"[线程 {threading.get_ident()}] 第{i+1}次抽奖 - 用户：{user_id[i]}执行抽奖结果：未解析到奖品名称")
                    self.prize_error_num = self.prize_error_num + 1
                    self.prize_error_user.append(user_id[i])
            else:
                error_msg = jsonpath.jsonpath(json_res, '$.retMsg')
                if error_msg:
                    logger.error(f"[线程 {threading.get_ident()}] 第{i+1}次抽奖错误 - 用户：{user_id[i]}执行抽奖，报错信息: {error_msg[0]}")
                    self.prize_error_num = self.prize_error_num + 1
                    self.prize_error_user.append(user_id[i])
                else:
                    logger.error(f"[线程 {threading.get_ident()}] 第{i+1}次抽奖 - 用户：{user_id[i]}执行抽奖，报错信息: 未知错误")
                    self.prize_error_num = self.prize_error_num + 1
                    self.prize_error_user.append(user_id[i])
        return self

    def main(self):
        start_time = time.time()
        threads = []
        for _ in range(self.THREAD_COUNT):
            t = Thread(target=self.lottery)
            t.start()
            threads.append(t)
        for t in threads:
            t.join()
        logger.info(f"总耗时: {time.time() - start_time:.2f}秒")
        logger.info(f"抽奖次数:{self.LOTTERY_TIMES_end - self.LOTTERY_TIMES_start}: "
                    f"奖品分布:AI语音机器人:{self.prize_ai_num}，双肩背包:{self.prize_backpack_num},"
                    f"满5000减300优惠券: {self.prize_coupon_num}，保温杯: {self.prize_tumbler_num},"
                    f"手机支架:{self.prize_support_num}，三充数据线:{self.prize_data_cable_num},"
                    f"报错次数：{self.prize_error_num}，报错用户id：{self.prize_error_user}")

        data = {
            "LOTTERY_TIMES_start": self.LOTTERY_TIMES_start,
            "LOTTERY_TIMES_end": self.LOTTERY_TIMES_end,
            "THREAD_COUNT": self.THREAD_COUNT,
            "prize_msg": {
                "抽奖次数": self.LOTTERY_TIMES_end - self.LOTTERY_TIMES_start,
                "奖品分布": {
                    "AI语音机器人": self.prize_ai_num,
                    "双肩背包": self.prize_backpack_num,
                    "满5000减300优惠券": self.prize_coupon_num,
                    "保温杯": self.prize_tumbler_num,
                    "手机支架": self.prize_support_num,
                    "三充数据线": self.prize_data_cable_num
                },
                "报错信息": {
                    "报错次数": self.prize_error_num,
                    "报错用户id": self.prize_error_user
                }

            }
        }
        return data

if __name__ == "__main__":
    LOTTERY_TIMES_start = 0
    LOTTERY_TIMES_end = 1
    THREAD_COUNT = 1
    Muniheiactivity(LOTTERY_TIMES_start, LOTTERY_TIMES_end, THREAD_COUNT).main()