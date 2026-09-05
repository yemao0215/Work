import pandas
import requests

from huaqiu_order_api.common.my_path import xl_dos_brand_dir, dos_stock_txt_sql


class TextXlDosBrandSql:
    def __init__(self):
        self.headers_json = {"Content-Type": "application/json; charset=utf-8"}
        self.rss = requests.Session()


    def main_text_sql(self, per_page=None):

        dos_data = pandas.read_excel(xl_dos_brand_dir)
        self.dos_brand_id = dos_data["DOS品牌id"]
        self.dos_brand_name = dos_data["DOS品牌简称"]
        self.xl_brand_id = dos_data["芯灵品牌id"]
        self.xl_brand_name = dos_data["芯灵品牌简称"]
        for i in range(len(self.dos_brand_id)):
            sql = "UPDATE ecs_dgk_brand_supplier SET shxl_brand_id = {} WHERE brand_id = {};".format(self.xl_brand_id[i], self.dos_brand_id[i])
            with open(dos_stock_txt_sql, "a+", encoding="utf-8") as f:
                f.write(f"-- 在ecs_dgk_brand_supplier修改品牌：{self.dos_brand_name[i]}的DOS品牌id：{self.dos_brand_id[i]}映射的芯灵品牌：{self.xl_brand_name[i]}的品牌id：{self.xl_brand_id[i]}\n")
                f.write(sql)
                f.write("\n")
if __name__ == '__main__':

    TextXlDosBrandSql().main_text_sql()