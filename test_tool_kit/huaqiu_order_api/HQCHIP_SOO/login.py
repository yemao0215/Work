import execjs
import jsonpath
import requests
import yaml

from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_data import Data
from huaqiu_order_api.common.my_path import yaml_file, account_yaml, encryption_auth_dir


class SOOLogin:

    def __init__(self, target_url=None, login_mark=None, environment=None, system_name=None):
        """
        :param account: 组织架构系统账号
        :param password: 组织架构系统密码
        :param target_url: 回跳目标系统地址
        :param login_mark: 衔接目标系统标识，
                        营销中台：ecmc，WMS:wms/base，rcs:api，scm：hqScm，srm：partnermanage, pcbames: pcbames, PAY：management
                        DFM：portal, ERP: AuthLogin
        :param environment: 执行环境
        :param system_name: 系统代号名称英文

        :return:
        """
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.Auth_Base_URL = data['Auth_Base_URL']
        self.serialzed_enc_auth_url = data['serialzed_enc_auth_url']
        with open(account_yaml, 'r', encoding='utf-8') as yamlfile:
            account = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.environment = environment
        if self.environment == "pro":
            self.Auth_Base_URL = data['Auth_Base_Pro_URL']
        print(self.Auth_Base_URL)
        if "uat" in self.Auth_Base_URL or "fat" in self.Auth_Base_URL:
            self.account = account["HQCHIP_SOO"]["admin_name"]
            self.password = account["HQCHIP_SOO"]["admin_pwd"]
        else:
            self.account = account["HQCHIP_SOO"]["pro_user"]
            self.password = account["HQCHIP_SOO"]["pro_pwd"]
        self.target_rss = requests.Session()
        self.target_url = target_url
        self.login_mark = login_mark

        self.system_name = system_name
        self.json_head = {"Content-Type": "application/json"}
        self.pda_json_head = {"Content-Type": "application/json", "User-Agent": "okhttp/3.14.9",
                                  "Connection": "keep-alive"}


    def target_url_splice_login_mark(self):
        if self.environment == None:
            self.environment = self.Auth_Base_URL.split("-")[0].split("https://")[1]
        if self.target_url == None:
            if self.environment != None and self.system_name != None:
                if self.system_name in ["wms", "rcs", "scm", "srm", "pay"]:
                    self.target_url = f'{self.environment}-{self.system_name}.huaqiu.com'
                elif self.system_name in ["activity", "erp", "pcbames"]:
                    if self.system_name == "erp":
                        self.system_name = "e"
                    self.target_url = f'{self.environment}-{self.system_name}.hqchip.com'
                elif self.system_name in ["pcb"]:
                    self.system_name = "www"
                    self.target_url = f'{self.environment}-{self.system_name}.hqpcb.com'
                elif self.system_name in ["dfm"]:
                    self.system_name = "dfm"
                    self.target_url = f'{self.environment}-{self.system_name}.elecfans.com'
                else:
                    self.target_url = None
            else:
                self.target_url = None
        else:
            print(f"传入的target_url不为空，跳过执行")
        if  self.login_mark == None:
            json_login_mark = {"wms": "wms/base", "activity": "ecmc", "rcs": "api", "srm": "partnermanage",
                               "pcbames": "pcbames", "pay": "management", "dfm": "portal", "e": "AuthLogin", "www": "hqjfpcb/OrgAuth",
                               "scm": "hqScm", "approval": "approval"}
            if self.system_name != None:
                for key in json_login_mark:
                    if self.system_name == key:
                        self.login_mark = json_login_mark[key]
            else:
                print(f"传入的system_name为空，跳过执行")
        else:
            print(f"传入的login_mark不为空，跳过执行")
        return self.target_url, self.login_mark

    def encrypt(self, data):
        """密码前置js加密"""
        serialzed_enc_res = self.target_rss.get(url=self.serialzed_enc_auth_url).json()
        # print(serialzed_enc_base64_res)
        serialzed_enc_auth = serialzed_enc_res["result"]
        # # 读取JavaScript文件内容
        with open(encryption_auth_dir, "r", encoding="utf-8") as f:
            js_content = f.read()
        # 编译JavaScript代码
        js_runtime = execjs.compile(js_content)
        # 调用JavaScript函数
        encipherPassword = js_runtime.call("encryptWithPublicKey", serialzed_enc_auth, data)
        print(encipherPassword)
        return encipherPassword




    def soo_login(self):
        """组织架构系统登录"""
        logger.info("组织架构系统登录")
        soo_login_url = '{}/orgauth/loginHq'.format(self.Auth_Base_URL)  # 登录
        passwordEncrypt = self.encrypt(self.password)
        soo_account = {"account": self.account, "password": self.password, "securityCode": "123", "isBind": 1}
        logger.info(f"登录soo系统, 账号:{self.account}, 密码：{self.password}")
        soo_account['password'] = passwordEncrypt
        soo_login_res = self.target_rss.post(url=soo_login_url, json=soo_account, headers=self.json_head)
        logger.info(f"登录完成,{soo_login_res}")
        return self.target_rss

    def target_login(self):
        """对接目标地址登录"""
        self.target_url, self.login_mark = self.target_url_splice_login_mark()
        logger.info("开始执行目标地址登录")
        passwordEncrypt = self.encrypt(self.password)
        soo_login_url = '{}/orgauth/loginHq'.format(self.Auth_Base_URL)  # 登录
        soo_account = {"account": self.account, "password": self.password, "securityCode": "123", "isBind": 1}
        logger.info(f"登录soo系统, 账号:{self.account}, 密码：{self.password}")
        soo_account['password'] = passwordEncrypt
        soo_login_res = self.target_rss.post(url=soo_login_url, json=soo_account, headers=self.json_head)
        logger.info(f"登录完成,{soo_login_res}")
        url = "{}/orgauth/getAuthToken?".format(self.Auth_Base_URL)
        target_login_connect_url = url + f'url={self.target_url}'  # 拿登录的token
        target_rss = self.target_rss.get(url=target_login_connect_url).json()
        logger.info(target_rss)
        self.token = target_rss['result']
        logger.info(f"获取重定向系统(https://{self.target_url})的登录token:{self.token}")
        # 拿登录目标系统的cookie
        if 'dfm' in self.target_url:
            target_login_url = f'https://{self.target_url}/admin/{self.login_mark}/checkLogin.html?authToken={self.token}'
        elif self.login_mark in ["AuthLogin", "OrgAuth"]:
            target_login_url = f'https://{self.target_url}/{self.login_mark}/ssoLogin?authToken={self.token}'
        else:
            target_login_url = f'https://{self.target_url}/{self.login_mark}/sso/login?authToken={self.token}'
        logger.info(f"打印组成目标系统登录地址：{target_login_url}")
        target_login_res = self.target_rss.get(url=target_login_url)
        print(target_login_res)
        if self.target_url not in ["uat-e.hqchip.com", "uat-dfm.elecfans.com", "uat-www.hqpcb.com", "uat-srm.huaqiu.com"]:
            # print(target_login_res.json())
            if "nickName" in target_login_res.json()["result"]:
                login_name = jsonpath.jsonpath(target_login_res.json(), "$..nickName")[0]
                login_userId = jsonpath.jsonpath(target_login_res.json(), "$..userId")[0]
                # print(login_name, login_userId)
                setattr(Data, "login_name", login_name)
                setattr(Data, "login_userId", login_userId)
        logger.info(f"获取到登录cookie")

        return self.target_rss


    def target_login_once_more(self,token):
        """对接目标地址登录"""
        self.target_url, self.login_mark = self.target_url_splice_login_mark()
        logger.info("开始执行目标地址登录")
        passwordEncrypt = self.encrypt(self.password)
        soo_login_url = '{}/orgauth/loginHq'.format(self.Auth_Base_URL)  # 登录
        soo_account = {"account": self.account, "password": self.password, "securityCode": "123","isBind": 1}
        logger.info(f"登录soo系统, 账号:{self.account}, 密码：{self.password}")
        soo_account['password'] = passwordEncrypt
        soo_login_res = self.target_rss.post(url=soo_login_url, json=soo_account, headers=self.json_head)
        logger.info(f"登录完成,{soo_login_res}")

        # target_login_connect_url = f'https://uat-auth.huaqiu.com/orgauth/getAuthToken?url={self.target_url}'  # 拿登录的token
        # target_rss = self.target_rss.get(url=target_login_connect_url).json()
        # token = target_rss['result']
        # logger.info(f"获取重定向系统(https://{self.target_url})的登录token:{token}")

        # 拿登录目标系统的cookie
        target_login_url = f'https://{self.target_url}/{self.login_mark}/sso/login?authToken={token}'
        logger.info(f"打印组成目标系统登录地址：{target_login_url}")
        target_login_res = self.target_rss.get(url=target_login_url)
        print(target_login_res)
        logger.info(f"获取到登录cookie")
        return self.target_rss




if __name__ == '__main__':
    # SOOLogin("uat-e.hqchip.com", "AuthLogin").target_login()
    # SOOLogin("admin", "12345678", "uat-activity.hqchip.com", "ecmc").target_login_once_more(token)
    # target_url, login_mark = SOOLogin(system_name="erp").target_url_splice_login_mark()
    # print(target_url, login_mark)
    SOOLogin("uat-wms.huaqiu.com", "wms/base").target_login()
    # SOOLogin().encrypt("1111")