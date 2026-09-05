import json

import requests
import yaml

from huaqiu_order_api.common.my_path import yaml_file


class SearchImgSelectGoods:

    def __init__(self, cat_id):
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.HQCHIP_URL = data['HQCHIP_URL']
        self.SEARCH_URL = data['SEARCH_URL']
        self.GO_SEARCH_URL = data['GO_SEARCH_URL']
        self.rss = requests.session()
        self.headers = {"Content-Type": "application/x-www-form-urlencoded",
                        "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://www.huaqiu.com)"
                        }
        self.headers_json = {"Content-Type": "application/json; charset=UTF-8",
                             "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://www.huaqiu.com)"
                             }
        self.cat_id = cat_id

    def search_img_select_goods(self):
        search_img_select_goods_url = "{}/category/getCateLookPic".format(self.HQCHIP_URL)
        search_img_select_goods_body = {"catId": self.cat_id}
        res = self.rss.post(url=search_img_select_goods_url, data=search_img_select_goods_body, headers=self.headers).json()
        # print(res)
        # 代码：json.dumps(res, ensure_ascii=False)将字典转换为 JSON 字符串，并且确保中文不被转义
        # 代码：replace("'", '"') 将单引号替换为双引号
        res_json = json.dumps(res, ensure_ascii=False).replace("'", '"')
        print(res_json)

if __name__ == '__main__':
    SearchImgSelectGoods(1512).search_img_select_goods()