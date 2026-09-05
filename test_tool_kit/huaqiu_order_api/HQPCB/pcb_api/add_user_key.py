import requests
import re
import yaml
import json
import pcb_tool
from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_path import pcb_config_yaml_dir


class UserKey:

    def __init__(self):
        with open(pcb_config_yaml_dir, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.HEADERS = {"Cookie": "PHPSESSID={}".format(data['PHPSESSID']), "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://uat-www.huaqiu.com)"}
        self.URL = data['HQJFPCB_URL']

    def exists(self, mid):
        url = '{}/hqjfpcb/App'.format(self.URL)
        data = {'pageNum': '1',
                'field': 'mid',
                'value': mid}
        resp = requests.post(url, data=data, headers=self.HEADERS)
        # print(resp.text)
        resp_number = "".join(list(filter(str.isdigit, re.findall('<span>([^<>]+)</span>', resp.text)[3])))
        if int(resp_number) >= 1:
            resp_list = re.findall('<td>([^<>]+)</td>', resp.text)
            API_KEY = resp_list[4]
            data = requests.get('{}/hqjfpcb/App/viewScrect/id/{}'.format(self.URL, resp_list[0]), headers=self.HEADERS)
            API_SEC = re.findall('<span>([^<>]+)</span>', data.text)[1]
            params = {'API_KEY': API_KEY, 'API_SEC': API_SEC}
            pcb_tool.PcbTools().write_yaml(params)
        else:
            UserKey().add_app_key(mid)

    def add_app_key(self, mid):
        url = '{}/hqjfpcb/App/insert/navTabId/App'.format(self.URL)
        data = {'app_name': '{}的应用KEY'.format(mid),
                'app_type': '0',
                'mid': mid,
                'scheme_id': '0',
                'expressage_type': '0',
                'deltime_type': '0',
                'permission_order': '1',
                'permission_payment': '1',
                'permission_compute': '1',
                'permission_eq': '1',
                'permission_partner': '1',
                'permission_finance': '1',
                'permission_analyze': '1',
                'permission_gerber': '1',
                'permission_stencilorder': '1',
                'status': '1',
                'ajax': '1',
                'is_iframe': '1'
                }
        resp = requests.post(url, data=data, headers=self.HEADERS)
        data = json.loads(resp.content)
        logger.info(data)
        if data['info'] == '新增成功':
            UserKey().exists(mid)

