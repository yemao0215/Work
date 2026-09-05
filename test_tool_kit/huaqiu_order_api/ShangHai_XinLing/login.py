import requests
import yaml

from huaqiu_order_api.ShangHai_XinLing.ollama_ai.llava_ai import OllamaLlavaAi
from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_data import Data
from huaqiu_order_api.common.my_imgcode import MyIMGCode
from huaqiu_order_api.common.my_path import yaml_file, account_yaml


class Login:
    def __init__(self):
        """
        :param phone:  登录账号
        :param psw:  登录密码
        """
        with open(account_yaml, 'r', encoding='utf-8') as yamlfile:
            account = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.user = account["ShangHai_XinLing"]["user"]
        self.psw = account["ShangHai_XinLing"]["pwd"]
        self.rss = requests.Session()
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.ShangHai_XinLing_URL = data['ShangHai_XinLing_URL']
        # self.url_login = 'https://uat-hc2019.hqchip.com/v1/authorize/User/login'
        self.body = {'user_name': self.user, 'password': self.psw}
        self.headers = {"Content-Type": "application/json;charset=UTF-8"}
        self.payload = {'origin': '1', 'content_unique': '1'}
    def login(self):
        # 获取图片BASE64验证码信息
        img_base64_code_url = "{}/dev-api/captchaImage".format(self.ShangHai_XinLing_URL)
        img_base64_response = self.rss.get(url=img_base64_code_url).json()
        img_base64_code = img_base64_response['data']['img']
        print(img_base64_code)
        # 解析图片获取计算结果
        code_calculate = MyIMGCode(img_base64_code).mian_img_base64_code()
        print(code_calculate)
        a = OllamaLlavaAi(img_base64_code).recognize_captcha()
        print(a)

        # self.url_login = '{}/v1/authorize/User/login'.format(self.HC2018_ADMIN_URL)
        # res = self.rss.post(url=self.url_login, data=self.body, headers={"Connection": "close"})
        # json_res = res.json()
        # print(f"开始执行登录账号:{self.body}, 开始提取响应报文相关应用字段")
        # code = json_res["code"]
        # print(f'状态码：{code}')
        # msg = json_res["msg"]
        # print(f'msg信息：{msg}')
        #
        # try:
        #     if code == 0 and msg == 'success':
        #         self.auth_token = json_res["data"]["auth_token"]
        #         logger.info(f'auth_token：{self.auth_token}')
        #         self.real_name = json_res["data"]['user_info']['real_name']
        #         print(f'真实姓名信息：{self.real_name}')
        #         logger.info(f"登录成功")
        #         # self.login_headers = {"Content-Type": "application/json;charset=UTF-8", "Authorization": self.auth_token}
        #         # 将获取的登录的token往Data里面作虚拟存储以【dos_auth_token】命名以便后续提取
        #         setattr(Data, 'dos_auth_token', self.auth_token)
        # except:
        #     logger.error(f"登录失败，请检查输入用户密码信息")
        #     return None
        # return self.rss
    def logout(self):
        self.url_login = '{}/v1/authorize/User/login'.format(self.HC2018_ADMIN_URL)
        res = self.rss.post(url=self.url_login, data=self.body, headers={"Connection": "close"})
        json_res = res.json()
        logger.info(f"开始执行登录账号:{self.body}, 开始提取响应报文相关应用字段")
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
                # self.login_headers = {"Content-Type": "application/json;charset=UTF-8", "Authorization": self.auth_token}
                # 将获取的登录的token往Data里面作虚拟存储以【dos_auth_token】命名以便后续提取
                setattr(Data, 'dos_auth_token', self.auth_token)
        except:
            logger.error(f"登录失败，请检查输入用户密码信息")
            return None
        return self.rss
if __name__ == '__main__':
    rss = Login().login()