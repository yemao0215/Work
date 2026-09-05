import os
import time

from datetime import datetime

import requests

from huaqiu_order_api.HQCHIP.mian_ic import RunIC
from huaqiu_order_api.HQCHIP_ERP.erp_order_cancellation import ErpOrderCancellation
from huaqiu_order_api.HQCHIP_SOO.login import SOOLogin


class WindowsShutdown:
    # windows 电脑自动关机
    def __init__(self, import_time):
        self.rss = requests.Session()
        self.import_time = import_time


    def get_time_difference(self):
        """计算目标关机时间与当前时间之间的秒数"""
        # 获取当前时间
        current_time = datetime.now()

        # 将目标日期时间字符串转换为日期时间对象
        target_datetime = datetime.strptime(self.import_time, "%Y-%m-%d %H:%M")

        # 计算时间差（单位：秒）
        time_difference = target_datetime - current_time
        print(time_difference)
        return time_difference.total_seconds()

    def schedule_shutdown(self):
        """根据目标日期时间安排关机"""
        try:
            # 获取与当前时间的差值（单位：秒）
            delay_seconds = self.get_time_difference()

            if delay_seconds < 0:
                print("目标时间已经过去，请输入一个未来的时间。")
                return

            # 执行关机命令
            os.system(f"shutdown /s /f /t {int(delay_seconds)}")
            print(f"系统将在 {self.import_time} 自动关机，距离现在还有 {int(delay_seconds)} 秒。")
            return True

        except Exception as e:
            print(f"发生错误: {e}")
            return False
    def schedule_create_ICorder(self):
        """根据目标日期时间安排自动生成IC订单"""
        try:
            # 获取与当前时间的差值（单位：秒）
            delay_seconds = self.get_time_difference()

            if delay_seconds < 0:
                print("目标时间已经过去，请输入一个未来的时间。")
                return
            # 延时后执行方法
            time.sleep(int(delay_seconds))
            print(f"系统将在 {self.import_time} 自动生成IC订单，距离现在还有 {int(delay_seconds)} 秒。")
            # 执行生单命令
            RunIC().mian_ic_order_create()
            target_rss = SOOLogin("uat-e.hqchip.com", "AuthLogin").target_login()
            ErpOrderCancellation(target_rss).erp_ic_order_transfer_claim()
        except Exception as e:
            print(f"发生错误: {e}")
if __name__ == '__main__':
    import_time = "2026-07-20 21:00"
    WindowsShutdown(import_time).schedule_shutdown()