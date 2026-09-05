import json
from concurrent.futures.thread import ThreadPoolExecutor
from urllib import parse
import pymysql
import requests
from common.loguru_logger import logger


# go语言实时搜索接口对比
def request_run(key_word):
    print(f"开始循环对比关键字: {key_word}")
    py_search_url = 'http://uat-websearch.hqchip.com/?supplier=tme&limit=3&keyword={}'
    go_search_url = 'http://uat-go-search.hqchip.com/?supplier=tme&limit=3&keyword={}'
    url_upkey = parse.quote_plus(key_word)
    old_url = py_search_url.format(url_upkey)
    new_url = go_search_url.format(url_upkey)
    try:
        old_res = request_resul(old_url)
    except Exception as e:
        logger.error(f"old接口请求出错{e},请求url{old_url},结束本轮关键字查询循环")
        return False
    if old_res is None:
        logger.error(f"old接口返回None,请求url{old_url},结束本轮关键字查询循环")
        return False
    if old_res == '':
        logger.error(f"old接口返回空,请求url{old_url},结束本轮关键字查询循环")
        return False
    try:
        new_res = request_resul(new_url)
    except Exception as e:
        logger.error(f"new接口请求出错{e},请求url{new_url} old请求结果{old_res},结束本轮关键字查询循环")
        return False
    if new_res is None:
        logger.error(f"new接口返回None,请求url{new_url} old请求结果{old_res},结束本轮关键字查询循环")
        return False
    try:
        old_dict = json.loads(old_res)
    except Exception as e:
        logger.error(f"old返回结果转换为字典出错{e},请求的url为:{old_url},结束本轮关键字查询循环")
        return False
    try:
        new_dict = json.loads(new_res)
    except Exception as e:
        logger.error(f"new返回结果转换为字典出错{e},请求的url为:{new_url},结束本轮关键字查询循环")
        return False
    recursion_fungible(None, None, old_dict, new_dict, old_url)


def recursion_fungible(key=None, goodsid=None, old=None, new=None, url=None):

    if isinstance(old, (int, float)):
        recursion_fungible(key, goodsid, str(old), new, url)

    elif isinstance(old, str):
        try:
            if key in ['time', 'change_count']:
                pass
            else:
                if isinstance(new, (int, float)):
                    new = str(new)
                if old != new:
                    logger.error(f"{url}:字段:{key},goodsid: {goodsid}, py接口返回的 {old} 值和 go接口返回{new} 的值不一致")
        except Exception as e:
            logger.error(f"{url}:字段:{key} 比较出错,错误信息为:{e}")

    elif isinstance(old, dict):
        if type(old) == type(new):
            for k, v in old.items():
                try:
                    if v == 'api fetch no source_data':
                        if not new['source_data']:
                            break
                        else:
                            logger.error(f"{url}: py接口返回空值，go接口返回 {new}")
                            break
                    elif k == 'ModelName':
                        if v == '':
                            pass
                        else:
                            recursion_fungible(k, goodsid, v, new[k], url)
                    else:
                        recursion_fungible(k, goodsid, v, new[k], url)
                except Exception as e:
                    logger.error(f"{url}:查找字典:{new} 的key:{k} 失败,错误信息为:{e}")
        else:
            logger.error(f"{url}:字段:{key},goodsid: {goodsid} 中{type(old)}的类型和{type(new)}的类型不一致")

    elif isinstance(old, list):
        if type(old) == type(new) and len(old) == len(new):
            if key == 'source_data':
                for i in range(len(old)):
                    goodsid = old[i]['GoodsId']
                    for ii in range(len(new) + 1):
                        try:
                            if goodsid == new[ii]['GoodsId']:
                                recursion_fungible('source_data', goodsid, old[i], new[ii], url)
                                break
                        except IndexError:
                            logger.error(f'{url}:新接口返回的 source_data 列表中没有找到goodsid:{goodsid}')

            elif key == 'Stock':
                if old != new:
                    logger.error(f"{url}:列表data中库存id：{goodsid},字段: {key}返回的结果不一致,py接口返回: {old}, go接口返回：{new}")
            elif key == 'Tiered':
                for price in range(len(old)):
                    if old[price][0] == new[price][0]:
                        if abs(old[price][1] - new[price][1]) >= 0.0001:
                            logger.error(f"{url}:库存id: {goodsid},py接口返回的阶梯价格为：{old}, go接口返回的阶梯价格为：{new}")
                    else:
                        logger.error(f"{url}:库存id: {goodsid},py接口返回的阶梯价格为：{old}, go接口返回的阶梯价格为：{new}")

            else:
                logger.info(f"字典:result 返回了意料之外的列表:{key}")

        else:
            logger.error(f"{url}:字段:{key} 中py接口返回的类型为：{type(old)},列表长度为：{len(old)},{old},go接口返回的类型为：{type(new)},列表长度为：{len(new)};")

    elif old is None:
        if new is not None:
            logger.error(f"{url}:goodsid: {goodsid},旧接口字段:{key} 返回的结果为None,新接口返回的结果为:{new}")
    else:
        logger.error(f"{url}: 字段:{old} 返回了意料之外的类型:{type(old)}")


def request_resul(url):
    """发送请求"""
    s = requests.session()
    try:
        res = s.get(url)
        return res.text
    except Exception as e:
        logger.error(f"接口请求出错{e}：\n{url}")


def read_data(file):
    """读取excel数据"""
    goods_id = []
    try:
        f = open(file, 'r', encoding='utf-8')
        for line in f.readlines():
            line = line.strip()
            goods_id.append(line)
        return goods_id
    except Exception as e:
        logger.error(f"读取数据出错{e}")
        return False


def read_sql() -> tuple:
    """读取数据库数据"""
    db = pymysql.connect(
        host='fat-www-db.hqchip.com',
        user='hqchip',
        password='gV6kmUg4MxyaYPXh',
        port=3306,
        database='hqchip',
        charset="utf8",
        cursorclass=pymysql.cursors.DictCursor
    )
    cur = db.cursor()
    try:
        sql = " SELECT  DISTINCT keyword  FROM  ecs_search_log_item   WHERE  keyword = '0603'  "
        cur.execute(sql)
        list_key = cur.fetchall()
        return list_key
    except Exception as e:
        logger.error(f"数据库读取数据出错{e}")
        raise e


# k_word = read_sql()
k_word = read_data(r'E:\HuaQiu_API\testdatas\data.xlsx')
with ThreadPoolExecutor(max_workers=5) as tp:
    tp.map(request_run, k_word)

print('运行结束')


# if __name__ == '__main__':
    # for keyword in k_word:
    #     print(f"开始循环对比关键词{keyword}")
    #     request_run(keyword)

    # request_run('AT28HC256-90SU')










