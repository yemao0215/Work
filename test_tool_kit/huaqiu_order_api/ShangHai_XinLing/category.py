
import math

from pipes import quote

import pandas
import pandas as pd
import requests
import yaml
from huaqiu_order_api.common.my_path import yaml_file, account_yaml, xl_brand_dir, xlsx_dos_brand_dir, xl_dos_brand_dir, \
    xl_dos_category_dir_pro, xl_category_dir


class XLCategory:

    def __init__(self):

        self.rss = requests.Session()
        self.json_head = {
  'Accept': 'application/json, text/plain, */*',
  'Accept-Language': 'zh-CN,zh;q=0.9',
  'Authorization': 'Bearer eyJhbGciOiJIUzUxMiJ9.eyJqdGkiOiJiZTdmNWU3ZmRlNTI0NzgwYTIyNWNiYjhjMzA1NmQwYiIsInVzZXIiOiJhZG1pbiIsInN1YiI6ImFkbWluIn0.B9sR9OLl1Yayu5Wvoc4rgYE0B9SNugL3NatDt80z3febdVdmIs1ujEXgLpZ28NkMnd9Jeh3XvnrHD-qFOmbxRQ',
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
        # self.token = account["ShangHai_XinLing"]["admin_token"]
        # self.json_head['Authorization'] = 'eyJhbGciOiJIUzUxMiJ9.eyJqdGkiOiIxZTU0NmM4MmY5MjU0ZGM0YjFiZWZlZTM0NWEwYTc5MyIsInVzZXIiOiJhZG1pbiIsInN1YiI6ImFkbWluIn0.5eQg3YtEn6aCFnMU6HL5G5V-x2OlQmD_XVmg5J89-_YdhDumFt1xx7NvENvZ7h0_RZ4CxR5pKKuxQYGquwTEng',


    def query_url_arguments(self, data):
        """将body参数转换成可拼接至url的参数"""
        lt = []
        for k, v in data.items():
            lt.append(k + '=' + quote(str(v)))
        # 这个是在for循环外面的，就是将列表的元素之间用用&符号连接起来
        query_string = '&'.join(lt)
        return query_string
    def xl_get_category_code(self):
        # xl_get_brand_url = "{}/api/protoss/mfg".format(self.ShangHai_XinLing_URL)
        xl_get_category_body = {
            "page": 1,
            "size": 100,
            "sort": "id,desc"
        }
        xl_get_category_body_conversion = self.query_url_arguments(xl_get_category_body)
        xl_get_category_url = "{}/api/protoss/cate??{}".format(self.ShangHai_XinLing_URL, xl_get_category_body_conversion)

        xl_get_category_res = self.rss.get(xl_get_category_url, headers=self.json_head).json()
        # print(xl_get_brand_res)
        totalElements = xl_get_category_res["totalElements"]
        data_json = []
        if int(totalElements) / 100 > 1:
            num = math.ceil(int(totalElements) / 100)
            for i in range(num):
                xl_get_category_body["page"] = i + 1
                xl_get_category_body_conversion = self.query_url_arguments(xl_get_category_body)
                xl_get_category_url = "{}/api/protoss/mfg?{}".format(self.ShangHai_XinLing_URL,
                                                                  xl_get_category_body_conversion)
                xl_get_category_res = self.rss.get(xl_get_category_url, headers=self.json_head).json()
                for a in range(len(xl_get_category_res["content"])):
                    brand_id = xl_get_category_res["content"][a]["id"]
                    brand_name = xl_get_category_res["content"][a]["displayName"]
                    brand_cn = xl_get_category_res["content"][a].get("displayNameCn", '')
                    data = {"brand_id": brand_id, "brand_name": brand_name, "brand_cn": brand_cn}
                    data_json.append(data)
        df = pd.DataFrame(data_json)
        # 重命名列
        df.rename(columns={"brand_id": "芯灵品牌id", "brand_name": "芯灵品牌简称", "brand_cn": "芯灵品牌中文简称"}, inplace=True)
        # 写入指定Excel文件，写到默认第一个sheet，覆盖原内容
        df.to_excel(xl_brand_dir, index=False)

        print("数据已成功写入Excel文件")
        return self
    def xl_get_xlsx_category_code(self):
        data_list = []
        xl_data_pro = pandas.read_excel(xl_dos_category_dir_pro)
        self.pro_xl_category_name = xl_data_pro["name"].tolist()
        self.pro_xl_category_cn = xl_data_pro["name_cn"]
        self.pro_xl_category_parent = xl_data_pro["parent"]
        print(self.pro_xl_category_name)
        for i in range(len(self.pro_xl_category_name)):
            xl_get_category_body = {
                "page": 1,
                "size": 10,
                "sort": "id,desc",
                "name": self.pro_xl_category_name[i].replace(" ", "%20").replace("(", "%28").replace(")", "%29"),
            }
            xl_get_category_body_conversion = self.query_url_arguments(xl_get_category_body)
            xl_get_category_url = "{}/api/protoss/cate?{}".format(self.ShangHai_XinLing_URL, xl_get_category_body_conversion)
            xl_get_category_res = self.rss.get(xl_get_category_url, headers=self.json_head).json()
            xl_category_id = xl_get_category_res["content"][0]["id"]
            xl_category_name = xl_get_category_res["content"][0]["name"]
            xl_category_cn = xl_get_category_res["content"][0]["nameCn"]
            xl_category_parent = xl_get_category_res["content"][0]["parentId"]
            xl_category_parent_name = ''
            if int(xl_category_parent) != 0:
                del xl_get_category_body["name"]
                xl_get_category_body["id"] = xl_category_parent
                xl_get_category_body_conversion = self.query_url_arguments(xl_get_category_body)
                xl_get_category_url = "{}/api/protoss/cate?{}".format(self.ShangHai_XinLing_URL, xl_get_category_body_conversion)
                xl_get_category_res = self.rss.get(xl_get_category_url, headers=self.json_head).json()
                xl_category_parent_name = xl_get_category_res["content"][0]["name"]
            print(xl_category_name, xl_category_cn, xl_category_parent, xl_category_parent_name)
            data = {"xl_category_id": xl_category_id, "xl_category_name": xl_category_name, "xl_category_cn": xl_category_cn,
                    "xl_category_parent": xl_category_parent, "xl_category_parent_name": xl_category_parent_name}
            data_list.append(data)
        df = pd.DataFrame(data_list)
        # 重命名列
        df.rename(columns={"xl_category_id": "芯灵类目id", "xl_category_name": "芯灵类目名称", "xl_category_cn": "芯灵类目中文名称",
                           "xl_category_parent": "芯灵上级类目id", "xl_category_parent_name": "芯灵上级类目名称"}, inplace=True)
        # 写入指定Excel文件，写到默认第一个sheet，覆盖原内容
        df.to_excel(xl_category_dir, index=False)
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
                #     break
        df = pd.DataFrame(xl_dos_brand_id)
        # 重命名列
        df.rename(columns={"dos_brand_id": "DOS品牌id", "dos_brand_name": "DOS品牌简称", "xl_brand_id": "芯灵品牌id", "xl_brand_name": "芯灵品牌简称"}, inplace=True)
        # 写入指定Excel文件，写到默认第一个sheet，覆盖原内容
        df.to_excel(xl_dos_brand_dir, index=False)
if __name__ == '__main__':
    rss = XLCategory().xl_get_xlsx_category_code()


