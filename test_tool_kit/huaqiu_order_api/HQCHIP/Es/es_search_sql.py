import json
from urllib import parse
from urllib.parse import quote

import jsonpath
import requests
import yaml

from huaqiu_order_api.HQCHIP.search.search_tool.search_tool_kit import SearchToolKit
from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_path import yaml_file, account_yaml


class EsSearchSQL:
    def __init__(self, keyword=None, version=None):
        self.rss = requests.Session()
        self.keyword = keyword
        self.version = version


    def es_search_sql_form(self):
        participlelist = SearchToolKit(self.keyword).mian_search_goods_log_push(self.version)
        if "Ω" in self.keyword:
            logger.info(f'第一层分词：{self.keyword}存在Ω，需要将其转化成特定字符，以防后续换算无法进行')
            # 转成英文小写
            self.keyword = self.keyword.replace('Ω', '&&&&').lower()
            # &&&& 转换回 Ω
            self.keyword = self.keyword.replace("&&&&", 'Ω')
        else:
            logger.info(f'第一层分词：{self.keyword}不存在Ω，直接转化英文小写')
            self.keyword = self.keyword.lower()
        logger.info(self.keyword)
        es_search_sql_basic = {"from": 0, "size": 30,
                               "query": "",
                               "sort": [{"_score": {"order": "desc"}}, {"goods_number": {"order": "desc"}}, {"lowest_price": {"order": "asc"}}],
                               "track_total_hits": 2147483647,
                               "aggregations": {
                                   "cat_id_aggs": {"terms": {"field": "cat_id", "size": 100, "min_doc_count": 1, "shard_min_doc_count": 0, "show_term_doc_count_error": False, "order": [{"_count": "desc"}, {"_key": "asc"}]}},
                                   "full_encap_aggs": {"terms": {"field": "full_encap", "size": 100, "min_doc_count": 1, "shard_min_doc_count": 0, "show_term_doc_count_error": False, "order": [{"_count": "desc"}, {"_key": "asc"}]}},
                                    "brand_id_aggs": {"terms": {"field": "brand_id", "size": 100, "min_doc_count": 1, "shard_min_doc_count": 0, "show_term_doc_count_error": False, "order": [{"_count": "desc"}, {"_key": "asc"}]}}},
                               "highlight": {"fields": {"goods_name_org": {}, "full_goods_name": {}, "goods_name": {}, "brand_name": {}, "brand_en2": {}, "cat_name": {},
                                                        "full_cat_name": {}, "encap": {}, "full_encap": {}, "goods_desc": {}, "goods_desc2": {}}}
                               }
        if len(participlelist) > 1:
            shoulds = []
            for i in range(len(participlelist)):
                shoulds.append({"multi_match": {"query": participlelist[i],
                        "fields": ["cat_name^30.0", "encap^30.0", "full_ebcap^20.0", "goods_desc^20.0", "goods_desc2^10.0", "goods_name^30.0", "goods_name_alias^1.0", "goods_no^10.0", "goods_sn^10.0", "tags^10.0"],
                        "type": "best_fields", "operator": "OR", "analyzer": "whitespace", "slop": 0, "prefix_length": 0, "max_expansions": 50, "zero_terms_query": "NONE", "auto_generate_synonyms_phrase_query": True, "fuzzy_transpositions": True, "boost": 1}})
            bools = {"should": shoulds, "adjust_pure_negative": True, "boost": 1}
        else:
             shoulds = [{"multi_match": {"query": self.keyword,
                                                      "fields": ["brand_cn^1000.0", "brand_en^1000.0",
                                                                 "cat_name^3000.0", "encap^1000.0", "full_ebcap^2000.0",
                                                                 "goods_desc^800.0", "goods_desc^500.0",
                                                                 "goods_name^5000.0", "goods_name_alias^5000.0",
                                                                 "goods_no^10.0", "goods_sn^10.0", "tags^10.0"],
                                                      "type": "best_fields", "operator": "OR", "analyzer": "whitespace",
                                                      "slop": 0, "prefix_length": 0, "max_expansions": 50,
                                                      "zero_terms_query": "NONE",
                                                      "auto_generate_synonyms_phrase_query": True,
                                                      "fuzzy_transpositions": True, "boost": 1}}]
             bools = {"should": shoulds, "adjust_pure_negative": True, "boost": 1}
        must_queries = [{"constant_score": {"filter": {"bool": {"must": [{"term": {"goods_name_org": {"value": self.keyword, "boost": 1}}}, {"term": {"brand_name": {"value": self.keyword, "boost": 1}}}, {"term": {"full_cat_name": {"value": self.keyword, "boost": 1}}}], "adjust_pure_negative": True, "boost": 1}}, "boost": 100006}},
                        {"constant_score": {"filter": {"bool": {"must": [{"term": {"goods_name_org": {"value": self.keyword, "boost": 1}}}, {"term": {"brand_name": {"value": self.keyword, "boost": 1}}}], "adjust_pure_negative": True, "boost": 1}}, "boost": 100005}},
                        {"constant_score": {"filter": {"bool": {"must": [{"term": {"goods_name_org": {"value": self.keyword, "boost": 1}}}, {"term": {"full_cat_name": {"value": self.keyword, "boost": 1}}}], "adjust_pure_negative": True, "boost": 1}}, "boost": 100004}},
                        {"constant_score": {"filter": {"bool": {"must": [{"term": {"brand_name": {"value": self.keyword, "boost": 1}}}, {"term": {"full_cat_name": {"value": self.keyword, "boost": 1}}}], "adjust_pure_negative": True, "boost": 1}}, "boost": 100003}},
                        {"constant_score": {"filter": {"bool": {"must": [{"term": {"brand_name": {"value": self.keyword, "boost": 1}}}], "adjust_pure_negative": True, "boost": 1}}, "boost": 100002}},
                        {"constant_score": {"filter": {"bool": { "must": [{"term": {"goods_name_org": {"value": self.keyword, "boost": 1}}}], "adjust_pure_negative": True, "boost": 1}}, "boost": 100001}},
                        {"constant_score": {"filter": {"bool": {"must": [{"term": {"goods_name_alias": {"value": self.keyword, "boost": 1}}}], "adjust_pure_negative": True, "boost": 1}}, "boost": 100001}},
                        {"constant_score": {"filter": {"bool": {"must": [{"term": {"full_cat_name": {"value": self.keyword, "boost": 1}}}], "adjust_pure_negative": True, "boost": 1}}, "boost": 100000}},
                        {"bool": bools}]
        es_search_sql_basic["query"] = {
            "bool": {
            "must": [{"dis_max": {"tie_breaker": 0, "queries": must_queries, "boost": 1}}],
            "must_not": [{"terms": {"brand_id": ["8196"], "boost": 1}}],
            "adjust_pure_negative": True, "boost": 1}}
        es_search_sql = json.dumps(es_search_sql_basic, ensure_ascii=False).replace("'", '"')
        return es_search_sql



if __name__ == '__main__':
    EsSearchSQL("0402 191KΩ 1安", "beta").es_search_sql_form()
