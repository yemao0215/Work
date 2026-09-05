
import requests
import yaml
from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_path import yaml_file, account_yaml
class TaskLogin:

    def __init__(self):

        self.rss = requests.Session()
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.HQCHIP_Task_Center_URL = data['HQCHIP_Task_Center_URL']
        with open(account_yaml, 'r', encoding='utf-8') as yamlfile:
            account = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.account = account["TASK"]["name"]
        self.password = account["TASK"]["pwd"]
        self.json_head = {'Content-Type': 'application/json;charset=UTF-8'}
    def login(self):
        logger.info("开始登录")
        login_url = "{}/api/v2/auth/login/".format(self.HQCHIP_Task_Center_URL)
        login_body = {"username": self.account, "password": self.password}
        login_res = self.rss.post(url=login_url, json=login_body, headers=self.json_head).json()
        logger.info("登录结果：{}".format(login_res))
        return self.rss
