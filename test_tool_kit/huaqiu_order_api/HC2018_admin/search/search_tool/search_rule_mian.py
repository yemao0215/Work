import requests
import yaml

from huaqiu_order_api.HC2018_admin.login.login import Login
from huaqiu_order_api.common.my_data import Data
from huaqiu_order_api.common.my_path import yaml_file, supplier_dir
from huaqiu_order_api.common.yaml_handler import read_yaml


class SearchRuleMain:
    def __init__(self, token=None, Keyword=None, supplier_name=None):
        self.token = token
        self.Keyword = Keyword
        self.rss = requests.Session()
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.HC2018_ADMIN_URL = data['HC2018_ADMIN_URL']
        self.headers = {"Content-Type": "application/x-www-form-urlencoded"}
        self.headers_json = {"Content-Type": "application/json; charset=utf-8"}
        self.supplier_name = supplier_name
    def search_analysis_V5(self):
        self.supplier_data= read_yaml(supplier_dir)
        for k, v in self.supplier_data.items():
            if k == self.supplier_name:
                self.supplierId = v
        search_tool_url = "{}/v1/esearch/SearchTool/searchAndAnalysisV5".format(self.HC2018_ADMIN_URL)
        search_tool_body = {
              "supplierId": self.supplierId,
              "keyword": self.Keyword,
              "isSearchTriggered": True,
              "offset": 0,
              "limit": 10
        }
        if self.token in [None, ""]:
            self.rss = Login().login()
            self.token = getattr(Data, "dos_auth_token")
        self.headers_json["Authorization"] = self.token
        search_tool_res = self.rss.post(url=search_tool_url, json=search_tool_body, headers=self.headers_json).json()
        print(search_tool_res)
        return search_tool_res
if __name__ == '__main__':
    Keyword = "0603 10k"
    supplier_name = "hqchip_self"
    SearchRuleMain(Keyword=Keyword, supplier_name=supplier_name).search_analysis_V5()