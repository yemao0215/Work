import requests
from huaqiu_order_api.common.my_Conf import MyConf
from huaqiu_order_api.common.my_data import Data
from huaqiu_order_api.common.my_path import conf_ini

login_url = MyConf(conf_ini).get("log", "url")
body = MyConf(conf_ini).get("log", "body")


def re_sso_authentication():
    """使用requests 方法获取到单点登录鉴权"""
    res = requests.post(url=Data.url, data=Data.body)
    json_res = res.json()
    sso_url = json_res["source_data"]["syncurl"][10]
    sso_res = requests.get(sso_url)
    cookie = requests.utils.dict_from_cookiejar(sso_res.cookies)
    ss0_auth = cookie["ICC_auth_hqchip"]
    token = cookie["auth_token"]

    return ss0_auth, token


def ses_sso_authentication():
    """使用 session 方法获取到单点登录鉴权,并设置到全局变量Data里面"""
    rss = requests.Session()
    res = rss.post(url=Data.url, data=Data.body)
    json_res = res.json()
    sso_url = json_res["source_data"]["syncurl"][10]
    sso_res = rss.get(sso_url)
    token = json_res["source_data"]["token"]
    # Session会自动处理cookie信息
    # 设置token为全局变量
    setattr(Data, 'token', token)
    yield rss


if __name__ == "__main__":
    # rs = requests.Session()
    # re = ses_sso_authentication(rs)
    ses = ses_sso_authentication()
    # re = re_sso_authentication()

    print(f"re方法获取的鉴权token:\n{ses}")
    # print(f"ses方法获取的鉴权结果:\n{ses}")
