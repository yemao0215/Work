class FieldComparison:
    def __init__(self, field1, field2, enable_log: bool = True):
        self.field1 = field1
        self.field2 = field2
        self.enable_log = enable_log

    def _log(self, msg):
        if self.enable_log:
            print(msg)

    def field_comparison(self):
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

    def _compare_list(self):
        """两个list对比"""
        set1 = set(self.field1)
        set2 = set(self.field2)
        only_in_field1 = sorted(list(set1 - set2))
        only_in_field2 = sorted(list(set2 - set1))
        diff_total = only_in_field1 + only_in_field2

        if not diff_total:
            self._log("✅ 列表内容完全一致，无差异")
        else:
            self._log("❌ 列表存在差异")
            self._log(f"【仅field1独有】{only_in_field1}")
            self._log(f"【仅field2独有】{only_in_field2}")

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
            self._log("✅ 基础值相等")
            return {
                "type": "basic",
                "equal": True,
                "diff_total": []
            }
        else:
            self._log(f"❌ 基础值不相等，field1={self.field1}, field2={self.field2}")
            return {
                "type": "basic",
                "equal": False,
                "diff_total": [self.field1, self.field2]
            }

    def _compare_basic_list(self, base, lst, base_name):
        """单个值 vs 列表"""
        exists = base in lst
        if exists:
            self._log(f"✅ {base_name}:{base} 存在于列表中")
            return {
                "type": "basic_vs_list",
                "exists": True,
                "diff_total": []
            }
        else:
            self._log(f"❌ {base_name}:{base} 不在列表内")
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
            self._log("✅ 两个字典完全一致")
        else:
            self._log("❌ 字典存在差异")
            self._log(f"【仅field1的key】{only_key1}")
            self._log(f"【仅field2的key】{only_key2}")
            self._log(f"【同key值不一致】{diff_key}")

        return {
            "type": "dict",
            "only_key_field1": only_key1,
            "only_key_field2": only_key2,
            "value_diff_keys": diff_key,
            "diff_detail": diff_detail
        }


# ------------------- 测试示例 -------------------
if __name__ == "__main__":
    # 测试1：你原来的两组列表
    field1 = ['1011138234', '1011078784', '1011078783', '1011138235', '1019027463', '1019025967', '1011078785',
              '1011258369', '1011369957', '1011258370', '1017398223', '1017404917', '1017408483', '1019030554',
              '1006942738', '1006934698', '1012118374', '1015517985', '1012422614', '4600479568', '4600286219',
              '4600284616', '4600285544', '1012464878', '1018578168', '1018650142', '1018327629', '1012108200',
              '1017828811', '1018793487', '1011187673', '1011222768', '1012405690', '1011208333', '1006963126',
              '1006963276', '1006963211']
    field2 = ['1011078784', '1011078783', '1011138234', '1011138235', '1011078785', '1011258369', '1011369957',
              '1011258370', '1017398223', '1017408483', '1017404917', '1006942738', '1006934698', '1012118374',
              '1015517985', '1012422614', '4600479568', '4600286219', '4600284616', '4600285544', '1012464878',
              '1018578168', '1018650142', '1018327629', '1012108200', '1017828811', '1018793487', '1011187673',
              '1011222768', '1011208333', '1012405690', '1006963126', '1006963276', '1006963211']
    cmp1 = FieldComparison(field1, field2)
    res1 = cmp1.field_comparison()
    print("\n【列表对比结果】")
    print(res1)

    # 测试2：字典对比
    d1 = {"a": 1, "b": 2, "c": 3}
    d2 = {"a": 1, "b": 99, "d": 4}
    cmp2 = FieldComparison(d1, d2)
    res2 = cmp2.field_comparison()
    print("\n【字典对比结果】")
    print(res2)

    # 测试3：字符串对比
    cmp3 = FieldComparison("hello", "world")
    print("\n【字符串对比结果】")
    print(cmp3.field_comparison())