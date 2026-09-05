import numpy as np
import translators

from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_path import yaml_file


# 自定义工具类
def field_translate(field):
    # 字段翻译
    ts = translators
    logger.info("开始翻译字段：{}".format(field))
    # 使用 有道 翻译
    translated = ts.translate_text(field, translator='youdao', to_language='en')
    # 将每个单词的首字母大写
    translated = translated.title()
    logger.info("翻译结果：{}".format(translated))
    return translated
def field_contrast(param_frist, param_second):
    # 参数对比
    #判定两个参数是否同一类型
    if type(param_frist) == type(param_second):
        logger.info("两个参数类型一致")
        if isinstance(param_frist, str) and isinstance(param_second, str):
            pass
        elif isinstance(param_frist, int) and isinstance(param_second, int):
            pass
        elif isinstance(param_frist, float) and isinstance(param_second, float):
            pass
        elif isinstance(param_frist, list) and isinstance(param_second, list):
            # 将列表转换为集合
            set_param_frist = set(param_frist)
            set_param_second = set(param_second)
            # 找出 a 有但 b 没有的元素
            only_in_param_frist = set_param_frist - set_param_second
            # 找出 b 有但 a 没有的元素
            only_in_param_second = set_param_second - set_param_frist
            # 合并所有不同值
            all_differences = only_in_param_frist.union(only_in_param_second)
        elif isinstance(param_frist, dict) and isinstance(param_second, dict):
            pass
        elif isinstance(param_frist, bool) and isinstance(param_second, bool):
            pass
        else:
            logger.error("两个参数类型不一致")
    else:
        logger.error("两个参数类型不一致")
# 辅助函数：递归转换所有 numpy.int64 为原生 int
def convert_numpy_types(obj):
    if isinstance(obj, np.int64):
        return int(obj)
    elif isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    else:
        return obj


if __name__ == '__main__':
    field = "要将翻译后的英文文本中每个单词的首字母设置为大写，你可以使用 Python 的 title() 方法。这个方法会将每个单词的首字母转换为大写。下面是一个简单的代码示例，展示如何翻译文本并将翻译结果中的每个单词首字母大写"
    field_translate(field)