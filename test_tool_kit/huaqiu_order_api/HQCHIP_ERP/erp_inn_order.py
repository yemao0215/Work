import re
import yaml
from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_data import Data
from huaqiu_order_api.common.my_path import yaml_file, account_yaml


class ErpInnOrder:


    def __init__(self, rss):
        """
        :param account:  登录ERP账号
        :param psw:  登录ERP密码
        :param order_sn:  前台商城生成订单编号
        :param uesr:    前台商城生成订单编号的用户名称
        """
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.ERP_URL = data['ERP_URL']
        self.in_order = getattr(Data, 'inn_sn')
        # self.in_order = "IN00154517"
        self.rss = rss
        self.headers = {'Content-Type': 'application/x-www-form-urlencoded',
                        "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://www.huaqiu.com)"
                        }

    def wanhong_order_obtain(self):
        search_url = "{}/putaway".format(self.ERP_URL)
        search_body = {'keytype': 'p.putaway_sn', 'keyword': self.in_order}
        logger.info(f"搜索订单编号: {self.in_order}")
        search_res = self.rss.post(url=search_url, data=search_body, headers=self.headers,
                                   timeout=1000).text  # 搜索订单，获取order_id
        inn_order_id = re.search('(<td><a class="edit" href="/putaway/edit/id/)([0-9]{6})', search_res).group(2)
        logger.info(f"搜索完成,获取到order_id: {inn_order_id}")
        wanhong_order_obtain_url = "{}/ajax/loadLogList".format(self.ERP_URL)
        wanhong_order_obtain_body = {"id": inn_order_id, "module": "Putaway"}

        wanhong_order_obtain_res = self.rss.post(url=wanhong_order_obtain_url, data=wanhong_order_obtain_body, headers=self.headers,
                                   timeout=1000).text
        wanghong_order_sn = re.search('(\u4e07\u9e3f\u5185\u914d\u9500\u552e\u5355:)(S[0-9]{13})', wanhong_order_obtain_res).group(2)
        # 将获取的万鸿内配销售单号往Data里面作虚拟存储以【ic_order_sn】命名以便后续提取
        setattr(Data, 'ic_order_sn', wanghong_order_sn)
        return wanghong_order_sn


if __name__ == '__main__':
    from huaqiu_order_api.HQCHIP_SOO.login import SOOLogin
    target_rss = SOOLogin("uat-e.hqchip.com", "AuthLogin").target_login()
    ErpInnOrder(target_rss).wanhong_order_obtain()
