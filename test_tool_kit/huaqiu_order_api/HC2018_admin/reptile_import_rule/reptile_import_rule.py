import json

import pymysql
import yaml

from huaqiu_order_api.common.loguru_logger import logger
import requests

from huaqiu_order_api.common.my_path import yaml_file


class AttributeVauleMapping:
    def __init__(self, user, psw):
        """
        :param phone:  登录账号
        :param psw:  登录密码
        :param goods_id:  购买的产品id
        """
        self.user = user
        self.rss = requests.Session()
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.HC2018_ADMIN_URL = data['HC2018_ADMIN_URL']
        self.auth_token = ''
        self.body = {'user_name': self.user, 'password': psw}
        self.headers = {"Content-Type":"application/json;charset=UTF-8"}
        self.payload = {'origin': '1', 'content_unique': '1'}
    def login(self):
        """登录"""

        self.url_login = '/v1/authorize/User/login'.format(self.HC2018_ADMIN_URL)
        res = self.rss.post(url=self.url_login, json=self.body, headers={"Connection": "close"})
        json_res = res.json()
        logger.info(f"开始执行登录账号:{self.body}")
        # json_res = res.json()
        logger.info(f'开始提取响应报文相关应用字段')
        # print(json_res)
        code = json_res["code"]
        logger.info(f'状态码：{code}')
        msg = json_res["msg"]
        logger.info(f'msg信息：{msg}')

        try:
            if code == 0 and msg == 'success':
                self.auth_token = json_res["data"]["auth_token"]
                logger.info(f'auth_token：{self.auth_token}')
                self.real_name = json_res["data"]['user_info']['real_name']
                logger.info(f'真实姓名信息：{self.real_name}')
                logger.info(f"登录成功")
                # return self.auth_token, self.real_name
                self.login_headers = {"Content-Type": "application/json;charset=UTF-8", "Authorization": self.auth_token}
        except:
            logger.error(f"登录失败，请检查输入用户密码信息")
            return None
        return self

    def sql_search(self, sql_key, sql_table, sql_search_key, sql_search_key1, nodelname):
        """数据库查询"""
        self.nodelname = '1451'
        if self.nodelname != '':
            db = pymysql.connect(host='192.168.18.42', user='test', password='joqgsUTPCalEM68I', db='dinikey', port=3306, charset='utf8')
            cursor = db.cursor()
            sql = f"select {sql_key} from {sql_table} where {sql_search_key} = '{self.nodelname}'"
            sql_select_replenish = f"and {sql_search_key1} = '{nodelname}';"
            sql = sql + sql_select_replenish
            logger.info(sql)
            cursor.execute(sql)
            desc = cursor.description # 获取字段的描述，默认获取数据库字段名称，重新定义时通过AS关键重新命名即可
            self.data_dict = [dict(zip([col[0] for col in desc], row)) for row in cursor.fetchall()] # 列表表达式把数据组装起来
            cursor.close()
            db.close()
        else:
            self.data_dict = []
        return self.data_dict

    def sql_submeter(self):
        """分表"""
        self.data_dict = self.sql_search("goods_id", "ic_goods", "cat_id", "provider_name", "Knomles Syfer")
        goods_id = []
        goods_id_first = []
        for i in range(len(self.data_dict)):
            goods_id.append(self.data_dict[i]["goods_id"])
        for a in range(len(goods_id)):
            goods_id_first.append(goods_id[a]["goods_id"])
        for b in range(len(goods_id)):
            # goods_id_first.append(goods_id[a]["goods_id"])
            self.data_dict1 = self.sql_search("ext_name, ext_value", f"ic_goods_attr_fields_{goods_id_first[b]}", "cat_id", "goods_id", f"{goods_id[b]}")
            if self.data_dict1 != []:
                logger.info(f"goods_id: {goods_id[b]}的属性值为：{self.data_dict1}")
        return self

    def reptile_import_rule(self):
        pass

if __name__ == '__main__':
    AttributeVauleMapping('admin', '123456').sql_submeter()