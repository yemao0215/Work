import requests


class OllamaLlavaAi:
    def __init__(self, img_base64_code):
        self.rss = requests.Session()
        self.img_base64_code = img_base64_code

    def recognize_captcha(self):
        # 构造API请求
        url = "http://localhost:11434/api/generate"
        payload = {
            "model": "llava",
            "prompt": "请严格识别图片中的数字加减乘除计算等式（纯文本）且其中只存在一个运算形式，不要添加任何描述, 忽略颜色和背景干扰，直接返回纯文本验证码（不要换行/标点）,图片里面等式是：",
            "images": [self.img_base64_code],
            "stream": False
        }

        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            return response.json()["response"].strip()
        except Exception as e:
            print(f"识别失败: {e}")
            return ""
if __name__ == '__main__':
    img_base64_code = "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"
    a = OllamaLlavaAi(img_base64_code).recognize_captcha()
    print(a)


