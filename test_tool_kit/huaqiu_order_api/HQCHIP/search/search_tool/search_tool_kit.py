from urllib import parse
from urllib.parse import quote

import jsonpath
import requests
import yaml

from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_path import yaml_file, account_yaml


class SearchToolKit:
    def __init__(self, keyword):
        self.rss = requests.Session()
        # 设置代理ip
        proxy_ip = "http://192.168.20.6:3128"
        # 设置代理
        self.proxies = {"http": proxy_ip, "https": proxy_ip}
        self.supplier_url = "https://api.mouser.com"
        self.appikey = "76f623be-ee57-4ae3-86b6-01e54048fd18"
        self.headers = {"Content-Type": "application/x-www-form-urlencoded",
                        "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://www.huaqiu.com)"
                        }
        self.headers_json = {"Content-Type": "application/json; charset=UTF-8",
                             "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://www.huaqiu.com)"
                             }
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.HQCHIP_URL = data['HQCHIP_URL']
        self.SEARCH_URL = data['SEARCH_URL']
        self.GO_SEARCH_URL = data['GO_SEARCH_URL']
        with open(account_yaml, 'r', encoding='utf-8') as yamlfile:
            account = yaml.load(yamlfile, Loader=yaml.FullLoader)
        # self.keyword = "0402 191KΩ 1安"
        self.keyword = keyword
        self.goods_id = [1017426139]

    def query_url_arguments(self, data):
        """将body参数转换成可拼接至url的参数"""
        lt = []
        for k, v in data.items():
            lt.append(k + '=' + quote(str(v)))
        # 这个是在for循环外面的，就是将列表的元素之间用用&符号连接起来
        query_string = '&'.join(lt)
        return query_string

    def self_search_data(self):
        """前台自营数据查询"""
        self_search_url = "{}/search/{}.html?debug_self_search=1".format(self.HQCHIP_URL, self.keyword)
        logger.info(self_search_url)
        self_search_res = self.rss.get(url=self_search_url, headers=self.headers_json).json()
        logger.info(f"执行结果为{self_search_res}")
        return self

    def keyword_participle(self):
        """关键词分词"""
        keyword_participle_url = "{}/searchTool/v3/keywordSegmentation".format(self.SEARCH_URL)
        logger.info(keyword_participle_url)
        keyword_participle_body = {"keyword": self.keyword}
        keyword_participle_res = self.rss.post(url=keyword_participle_url, json=keyword_participle_body, headers=self.headers_json).json()
        logger.info(f"执行结果为{keyword_participle_res}")
        return self

    def search_goods_es_doc(self):
        """查询指定库存id文档信息"""
        goods_es_search_url = "{}/searchTool/v3/getEsDosByStockId".format(self.SEARCH_URL)
        goods_es_search_body = {"stockIds": self.goods_id}
        goods_es_search_res = self.rss.post(url=goods_es_search_url, json=goods_es_search_body, headers=self.headers_json).json()
        logger.info(f"执行结果为{goods_es_search_res}")
        return self
    def search_goods_participle(self):
        """对库存信息进行分词"""
        search_goods_participle_url = "{}/searchTool/v3/stockSegmentation".format(self.SEARCH_URL)
        search_goods_participle_body = {
            "isSelf": True, "goodsName": self.keyword, "eccap": "", "goodsDesc": "", "goodsSn": "",
            "tags": [], "catName": [], "goodsOtherName": ""}
        search_goods_participle_res = self.rss.post(url=search_goods_participle_url, json=search_goods_participle_body, headers=self.headers_json).json()
        logger.info(f"执行结果为{search_goods_participle_res}")
        return self
    def keyword_hit_mongo_filed_type(self):
        headers = {"Content-Type": "application/json"}
        url = "{}/searchTool/v3/querySingleWord".format(self.SEARCH_URL)
        body = {"keyword": self.keyword}
        res = self.rss.post(url=url, json=body, headers=headers).json()
        print(res)
        return self


    def search_goods_interior_port_v4(self):
        search_v4_url = "https://uat-www.hqchip.com/betasearch"
        keyword_ud = parse.quote(self.keyword)
        logger.info(f"关键词编码为{keyword_ud}")
        search_goods_interior_port_url = "{}/{}.html?debug_self_search=1&showDsl=true".format(search_v4_url, keyword_ud)
        interior_port_res = self.rss.get(url=search_goods_interior_port_url, headers=self.headers).json()
        self.search_interior_url = interior_port_res["$url"]
        self.search_interior_params = interior_port_res["$params"]
        print(type(self.search_interior_params))
        # logger.info(f"执行结果为{interior_port_res}")
        return self
    def search_goods_interior_port_v3(self):
        search_v3_url = "https://uat-www.hqchip.com/search"
        keyword_ud = parse.quote(self.keyword)
        logger.info(f"关键词编码为{keyword_ud}")
        search_goods_interior_port_url = "{}/{}.html?debug_self_search=1&showDsl=true".format(search_v3_url, keyword_ud)
        logger.info(search_goods_interior_port_url)
        interior_port_res = self.rss.get(url=search_goods_interior_port_url, headers=self.headers).json()
        self.search_interior_url = interior_port_res["$url"]
        self.search_interior_params = interior_port_res["$params"]
        logger.info(f"执行结果为{interior_port_res}")
        return self
    def search_goods_log_push_v4(self):
        """hqchip_search日志实时推送"""
        keyword_ud = parse.quote(self.keyword)
        logger.info(f"关键词编码为{keyword_ud}")
        search_goods_url = "{}/search/v4/self?offset=0&limit=30&keyword={}&stockNum=-1&priceStart=0&priceEnd=0&orderType=0&sortType=1&userId=3234324&showDsl=true&onlySpotGoods=0&brandId=".format(self.SEARCH_URL,keyword_ud)
        search_goods_res = self.rss.get(url=search_goods_url).json()
        participlelist = jsonpath.jsonpath(search_goods_res, '$..participleList')
        logger.info(f"执行结果为{participlelist}")
        return self

    def search_goods_log_push_v3(self):
        """hqchip_search日志实时推送"""
        keyword_ud = parse.quote(self.keyword)
        logger.info(f"关键词编码为{keyword_ud}")
        search_goods_url = "{}/search/v3/self?offset=0&limit=30&keyword={}&stockNum=-1&priceStart=0&priceEnd=0&orderType=0&sortType=1&userId=3234324&showDsl=true&onlySpotGoods=0&brandId=".format(self.SEARCH_URL,keyword_ud)
        print(search_goods_url)
        search_goods_res = self.rss.get(url=search_goods_url).json()
        self.participlelist = jsonpath.jsonpath(search_goods_res, '$..participleList')[0]
        logger.info(f"执行结果为{search_goods_res}")
        return self
    def search_goods_log_push(self):
        """hqchip_search日志实时推送"""
        keyword_ud = parse.quote(self.keyword)
        logger.info(f"关键词编码为{keyword_ud}")
        search_interior_params_url_1 = self.query_url_arguments(self.search_interior_params)
        search_goods_url = self.search_interior_url + '?' + search_interior_params_url_1
        logger.info(search_goods_url)
        search_goods_res = self.rss.get(url=search_goods_url).json()
        self.participlelist = jsonpath.jsonpath(search_goods_res, '$..participleList')[0]
        logger.info(f"执行结果为{self.participlelist}")
        # logger.info(f"执行结果为{search_goods_res}")
        return self
    def mian_search_goods_log_push(self, type=None):
        if type == "beta":
            logger.info(f"执行版本为V4")
            self.search_goods_interior_port_v4().search_goods_log_push().keyword_unit_replace()
            self.keyword_hit_mongo_filed_type()
            return self.participlelist
        else:
            logger.info(f"执行版本为V3")
            self.search_goods_interior_port_v3().search_goods_log_push_v3()
            self.keyword_hit_mongo_filed_type()
            return self.participlelist
    def keyword_unit_replace(self):
        """获取单位替换数据"""
        keyword_unit_replace_search_url = "{}/searchTool/v3/keywordSegmentation".format(self.SEARCH_URL)
        keyword_unit_replace_search_body = {"keyword": self.keyword}
        keyword_unit_replace_search_res = self.rss.post(url=keyword_unit_replace_search_url, json=keyword_unit_replace_search_body, headers=self.headers_json).json()
        print(keyword_unit_replace_search_res)
        normAttrValueMap = jsonpath.jsonpath(keyword_unit_replace_search_res, "$..normAttrValueMap")[0]
        logger.info(normAttrValueMap)
        if len(normAttrValueMap) == 0:
            logger.info("关键词无单位替换数据")
            return self.participlelist
        else:
            logger.info("关键词存在单位替换数据")
            new_lst = []
            for i in self.participlelist:
                new_lst.append(i)
                if i in normAttrValueMap:
                    # self.participlelist.append(normAttrValueMap[i])
                    new_lst.append(normAttrValueMap[i])
            self.participlelist = set(new_lst)
            return self.participlelist









if __name__ == '__main__':
    participlelist = SearchToolKit("Board to Board & Mezzanine Connectors Flexible Boa").mian_search_goods_log_push("V3")
    print(participlelist)