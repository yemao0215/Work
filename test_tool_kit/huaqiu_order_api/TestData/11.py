import base64
import ddddocr

# ========== 修复1：解决 Pillow 高版本报错 ==========
try:
    from PIL import Image
    Image.ANTIALIAS = Image.Resampling.LANCZOS
except ImportError:
    pass

# ========== 修复2：自动补全 Base64 填充（解决 Incorrect padding） ==========
def safe_base64_decode(data):
    missing_padding = len(data) % 4
    if missing_padding:
        data += '=' * (4 - missing_padding)
    return base64.b64decode(data)

# 你的 Base64 图片字符串
img_base64 = "iVBORw0KGgoAAAANSUhEUgAAAHgAAAAkCAIAAADNSmkJAAACIUlEQVR4Xu3Zu01DQRCFYZfgiEqogRYcUgUBGRmlUAllmcFi8Mo+Z3d29ulra38N0Z37+gSWgN3x+LNmwuxOX7IaXA30x3V4eBWrBhoC90UfrQO0Np948u0a6wY9vwU9qQVdUAtWy7nz6wD9/PJZN3p66sN9//2aGl2InqV9vb+l5nLtsH/yzOUp/uDxbg+thcdiVmPgZZjVGHFD13FvFFr+nowp7bl8Gaa0RwqhG60t6NQPNcSCzoHrsGN2wuOxY3akHPpQaO2F1pzcdnXKsKMxNCOqI2dD4zYtRHfsAl0eWmvhrlAW+ozjFNpJDDmhxbdjVAytVXCzchYajhoxNG6YeRA9O57KoEtj4qxyEXTdt3PIg+jZ8TQQmolZWQgaD5u1KIsP0bPjaRQ0E0eVZdvQ2QV/86Bx45wTGtZ0nNCwFgYcs4PXLWkItF9ZSBAPn2PlmdB4xfL6Q7Pygpbu0ExsKwsJ4uFzrDwTut26JzQTZ5UlJogb1xnQhrVmQ8NyX+tu0EzsUdai0KnfjGB5HLR0tR4IjRvpwE6t66Bt67uHblHW2HpPf26ObgrxGdyl0NLPugM0KzsHrsPQntFzGdozHsEHhJYq63AuO2bHKdjFelvQUmgN5zKlMUKC0U8q7QGhQ8ya8uWY9dI3xHwpa9issO4APbTUm49r0B0XdKSK/2+kCtfZOrTcyFr63Vevs6Ctutz6bqAfoJP1P/SaCfML4S9zP1/PB74AAAAASUVORK5CYII="
# 初始化识别器
ocr = ddddocr.DdddOcr()

# 安全解码 + 识别
image_bytes = safe_base64_decode(img_base64)
result = ocr.classification(image_bytes)

print("✅ 验证码识别结果：", result)
