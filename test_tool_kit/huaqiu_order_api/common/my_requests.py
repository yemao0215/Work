import os
import requests
from huaqiu_order_api.common.my_Conf import MyConf
from huaqiu_order_api.common.my_path import conf_dir
from huaqiu_order_api.common.rsa_encrypt import generator_sign
from huaqiu_order_api.common.loguru_logger import logger


class MyRequests:
    # 初始化方法
    def __init__(self):
        self.headers = {"Content-Type": "application/x-www-form-urlencoded"}
        # 读取配置文件当中的，server地址。
        self.base_url = MyConf(os.path.join(conf_dir, "conf.ini")).get("server", "host")

    def send_requests(self, method, api_url, data=None, token=None):
        # 处理请求头
        self.__deal_header(token)
        # 处理请求url
        url = self.__deal_url(api_url)
        logger.info("请求url: \n{}".format(url))
        logger.info("请求方法: \n{}".format(method))

        # 如果是v3版本，则添加向请求体当中，添加timestamp和sign字段
        if self.headers.get("X-Lemonban-Media-Type") == "lemonban.v3" and token:
            logger.info("使用RSA加密。")
            # 生成sign,和timestamp
            sign, timestamp = generator_sign(token)
            data["sign"] = sign
            data["timestamp"] = timestamp
        logger.info("请求数据: \n{}".format(data))

        # 调用requests的方法去发起一个请求。并得到响应结果
        if method.upper() == "GET":    # 请求方法转换成大写
            response = requests.request(method, url, params=data, headers=self.headers)
        else:
            response = requests.request(method, url, data=data, headers=self.headers)
        logger.info("响应结果：\n{}".format(response.text))
        return response

    def send_session(self, method, api_url, data=None, token=None):
        # 处理请求头
        self.__deal_header(token)
        # 处理请求url
        url = self.__deal_url(api_url)
        logger.info("请求url: \n{}".format(url))
        logger.info("请求方法: \n{}".format(method))

        # 调用session方法去发起一个请求。并得到响应结果
        if method.upper() == "GET":  # 请求方法转换成大写
            response = requests.get(url=url, headers=self.headers)
        else:
            response = requests.post(url=url, data=data, headers=self.headers)
        logger.info("响应结果：\n{}".format(response.text))
        return response

    def __deal_header(self, token=None):
        if token:
            self.headers["Authorization"] = token
        logger.info("请求头为：\n{}".format(self.headers))

    def __deal_url(self, api_url: str):
        if api_url.startswith("https://") or api_url.startswith("http://"):
            return api_url
        else:
            url = self.base_url + api_url
            return url


if __name__ == '__main__':
    mr = MyRequests()
    url = "http://api.lemonban.com/futureloan/member/register"
    req_data = {
        "mobile_phone": "18610100022",
        "pwd": "123456789",
        "reg_name": "py37"
    }
    method = "post"
    resp = mr.send_requests(method, url, req_data)
    print(resp.json())

    # url地址
    url = "http://api.lemonban.com/futureloan/member/login"
    # 请求类型：post

    # 请求体
    req_data = {
        "mobile_phone": "18610100020",
        "pwd": "123456789"
    }
    method = "post"
    resp = mr.send_requests(method, url, req_data)
    print(resp.json())

    # 提取出来，给到下一接口去作为请求
    json_res = resp.json()
    token = json_res["source_data"]["token_info"]["token"]
    member_id = json_res["source_data"]["id"]

    url = "http://api.lemonban.com/futureloan/member/recharge"
    # 请求数据
    req_data = {
        "member_id": member_id,
        "amount": 1000
    }
    method = "post"
    resp = mr.send_requests(method, url,  req_data, token=token)
    print(resp.json())
