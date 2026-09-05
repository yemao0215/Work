var CryptoJS = require("crypto-js");

function encryptionPassword(serializeEnc, message) {
    // var text = JSON.stringify(message);
    /* 加密基础方法
    * @param message
    * @returns {string}
    */
    text = CryptoJS.enc.Base64.stringify(CryptoJS.enc.Utf8.parse(message)).toString();
    var key = CryptoJS.enc.Utf8.parse(serializeEnc.hash_key); // 为了避免补位，直接用16位的秘钥
    var iv = CryptoJS.enc.Utf8.parse(serializeEnc.hash_iv); // 16位初始向量
    var encrypted = CryptoJS.AES.encrypt(text, key, {
        iv: iv,
        mode: CryptoJS.mode.CBC,
        padding: CryptoJS.pad.ZeroPadding
    }).toString();
    return CryptoJS.enc.Base64.stringify(CryptoJS.enc.Utf8.parse(encrypted)).toString();
}
function encrypt(serialzed_enc_base64, message) {
    /* 加密
    * @param message
    * @returns {string}
    */
    // 解密window.transfer值获取hash_name、hash_key、hash_iv
    var serializeEnc = JSON.parse(CryptoJS.enc.Base64.parse(serialzed_enc_base64).toString(CryptoJS.enc.Utf8));
    var key = serializeEnc.hash_key;
    var iv = serializeEnc.hash_iv;
    // 生成加密明文并与hash_name拼接组成新得加密密码，并且返回
    var encrypt = serializeEnc.hash_name + encryptionPassword(serializeEnc, message);
    return encrypt;
}
function decryptionPassword(decryptserializeEnc, data) {
    /* 解密基础方法
    * @param message
    * @returns {string}
    */
    // 将message进行Base64编码
     var encrypted = CryptoJS.enc.Utf8.stringify(CryptoJS.enc.Base64.parse(data)).toString();
     var key = CryptoJS.enc.Utf8.parse(decryptserializeEnc.hash_key); // 为了避免补位，直接用16位的秘钥
     var iv = CryptoJS.enc.Utf8.parse(decryptserializeEnc.hash_iv); // 16位初始向量
     var decrypted = CryptoJS.AES.decrypt(encrypted, key, {
        iv: iv,
        mode: CryptoJS.mode.CBC,
        padding: CryptoJS.pad.ZeroPadding
    }).toString(CryptoJS.enc.Utf8);
    return CryptoJS.enc.Utf8.stringify(CryptoJS.enc.Base64.parse(decrypted)).toString();
}
function decrypt(serialzed_enc_base64, data) {
    // 解密window.transfer值获取hash_name、hash_key、hash_iv
    var decryptserializeEnc = JSON.parse(CryptoJS.enc.Base64.parse(serialzed_enc_base64).toString(CryptoJS.enc.Utf8));
    var data = data;
    // 使用 JavaScript 的正则表达式来匹配serializeEnc.hash_name并将其切割，得到需要解密的内容
    var pattern = new RegExp(decryptserializeEnc.hash_name + "(.*)");
    var match = data.match(pattern);
    if (match && match[1]) {
        let result = match[1];
        // 生成解密明文并且返回
        var password = decryptionPassword(decryptserializeEnc, result);
        return password;
        }
 }