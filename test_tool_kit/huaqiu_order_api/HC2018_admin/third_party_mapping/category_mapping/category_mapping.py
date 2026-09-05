import json

import jsonpath
import requests
import yaml

from huaqiu_order_api.HC2018_admin.login.login import Login
from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_data import Data
from huaqiu_order_api.common.my_path import yaml_file


class CategoryMapping:
    # 类目映射
    def __init__(self, rss, supplier_id):
        """
        :param rss:  登录token信息
        :param supplier_id:  厂商id，1Digikey 2立创（代号：Szlcsc）
        """
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.HC2018_ADMIN_URL = data['HC2018_ADMIN_URL']
        self.rss = rss
        self.supplier_id = supplier_id
        self.auth_token = getattr(Data, 'dos_auth_token')
        self.headers = {"Content-Type":"application/json;charset=UTF-8"}
        self.headers["Authorization"] = self.auth_token



    def category_mapping_search(self):
        """类目映射列表"""
        search_url = "{}/v1/third/CateRelation/findList".format(self.HC2018_ADMIN_URL)
        search_body = {"is_attr_relation": "-1", "is_cat_relation": "-1", "page": 1, "per_page": 100,
                       "cat_id": "", "cat_name": "", "supplier_id": self.supplier_id}
        search_res = self.rss.post(url=search_url, json=search_body, headers=self.headers).json()
        # print(json.dumps(search_res["data"][0], ensure_ascii=False).replace("'", '"'))
        supplier_cat_id = jsonpath.jsonpath(search_res, "$..cat_id")
        print(supplier_cat_id)
        # 获取可以映射的类目id，即类目下不存在下级类目
        if supplier_cat_id:
            reflection_cat_id_count = []
            for parent_cat_id in supplier_cat_id:
                print(f'第一父级为：{parent_cat_id}')
                leaf_categories = self.find_leaf_categories(parent_cat_id, search_url)
                if leaf_categories:
                    reflection_cat_id_count.append(leaf_categories)
            #
            # reflection_search_res = self.rss.post(url=search_url, json=reflection_search_body, headers=self.headers).json()
            # if reflection_search_res["data"] != []:
            #     junior_cat_id = jsonpath.jsonpath(reflection_search_res, "$..cat_id")
            #     print(junior_cat_id)
            #     while True:
            #         for junior_id in junior_cat_id:
            #             reflection_junior_body = {"supplier_id": self.supplier_id, "parent_cat_id": junior_id}
            #             res = self.rss.post(url=search_url, json=reflection_junior_body, headers=self.headers).json()
            #             cat_id = jsonpath.jsonpath(res, "$..cat_id")
            #             if cat_id:
            #                 print("继续请求，ids为:", cat_id)
            #             else:
            #                 reflection_cat_id.append(parent_cat_id)
            #                 reflection_cat_id_count = reflection_cat_id_count + reflection_cat_id
            #                 break
            # else:
            #     reflection_cat_id.append(parent_cat_id)
            #     reflection_cat_id_count = reflection_cat_id_count + reflection_cat_id
            print(reflection_cat_id_count)








if __name__ == '__main__':
    rss = Login().login()
    CategoryMapping(rss, '2').category_mapping_search()


