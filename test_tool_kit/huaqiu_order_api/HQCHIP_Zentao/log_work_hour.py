import math
import re

import jsonpath
import requests
import yaml

from huaqiu_order_api.HQCHIP_Zentao.login import ZenTaoLogin
from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_data import Data
from huaqiu_order_api.common.my_path import yaml_file, account_yaml, cookie_dir
from datetime import datetime, date, timedelta
from dateutil.tz import tzutc

class LogWorkHour:
    def __init__(self, rss=None, start_day=None):
        self.rss = requests.Session()
        self.json_head = {"Accept": "application/json, text/javascript, */*; q=0.01",
                          "Accept-Language": "zh-CN,zh;q=0.9",
                          "Connection": "keep-alive",
                          "Sec-Fetch-Dest": "empty",
                          "Sec-Fetch-Mode": "cors",
                          "Sec-Fetch-Site": "same-origin",
                          "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
                          "X-Requested-With": "XMLHttpRequest",
                          "sec-ch-ua": '"Google Chrome";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
                          "sec-ch-ua-mobile": "?0",
                          "sec-ch-ua-platform": '"Windows"',
                          "Referer": "https://p.huaqiu.com/index.php?m=effort&f=calendar"
                          }
        self.start_day = start_day

    def read_cookie_string(self, file_path="Zentao_cookie.txt"):
        """
        直接从cookie.txt读取整个cookie字符串
        文件内容应该是：lang=zh-cn; device=desktop; hideMenu=false; ...
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                cookie_str = f.read().strip()

            # print(f"读取到cookie字符串长度: {len(cookie_str)}")
            return cookie_str
        except Exception as e:
            print(f"读取cookie文件失败: {e}")
            return ""
    def week_day_create(self):
        # 获取当前日期
        today = date.today()

        # 计算本周一（weekday()返回0=周一, 1=周二, ..., 6=周日）
        monday = today - timedelta(days=today.weekday())

        # 生成一周的日期（周一到周日）
        week_dates = []
        for i in range(7):
            current_date = monday + timedelta(days=i)
            week_dates.append(current_date.strftime('%Y-%m-%d'))

        # 输出结果
        print("当前周日期（周一 ~ 周日）:")
        for i, date_str in enumerate(week_dates, 1):
            weekday_name = ['周一', '周二', '周三', '周四', '周五', '周六', '周日'][i - 1]
            print(f"{weekday_name}: {date_str}")

        # 如果需要作为列表获取
        print(f"\n日期列表: {week_dates}")
        return week_dates

    def month_dates_create(self, month=None, year=None):
        # 获取当前日期
        today = date.today()

        # 如果没有传入月份，使用当前月份
        if month is None:
            month = today.month
            year = today.year
        else:
            # 如果只提供了月份而没有年份，默认为当前年份
            if year is None:
                year = today.year

        # 获取当前月份的第一天和最后一天
        first_day_of_month = date(year, month, 1)
        if month == 12:
            last_day_of_month = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            last_day_of_month = date(year, month + 1, 1) - timedelta(days=1)

        # 生成指定月份的日期
        month_dates = []
        current_date = first_day_of_month
        while current_date <= last_day_of_month:
            month_dates.append(current_date.strftime('%Y-%m-%d'))
            current_date += timedelta(days=1)

        # 输出结果
        print(f"月份 {year} 年 {month} 月的日期:")
        for date_str in month_dates:
            print(date_str)

        # 如果需要作为列表获取
        print(f"\n日期列表: {month_dates}")
        return month_dates

    def log_work_hour(self, day=None):
        if day != None:
            self.start_day = day
        toay_work_hour_lst = []
        toay_work_hour_type = []
        cookie = self.read_cookie_string(cookie_dir)
        # print(cookie)
        self.json_head["Cookie"] = cookie
        url = "https://p.huaqiu.com/index.php?m=effort&f=ajaxGetEfforts&userID=29&year=2026"
        log_work_hour_res = self.rss.get(url=url, headers=self.json_head).json()
        # print(log_work_hour_res)
        if isinstance(log_work_hour_res, list):
            for i in range(len(log_work_hour_res)):
                # print(log_work_hour_res[i])
                if log_work_hour_res[i]["start"] == self.start_day and log_work_hour_res[i]["end"] == self.start_day:
                    toay_work_hour_lst.append(log_work_hour_res[i]["consumed"])
                    log_work_hour_detail_url = "https://p.huaqiu.com/index.php?m=effort&f=view&id={}&onlybody=yes".format(log_work_hour_res[i]['id'])
                    log_work_hour_detail_res = self.rss.get(url=log_work_hour_detail_url, headers=self.json_head).text
                    # print(log_work_hour_detail_res)
                    pattern = r'<th[^>]*>对象</th>\s*<td[^>]*>任务<a\s+href'
                    if re.search(pattern, log_work_hour_detail_res) is not None:
                        type = True
                        toay_work_hour_type.append(type)
                    else:
                        type = False
                        toay_work_hour_type.append(type)
        # print(toay_work_hour_lst, toay_work_hour_type)
        return toay_work_hour_lst, toay_work_hour_type

    def week_work_hour(self):
        # 获取当前周日期
        if self.start_day == None or self.start_day == '':
            week_dates = self.week_day_create()
        else:
            week_dates = [self.start_day]
        date_total = []
        date_total_type = []
        for date in week_dates:
            date_work_hour_lst, date_work_hour_type = self.log_work_hour(date)
            if date_work_hour_lst != []:
                total = sum(date_work_hour_lst)
                total_type_lst = [value for value, flag in zip(date_work_hour_lst, date_work_hour_type) if flag]
                total_type_num = sum(total_type_lst)
            else:
                total = 0
                total_type_num = 0
            date_total.append(total)
            date_total_type.append(total_type_num)
        date_work_hour_count = sum(date_total)
        date_total_type_count = sum(date_total_type)
        date_work_hour = dict(zip(week_dates, date_total))
        date_work_hour_type = {k: (v, info) for k, v, info in zip(week_dates, date_total, date_total_type)}

        date_hours = []
        for day, hours in date_work_hour_type.items():
            work_hours, actual_hours = hours
            date_hours.append(f"日期: {day}, 工时: {work_hours}小时，关联任务所用工时：{actual_hours}小时")
        print(date_hours)
        print("工时：{}".format(date_work_hour_count))
        print("关联任务工时：{}".format(date_total_type_count))
        return date_hours, date_work_hour_count, date_total_type_count

    def month_work_hour(self, month=None, year=None):
        month_dates = self.month_dates_create(month=int(month), year=int(year))
        date_total = []
        date_total_type = []
        for date in month_dates:
            date_work_hour_lst, date_work_hour_type = self.log_work_hour(date)
            if date_work_hour_lst != []:
                total = sum(date_work_hour_lst)
                total_type_lst = [value for value, flag in zip(date_work_hour_lst, date_work_hour_type) if flag]
                total_type_num = sum(total_type_lst)
            else:
                total = 0
                total_type_num = 0
            date_total.append(total)
            date_total_type.append(total_type_num)
        date_work_hour_count = sum(date_total)
        date_total_type_count = sum(date_total_type)
        date_work_hour = dict(zip(month_dates, date_total))
        date_work_hour_type = {k: (v, info) for k, v, info in zip(month_dates, date_total, date_total_type)}
        date_hours = []
        for day, hours in date_work_hour_type.items():
            work_hours, actual_hours = hours
            date_hours.append(f"日期: {day}, 工时: {work_hours}小时，关联任务所用工时：{actual_hours}小时")
        print(date_hours)
        print("工时：{}".format(date_work_hour_count))
        print("关联任务工时：{}".format(date_total_type_count))
        return date_hours, date_work_hour_count, date_total_type_count








# 使用示例
if __name__ == "__main__":
    start_day = "2026-01-13"
    # start_day = None
    month = None
    year = None
    # from huaqiu_order_api.HQCHIP_Zentao.login import ZenTaoLogin
    # iso_time = ZenTaoLogin().get_current_iso_utc()
    # print(f"当前UTC时间: {iso_time}")
    # rss = ZenTaoLogin().login()
    LogWorkHour(start_day=start_day).month_dates_create()
    LogWorkHour(start_day=start_day).week_work_hour()
    # LogWorkHour(start_day=start_day).month_work_hour(month=month, year=year)