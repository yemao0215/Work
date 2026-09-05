import json
from queue import Queue
from threading import Thread
import requests
from common.loguru_logger import logger


php_address = 'https://uat-hc2019.hqchip.com/sync/test/syncApiDebug?id={}'
java_address = 'https://uat-es-search.hqchip.com/v1/testParticiple?goodsIds={}'
goods_id= []
def read_data(file):
    """读取excel文件数据"""
    try:
        f = open(file, 'r', encoding='utf-8')
        for line in f.readlines():
            line = line.strip()
            goods_id.append(line)
    except Exception as e:
        logger.error(f"读取excel数据出错{e}")

q = Queue()
for i in goods_id:
    q.put(i)

def work():
    while not q.empty():
        try:
            good_id = q.get(timeout=2)
            php_url = php_address.format(good_id)
            java_url = java_address.format(good_id)
        except Exception as e:
            print(f"获取队列中库存id异常{e}")
            break  # 获取队列中url异常，说明url已经全部获取完毕，结束循环
        try:
            php_res = request_resul(php_url)  # 发送php请求
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
            java_res = request_resul(java_url)  # 发送Java请求
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
                    php_value = str_sort(php_dict[k])
                    java_value = str_sort(java_dict[k])
                    if php_value != java_value:
                        logger.error(
                            f"Java接口返回的值不一致，url为:{java_url},key值为:{k},php返回的内容为:{php_value} Java返回的内容为:{java_value}")
                except Exception as e:
                    logger.error(f"获取Java接口返回信息出错:{e}, 请求的接口为:{java_url}, 出错的key为:{k}")
            else:
                try:
                    if php_dict[k] != java_dict[k]:
                        logger.error(
                            f"Java接口返回的值不一致，url为:{java_url}, key值为{k}, php返回的内容为:{v}{type(v)},Java返回的字段内容为:{java_dict[k]}{type(java_dict[k])}")
                except Exception as e:
                    logger.error(f"获取Java接口返回信息出错:{e}, 请求接口为:{java_url},出错的key为:{k}")

def request_resul(url):
    """发送请求"""
    s = requests.Session()
    try:
        res = s.get(url)
        return res.text
    except Exception as e:
        logger.error(f"接口请求出错{e}: {url}")

def str_sort(name):
    li = list(name)
    li.sort()
    str_key = ''.join(li)
    return str_key



def main():
    for i in range(1000):
        t1 = Thread(target=work)
        t1.start()



        
        

