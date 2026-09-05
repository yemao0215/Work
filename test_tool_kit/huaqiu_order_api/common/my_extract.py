import jsonpath
from huaqiu_order_api.common.my_data import Data
from huaqiu_order_api.common.loguru_logger import logger


def extract_data_from_response(extract_epr, response_dict, share_data_obj: Data):
    """
    从响应结果当中提取值，并设置为Data类的属性。
    :param extract_epr: excel当中extract列中的提取表达式。是一个字典形式的字符串。
                        key为全局变量名。value为jsonpath提取表达式。
                        '{"token":"$..token","member_id":"$..id","leave_amount":"$..leave_amount"}'
    :param response_dict: http请求之后的响应结果。字典类型。
    :return:None
    """
    # 从excel中读取的提取表达式，转成字典对象
    extract_dict = eval(extract_epr)

    # 遍历字典的key,value  key是全局变量名，value是jsonpath表达式
    for key, value in extract_dict.items():

        # 根据jsonpath从响应结果当中，提取真正的值。value就是jsonpath表达式
        logger.info("提取的变量名是：{}，提取的jsonpath表达式是：{}".format(key, value))
        result = jsonpath.jsonpath(response_dict, value)
        logger.info("jsonpath提取之后的值为:{}".format(result))
        # jsonpath找了就是列表，找不到返回False
        # 如果提取到了真正的值，那么将它设置为Data类的属性。key是全局变量名，result[0]就是提取后的值
        if result:
            setattr(share_data_obj, key, str(result[0]))
            logger.info("提取的变量名是：{}，提取到的值是：{},并设置为Data类实例化对象的属性和值".format(key, str(result[0])))
        return result
