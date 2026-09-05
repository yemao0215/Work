// ==========================
// YAML 配置读取（Java 原生实现）
// ==========================
var loadYamlConfig = function() {
    try {
            // 🔥 直接读取 Python 传过来的路径（来自 my_math.py）
            var yamlPath = vars.get(encryptConfYaml_dir);
            log.info("✅ 从Python获取到YAML路径：" + yamlPath);
            var Paths = java.nio.file.Paths;
            var Files = java.nio.file.Files;
            var yamlContent = new String(Files.readAllBytes(Paths.get(yamlPath)), "UTF-8");

            // 简单解析 YAML 数组（不需要第三方库）
            var whiteList = [];
            var sensitiveKeys = [];
            var lines = yamlContent.split("\n");

            var section = "";
            for (var i = 0; i < lines.length; i++) {
                var line = lines[i].trim();
                if (!line || line.startsWith("#")) continue;

                if (line.startsWith("whiteList:")) {
                    section = "white";
                    continue;
                }
                if (line.startsWith("sensitiveKeys:")) {
                    section = "sensitive";
                    continue;
                }

                if (line.startsWith("- ")) {
                    var val = line.substring(2).trim();
                    if (section === "white") whiteList.push(val);
                    if (section === "sensitive") sensitiveKeys.push(val);
                }
            }

            return {
                whiteList: whiteList,
                sensitiveKeys: sensitiveKeys
            };
    } catch (e) {
        console.log("YAML 配置读取失败：" + e);
        return {
//            whiteList: ["id", "suc", "code", "msg", "type", "status", "createTime"],
//            sensitiveKeys: ["phone","mobile","name","address","invoice","idCard","wechat","qq"]
            whiteList: [],
            sensitiveKeys: []
        };
    }
};

// 全局加载一次配置
var config = loadYamlConfig();

