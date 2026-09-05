import calendar
import math
import re

import jsonpath
import requests
import yaml

from huaqiu_order_api.HQCHIP_Zentao.login import ZenTaoLogin
from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_data import Data
from huaqiu_order_api.common.my_path import yaml_file, account_yaml, cookie_dir, ehr_cookie_dir
from datetime import datetime, date, timedelta
from urllib.parse import quote
from dateutil.tz import tzutc

class Attendance:
    # EHR
    def __init__(self, rss=None, start_day=None):
        self.rss = requests.Session()
        self.json_head ={
                          'Accept': 'application/json, application/xml, text/play, text/html, */*',
                          'Accept-Language': 'zh-CN,zh;q=0.9',
                          'Connection': 'keep-alive',
                          'Content-Type': 'application/json; charset=utf-8',
                          'Origin': 'https://huaqiu.italent.cn',
                          'Referer': 'https://huaqiu.italent.cn/',
                          'Sec-Fetch-Dest': 'empty',
                          'Sec-Fetch-Mode': 'cors',
                          'Sec-Fetch-Site': 'same-site',
                          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36',
                          'X-Sourced-By': 'ajax',
                          'sec-ch-ua': '"Not(A:Brand";v="8", "Chromium";v="144", "Google Chrome";v="144"',
                          'sec-ch-ua-mobile': '?0',
                          'sec-ch-ua-platform': '"Windows"',
                          'Cookie': 'Tita_PC=s8xlqYIGF_v6RIji2hB8p--pC51qjvI1L_xoxkWURoJw6ljYcOF1WXE2J7NpW3IB; ssn_Tita_PC=s8xlqYIGF_v6RIji2hB8p--pC51qjvI1L_xoxkWURoJw6ljYcOF1WXE2J7NpW3IB; key-637955336=true; user_polling_timespace_615346=0'
}
        self.start_day = start_day
    def read_file_string(self, file_path="file_path"):
        """
        直接从file_path读取整个字符串
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

    def month_dates_create(self, year=None, month=None):
        """
        生成当前月的所有日期以及月份时间段

        Returns:
            tuple: (dates_list, month_range_str)
            - dates_list: 当前月所有日期的字符串列表，格式为 'YYYY/MM/DD'
            - month_range_str: 当前月的时间范围字符串，格式为 'YYYY-MM-01 ~ YYYY-MM-LastDay'
        """
        current_year = year
        current_month = month
        # 获取当前日期
        today = date.today()
        # 如果没有传入月份，使用当前月份
        if current_month is None:
            current_month = today.month
            current_year = today.year
        else:
            # 如果只提供了月份而没有年份，默认为当前年份
            if current_year is None:
                current_year = today.year

        # 获取当前月的第一天和最后一天
        # 本月第一天永远是1号
        first_day = date(current_year, current_month, 1)

        # 使用calendar.monthrange获取当月天数和最后一天的日期
        # monthrange返回(当月第一天是星期几, 当月天数)
        _, last_day_num = calendar.monthrange(current_year, current_month)
        last_day = date(current_year, current_month, last_day_num)

        # 生成当前月的所有日期
        month_dates = []
        current_date = first_day

        while current_date <= last_day:
            month_dates.append(current_date.strftime('%Y/%m/%d'))
            current_date += timedelta(days=1)

        # 生成月份时间段字符串
        month_range_str = f"{first_day.strftime('%Y/%m/%d')}~{last_day.strftime('%Y/%m/%d')}"
        # 输出结果
        print(f"=== {current_year}年{current_month}月 ===")
        print(f"月份时间段: {month_range_str}")
        print(f"总天数: {len(month_dates)}天")

        print("\n当月所有日期:")
        # 按周分组显示，更直观
        for i, date_str in enumerate(month_dates, 1):
            # 将字符串转换回date对象以获取星期几
            d = date.fromisoformat(date_str.replace('/', '-'))
            weekday_name = ['周一', '周二', '周三', '周四', '周五', '周六', '周日'][d.weekday()]

            # 每周换行显示
            if i == 1:
                print(f"第1周: ", end="")
            elif d.weekday() == 0:  # 周一
                week_num = i // 7 + (1 if i % 7 != 0 else 0)
                print(f"\n第{week_num}周: ", end="")

            # 标记今天
            today_marker = "✓" if date_str == today.strftime('%Y/%m/%d') else " "
            print(f"{today_marker}{weekday_name}({date_str[8:]}) ", end="")

        print(f"\n\n日期列表: {month_dates}")
        return month_dates, month_range_str
    def query_url_arguments(self, data):
        """将body参数转换成可拼接至url的参数"""
        lt = []
        for k, v in data.items():
            lt.append(k + '=' + quote(str(v)))
        # 这个是在for循环外面的，就是将列表的元素之间用用&符号连接起来
        query_string = '&'.join(lt)
        return query_string
    def user_attendance(self):
        month_dates, month_range_str = self.month_dates_create()
        param_body = {
            "viewName": "Attendance.SingleObjectListView.EmpAttendanceDataList",
            "metaObjName": "Attendance.AttendanceStatistics",
            "app": "Attendance",
            "PaaS-SourceApp": "Attendance",
            "PaaS-CurrentView": "Attendance.AttendanceDataRecordNavView",
            "frontendVersion": "2025121900",
            "_qsrcapp": "attendance",
            "quark_s": "d60573b96865cfd0560f120cd7ac798ba0abd9d63bb9dfd98f09c72537224c6e"
        }
        query_string = self.query_url_arguments(param_body)
        cookie = self.read_file_string(ehr_cookie_dir)
        print(cookie)
        self.json_head["Cookie"] = cookie
        print(query_string)
        url = "https://cloud.italent.cn/api/v2/UI/TableList?" + query_string + "&" + "shadow_context=%7BappModel%3A%22italent%22%2Cuppid%3A%221%22%7D"
        print(url)
        body = {
            "table_data":
                {
                    "advance": {"cmp_render": {"viewPath": "MyAttendanceStatisticsTable", "status": "enable"}},
                    "hasCheckColumn": True, "ext_data": {"ListViewLabel": "我的考勤列表"},
                    "isEnableGlobleCheck": False,
                    "hasRowHandler": True,
                    "paging": {"total": 0, "capacity": 100, "page": 0, "capacityList": [15, 30, 60, 100]},
                    "isAvatars": True,
                    "viewName": "Attendance.SingleObjectListView.EmpAttendanceDataList",
                    "operateColumWidth": 140,
                    "extendsParam": "",
                    "isSyncRowHandler": True,
                    "isFrozenOperationColumnHandler": False,
                    "isCustomListViewExisted": False,
                    "getTreeNodeUrl": None,
                    "sort_fields": [{"sort_column": "SwipingCardDate", "sort_dir": "desc"}],
                    "description": "员工出勤列表",
                    "metaObjName": "Attendance.AttendanceStatistics",
                    "isCustomListView": True,
                    "navViewIsCustom": False,
                    "navViewName": "Attendance.AttendanceDataRecordNavView",
                    "navViewVersion":"0"
                },
            "search_data":
                {
                    "metaObjName": "Attendance.AttendanceStatistics",
                    "searchView": "Attendance.EmpAttendanceDataSearch",
                    "items": [
                        {
                            "name": "Attendance.AttendanceStatistics.StaffId",
                            "text": "叶茂(yemao@huaqiu.com)",
                            "value": "637955336",
                            "num": "1",
                            "metaObjName": "",
                            "metaFieldRelationIDPath": "",
                            "queryAreaSubNodes": False
                        },
                        {
                            "name": "Attendance.AttendanceStatistics.StdIsDeleted",
                            "text": "否",
                            "value": "0",
                            "num":"5",
                            "metaObjName": "",
                            "metaFieldRelationIDPath": "",
                            "queryAreaSubNodes": False
                        },
                        {
                            "name": "Attendance.AttendanceStatistics.Status",
                            "text": "启用",
                            "value": "1",
                            "num": "6",
                            "metaObjName": "",
                            "metaFieldRelationIDPath": "",
                            "queryAreaSubNodes": False
                        },
                        {
                            "name": "Attendance.AttendanceStatistics.SwipingCardDate",
                            "text": month_range_str,
                            "value": month_range_str,
                            "num":"2",
                            "metaObjName":"",
                            "metaFieldRelationIDPath":"",
                            "queryAreaSubNodes":False
                        }
                    ],
                    "searchFormFilterJson": None
                }
        }
        user_attendance_res = self.rss.post(url=url, json=body, headers=self.json_head).json()
        print(user_attendance_res)



# 使用示例
if __name__ == "__main__":
    # Attendance().month_dates_create()
    Attendance().user_attendance()
