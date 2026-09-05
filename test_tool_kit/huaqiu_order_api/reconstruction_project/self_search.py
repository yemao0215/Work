import json
from concurrent.futures.thread import ThreadPoolExecutor
import pymysql
import requests
from loguru import logger


def request_run(key_word):
    php_address = 'https://www.hqchip.com/search/{}.html?format=json&limit=30'  # &cat_id%5B%5D=398&brand_id%5B%5D=472
    java_address = 'https://www.hqchip.com/search/{}.html?format=json&limit=30&test=1'

    if key_word[0] in ['#', '$', '/', '%']:
        return key_word
    php_url = php_address.format(key_word)
    java_url = java_address.format(key_word)
    try:
        php_res = request_resul(php_url)
    except Exception as e:
        logger.error(f"php接口请求出错{e},请求url{php_url}")
        raise e
    if php_res is None:
        logger.error(f"php接口返回None,请求url{php_url}")
        raise TypeError
    if php_res == '':
        logger.error(f"php接口返回空,请求url{php_url}")
        raise TypeError
    try:
        java_res = request_resul(java_url)
    except Exception as e:
        logger.error(f"java接口请求出错{e},请求url{java_url} php请求结果{php_res}")
        raise e
    if java_res is None:
        logger.error(f"java接口请求出错,请求url{java_url} php请求结果{php_res}")
        raise TypeError
    try:
        php_dict = json.loads(php_res)
    except Exception as e:
        logger.error(f"php返回结果转换为字典出错{e},请求的url为:{php_url}")
        raise e
    try:
        java_dict = json.loads(java_res)
    except Exception as e:
        logger.error(f"java返回结果转换为字典出错{e},请求的url为:{java_url}")
        raise e
    for k, v in php_dict.items():
        """循环php接口返回的数据"""
        php_v = php_dict[k]
        java_v = java_dict[k]
        if isinstance(php_v, dict):
            if k == 'aggs':
                for aggs_k, aggs_v in php_v.items():
                    try:
                        if aggs_k == 'full_encap_aggs':
                            if len(aggs_v) != len(java_v[aggs_k]):
                                logger.error(f"url:{java_url},Java接口返回的{k}中列表{aggs_k}长度不一致")
                            else:
                                if not aggs_v:
                                    if not java_v[aggs_k]:
                                        continue
                                    else:
                                        logger.error(f"url:{java_url},字段{k}-{aggs_k}php为空列表，Java返回的值为{java_v[aggs_k]}")
                                else:
                                    for full_aggs_item in range(len(aggs_v)):
                                        for full_k, full_v in aggs_v[full_aggs_item].items():
                                            if type(full_v) in [int, float]:
                                                full_v = str(full_v)
                                            if type(java_v[aggs_k][full_aggs_item][full_k]) in [int, float]:
                                                java_v[aggs_k][full_aggs_item][full_k] = str(
                                                    java_v[aggs_k][full_aggs_item][full_k])
                                            if full_v != java_v[aggs_k][full_aggs_item][full_k]:
                                                logger.error(
                                                    f"url:{java_url},字段{k}-{aggs_k}返回的结果不一致,第{full_aggs_item}字典中字段 {full_k},php返回的结果:{full_v},Java返回的结果:{java_v[aggs_k][full_aggs_item][full_k]}")
                        elif aggs_k == 'cat_aggs':
                            if len(aggs_v) != len(java_v[aggs_k]):
                                logger.error(f"url:{java_url},Java接口返回的{k}-{aggs_k}长度不一致")
                            else:
                                if aggs_v == []:
                                    if java_v[aggs_k] == []:
                                        continue
                                    else:
                                        logger.error(
                                            f"url:{java_url},字段{k}-{aggs_k}php为空列表，Java返回的值为{java_v[k][aggs_k]}")
                                else:
                                    for cat_aggs_item in range(len(aggs_v)):
                                        for cat_k, cat_v in aggs_v[cat_aggs_item].items():
                                            if type(cat_v) in [int, float]:
                                                cat_v = str(cat_v)
                                            if type(java_v[aggs_k][cat_aggs_item][cat_k]) in [int, float]:
                                                java_v[aggs_k][cat_aggs_item][cat_k] = str(
                                                    java_v[aggs_k][cat_aggs_item][cat_k])
                                            if cat_v != java_v[aggs_k][cat_aggs_item][cat_k]:
                                                logger.error(
                                                    f"url:{java_url},字段{k}-{aggs_k}返回的结果不一致,第{cat_aggs_item}字典中字段 {cat_k},php返回的结果:{cat_v},Java返回的结果:{java_v[aggs_k][cat_aggs_item][cat_k]}")
                        else:
                            if type(aggs_v) in [int, float]:
                                aggs_v = str(aggs_v)
                            if type(java_v[aggs_k]) in [int, float]:
                                java_v[aggs_k] = str(java_v[aggs_k])
                            if aggs_v != java_v[aggs_k]:
                                logger.error(
                                    f"url{java_url},字段{k}-{aggs_k}返回结果不一致，php返回:{aggs_v},Java返回:{java_v[aggs_k]}")
                    except Exception as e:
                        logger.error(f"url{java_url},字段{k}-{aggs_k}比对结果出错{e}")
            else:
                for key, value in php_v.items():
                    if type(value) in [int, float]:
                        value = str(value)
                    if type(java_v[key]) in [int, float]:
                        java_v[key] = str(java_v[key])
                    if value != java_v[key]:
                        logger.error(
                            f"java接口返回的值不一致,url为:{java_url},key值为{key},php返回的内容为:{value} java返回的字段内容为:{java_v[key]}")
        elif isinstance(php_v, list):
            if not v:
                continue
            elif v == [[]]:
                continue
            elif len(php_v) != len(java_v):
                logger.error(f"url为 {java_url},Java接口返回的{k}字段列表长度与php接口返回的长度不一致")
                continue
            elif k == 'PD':
                for php_item_dict in php_v:
                    good_id = php_item_dict['GoodsId']
                    for kk, vv in php_item_dict.items():
                        try:
                            for i in range(len(php_v) + 1):
                                if isinstance(java_v[i]['GoodsId'], str):
                                    java_v[i]['GoodsId'] = int(java_v[i]['GoodsId'])
                                if good_id == java_v[i]['GoodsId']:
                                    try:
                                        if kk in ['delivery', 'tags_str', 'isCanbook', '_score', 'select_order',
                                                  'has_switch_goods']:  # 废弃字段不做比较
                                            break  # package spq 封装信息需要连库去查找   img_url url是拼接后的字段暂时先不管  cat_name 分类取值规则不一致 不做比较
                                        elif kk in ['package', 'img_url', 'spq', 'package_info', 'cat_name',
                                                    'cat_name1', 'cat_name2', 'urlName', 'ModelNameUrl']:
                                            break
                                        elif kk in ['SelfBrand', 'promote_info']:
                                            for brand_k, brand_v in vv.items():
                                                if type(brand_v) in [int, float]:
                                                    brand_v = str(brand_v)
                                                if type(java_v[i][kk][brand_k]) in [int, float]:
                                                    java_v[i][kk][brand_k] = str(java_v[i][kk][brand_k])
                                                if brand_v != java_v[i][kk][brand_k]:
                                                    logger.error(
                                                        f"url为:{java_url},字段{k}中GoodsId：{good_id},字典{kk}中{brand_k}返回结果不一致,php返回结果:{brand_v},Java返回结果:{java_v[i][kk][brand_k]}")
                                        elif kk == 'attr':
                                            if vv == []:
                                                if java_v[i][kk] != []:
                                                    logger.error(
                                                        f"uar:{java_v},字段PD中attr php返回为空列表，Java返回:{java_v[i][kk]}")
                                            else:
                                                for attr_k, attr_v in vv.items():
                                                    if attr_v != java_v[i]['attr'][attr_k]:
                                                        logger.error(
                                                            f"url为:{java_url},字段{k}中GoodsId：{good_id},字典attr中{attr_k}返回结果不一致,php返回结果:{attr_v},Java返回结果:{java_v[i]['attr'][attr_k]}")
                                        elif kk == 'DT':
                                            for dt_k, dt_v in vv.items():
                                                if dt_v != java_v[i]['DT'][dt_k]:
                                                    logger.error(
                                                        f"url为:{java_url},字段{k}中GoodsId:{good_id},字典DT中{dt_k}返回结果不一致,php返回结果:{dt_v},Java返回结果:{java_v[i]['DT'][dt_k]}")
                                        elif kk == 'Stock':
                                            if len(vv) != len(java_v[i]['Stock']):
                                                logger.error(
                                                    f"url为:{java_url},字段PD中GoodsId:{good_id},列表Stock,php和Java返回的结果列表长度不一致")
                                                break
                                            else:
                                                for stock_int in range(len(vv)):
                                                    if type(vv[stock_int]) in [int, float]:
                                                        vv[stock_int] = str(vv[stock_int])
                                                    if type(java_v[i]['Stock'][stock_int]) in [int, float]:
                                                        java_v[i]['Stock'][stock_int] = str(
                                                            java_v[i]['Stock'][stock_int])
                                                php_stock = sorted(vv)
                                                java_stock = sorted(java_v[i]['Stock'])
                                                for stock_n in range(len(php_stock)):
                                                    if php_stock[stock_n] != java_stock[stock_n]:
                                                        logger.error(
                                                            f"url为:{java_url},字段PD中GoodsId:{good_id},列表Stock返回的结果不一致,php返回的结果:{php_stock[stock_n]},Java返回的结果:{java_stock[stock_n]}")
                                        elif kk == 'Tiered':
                                            if len(vv) != len(java_v[i]['Tiered']):
                                                logger.error(
                                                    f"url为:{java_url},字段PD中GoodsId:{good_id},列表Tiered,php和Java返回的结果列表长度不一致")
                                                break
                                            else:
                                                for tiered_item in range(len(vv)):  # java_v[i][Tiered][tiered_item]
                                                    if len(vv[tiered_item]) != len(java_v[i]['Tiered'][tiered_item]):
                                                        logger.error(
                                                            f"url为:{java_url},字段PD中GoodsId:{good_id},列表Tiered,php和Java返回的结果列表长度不一致")
                                                        continue
                                                    for tiered_str in range(len(vv[
                                                                                    tiered_item])):  # java_v[i][Tiered][tiered_item][tiered_n]
                                                        if type(vv[tiered_item][tiered_str]) != str:
                                                            vv[tiered_item][tiered_str] = str(vv[tiered_item][
                                                                                                  tiered_str])  # 把Tiered列表里面所有的值 全部转换成字符串后进行对比
                                                        if type(java_v[i]['Tiered'][tiered_item][tiered_str]) != str:
                                                            java_v[i]['Tiered'][tiered_item][tiered_str] = str(
                                                                java_v[i]['Tiered'][tiered_item][tiered_str])
                                                    php_tieded = sorted(vv[tiered_item])
                                                    java_tieded = sorted(java_v[i]['Tiered'][tiered_item])
                                                    for tiered_n in range(len(php_tieded)):
                                                        if php_tieded[tiered_n] != java_tieded[tiered_n]:
                                                            logger.error(
                                                                f"url为:{java_url},字段PD中GoodsId:{good_id},列表Tiered返回的结果不一致,php返回的结果:{php_tieded[tiered_n]},Java返回的结果:{java_tieded[tiered_n]}")
                                        elif kk == 'image_list':
                                            if len(vv) != len(java_v[i]['image_list']):
                                                logger.error(
                                                    f"url为:{java_url},字段PD中GoodsId:{good_id},列表image_list,php和Java返回的结果列表长度不一致")
                                                break
                                            else:
                                                for ima_item in range(len(vv)):
                                                    for ima_k, ima_v in vv[ima_item].items():
                                                        if ima_v != java_v[i]['image_list'][ima_item][ima_k]:
                                                            logger.error(
                                                                f"url为:{java_url},字段PD中GoodsId: {good_id},列表:image_list中字段{ima_k},返回的内容不一致,php返回结果:{ima_v},Java返回结果:{java_v[i]['image_list'][ima_item][ima_k]}")
                                                            continue
                                        elif kk == 'activity_discount':
                                            if vv == "":
                                                pass
                                                # if java_v[i][kk] != None:
                                                #     logger.error(f"url为:{java_url},PD字段GoodsId：{good_id}中,php返回的activity_discount为空，Java返回的结果为:{java_v[i][kk]}")
                                            else:
                                                for active_k, active_v in vv.items():
                                                    if active_k == 'discount_tiered':
                                                        if len(vv[active_k]) != len(java_v[i][kk][active_k]):
                                                            logger.error(
                                                                f"url:{java_url},字段PD中GoodsId:{good_id},字典{kk}中列表discount_tiered,php和Java返回的结果列表长度不一致")
                                                            continue
                                                        for active_n in range(len(vv[active_k])):
                                                            if len(vv[active_k][active_n]) != len(
                                                                    java_v[i][kk][active_k][active_n]):
                                                                logger.error(
                                                                    f"url:{java_url},字段PD中GoodsId:{good_id},字典{kk}中列表discount_tiered明细中,php和Java返回的结果列表长度不一致")
                                                                continue
                                                            for active_str in range(len(vv[active_k][active_n])):
                                                                if type(vv[active_k][active_n][active_str]) in [int,
                                                                                                                float]:
                                                                    vv[active_k][active_n][active_str] = str(
                                                                        vv[active_k][active_n][active_str])
                                                                if '.' in vv[active_k][active_n][
                                                                    active_str]:  # php最后一位小数如果是0，需要移除掉
                                                                    vv[active_k][active_n][active_str] = \
                                                                    vv[active_k][active_n][active_str].rstrip('0')
                                                                if type(java_v[i][kk][active_k][active_n][
                                                                            active_str]) in [int, float]:
                                                                    java_v[i][kk][active_k][active_n][active_str] = str(
                                                                        java_v[i][kk][active_k][active_n][active_str])
                                                            php_active = sorted(vv[active_k][active_n])
                                                            java_active = sorted(java_v[i][kk][active_k][active_n])
                                                            for active_item in range(len(php_active)):
                                                                if php_active[active_item] != java_active[active_item]:
                                                                    logger.error(
                                                                        f"url为:{java_url},字段PD中GoodsId:{good_id},字典activity_discount中列表discount_tiered返回的结果明细不一致,php返回的结果:{php_active},Java返回的结果:{java_active}")
                                                                    continue
                                                    else:
                                                        if type(active_v) in [int, float]:
                                                            active_v = str(active_v)
                                                        if type(java_v[i][kk][active_k]) in [int, float]:
                                                            java_v[i][kk][active_k] = str(java_v[i][kk][active_k])
                                                        if '.' in active_v:
                                                            active_v = active_v.rstrip('0')
                                                        if active_v != java_v[i][kk][active_k]:
                                                            logger.error(
                                                                f"url为:{java_url},字段{k}中GoodsId：{good_id},字典{kk}中{active_k}返回结果不一致,php返回结果:{active_v},Java返回结果:{java_v[i][kk][active_k]}")
                                        elif kk == 'activity_freight':
                                            if vv == "":
                                                pass
                                                # if java_v[i][kk] != None:
                                                #     logger.error(f"url为:{java_url},PD字段GoodsId：{good_id}中,php返回的activity_freight为空，Java返回的结果为:{java_v[i][kk]}")
                                            else:
                                                if vv != java_v[i][kk]:
                                                    logger.error(
                                                        f"url为:{java_url},字段PD中GoodsId: {good_id},字段:{kk},返回的内容不一致,php返回结果:{vv},Java返回结果:{java_v[i][kk]}")
                                        elif kk == 'warehouse_info':
                                            if len(vv) != len(java_v[i]['warehouse_info']):
                                                logger.error(
                                                    f"url为:{java_url},字段PD中GoodsId:{good_id},列表warehouse_info,php和Java返回的结果列表长度不一致")
                                                break
                                            else:
                                                for ware_item in range(len(vv)):
                                                    for ware_k, ware_v in vv[ware_item].items():
                                                        if type(ware_v) in [int, float]:
                                                            ware_v = str(ware_v)
                                                        if type(java_v[i]['warehouse_info'][ware_item][ware_k]) in [int,
                                                                                                                    float]:
                                                            java_v[i]['warehouse_info'][ware_item][ware_k] = str(
                                                                java_v[i]['warehouse_info'][ware_item][ware_k])
                                                        if ware_v != java_v[i]['warehouse_info'][ware_item][ware_k]:
                                                            logger.error(
                                                                f"url为:{java_url},字段PD中GoodsId: {good_id},列表:warehouse_info中字段{ware_k},返回的内容不一致,php返回结果:{ware_v},Java返回结果:{java_v[i]['warehouse_info'][ware_item][ware_k]}")
                                                            continue
                                        else:
                                            if type(vv) in [int, float]:
                                                vv = str(vv)
                                            if type(java_v[i][kk]) in [int, float]:
                                                java_v[i][kk] = str(java_v[i][kk])
                                            if vv != java_v[i][kk]:
                                                logger.error(
                                                    f"url为:{java_url},字段PD中GoodsId: {good_id},字段:{kk},返回的内容不一致,php返回结果:{vv},Java返回结果:{java_v[i][kk]}")
                                    except Exception as e:
                                        logger.error(f"url:{java_url},接口返回结果对比出错{e},字段PD中GoodsId: {good_id},字段:{kk}")
                                    break  # 条件满足跳出内层循环，继续外层循环
                        except Exception as e:  # 捕获比对异常，出现这个异常的原因可能是Java接口返回的结果中没有找到goodsid
                            logger.error(f"url为:{java_url},PD字段GoodsId：{good_id},字段:{kk},错误信息:{e}")
                            break
            elif k == 'PB':
                for php_item_dict in php_v:
                    brand_id = php_item_dict['brand_id']
                    for pdk, pdv in php_item_dict.items():
                        try:
                            for i in range(len(php_v) + 1):
                                if isinstance(java_v[i]['brand_id'], str):
                                    java_v[i]['brand_id'] = int(java_v[i]['brand_id'])
                                if brand_id == java_v[i]['brand_id']:
                                    try:
                                        if type(pdv) in [int, float]:
                                            pdv = str(pdv)
                                        if type(java_v[i][pdk]) in [int, float]:
                                            java_v[i][pdk] = str(java_v[i][pdk])
                                        if pdv != java_v[i][pdk]:
                                            logger.error(
                                                f"url为 {java_url},字段{k}中brand_id: {brand_id},字段:{pdk}返回的内容不一致,php返回结果:{pdv},Java返回结果:{java_v[i][pdk]}")
                                    except Exception as e:
                                        logger.error(f"url:{java_url},Java获取值出错,字段{k}中brand_id: {brand_id},字段:{pdk}")
                                    break
                        except IndexError as e:
                            logger.error(f"url为 {java_url},java接口返回的结果中PB字段没有找到brand_id：{brand_id}")
                            break
            elif k == 'mapping_goods':
                if php_v != java_v:
                    logger.error(f'url为 {java_url},php的值为:{php_v},Java的值为:{java_v}')
            else:
                logger.error(f"url为 {java_url},返回结果中，未做处理的新列表:{k}")
                try:
                    if php_v != java_v:
                        logger.error(f'url为 {java_url},php的值为:{php_v},Java的值为:{java_v}')
                except Exception as e:
                    logger.error(f"返回结果对比异常{e},url为 {java_url},k值为:{k},php返回的结果为:{php_v},Java返回的结果为:{java_v}")
        else:
            if k == 'has_page':
                if v == 0 and java_dict[k] is None:
                    pass
                elif php_dict[k] != java_dict[k]:
                    logger.error(
                        f"java接口返回的值不一致,url为:{java_url}, key值为{k},php返回的内容为:{v}{type(v)} java返回的字段内容为:{java_dict[k]}{type(java_dict[k])}")
            else:
                if php_dict[k] != java_dict[k]:  # 对比两个接口返回的字段值是否一致
                    logger.error(
                        f"java接口返回的值不一致,url为:{java_url}, key值为{k},php返回的内容为:{v}{type(v)} java返回的字段内容为:{java_dict[k]}{type(java_dict[k])}")


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


def read_sql_zy():
    """读取数据库数据拿自营库存"""
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
        sql = " SELECT  DISTINCT keyword  FROM  ecs_search_log_item   WHERE  keyword != '' "
        cur.execute(sql)
        list_key = cur.fetchall()
        return list_key
    except Exception as e:
        logger.error(f"读取数据库库存id出错{e}")
        raise e


# k_weord = read_sql_zy()
k_word = read_data(r'E:\HuaQiu_API\testdatas\data.xlsx')
with ThreadPoolExecutor(max_workers=10) as tp:
    tp.map(request_run, k_word)