const Obfuscator = {
    // 生成指定长度的随机字符串
    _generateRandomString: function (length) {
//        console.log(`[JS日志] 生成${length}位随机字符串`); // 新增日志
        const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
        let result = '';

        for (let i = 0; i < length; i++) {
            result += chars.charAt(Math.floor(Math.random() * chars.length));
        }
        return result;
    },
    // 旧代码
//    // 标准 Base64编码（处理中文等Unicode字符）
//    _encodeBase64: function (str) {
//        return btoa(unescape(encodeURIComponent(str)));
//    },
//    // 标准 Base64解码
//    _decodeBase64: function (str) {
//        return decodeURIComponent(escape(atob(str)));
//    },
    // 新代码
    // 标准 Base64编码（处理中文等Unicode字符）
    _encodeBase64: function (str) {
        try { return btoa(unescape(encodeURIComponent(str))); } catch(e){ return btoa(str); }
    },
    // 标准 Base64解码
    _decodeBase64: function (str) {
        try {
            return decodeURIComponent(escape(atob(str)));
        } catch (e) {
            return atob(str);
        }
    },
    // 统计尾部‘=’数量
    _countTrailingEquals:  function (str) {
        if (!str) return 0;  // 新增空值检查
        let count = 0;
        for (let i = str.length - 1; i >= 0; i--) {
            if (str[i] === '=') count++;
            else break;
        }
        return count;
    },
    // 加密
    encode: function (data) {
        // 1. 转JSON 中文默认转为\\uXXX(无需额外参数)
        let contentStr = typeof data === 'object' ? JSON.stringify(data): String(data);

        // 2.前插7位随机
        const rand1 = this._generateRandomString(7);
        const step2 = rand1 + contentStr;
        // 3.Base64
        const base64Full = this._encodeBase64(step2);
        // 4.计算取余（忽略=）
        const base64NoPadding = base64Full.replace(/=+$/,'');
        const remainder = base64NoPadding.length % 7;
        // 5.插入第二个7位数随机
        const rand2 = this._generateRandomString(7);
        return base64Full.slice(0, remainder) + rand2 + base64Full.slice(remainder);
    },
    // 解密
    decode: function (obfuscatedStr) {
        if (!obfuscatedStr) return null;  // 新增空值检查
        // 1.数尾巴
        const padCount = this._countTrailingEquals(obfuscatedStr);
        // 2.计算原长度
        const originalBase64Len = obfuscatedStr.length - 7;
        // 3.计算无padding长度
        const originalNoPadLen = originalBase64Len - padCount;
        // 4.反推插入点
        const remainder = originalNoPadLen % 7;
        // 5.还原Base64
        const base64Full = obfuscatedStr.slice(0, remainder) + obfuscatedStr.slice(remainder + 7);
        // 6.解码
        const step6 = this._decodeBase64(base64Full);
        const contentStr = step6.slice(7);
        // 7.还原类型（JSON.parse会自动\\uXXX转回中文)
        try{
           return JSON.parse(contentStr);
        } catch (e) {
           return !isNaN(contentStr) && contentStr.trim() !== '' ? Number(contentStr) : contentStr;
        }

    },
    // ===================== 【核心：智能判断 + 自动解密】 =====================
    // 🔥 判断字符串是否是你们的加密串
    _isEncryptedString: function (s) {
        if (typeof s !== 'string') return false;
        if (s.length < 20) return false;  // 加密串一定很长
        if (/^\s+$/.test(s)) return false;
        if (s.indexOf("{") !== -1) return false; // 排除JSON
        if (s.indexOf(" ") !== -1) return false;
        return true; // 符合条件 → 是加密串
    },
    // 新增：递归自动解密JSON中的所有加密字段 ---旧方法
//    autoDecodeJSON: function (data) {
//        // 递归终止条件：非对象/数组直接尝试解密
//        if (typeof data !== 'object' || data === null) {
//            // 仅对字符串尝试解密，其他类型直接返回
//            if (typeof data === 'string') {
//                return this.decode(data);
//            }
//            return data;
//        }
      autoDecodeJSON: function (data) {
            if (typeof data !== 'object' || data === null) {
                if (this._isEncryptedString(data)) {
                    try {
                        return this.decode(data);
                    } catch (e) {
                        return data;
                    }
                }
                return data;
        }

        // 处理数组：遍历每个元素递归解密
        if (Array.isArray(data)) {
            return data.map(item => this.autoDecodeJSON(item));
        }

        // 处理对象：遍历每个字段值递归解密
        const decodedObj = {};
        for (const key in data) {
            if (data.hasOwnProperty(key)) {
                decodedObj[key] = this.autoDecodeJSON(data[key]);
            }
        }
        return decodedObj;
    },
      // ===================== 【核心：智能判断 + 自动加密】 =====================
     // 🔥 判断字符串是否是你们的加密串
      autoEncryptJSONold: function (data) {
        var whiteList = config.whiteList;
        var sensitiveKeys = config.sensitiveKeys;

        var isSensitive = function (key) {
            if (!key) return false;
            key = String(key).trim().toLowerCase();
//            key = String(key).toLowerCase();
            for (var i = 0; i < sensitiveKeys.length; i++) {
                  keyword = sensitiveKeys[i].toLowerCase().trim();
//                if (key.indexOf(sensitiveKeys[i].toLowerCase()) !== -1) return true;
                  // 改为 【完全相等】 才加密，不再用 indexOf 模糊匹配
                  if (key === keyword) return true;
            }
            return false;
        };

        if (typeof data !== 'object' || data === null) {
            return data;
        }

        if (Array.isArray(data)) {
            var arr = [];
            for (var i = 0; i < data.length; i++) {
                arr.push(this.autoEncryptJSON(data[i]));
            }
            return arr;
        }

        var encryptedObj = {};
        for (var key in data) {
            if (data.hasOwnProperty(key)) {
                var value = data[key];
                if (whiteList.indexOf(key) !== -1) {
                    encryptedObj[key] = value;
                } else if (isSensitive(key) && typeof value === 'string' && value) {
                    encryptedObj[key] = this.encode(value);
                } else {
                    encryptedObj[key] = this.autoEncryptJSON(value);
                }
            }
        }
        return encryptedObj;
    },
    // ===================== ✅ 自动加密（接收外部配置） =====================
    autoEncryptJSON: function (data, whiteList, sensitiveKeys) {
        const isSensitive = (key) => {
            if (!key) return false;
            const k = key.toLowerCase().trim();
            return sensitiveKeys.some(s => s.toLowerCase().trim() === k);
        };

        if (typeof data !== 'object' || data === null) return data;
        if (Array.isArray(data)) return data.map(item => this.autoEncryptJSON(item, whiteList, sensitiveKeys));

        const encryptedObj = {};
        for (const key in data) {
            if (data.hasOwnProperty(key)) {
                const value = data[key];
                if (whiteList.includes(key)) {
                    encryptedObj[key] = value;
                } else if (isSensitive(key) && typeof value === 'string' && value) {
                    encryptedObj[key] = this.encode(value);
                } else {
                    encryptedObj[key] = this.autoEncryptJSON(value, whiteList, sensitiveKeys);
                }
            }
        }
        return encryptedObj;
    }

};
// str是否为json格式
function isJson(str) {
    if (typeof str !== 'string') return false;
    try {
        var obj = JSON.parse(str);
        return typeof obj === 'object' && obj !== null;
    } catch (e) {
        return false;
    }
}
// 新增：全局加密函数，手动绑定this到Obfuscator
function encryptData(data) {
    return Obfuscator.encode.call(Obfuscator, data);
};

// 新增：全局解密函数，绑定this
function decodeData(encryptedStr) {
    return Obfuscator.decode.call(Obfuscator, encryptedStr);
};

// 新增：全局自动解密JSON函数
function autoDecodeData(jsonData) {
        if (isJson(jsonData)) {
        log.info("✅ 判定为 JSON 字符串，自动解析");
        jsonData = JSON.parse(jsonData);
    }
    return Obfuscator.autoDecodeJSON.call(Obfuscator, jsonData);
};

// 新增：全局自动加密JSON函数
function autoEncryptData(jsonData, whiteList, sensitiveKeys) {
    if (isJson(jsonData)) jsonData = JSON.parse(jsonData);
    return Obfuscator.autoEncryptJSON.call(Obfuscator, jsonData, whiteList, sensitiveKeys);
}