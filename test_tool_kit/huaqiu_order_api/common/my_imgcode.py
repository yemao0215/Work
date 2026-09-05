import base64
import os
import re

from PIL import Image
import cv2
import numpy as np
import pytesseract
import requests
from pygments.formatters import img

from huaqiu_order_api.common.my_path import img_code_dir, img_processed_captcha_dir


class MyIMGCode:
    # 图片验证码
    def __init__(self, img_base64_code):
        self.img_url = img_code_dir
        self.img_base64_code = img_base64_code
        self.rss = requests.session()
    def get_img_base64_code_decode(self):
        # base64的图片编码转成图片
        # 解码Base64
        image_data = base64.b64decode(self.img_base64_code)

        # 将解码后的数据保存为图片
        with open(img_code_dir, "wb") as file:
            file.write(image_data)
        print("图片已保存为 'output_image.png'")
        return self

    def get_img_code(self):
        # 获取图片验证码
        # # 配置tesseract路径（根据安装位置调整）
        print("文件存在:", os.path.exists(img_code_dir))
        print("文件大小:", os.path.getsize(img_code_dir), "字节")
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        print("可读权限:", os.access(img_code_dir, os.R_OK))
        pil_img = Image.open(img_code_dir)
        img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
        print(img)
        # 转为灰度图像
        # gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        print(f"灰度图像最小值: {gray.min()}, 最大值: {gray.max()}")
        print(f"灰度图像: {gray.shape}")  # 打印灰度图像的尺寸

        # 使用阈值进行二值化处理
        _, binary_img = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY)
        # binary_img = cv2.adaptiveThreshold(
        #     gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        #     cv2.THRESH_BINARY, 11, 2
        # )
        print(f"二值化后的图像: {binary_img.shape}")  # 打印二值化图像的尺寸
        # 使用开运算去除噪点
        processed_img = cv2.fastNlMeansDenoising(binary_img, None, 30, 7, 21)
        # # 显示处理后的图像（用于调试）
        # cv2.imshow('Processed Image', processed_img)
        #
        # 保存处理后的图像（用于调试）
        success = cv2.imwrite(img_processed_captcha_dir, processed_img)
        if success:
            print(f"图像保存成功：{img_processed_captcha_dir}")
        else:
            print(f"图像保存失败：{img_processed_captcha_dir}")
        # 设置 Tesseract 的配置
        custom_config = r'--oem 3 --psm 6'  # OEM 3 表示使用默认OCR引擎，PSM 6 表示自动检测文本块

        # 使用 pytesseract 识别文本
        scaled_image = cv2.resize(processed_img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
        captcha_text = pytesseract.image_to_string(scaled_image, config=custom_config)

        #
        # 输出识别结果
        print("识别的验证码是：", captcha_text.replace(" ", "").replace('"', "").replace("=", "").strip())
        # 只保留数字、运算符和小数点的有效字符
        cleaned_text = re.sub(r'[^0-9\+\-\*/\.\(\)]', '', captcha_text)
        # 解析文本并计算数学表达式
        if re.match(r'^[\d\+\-\*/\.\(\)]+$', cleaned_text):
            try:
                result = eval(cleaned_text)  # 使用eval计算表达式
                print(f"计算结果: {result}")
                return result
            except Exception as e:
                print(f"计算错误: {e}")
                return None
        else:
            print("无效的数学表达式")
            return None
    def mian_img_base64_code(self):
        self.get_img_base64_code_decode()
        code = self.get_img_code()
        return code



if __name__ == '__main__':
    img_base64_code = "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"
    MyIMGCode(img_base64_code=img_base64_code).get_img_code()