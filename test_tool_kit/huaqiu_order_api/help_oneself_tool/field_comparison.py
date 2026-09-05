import json
import re
from datetime import datetime, timedelta

import jsonpath

import yaml

from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_data import Data
from huaqiu_order_api.common.my_path import yaml_file, account_yaml, field1_goodsId_yaml, field2_goodsId_yaml
from huaqiu_order_api.common.yaml_handler import read_yaml


class FieldComparison:
    def __init__(self, field1=None, field2=None, enable_log: bool = True):
        self.field1 = field1
        self.field2 = field2
        self.enable_log = enable_log  # 是否打印日志，方便调试关闭

    def _log(self, msg):
        """日志打印封装"""
        if self.enable_log:
            print(msg)

    def field_comparison(self):
        """
        字段对比入口
        :return: dict{
            "only_in_field1": [],    # field1独有元素
            "only_in_field2": [],    # field2独有元素
            "diff_total": [],        # 所有差异合并
        }
        """
        # 标准化：统一转为集合用于成员判断
        set1 = self._to_set(self.field1)
        set2 = self._to_set(self.field2)

        only_in_field1 = sorted(list(set1 - set2))
        only_in_field2 = sorted(list(set2 - set1))
        diff_total = only_in_field1 + only_in_field2

        # 输出日志
        if not diff_total:
            logger.info("✅ 两边内容完全一致，无差异")
        else:
            logger.info(f"❌ 存在差异")
            logger.info(f"【仅field1独有】{only_in_field1}")
            logger.info(f"【仅field2独有】{only_in_field2}")
            logger.info(f"【所有差异元素汇总】{only_in_field1 + only_in_field2}")

        result = {
            "only_in_field1": only_in_field1,
            "only_in_field2": only_in_field2,
            "diff_total": diff_total
        }
        return result
    def field_automatch_comparison(self):
        """
        统一入口分发不同类型对比
        返回结构化结果字典
        """
        if isinstance(self.field1, list) and isinstance(self.field2, list):
            return self._compare_list()
        elif isinstance(self.field1, dict) and isinstance(self.field2, dict):
            return self._compare_dict()
        elif isinstance(self.field1, (str, int)) and isinstance(self.field2, (str, int)):
            return self._compare_basic()
        # 一边基础类型，一边列表
        elif isinstance(self.field1, (str, int)) and isinstance(self.field2, list):
            return self._compare_basic_list(base=self.field1, lst=self.field2, base_name="field1")
        elif isinstance(self.field1, list) and isinstance(self.field2, (str, int)):
            return self._compare_basic_list(base=self.field2, lst=self.field1, base_name="field2")
        else:
            raise TypeError(f"暂不支持对比类型：{type(self.field1)} <-> {type(self.field2)}")

    def _to_set(self, data):
        """
        通用转换方法：任意支持类型转为集合
        支持 list / str / int
        """
        if isinstance(data, list):
            return set(data)
        elif isinstance(data, (str, int)):
            # 单个值，包装成单元素集合
            return {data}
        elif isinstance(data, dict):
            # dict后续扩展，这里抛出提示，你可以自行实现key/value对比
            raise NotImplementedError("字典对比逻辑尚未实现，请补充")
        else:
            raise TypeError(f"暂不支持该类型对比：{type(data)}")
    def _compare_list(self):
        """两个list对比"""
        set1 = set(self.field1)
        set2 = set(self.field2)
        only_in_field1 = sorted(list(set1 - set2))
        only_in_field2 = sorted(list(set2 - set1))
        diff_total = only_in_field1 + only_in_field2

        if not diff_total:
            logger.info("✅ 列表内容完全一致，无差异")
        else:
            logger.info("❌ 列表存在差异")
            logger.info(f"【仅field1独有】{only_in_field1}")
            logger.info(f"【仅field2独有】{only_in_field2}")
            logger.info(f"【所有差异元素汇总】{diff_total}")


        return {
            "type": "list",
            "only_in_field1": only_in_field1,
            "only_in_field2": only_in_field2,
            "diff_total": diff_total
        }
    def _compare_basic(self):
        """str / int 基础类型对比"""
        equal = self.field1 == self.field2
        if equal:
            logger.info("✅ 基础值相等")
            return {
                "type": "basic",
                "equal": True,
                "diff_total": []
            }
        else:
            logger.info(f"❌ 基础值不相等，field1={self.field1}, field2={self.field2}")
            return {
                "type": "basic",
                "equal": False,
                "diff_total": [self.field1, self.field2]
            }

    def _compare_basic_list(self, base, lst, base_name):
        """单个值 vs 列表"""
        exists = base in lst
        if exists:
            logger.info(f"✅ {base_name}:{base} 存在于列表中")
            return {
                "type": "basic_vs_list",
                "exists": True,
                "diff_total": []
            }
        else:
            logger.info(f"❌ {base_name}:{base} 不在列表内")
            diff_total = [base] + lst
            return {
                "type": "basic_vs_list",
                "exists": False,
                "diff_total": diff_total
            }

    def _compare_dict(self):
        """
        字典深度对比（一级key对比，如需嵌套字典递归我再改）
        返回：
            only_key1: 只在field1存在的key
            only_key2: 只在field2存在的key
            diff_key: 两边都有key，但value不一致的key列表
        """
        d1 = self.field1
        d2 = self.field2
        keys1 = set(d1.keys())
        keys2 = set(d2.keys())

        only_key1 = sorted(list(keys1 - keys2))
        only_key2 = sorted(list(keys2 - keys1))
        common_keys = keys1 & keys2

        diff_key = []
        diff_detail = {}
        for k in common_keys:
            v1 = d1[k]
            v2 = d2[k]
            if v1 != v2:
                diff_key.append(k)
                diff_detail[k] = {"field1_value": v1, "field2_value": v2}

        if not only_key1 and not only_key2 and not diff_key:
            logger.info("✅ 两个字典完全一致")
        else:
            logger.info("❌ 字典存在差异")
            logger.info(f"【仅field1的key】{only_key1}")
            logger.info(f"【仅field2的key】{only_key2}")
            logger.info(f"【同key值不一致】{diff_key}")

        return {
            "type": "dict",
            "only_key_field1": only_key1,
            "only_key_field2": only_key2,
            "value_diff_keys": diff_key,
            "diff_detail": diff_detail
        }
    def mian_field_automatch_comparison(self):
        fieId1 = read_yaml(field1_goodsId_yaml)
        fieId2 = read_yaml(field2_goodsId_yaml)
        if self.field1 == None:
            self.field1 = fieId1
        if self.field2 == None:
            self.field2 = fieId2
        field_comparison = self.field_automatch_comparison()
        print(field_comparison)
        return field_comparison

if __name__ == '__main__':
    field_comparison = FieldComparison().mian_field_automatch_comparison()

