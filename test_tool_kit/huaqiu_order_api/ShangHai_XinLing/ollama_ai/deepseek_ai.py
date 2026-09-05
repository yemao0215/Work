
import requests
import json


class OllamaDeepSeekAi:
    def __init__(self, model_version, prompt, stream=False, options=None):
        """
        调用本地Ollama的DeepSeek模型

        参数:
        model_version: "deepseek-r1:8b" 或 "deepseek-r1:1.5b"
        prompt: 输入的提示文本
        stream: 是否使用流式响应
        options: 模型参数配置

        返回:
        完整的响应文本
        """

        self.model_version = model_version
        self.prompt = prompt
        self.stream = stream
        self.options = options

    def call_ollama_deepseek(self):

        # API端点
        url = "http://localhost:11434/api/generate"

        # 默认参数
        if self.options is None:
            self.options = {
                "temperature": 0.7,
                "max_tokens": 4096,
                "top_p": 0.9,
                "repeat_penalty": 1.1,
                "num_ctx": 8192  # 上下文长度
            }

        # 请求数据
        data = {
            "model": self.model_version,
            "prompt": self.prompt,
            "stream": self.stream,
            "options": self.options
        }

        # 发送请求
        response = requests.post(
            url,
            headers={"Content-Type": "application/json"},
            data=json.dumps(data))

        # 处理响应
        if response.status_code != 200:
            raise Exception(f"API错误: {response.status_code} - {response.text}")

        if self.stream:
            # 处理流式响应
            full_response = ""
            for line in response.iter_lines():
                if line:
                    decoded_line = json.loads(line.decode('utf-8'))
                    if 'response' in decoded_line:
                        print(decoded_line['response'], end='', flush=True)
                        full_response += decoded_line['response']
                    if decoded_line.get('done', False):
                        print("\n")
                        return full_response
        else:
            # 处理非流式响应
            result = response.json()
            return result.get('response', '')


# 使用示例
if __name__ == "__main__":
    # 选择模型版本
    model_version = "deepseek-r1:1.5b"  # 或 "deepseek-r1:1.5b"

    # 创建提示
    prompt = """
    你是一个AI助手，请帮我解决以下问题：

    问题：影石Insta360 Ace Pro 2和大疆Osmo Action 5 Pro差异以及推荐度。
    要求：用中文回答，内容简洁明了，适合初学者理解。
    """

    # 调用模型
    print(f"调用 {model_version} 模型...")
    response = OllamaDeepSeekAi(model_version, prompt, stream=True).call_ollama_deepseek()

    # 打印完整响应
    print("\n\n完整响应:")
    print(response)
    # 打印完整响应
    print("\n\n思考思路:")
    print(response.split("<think>")[1].split("</think>")[0])

    # 打印完整响应
    print("\n\n回答:")
    print(response.split("</think>")[1])

