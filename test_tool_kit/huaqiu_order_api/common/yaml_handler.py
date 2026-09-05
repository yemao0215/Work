import yaml

from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_path import yaml_file


def read_yaml(fpath):
    """fpath: yaml文件的路径"""
    with open(fpath, encoding='utf-8') as f:
        """读取yaml当中的数据"""
        data = yaml.safe_load(f)
        return data

def write_yaml(fpath, params):
    key = []
    with open(fpath, "r", encoding="utf-8") as f:
        data = yaml.load(f, Loader=yaml.FullLoader)
    for i in params:
        key.append(i)
        data[i] = params[i]
    with open(fpath, "w", encoding="utf-8") as f:
        yaml.dump(data, f)
    is_equal(fpath, params, key)

def is_equal(fpath, params, key):
    with open(fpath, "r", encoding="utf-8") as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
    for i in key:
        if params[i] != data[i]:
            logger.error('\033[91m'+str(params)+'写入yaml异常\033[00m')
            return
    logger.info(str(params)+'写入yaml成功')
def yaml_fields_hierarchy(fpath, params):
    level = 0
    with open(fpath, "r", encoding="utf-8") as f:
        data = yaml.load(f, Loader=yaml.FullLoader)
    for key in data:
        if key == params.keys().index(key):
            break
        data = data[next(iter(data))]
        level += 1
    print(data)
    return level

    # position = -1
    # for key in data:
    #     if key == params:
    #         position = data.keys().index(key)
    #         break
    # return position


# 获取yaml配置项
yaml_config = read_yaml(yaml_file)

if __name__ == '__main__':
    from huaqiu_order_api.common.my_path import log_file, account_yaml
    result = read_yaml(yaml_file)
    # print(result)
    # print(f"hose的值为:{result['url']}")
    # print(f"site的值为:{result['log']['file']}")
    # print({result['test_case1']['title1']})

    API_KEY = {
            "phone1": '13',
            "pwd1": "a123222222222222222456",
            "user1": "jf_1511322222222222222305"}
    params = {'aaaaPassPort': API_KEY}
    write_yaml(account_yaml, params)

