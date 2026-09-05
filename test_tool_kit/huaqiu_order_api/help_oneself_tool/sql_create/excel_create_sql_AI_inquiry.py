import pandas
import requests

from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_path import excel_create_sql_ai_inquiry_dir, excel_create_sql_ai_inquiry_dir_sql


class ExcelCreateSqlAIInquiry:
    def __init__(self):
        self.headers_json = {"Content-Type": "application/json;charset=utf-8"}
        self.rss = requests.Session()
    def read_data(self):
        logger.info("开始读取数据")
        data = pandas.read_excel(excel_create_sql_ai_inquiry_dir)
        self.goods_id = data['库存ID']
        self.goods_no = data['芯城编号']
        self.no_sales_day = data['无销售天数']
        return self
    def excel_create_sql(self):
        for i in range(len(self.goods_id)):
            sql = ("INSERT INTO `ecs_goods_ic_contrast_stats` (`goods_id`, `goods_no`,`stock_num_7`,`stock_num_30`,`stock_num_90`, `stock_num_180`, `stock_num_365`, `stock_num_year`"
                   ", `stock_amount_7`, `stock_amount_30`, `stock_amount_90`, `stock_amount_180`,`stock_amount_365`, `stock_amount_year`, `no_sale_day`) "
                   "VALUES({}, '{}', 0, 0, 0, 0, 0, 0, 0.00000, 0.00000, 0.00000, 0.00000, 0.00000, 0.00000, {});").format(self.goods_id[i], self.goods_no[i], self.no_sales_day[i])
            with open(excel_create_sql_ai_inquiry_dir_sql, 'a', encoding='utf-8') as f:
                f.write(f'-- 在`ecs_goods_ic_contrast_stats` 插入数据：字段goods_id：{self.goods_id[i]}，goods_no：{self.goods_no[i]}，无销售天数：{self.no_sales_day[i]}\n')
                f.write(sql)
                f.write('\n')
        return self


if __name__ == '__main__':
    ExcelCreateSqlAIInquiry().read_data().excel_create_sql()