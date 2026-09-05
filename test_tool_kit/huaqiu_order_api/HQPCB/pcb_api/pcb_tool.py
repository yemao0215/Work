import yaml

from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_path import pcb_config_yaml_dir


class PcbTools:

    def write_yaml(self, params):
        key = []
        with open(pcb_config_yaml_dir, "r", encoding="utf-8") as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
        for i in params:
            key.append(i)
            data[i] = params[i]
        with open(pcb_config_yaml_dir, "w", encoding="utf-8") as f:
            yaml.dump(data, f)
        PcbTools().is_equal(params, key)

    def is_equal(self, params, key):
        with open(pcb_config_yaml_dir, "r", encoding="utf-8") as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
        for i in key:
            if params[i] != data[i]:
                logger.error('\033[91m'+str(params)+'写入yaml异常\033[00m')
                return
        logger.info(str(params)+'写入yaml成功')

