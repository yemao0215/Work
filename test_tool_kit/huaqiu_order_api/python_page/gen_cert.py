from OpenSSL import crypto
import os

# 生成RSA私钥
key = crypto.PKey()
key.generate_key(crypto.TYPE_RSA, 4096)

# 构造证书信息
cert = crypto.X509()
subj = cert.get_subject()
subj.C = "CN"
subj.ST = "Guangdong"
subj.L = "Shenzhen"
subj.O = "Test"
subj.OU = "Dev"
subj.CN = "www.yemaotest.com"

cert.set_serial_number(1000)
cert.gmtime_adj_notBefore(0)
cert.gmtime_adj_notAfter(365 * 24 * 60 * 60)  # 有效期一年
cert.set_issuer(subj)
cert.set_pubkey(key)
# 修复点：去掉b，直接传字符串 sha256
cert.sign(key, "sha256")

# 写入私钥
with open("server.key", "wb") as f:
    f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, key))

# 写入证书
with open("server.crt", "wb") as f:
    f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))

print("证书生成完成，当前目录生成 server.crt、server.key")