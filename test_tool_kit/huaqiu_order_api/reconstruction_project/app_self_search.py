import json
from concurrent.futures.thread import ThreadPoolExecutor
from urllib import parse
import pymysql
import requests
from huaqiu_order_api.common.loguru_logger import logger


# M端切换Java搜索
def request_run(key_word):
    php_search_url = 'https://uat-www.hqchip.com/search/{}.html?format=json&limit=10'
    java_search_url = 'https://uat-m.hqchip.com/ajax/search.html?keyword={}&limit=10'
    if key_word[0] in [r'#', '/', '%', '&', '+', '.', '*']:
        pass
    print(f"开始循环对比关键词{key_word}")
    # url_upkey = parse.quote_plus(key_word)
    old_url = php_search_url.format(key_word)
    new_url = java_search_url.format(key_word)
    try:
        old_res = request_resul1(old_url)
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
    contrast(None, None, old_dict, new_dict, old_url)


def contrast(key=None, goodsid=None, old=None, new=None, url=None):

    if isinstance(old, (int, float)):
        contrast(key, goodsid, str(old), new, url)

    elif isinstance(old, str):
        try:
            if key in ['has_page', 'activity_discount', 'activity_freight']:
                if old in ['0', '']:
                    if new is None:
                        pass
                    else:
                        logger.error(f"{url}:字段:{key},goodsid:{goodsid}, php接口返回的 {old} 值和Java接口返回的 {new} 值不一致")

                elif isinstance(new, (int, float)):
                    new = str(new)
                    if old != new:
                        logger.error(f"{url}:字段:{key},goodsid:{goodsid}, php接口返回的 {old} 值和Java接口返回的 {new} 值不一致")

            elif key in ['cat_name', 'cat_name1', 'cat_name2', '_score', 'package', 'spq', 'package_info', 'total', 'urlName']:
                pass

            else:
                if isinstance(new, (int, float)):
                    new = str(new)
                if old != new:
                    logger.error(f"{url}:字段:{key},goodsid:{goodsid}, php接口返回的 {old} 值和Java接口返回的 {new} 值不一致")
        except Exception as e:
            logger.error(f"{url}:字段:{key} 比较出错,错误信息为:{e}")

    elif isinstance(old, dict):
        if type(old) == type(new):
            for k, v in old.items():
                if k in ['delivery', 'tags_str', 'isCanbook', 'select_order', 'has_switch_goods']:
                    pass
                else:
                    try:
                        contrast(k, goodsid, v, new[k], url)
                    except Exception as e:
                        logger.error(f"{url}:字段:{key},goodsid:{goodsid} 查找key:{k} 失败,错误信息为:{e}")
        else:
            logger.error(f"{url}:字段:{key},goodsid:{goodsid} 中{type(old)}的类型和{type(new)}的类型不一致")

    elif isinstance(old, list):
        if key == 'Tiered':
            for price in range(len(old)):
                for pi in range(len(old[price])):
                    if pi != 1:
                        contrast(f'Tiered-{price}', goodsid, old[price][pi], new[price][pi], url)
        elif key == 'aggs' and old == []:
            if new['cat_aggs'] == [] and new['full_encap_aggs'] == []:
                pass
            else:
                logger.error(f"{url}:字段:{key},goodsid:{goodsid}, php接口返回的 {old} 值和Java接口返回的 {new} 值不一致")

        elif type(old) == type(new) and len(old) == len(new):
            if key == 'PD':
                for i in range(len(old)):
                    goodsid = old[i]['GoodsId']
                    for ii in range(len(new)):
                        if goodsid == new[ii]['GoodsId']:
                            contrast('PD', goodsid, old[i], new[ii], url)
                            break
                    else:
                        logger.error(f'{url}:新接口返回的 PD 列表中没有找到goodsid:{goodsid}')
            elif key in ['full_encap_aggs', 'cat_aggs']:
                for aggs_i in range(len(old)):
                    aggs_key = str(old[aggs_i]['key'])
                    for aggs_ii in range(len(new)):
                        if aggs_key == new[aggs_ii]['key']:
                            contrast(key, aggs_key, old[aggs_i], new[aggs_ii], url)
                            break
                    else:
                        logger.error(f'{url}:新接口返回的 {key} 列表中没有找到key:{aggs_key}')

            else:
                for i in range(len(old)):
                    contrast(key, goodsid, old[i], new[i], url)

        else:
            logger.error(f"{url}:字段:{key},goodsid:{goodsid},php接口返回的类型为：{type(old)},列表长度为：{len(old)},{old},Java接口返回的类型为：{type(new)},列表长度为：{len(new)};")

    elif old is None:
        if new is not None:
            logger.error(f"{url}:goodsid:{goodsid},旧接口字段:{key} 返回的结果为None,新接口返回的结果为:{new}")
    else:
        logger.error(f"{url}: 字段:{old} 返回了意料之外的类型:{type(old)}")


def request_resul(url):
    """发送请求"""
    s = requests.session()
    try:
        headers = {'user-agent':'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Mobile Safari/537.36'}
        res = s.get(url=url, headers=headers)
        return res.text
    except Exception as e:
        logger.error(f"接口请求出错{e}：\n{url}")

def request_resul1(url):
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
# with ThreadPoolExecutor(max_workers=5) as tp:
#     tp.map(request_run, k_word)


if __name__ == '__main__':
    for keyword in k_word:
        request_run(keyword)

    # request_run('0603')










