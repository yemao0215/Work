from decimal import Decimal

import pymysql

# 1. 建立数据库连接
from pymysql.cursors import DictCursor

from huaqiu_order_api.common.loguru_logger import logger


class  MySQLConnection:
    def __init__(self, table_name=None, where_field_name=None, where_field_value=None, orderby_field_name=None):
        self.table_name = table_name
        self.where_field_name = where_field_name
        self.where_field_value = where_field_value
        self.orderby_field_name = orderby_field_name
    def mysql_connection(self):

        conn = pymysql.connect(
            host="192.168.18.42",    # 数据库地址
            port=3306,           # mysql端口
            user="test",         # 账号
            password="joqgsUTPCalEM68I", # 密码
            database="hqchip",  # 数据库名
            charset="utf8mb4"    # 支持完整utf8，含emoji
        )

        # 2. 创建游标（执行SQL用）
        cursor = conn.cursor(DictCursor)
        return cursor

    def convert_decimal_to_float(self, data):
        """递归把所有Decimal转float，兼容字典/元组/列表"""
        if isinstance(data, Decimal):
            return float(data)
        elif isinstance(data, dict):
            return {k: self.convert_decimal_to_float(v) for k, v in data.items()}
        elif isinstance(data, (list, tuple)):
            return type(data)(self.convert_decimal_to_float(item) for item in data)
        else:
            return data
    def mysql_select_main(self, ):
        cursor = self.mysql_connection()
        sql = f"SELECT * FROM {self.table_name} WHERE {self.where_field_name} ='{self.where_field_value}' order by {self.orderby_field_name} desc limit 1;"
        logger.info(sql)
        cursor.execute(sql)
        row = cursor.fetchone()
        new_row = self.convert_decimal_to_float(row)
        logger.info(row)
        # 3. 关闭资源
        cursor.close()
        if self.table_name == "ecs_goods_ic_count":
            return new_row["purchase_price"], new_row["turnover_rate"], new_row["avg_gross_profit"], new_row["sales_customers"]
        else:
            return new_row



if __name__ == '__main__':
    table_name = "ecs_goods_ic_count"
    where_field_name = "goods_name"
    where_field_value = "searchV4.13.24"
    orderby_field_name = "c_time"
    MySQLConnection(table_name=table_name, where_field_name=where_field_name, where_field_value=where_field_value, orderby_field_name=orderby_field_name).mysql_select_main()