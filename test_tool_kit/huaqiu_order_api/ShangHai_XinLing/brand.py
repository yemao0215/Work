
import math

from pipes import quote

import pandas
import pandas as pd
import requests
import yaml
from huaqiu_order_api.common.my_path import yaml_file, account_yaml, xl_brand_dir, xlsx_dos_brand_dir, xl_dos_brand_dir


class XLBrand:

    def __init__(self, brand_name=None, brand_name_cn=None, brand_name_en_long=None, brand_name_cn_long=None):

        self.rss = requests.Session()
        self.json_head = {
  'Accept': 'application/json, text/plain, */*',
  'Accept-Language': 'zh-CN,zh;q=0.9',
  'Authorization': 'Bearer eyJhbGciOiJIUzUxMiJ9.eyJqdGkiOiJhODZlNGU5OGZlNjM0NjhkOGM2ZTVjZjMzZTk3ZTFiYyIsInVzZXIiOiJhZG1pbiIsInN1YiI6ImFkbWluIn0.r9KWO9ZYAP7cGbusQaX7sDLf2OdO7-J0FRVa8jX25TspbnoXTZ9z-oSASiiDzslXWsUhCNW-8J891JWsBM7PNg',
  'Connection': 'keep-alive',
  'Referer': 'http://47.100.4.100/metadata/manufacturer',
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
  #'Cookie': 'username=admin; password=Ble2Iqhr2CsxnuMBiwYEBxUSLq3MBRtQAITkfjperIWTqWNrQ9KcteI8Q0G6rI5WO3bosCUHO1tmJAcq+50lYw==; rememberMe=true; ELADMIN-TOEKN=Bearer%20eyJhbGciOiJIUzUxMiJ9.eyJqdGkiOiIxZTU0NmM4MmY5MjU0ZGM0YjFiZWZlZTM0NWEwYTc5MyIsInVzZXIiOiJhZG1pbiIsInN1YiI6ImFkbWluIn0.5eQg3YtEn6aCFnMU6HL5G5V-x2OlQmD_XVmg5J89-_YdhDumFt1xx7NvENvZ7h0_RZ4CxR5pKKuxQYGquwTEng',
  #'Cookie': 'username=admin; password=Ble2Iqhr2CsxnuMBiwYEBxUSLq3MBRtQAITkfjperIWTqWNrQ9KcteI8Q0G6rI5WO3bosCUHO1tmJAcq+50lYw==; rememberMe=true; ELADMIN-TOEKN=Bearer%20eyJhbGciOiJIUzUxMiJ9.eyJqdGkiOiIxZTU0NmM4MmY5MjU0ZGM0YjFiZWZlZTM0NWEwYTc5MyIsInVzZXIiOiJhZG1pbiIsInN1YiI6ImFkbWluIn0.5eQg3YtEn6aCFnMU6HL5G5V-x2OlQmD_XVmg5J89-_YdhDumFt1xx7NvENvZ7h0_RZ4CxR5pKKuxQYGquwTEng'
}
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.ShangHai_XinLing_URL = data["ShangHai_XinLing_admin_URL"]
        self.courier_number = data["courier_number"]
        with open(account_yaml, 'r', encoding='utf-8') as yamlfile:
            account = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.brand_name = brand_name
        self.brand_name_cn = brand_name_cn
        self.brand_name_en_long = brand_name_en_long
        self.brand_name_cn_long = brand_name_cn_long
        self.token = account["ShangHai_XinLing"]["admin_token"]
        self.json_head['Authorization'] = self.token



    def query_url_arguments(self, data):
        """将body参数转换成可拼接至url的参数"""
        lt = []
        for k, v in data.items():
            lt.append(k + '=' + quote(str(v)))
        # 这个是在for循环外面的，就是将列表的元素之间用用&符号连接起来
        query_string = '&'.join(lt)
        return query_string
    def xl_get_brand_code(self):
        # xl_get_brand_url = "{}/api/protoss/mfg".format(self.ShangHai_XinLing_URL)
        xl_get_brand_body = {
            "page": 1,
            "size": 100,
            "sort": "id,desc"
        }
        xl_get_brand_body_conversion = self.query_url_arguments(xl_get_brand_body)
        xl_get_brand_url = "{}/api/protoss/mfg?{}".format(self.ShangHai_XinLing_URL, xl_get_brand_body_conversion)

        xl_get_brand_res = self.rss.get(xl_get_brand_url, headers=self.json_head).json()
        # print(xl_get_brand_res)
        totalElements = xl_get_brand_res["totalElements"]
        data_json = []
        if int(totalElements) / 100 > 1:
            num = math.ceil(int(totalElements) / 100)
            for i in range(num):
                xl_get_brand_body["page"] = i + 1
                xl_get_brand_body_conversion = self.query_url_arguments(xl_get_brand_body)
                xl_get_brand_url = "{}/api/protoss/mfg?{}".format(self.ShangHai_XinLing_URL,
                                                                  xl_get_brand_body_conversion)
                xl_get_brand_res = self.rss.get(xl_get_brand_url, headers=self.json_head).json()
                for a in range(len(xl_get_brand_res["content"])):
                    brand_id = xl_get_brand_res["content"][a]["id"]
                    brand_name = xl_get_brand_res["content"][a]["displayName"]
                    brand_cn = xl_get_brand_res["content"][a].get("displayNameCn", '')
                    data = {"brand_id": brand_id, "brand_name": brand_name, "brand_cn": brand_cn}
                    data_json.append(data)
        df = pd.DataFrame(data_json)
        # 重命名列
        df.rename(columns={"brand_id": "芯灵品牌id", "brand_name": "芯灵品牌简称", "brand_cn": "芯灵品牌中文简称"}, inplace=True)
        # 写入指定Excel文件，写到默认第一个sheet，覆盖原内容
        df.to_excel(xl_brand_dir, index=False)

        print("数据已成功写入Excel文件")
        return self
    def xl_dos_brand_Corresponde(self):
        dos_data = pandas.read_excel(xlsx_dos_brand_dir)
        self.dos_brand_id = dos_data["品牌id"]
        self.dos_brand_name = dos_data["品牌简称"]
        self.dos_brand_cn = dos_data["品牌中文简称"]
        # self.web_display = data["前端显示文本"]
        self.dos_row_count = len(dos_data)
        self.dos__column_count = dos_data.shape[1]
        xl_data = pandas.read_excel(xl_brand_dir)
        self.xl_brand_id = xl_data["芯灵品牌id"]
        self.xl_brand_name = xl_data["芯灵品牌简称"]
        self.xl_brand_cn = xl_data["芯灵品牌中文简称"]
        self.xl_row_count = len(xl_data)
        self.xl__column_count = xl_data.shape[1]
        print("DOS品牌数量：", self.dos_row_count)
        print("芯灵品牌数量：", self.xl_row_count)
        xl_dos_brand_id = []
        for i in range(len(self.xl_brand_id)):
            for j in range(len(self.dos_brand_id)):
                if self.xl_brand_name[i] == self.dos_brand_name[j] and self.dos_brand_cn[j] != '' and self.xl_brand_cn[i] != '':
                    dos_brand_id = self.dos_brand_id[j]
                    xl_brand_id = self.xl_brand_id[i]
                    dos_brand_name = self.dos_brand_name[j]
                    xl_brand_name = self.xl_brand_name[i]
                    xl_dos_brand = {"dos_brand_id": dos_brand_id, "dos_brand_name": dos_brand_name, "xl_brand_id": xl_brand_id, "xl_brand_name": xl_brand_name}
                    xl_dos_brand_id.append(xl_dos_brand)
                    break
                elif self.xl_brand_cn[i] == self.dos_brand_cn[j] and self.dos_brand_cn[j] != '' and self.xl_brand_cn[i] != '':
                    dos_brand_id = self.dos_brand_id[j]
                    xl_brand_id = self.xl_brand_id[i]
                    dos_brand_name = self.dos_brand_name[j]
                    xl_brand_name = self.xl_brand_name[i]
                    xl_dos_brand = {"dos_brand_id": dos_brand_id, "dos_brand_name": dos_brand_name, "xl_brand_id": xl_brand_id, "xl_brand_name": xl_brand_name}
                    xl_dos_brand_id.append(xl_dos_brand)
                    break
                # elif str(self.dos_brand_cn[j]) in str(self.xl_brand_cn[i]) and self.dos_brand_cn[j] != '' and self.xl_brand_cn[i] != '':
                #     dos_brand_id = self.dos_brand_id[j]
                #     xl_brand_id = self.xl_brand_id[i]
                #     dos_brand_name = self.dos_brand_name[j]
                #     xl_brand_name = self.xl_brand_name[i]
                #     xl_dos_brand = {"dos_brand_id": dos_brand_id, "dos_brand_name": dos_brand_name, "xl_brand_id": xl_brand_id, "xl_brand_name": xl_brand_name}
                #     xl_dos_brand_id.append(xl_dos_brand)
                #     break
                # elif str(self.xl_brand_cn[i]) in str(self.dos_brand_cn[j]) and self.dos_brand_cn[j] != '' and self.xl_brand_cn[i] != '':
                #     dos_brand_id = self.dos_brand_id[j]
                #     xl_brand_id = self.xl_brand_id[i]
                #     dos_brand_name = self.dos_brand_name[j]
                #     xl_brand_name = self.xl_brand_name[i]
                #     xl_dos_brand = {"dos_brand_id": dos_brand_id, "dos_brand_name": dos_brand_name, "xl_brand_id": xl_brand_id, "xl_brand_name": xl_brand_name}
                #     xl_dos_brand_id.append(xl_dos_brand)
                #     break
        df = pd.DataFrame(xl_dos_brand_id)
        # 重命名列
        df.rename(columns={"dos_brand_id": "DOS品牌id", "dos_brand_name": "DOS品牌简称", "xl_brand_id": "芯灵品牌id", "xl_brand_name": "芯灵品牌简称"}, inplace=True)
        # 写入指定Excel文件，写到默认第一个sheet，覆盖原内容
        df.to_excel(xl_dos_brand_dir, index=False)
        return self
    def xl_brand_add(self):
        """品牌添加 + 调度中心消费任务：brand-queue-syncsh，不能两个环境同时启动，只能一个对应任务启动"""
        xl_brand_add_url = "{}/api/protoss/mfg".format(self.ShangHai_XinLing_URL)
        xl_brand_add_body = {
            "id":  None,
            "displayName": self.brand_name,
            "displayNameCn": self.brand_name_cn,
            "displayNameCh": "",
            "formalName": self.brand_name_en_long,
            "formalNameCn": self.brand_name_cn_long,
            "shortName": self.brand_name,
            "region": 3,
            "alias": None,
            "referName": None,
            "relationship": None,
            "homepageUrl": None,
            "logoUrl": None,
            "description": "test",
            "descriptionCh": "测试"
        }
        xl_brand_add_res = self.rss.post(xl_brand_add_url, json=xl_brand_add_body, headers=self.json_head)
        print(xl_brand_add_res)
        if xl_brand_add_res.status_code != 201:
            print(xl_brand_add_res.json())
            xl_brand_add_res = xl_brand_add_res.json()
            if xl_brand_add_res["status"] == 401 and xl_brand_add_res["error"] == "Unauthorized":
                print("请检查token是否正确或过期")
                raise ValueError("模拟异常")
            elif "message" in xl_brand_add_res and xl_brand_add_res["message"] == "制造商名称已经存在!":
                print("该品牌: {}在芯灵中已存在".format(self.brand_name))
                raise ValueError("模拟异常")
            elif "message" in xl_brand_add_res and xl_brand_add_res["message"] == "制造商展示名称在dos主品牌中已存在!":
                print("该品牌: {}在DOS系统中已存在".format(self.brand_name))
                raise ValueError("模拟异常")
        else:
            print("品牌：{}添加成功".format(self.brand_name))
        return self


if __name__ == '__main__':
    brand_name = "searchV5.21"
    brand_name_cn = "搜索V5.2"
    brand_name_en_long = "huaqiu search test Version 5.2"
    brand_name_cn_long = "华秋搜索测试版本5.2"
    rss = XLBrand(brand_name=brand_name, brand_name_cn=brand_name_cn, brand_name_en_long=brand_name_en_long, brand_name_cn_long=brand_name_cn_long).xl_brand_add()


