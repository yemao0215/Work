import glob
import os

from flask import render_template

from huaqiu_order_api.common.my_path import log_file



def get_latest_log():
        log_files = glob.glob(os.path.join(log_file, '*.log'))
        # 对日志文件按照修改时间进行排序
        log_files.sort(key=os.path.getmtime, reverse=True)
        # 获取最新的日志文件
        latest_log_file = log_files[0] if log_files else None
        if latest_log_file:
            with open(latest_log_file, 'rb') as f:
                log_content = f.readlines()
                # print(type(log_content))
                total_lines = len(log_content)
                for i, content in enumerate(log_content):
                    log_content[i] = content.decode('utf-8', 'ignore')
                return render_template('logs.html', data=log_content, encoding='utf-8')
        else:
                return '没有找到日志文件'