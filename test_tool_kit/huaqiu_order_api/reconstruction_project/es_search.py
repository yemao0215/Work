"""
脚本需要实现什么功能： 根据需要实现的功能去思考具体实现的步骤
实现的功能：要实现两个接口返回的数据对比
    实现的步骤：1.需要两个接口 ，接口里面的参数goods_id需要动态替换
                获取good_id：数据库读取  或者在excel读取
              2.需要发送接口请求
                定义一个发送请求的方法，返回接口执行的结果
              3.发送请求，返回结果比对
               循环遍历 读取出来的good_id，拼接到url里面
               调用发送请求的方法，分别执行需要对比的两个接口，并把返回的值用变量接受
               把返回的结果转换成字典格式，遍历循环字典的key value
               根据旧的接口去对比新接口，同一个key对应的value值不相等就continue结束本轮循环  打印出日志 手动排查
              4.根据需求 判断需要排除的异常数据
              5.捕获程序运行中各种可能出现的异常，捕获到后continue结束本轮循环，记录出错的url接口信息 手动排查
"""
import json
import logging

import pymysql
import requests
from huaqiu_order_api.common.loguru_logger import logger


class TestSearch:
    """es分词搜索接口对比脚本"""
    goods_id = []

    def __init__(self):
        self.php_address = 'https://uat-hc2019.hqchip.com/sync/test/syncApiDebug?id={}'
        self.java_address = 'https://uat-es-search.hqchip.com/v1/testParticiple?goodsIds={}'
        self.read_data(r'C:\Users\WIN\Desktop\1\goods_id1.xlsx')

    def request_run(self):
        logger.info('开始循环获取id进行数据对比')
        for i in self.goods_id:
            php_url = self.php_address.format(i)  # 拼接php接口url
            java_url = self.java_address.format(i)  # 拼接Java接口url
            try:
                php_res = self.request_resul(php_url)  # 发送php请求
            except Exception as e:
                logger.error(f"php接口请求出错{e},请求的url为:{php_url}")
                continue
            if php_res is None:
                # logger.error(f"php接口返回None,请求的url为:{php_url}")
                continue
            if php_res == '':
                # logger.info(f"php接口返回空值,请求的url为:{php_url}")
                continue
            try:
                java_res = self.request_resul(java_url)  # 发送Java请求
            except Exception as e:
                logger.error(f"Java接口请求出错{e},请求的url为:{java_url}")
                continue
            if java_res is None:
                logger.error(f"java接口请求返回为None,请求的url为:{java_url}")
                continue
            try:
                php_dict = json.loads(php_res)  # 将php接口请求的结果转换为字典格式
            except Exception as e:
                logger.error(f"php返回结果转换为字典出错{e}, 请求的url为:{php_url},返回的请求结果为:{php_res}")
                continue
            try:
                java_dict = json.loads(java_res)['body']  # 将java接口请求的结果转换为字典格式,并获取body内容
            except Exception as e:
                logger.error(f"Java返回结果转换为字典出错{e}, 请求的url为:{java_url},返回的请求结果为:{java_res}")
                continue
            for k, v in php_dict.items():
                """循环php接口返回的数据"""
                if k == 'collection':  # 过滤掉废弃字段
                    continue
                elif k == 'goods_id':
                    try:
                        if isinstance(php_dict[k], str):
                            php_dict[k] = int(php_dict[k])  # 把php接口返回的goods_id转换为int类型
                        if php_dict[k] != java_dict[k]:
                            logger.error(
                                f"Java接口返回的值不一致，url为:{java_url}, key值为{k}, php返回的内容为:{v}{type(v)},Java返回的字段内容为:{java_dict[k]}{type(java_dict[k])}")
                    except Exception as e:
                        logger.error(f"错误信息为:{e}, 请求接口信息为:{java_url},出错的key为:{k}")
                elif php_dict[k] == '':
                    if java_dict[k] not in ('', '[]'):
                        logger.error(f"请求的url为:{java_url}, key值为:{k},php接口返回空值,Java接口返回的内容为:{java_dict[k]}")
                elif k in ('goods_name', 'cat_name'):
                    try:
                        php_value = self.str_sort(php_dict[k])
                        java_value = self.str_sort(java_dict[k])
                        if php_value != java_value:
                            logger.error(f"Java接口返回的值不一致，url为:{java_url},key值为:{k},php返回的内容为:{php_value} Java返回的内容为:{java_value}")
                    except Exception as e:
                        logger.error(f"获取Java接口返回信息出错:{e}, 请求的接口为:{java_url}, 出错的key为:{k}")
                else:
                    try:
                        if php_dict[k] != java_dict[k]:
                            logger.error(
                                f"Java接口返回的值不一致，url为:{java_url}, key值为{k}, php返回的内容为:{v}{type(v)},Java返回的字段内容为:{java_dict[k]}{type(java_dict[k])}")
                    except Exception as e:
                        logger.error(f"获取Java接口返回信息出错:{e}, 请求接口为:{java_url},出错的key为:{k}")
        else:
            logger.info('数据全部对比结束')

    def request_resul(self, url):
        """发送请求"""
        s = requests.Session()
        try:
            res = s.get(url)
            return res.text
        except Exception as e:
            logger.error(f"接口请求出错{e}: {url}")

    def read_data(self, file):
        """读取excel文件数据"""
        try:
            f = open(file, 'r', encoding='utf-8')
            for line in f.readlines():
                line = line.strip()
                self.goods_id.append(line)
        except Exception as e:
            logger.error(f"读取excel数据出错{e}")

    def read_sql_zy(self):
        """读取数据库拿自营库存数据"""
        # 链接数据库
        db = pymysql.connect(
            host='',
            user='',
            password='',
            port='',
            database='',
            charset='',
            cursorclass=''
        )
        cur = db.cursor()
        try:
            sql = "select goods_id from ecs_goods_ic"
            cur.execute(sql)
            id = cur.fetchall()  # 获取数据库查询结果
            return id
        except Exception as e:
            logger.error(f"读取数据库id出错{e}")
            raise e

    def str_sort(self, name):
        li = list(name)
        li.sort()
        str_key = ''.join(li)
        return str_key


if __name__ == '__main__':
    TestSearch().request_run()
    # goods_id = []
    # def read_data(file):
    #     """读取excel文件数据"""
    #     try:
    #         f = open(file, 'r', encoding='utf-8')
    #         for line in f.readlines():
    #             line = line.strip()
    #             goods_id.append(line)
    #     except Exception as e:
    #         logger.error(f"读取excel数据出错{e}")
    #
    #
    # read_data('E:\goods_id1.xlsx')
