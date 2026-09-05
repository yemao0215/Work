from itertools import combinations

from huaqiu_order_api.common.loguru_logger import logger





class EsSearchConstiute:
    def __init__(self):
        self.list = ["aaa", "ah", "a1", "aaa555"]


    def combine_keylist(self, n):
        '''根据n获得列表中的所有可能组合（n个元素为一组）'''
        temp_list2 = []
        for c in combinations(self.list, n):  # 其实主要用到的是这个函数
            temp_list2.append(c)
        return temp_list2

    # def remove_empty_strings(self,list):
    #     """list里面元组删除空字符串"""
    #     return [tuple(filter(None, i)) for i in list]


    def obtain_combine(self):
        end_list = []
        for i in range(1, len(self.list)+1):
            end_list.extend(self.combine_keylist(i))

        logger.info(f"得到分词组合为：{end_list}")
        # logger.info(end_list[0: -1])
        return end_list
    def create_es_select_sentence(self):
        pass


if __name__ == '__main__':
    EsSearchConstiute().obtain_combine()



