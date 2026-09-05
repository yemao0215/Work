import jsonpath
import requests
import yaml
import math
from huaqiu_order_api.common.my_data import Data
from huaqiu_order_api.common.my_path import yaml_file, dos_stock_txt_sql
from jsonpath_ng import parse
import json


class TextSql:
    def __init__(self, rss):
        self.rss = rss
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.HC2018_ADMIN_URL = data['HC2018_ADMIN_URL']
        self.auth_token = getattr(Data, 'dos_auth_token', "")
        self.headers = {"Content-Type": "application/x-www-form-urlencoded", "Authorization": self.auth_token}
        self.headers_json = {"Content-Type": "application/json; charset=utf-8", "Authorization": self.auth_token}
    def stock_pricing_list(self, per_page=None):

        json_data_list = []
        print("开始获取库存定价列表")
        stock_pricing_list_url = "{}/v1/pricing/StockPricing/getStockList".format(self.HC2018_ADMIN_URL)
        stock_pricing_list_body = {
            "erp_type": -1,
            "hasGuidePrice": "0",
            "is_lock_pricing_v4": -1,
            "is_marketing_discount": "0",
            "is_on_sale": 0,
            "last_putaway_date": ["2025-06-30", "2025-06-30"],
            "last_putaway_date_end": "2025-06-30",
            "last_putaway_date_start": "2025-06-30",
            "order_sort": 1,
            "page": 1,
            "per_page": 100,
            "range_type": 3,
            "stair_id": -1,
            "tag_type": "-1"
        }
        if per_page:
            stock_pricing_list_body["per_page"] = int(per_page)
        stock_pricing_list_res = self.rss.post(url=stock_pricing_list_url, json=stock_pricing_list_body,
                                              headers=self.headers_json).json()
        # print(stock_pricing_list_res["data"]["total"])
        if int(stock_pricing_list_res["data"]["total"]) / int(stock_pricing_list_body["per_page"]) > 1:
            num = math.ceil(int(stock_pricing_list_res["data"]["total"]) / int(str(stock_pricing_list_body["per_page"])))
            print(f"页数：{num}")
            # stock_pricing_list_body["per_page"] = num
            for i in range(num):
                stock_pricing_list_body["page"] = i + 1
                # print(f"请求的stock_pricing_list_body['page']: {stock_pricing_list_body['page']}")
                stock_pricing_list_res = self.rss.post(url=stock_pricing_list_url, json=stock_pricing_list_body,
                                                  headers=self.headers_json).json()
                # 若使用jsonpath解析stock_pricing_list_res的话，则用jsonpath获取的goods_no、goods_name、provider_name、encap跟goods_id 顺序关系会被打乱，
                # jsonpath 默认排序按字母的小大写的先后顺序
                # print(f"请求返回数据：{stock_pricing_list_res}")
                data = stock_pricing_list_res["data"]["data"]
                # print(f"请求后返回数据个数：{len(data)}")
                for a in range(len(data)):
                    goods_id = data[a]["goods_id"]
                    goods_no = data[a]["goods_no"]
                    goods_name = data[a]["goods_name"]
                    provider_name = data[a]["provider_name"]
                    encap = data[a]["encap"]
                    json_data = {goods_id: [goods_no, goods_name, provider_name, encap]}
                    json_data_list.append(json_data)

        else:

            data = stock_pricing_list_res["data"]["data"]
            for i in range(len(data)):
                goods_id = data[i]["goods_id"]
                goods_no = data[i]["goods_no"]
                goods_name = data[i]["goods_name"]
                provider_name = data[i]["provider_name"]
                encap = data[i]["encap"]
                json_data = {goods_id: [goods_no, goods_name, provider_name, encap]}
                json_data_list.append(json_data)
            # print(json_data_list)
        print(len(json_data_list))
        return json_data_list

    def sql_Splicing(self, goods_id, goods_no, goods_name, provider_name, encap, num):
        lc_ladder_price = [{"purchases": "1", "price": "0.780356"}, {"purchases": "20", "price": "0.760253"}, {"purchases": "50", "price": "0.740253"}, {"purchases": "100", "price": "0.720253"}, {"purchases": "200", "price": "0.700253"}, {"purchases": "500", "price": "0.680253"}, {"purchases": "1000", "price": "0.660253"}]
        sht_ladder_price = [{"purchases": "1", "price": "0.780356"}, {"purchases": "20", "price": "0.760253"}, {"purchases": "50", "price": "0.740253"}, {"purchases": "100", "price": "0.720253"}, {"purchases": "200", "price": "0.700253"}, {"purchases": "500", "price": "0.680253"}, {"purchases": "1000", "price": "0.660253"}]
        yh_ladder_price = [{"purchases": "1", "price": "0.780356"}, {"purchases": "20", "price": "0.760253"}, {"purchases": "50", "price": "0.740253"}, {"purchases": "100", "price": "0.720253"}, {"purchases": "200", "price": "0.700253"}, {"purchases": "500", "price": "0.680253"}, {"purchases": "1000", "price": "0.660253"}]
        sql_ic_compare_original = ("INSERT INTO ecs_goods_ic_compare ("
                                   "goods_id, goods_no, tag_type, tag_time, notify_type, notify_status, notify_rule, compare_high_rate, compare_low_rate, compare_between_rate, notify_remark,"
                                   "lc_price_diff, lc_cost_diff, lc_goods_no, lc_shop_price, lc_goods_number, lc_price_uptime, lc_ladder_price,"
                                   "sht_ladder_price, sht_goods_number, sht_price_diff, sht_cost_diff, sht_goods_no, sht_price_uptime, sht_shop_price, sht_cpt_price, lc_cpt_price, "
                                   "yh_goods_no, yh_ladder_price, yh_goods_number, yh_price_uptime, yh_shop_price)"
                                   "VALUES ("
                                   "{}, '{}', 0, 0, 2, 1, 3, 2.00, 3.00, 4.00, '', "
                                   "-99.98, -99.97, 'C47345373', 0.0152, 38097, 1750926099, '{}', "
                                   "'{}', 4246, -99.98, -99.97, 'BM0000002620', 1750926099, 0.00380,0.00000, 0.00000, "
                                   "'{}M-{}', '{}', 136846, 1750926099, 0.0038);\n").format(goods_id, goods_no, lc_ladder_price, sht_ladder_price,num, goods_name, yh_ladder_price)
        sql_compete_detiall = ("INSERT INTO ecs_compete_detail ("
                               "goods_no, goods_name, provider_name, encap, compete_type, "
                               "compete_goods_no, compete_goods_name, compete_provider_name, compete_encap, operator_name, operator_id, manual_goods_no, has_material)"
                               "VALUES ('{}','{}','{}', '{}', 1, 'C47345373', '{}', '{}', '{}', '', 0, '{}', 1);\n".format(goods_no, goods_name, provider_name, encap, goods_name, provider_name, encap, goods_no))

        print(sql_ic_compare_original)
        print(sql_compete_detiall)

        return sql_ic_compare_original, sql_compete_detiall
    def main_text_sql(self, per_page=None):
        json_data_list = self.stock_pricing_list(per_page=per_page)
        for i in range(len(json_data_list)):
            for k, v in json_data_list[i].items():
                sql_ic_compare_original, sql_compete_detiall = self.sql_Splicing(k, v[0], v[1], v[2], v[3], i+1)
                with open(dos_stock_txt_sql, "a+", encoding="utf-8") as f:
                    f.write(f"-- 插入型号id：{k}到ecs_goods_ic_compare表\n")
                    f.write(sql_ic_compare_original)
                    f.write(f"-- 插入型号名称：{v[1]}到ecs_compete_detail表\n")
                    f.write(sql_compete_detiall)
                    f.write("\n")
if __name__ == '__main__':
    from huaqiu_order_api.HC2018_admin.login.login import Login
    target_rss = Login().login()
    TextSql(target_rss).main_text_sql()