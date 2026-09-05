/**
 * 使用 RSA 公钥加密密码/消息
 * @param {string} publicKey PEM 格式的公钥字符串
 * @param {string} message 待加密的明文（如密码）
 * @returns {string} Base64 编码的密文
 */
const JSEncrypt = require('jsencrypt')
function encryptWithPublicKey(publicKey, message) {
    // 创建 JSEncrypt 实例（库加载后，JSEncrypt 是一个全局变量，可以直接使用）
    var crypt = new JSEncrypt();

    // 设置公钥
    crypt.setPublicKey(publicKey);

    // 执行加密（结果已是 Base64 字符串）
    var encrypted = crypt.encrypt(message);

    return encrypted;
}