import ast
from decimal import Decimal
import jsonpath
from huaqiu_order_api.common.my_mysql import MyMysql
from huaqiu_order_api.common.loguru_logger import logger


class MyAssert:
    def assert_response_value(self, check_str, response_dict):
        """
        :param check_str: 从excel当中，读取出来的断言列。是一个列表形式的字符串。里面的成员是一个断言
        :param response_dict: 接口请求之后的响应数据，是字典类型。
        :return: None
        """
        # 所有断言的比对结果列表
        check_res = []

        # 把字符串转换成python列表
        check_list = eval(check_str)
        logger.info("用例字符串转换成列表:\n{}".format(check_list))

        for check in check_list:
            logger.info("要断言的内容为：\n{}".format(check))

            # 通过jsonpath表达式，从响应结果当中拿到实际结果
            actual = jsonpath.jsonpath(response_dict, check["expr"])
            if isinstance(actual, list):  # isinstance：判断 actual是不是列表类型
                actual = actual[0]
            logger.info("从响应结果当中，提取到的值为:\n{}".format(actual))
            logger.info("期望结果为:\n{}".format(check["expected"]))

            # 与实际结果做比对
            if check["type"] == "eq":
                logger.info("比对2个值是否相等")
                logger.info("比对结果为：\n{}".format(actual == check["expected"]))
                check_res.append(actual == check["expected"])
            elif check["type"] == "gt":
                logger.info("比对2个值的大小。")
                logger.info("比对结果为：\n{}".format(actual > check["expected"]))
                check_res.append(actual > check["expected"])
            elif check["type"] == "in":
                logger.info("包含关系。")
                logger.info("比对结果为：\n{}".format(actual in check["expected"]))
                check_res.append(actual in check["expected"])

        if False in check_res:
            logger.error("部分断言失败!!!")
            return False
        else:
            logger.info("所有断言成功！")
            return True

    def assert_db(self, check_db_str):
        """
        :param check_db_str: 测试数据excel当中，assert_db列读取出来的数据库检验字符串。
              示例：[{"sql":"select id from member where mobile_phone='#phone#'","expected":1,"type":"count"}]
              1）调用数据库类，执行sql语句。调哪个方法，根据type来决定。得到实际结果
              2）与期望结果比对
        :return:
        """
        # 所有断言的比对结果列表
        check_db_res = []

        # 把字符串转换成python列表
        check_db_list = eval(check_db_str)
        logger.info("用例字符串转换成列表:\n{}".format(check_db_list))

        # 建立数据库连接
        db = MyMysql()

        # 遍历check_db_list
        for check_db_dict in check_db_list:
            logger.info("当前要比对的sql语句：\n{}".format(check_db_dict["sql"]))
            logger.info("当前执行sql的查询类型(查询结果条数/查询某个值)：\n{}".format(check_db_dict["db_type"]))
            logger.info("期望结果为：{}".format(check_db_dict["expected"]))

            # 根据type来调用不同的方法来执行sql语句
            if check_db_dict["db_type"] == "count":
                logger.info("比对数据库查询的结果条数，是否符合期望")
                # 执行sql语句 查询结果是一个整数
                res_db = db.get_count(check_db_dict["sql"])
                logger.info("sql的执行结果为：{}".format(res_db))

            elif check_db_dict["db_type"] == "eq":
                logger.info("比对数据库查询出来的数据，是否与期望相等")
                # 执行sql语句 查询结果是一个字典key-value
                res_db = db.get_one_data(check_db_dict["sql"])
                logger.info("sql的执行结果为：{}".format(res_db))
                # 对于数据库查询结果当中，如果有Decimal类型，则转换为float类型
                for key, value in res_db.items():
                    if isinstance(value, Decimal):
                        res_db[key] = float(value)

            else:
                logger.error("不支持的数据库比对类型！！，请检查你的断言写法！！")
                raise Exception

            # 将比对结果添加到结果列表当中
            check_db_res.append(res_db == check_db_dict["expected"])
            logger.info("比对结果为：{}".format(res_db == check_db_dict["expected"]))

        if False in check_db_res:
            logger.error("部分断言失败!!")
            raise AssertionError
            # return False
        else:
            logger.info("所有断言成功！")
            return True


if __name__ == '__main__':
    check_db_str = """[{"sql":"select id from member where mobile_phone='15500000000'","expected":1,
    "db_type":"count"}] """
    re_s = MyAssert().assert_db(check_db_str)
    print(re_s)
