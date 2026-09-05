import datetime
import sys
from loguru import logger as log
from huaqiu_order_api.common.my_path import log_file


class MyLogger:
    def __init__(self):
        data = datetime.datetime.now().strftime('%Y-%m-%d')
        self.logger = log
        # 清空所有设置
        self.logger.remove()
        # 添加控制台输出的格式,sys.stdout为输出到屏幕;关于这些配置还需要自定义请移步官网查看相关参数说明
        self.logger.add(sys.stdout,
                        format="<blue>{time:YYYYMMDD HH:mm:ss}</blue> | "  # 颜色>时间
                               # "{process.name} | "  # 进程名
                               # "{thread.name} | "  # 进程名
                               "<cyan>{module}</cyan>.<cyan>{function}</cyan>"  # 模块名.方法名
                               ":<green>{line}</green> | "  # 行号
                               "<level>{level}</level>: "  # 等级
                               "<level>{message}</level>",  # 日志内容
                        )
        # 输出到文件的格式,注释下面的add',则关闭日志写入
        self.logger.add(r'%s\%s.log' % (log_file, data),
                        level='DEBUG',
                        format='{time:YYYYMMDD HH:mm:ss} - '  # 时间
                               # "{process.name} | "  # 进程名
                               # "{thread.name} | "   # 进程名
                               '{module}.{function}:{line} - {level} -{message}',  # 模块名.方法名:行号
                        encoding='utf-8',
                        retention='10 days',  # 设置历史保留时长
                        backtrace=True,  # 回溯
                        diagnose=True,  # 诊断
                        enqueue=True  # 异步写入
                        )

    def get_logger(self):
        return self.logger


logger = MyLogger().get_logger()


def ss():
    logger.info(1111111)
    logger.debug(2222222)
    logger.warning(333333333333)
    logger.error(444444444444444)
    logger.critical(55555555555)


if __name__ == '__main__':
    ss()

