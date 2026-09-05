import datetime


class TimestampConvert:
    def __init__(self):
        pass
    def timestamp_real_time(self):
        current_time = datetime.datetime.now()
        timestamp = int(current_time.timestamp())
        return timestamp
    def timestamp_convert_time(self, timestamp):
        # 转换成时间格式
        timestamp = int(timestamp)
        # 将时间戳转换为 datetime 对象
        dt_object = datetime.datetime.fromtimestamp(timestamp)

        # 打印具体的时间
        print("具体时间为:", dt_object)

        # 如果需要格式化输出，可以使用 strftime()
        formatted_time = dt_object.strftime("%Y-%m-%d %H:%M:%S")
        print("格式化后的时间:", formatted_time)
        return formatted_time
    def time_convert_timestamp(self, time_str):
        # 转换为时间戳
        # 将日期字符串转换为 datetime 对象
        dt_object = datetime.datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")

        # 将 datetime 对象转换为时间戳（秒）
        timestamp = int(dt_object.timestamp())

        print("时间戳为:", timestamp)
        return timestamp



if __name__ == '__main__':
    time_str = '2023-07-05 12:34:56'
    timestamp_convert = TimestampConvert()
    timestamp_convert.time_convert_timestamp(time_str)


