from Crypto.Cipher import AES
import binascii


def navicat_decrypt(hex_cipher):
    key = b"libcckeylibcckey"
    iv = b"libcciv libcciv "
    raw = binascii.unhexlify(hex_cipher)
    aes = AES.new(key, AES.MODE_CBC, iv)
    raw_pwd = aes.decrypt(raw)

    # PKCS7填充移除逻辑（核心修复乱码）
    pad_len = raw_pwd[-1]
    raw_pwd = raw_pwd[:-pad_len]

    # 再清理多余空字节，转字符串
    return raw_pwd.rstrip(b"\x00").decode("utf-8")


# 填入你的密文
cipher_text = "502B4037DB2A25AE7012FBF8B5F0F99711BEE143ABD820A1206CE865DB399143"
pwd = navicat_decrypt(cipher_text)
print("明文密码：", pwd)