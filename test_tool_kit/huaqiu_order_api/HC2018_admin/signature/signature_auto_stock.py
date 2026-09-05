import hashlib
import time
import requests
import yaml
from huaqiu_order_api.common.my_path import yaml_file
class SignatureAutoStock:
    def __init__(self):
        self.goods_id = "2500220263"
        self.goods_name = "TAJC227K010RNJ"
        self.rss = requests.Session()
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.HC2018_ADMIN_URL = data['HC2018_ADMIN_URL']
        self.headers = {"Content-Type": "application/x-www-form-urlencoded"}


    def MD5_encryption(self, str):
        """MD5加密"""
        md5 = hashlib.md5()
        md5.update(str.encode("utf-8"))
        str_md5 = md5.hexdigest()
        return str_md5

    def token_ceate(self):
        """密钥token生成"""
        # 获取当前时间戳
        timestamp = time.mktime(time.localtime(time.time()))
        timestamp_str = str(int(timestamp))
        token_encryption = self.sign + timestamp_str
        token = self.MD5_encryption(token_encryption)
        return timestamp, token

    def signature_ceate(self):
        """自动补货接口"""
        if "uat" in self.HC2018_ADMIN_URL:
            self.sign = "eTGDt6NkOmNLJ94WayOLIaYJZPzEbrCL"
        if "fat" in self.HC2018_ADMIN_URL:
            self.sign = "klsjdflfe&&(#02jjYWY"
        timestamp, self.sign_encryption = self.token_ceate()
        return timestamp, self.sign_encryption