
import json
import requests
import yaml

from huaqiu_order_api.common.my_path import yaml_file


class ProductObtainImges:
    def __init__(self, goods_id, goods_no):

        self.rss = requests.Session()
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.PRODUCT_DETAIL_URL = data['PRODUCT_DETAIL_URL']
        self.headers_urlencoded = {"Content-Type": "application/x-www-form-urlencoded"}
        self.headers_json = {"Content-Type": "application/json;charset=UTF-8"}
        self.goods_id = goods_id
        self.goods_no = goods_no
    def obtain_imges(self):
        obtain_imges_url = "{}/api/v2/goods/getImages".format(self.PRODUCT_DETAIL_URL)
        obtain_imges_body = {"infos": [{"stockId": self.goods_id, "goodsNo": self.goods_no}]}
        obtain_imges_res = self.rss.post(url=obtain_imges_url, json=obtain_imges_body, headers=self.headers_json).json()
        obtain_imges_res_json = json.dumps(obtain_imges_res, ensure_ascii=False).replace("'", '"')
        print(obtain_imges_res_json)
if __name__ == '__main__':
    ProductObtainImges("2500232121", "").obtain_imges()