import requests

from huaqiu_order_api.common.loguru_logger import logger


class ErpUsersBalanceRecharge:


    def __init__(self, account, psw, order_sn,uesr):
        """
        :param account:  登录ERP账号
        :param psw:  登录ERP密码
        :param order_sn:  前台商城生成订单编号
        :param uesr:    前台商城生成订单编号的用户名称
        """
        self.account = account
        self.password = psw
        self.order_sn = order_sn
        self.uesr = uesr
        self.rss = requests.Session()
        self.login_url = 'https://uat-e.hqchip.com/public/checkLogin/'
        self.body = {'account': self.account, 'password': self.password}
        self.headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    def login(self):
        """
        登录ERP
        """
        logger.info(f"开始执行登录账号:{self.body}")
        self.rss.post(url=self.login_url, data=self.body, headers=self.headers)
        logger.info(f"登录完成")
        return self