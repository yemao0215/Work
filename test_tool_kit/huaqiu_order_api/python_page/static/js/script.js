document.querySelectorAll('input[type=checkbox]').forEach(function(checkbox) {
  			checkbox.addEventListener('change', function() {
    			if (this.checked) {
      				document.getElementById('myField').value += this.value + ',';
    			} else {
      			var values = document.getElementById('myField').value.split(',');
      			values.splice(values.indexOf(this.value), 1);
      			document.getElementById('myField').value = values.join(',');
    			}
 			 });
});
document.querySelectorAll('input[type=checkbox]').forEach(function(checkbox) {
  			checkbox.addEventListener('change', function() {
    			if (this.checked) {
      				document.getElementById('myField1').value += this.value + ',';
    			} else {
      			var values = document.getElementById('myField1').value.split(',');
      			values.splice(values.indexOf(this.value), 1);
      			document.getElementById('myField1').value = values.join(',');
    			}
 			 });
});
document.querySelectorAll('input[type=checkbox]').forEach(function(checkbox) {
  			checkbox.addEventListener('change', function() {
    			if (this.checked) {
      				document.getElementById('myField2').value += this.value + ',';
    			} else {
      			var values = document.getElementById('myField2').value.split(',');
      			values.splice(values.indexOf(this.value), 1);
      			document.getElementById('myField2').value = values.join(',');
    			}
 			 });
});
// 获取当前日期
const today = new Date();

// 将日期格式化为 YYYY-MM-DD（input type="date` 的默认格式）
const formattedDate = today.toISOString().slice(0, 10);
// 将当前日期设置为 input 标签的值
document.getElementById('TagDay').value = formattedDate;
document.getElementById('InventoryTagDay').value = formattedDate;

// 解码工具js
let imageData;
document.getElementById('fileInput').addEventListener('change', function(event) {
            const file = event.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    const img = new Image();
                    img.src = e.target.result;
                    img.onload = function() {
                        const canvas = document.createElement('canvas');
                        const ctx = canvas.getContext('2d');
                        canvas.width = img.width;
                        canvas.height = img.height;
                        ctx.drawImage(img, 0, 0, img.width, img.height);
                        imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
                    };
                };
                reader.readAsDataURL(file);
            }
});
 document.getElementById('decodeButton').addEventListener('click', function() {
            if (imageData) {
                const code = jsQR(imageData.data, imageData.width, imageData.height);
                if (code) {
                	decodedData = code.data;
                    document.getElementById('result').textContent = '解码结果: ' + code.data;
                    document.getElementById('hint').style.display = 'block'; // Show the hint
                    document.getElementById('result').style.userSelect = 'text';
                    document.getElementById('result').style.cursor = 'text';


                } else {
                    document.getElementById('result').textContent = '解码结果: ' + '解码失败或文件不为二维码文件！！！';
                    document.getElementById('result').style.color = 'red'; // 设置字体颜色为红色
                    decodedData = '';
                }
            } else {
                document.getElementById('result').textContent = '请选择文件！！！';
                document.getElementById('result').style.color = 'red'; // 设置字体颜色为红色
                decodedData = '';
            }
});
document.getElementById('result').addEventListener('click', function() {
			if (decodedData) {
				const textarea = document.createElement('textarea');
				textarea.value = decodedData;
				document.body.appendChild(textarea);
				textarea.select();
				document.execCommand('copy');
				document.body.removeChild(textarea);
				alert('结果复制到剪贴板! 😊😊😊😊😊😊');
			}

// <!--          	if (decodedData) {-->
// <!--				try {-->
// <!--					await navigator.clipboard.writeText(decodedData);-->
// <!--					// Show the success message for a short duration-->
// <!--					const copySuccessElement = document.getElementById('copySuccess');-->
// <!--					copySuccessElement.style.display = 'block';-->
// <!--					setTimeout(() => copySuccessElement.style.display = 'none', 2000);-->
// <!--				} catch (err) {-->
// <!--					console.error('Failed to copy text: ', err);-->
// <!--				}-->
// <!--        	}-->
});
 // 对接口获取时间戳
 // 获取时间戳的函数
// <!--		function updateTimestamp() {-->
//<!--                    fetch('/timestamp_real_time')-->
//<!--                        .then(response => response.json())-->
//<!--                        .then(data => {-->
//<!--                            document.getElementById('timestamp').textContent = data.timestamp;-->
//<!--                        });-->
//<!--                }-->

//<!--                // 初始加载时立即更新-->
//<!--                updateTimestamp();-->
//<!--                // 每隔500毫秒更新一次-->
//<!--                setInterval(updateTimestamp, 500);-->
// JavaScript代码获取时间戳
// 等待DOM加载完成
document.addEventListener('DOMContentLoaded', () => {
// 更新时间戳的函数
        function updateTime() {
            const timeDisplay = document.getElementById('timestamp');
            console.log('获取到的元素:', timestamp); // 应为HTMLLabelElement对象
            console.log('生成的时间戳:', Date.now()); // 应输出13位数字
            const currentTimeStamp = Math.floor(Date.now() / 1000); // 获取当前时间戳且将13位毫秒级时间戳转为10位秒级
            timeDisplay.textContent = "当前时间戳: " + currentTimeStamp;
        }
        async function handleCopy(event) {
			event.preventDefault();
			const timestampText = document.getElementById("timestamp").textContent
				.split(": ")[1]  // 更安全的切割方式
				.trim();
			if (!timestampText) {
				alert("时间戳尚未加载！");
				return;
			}
			// 检查 Clipboard API 是否可用
        	if (navigator.clipboard) {
        		try {
					await navigator.clipboard.writeText(timestampText);
					console.log("Clipboard API 成功！");
					showFeedback();
            	} catch (err) {
					console.error("Clipboard API 错误:", err);
					alert("无法使用 Clipboard API，请手动复制。");
            	}
        	}  else {
				// 如果 Clipboard API 不可用，使用传统的复制方法
				const tempInput = document.createElement("input");
				tempInput.value = timestampText;
				tempInput.style.position = 'fixed';  // 防止页面滚动
				document.body.appendChild(tempInput);
				tempInput.select();
				try {
					const successful = document.execCommand("copy");
					if (successful) {
						showFeedback();
					} else {
						alert("复制失败，请手动选择文本复制：" + timestampText);
					}
				} catch (err) {
				     alert("复制失败，请手动选择文本复制：" + timestampText);
            	}
            	document.body.removeChild(tempInput);
            }
		}
        // 显示复制成功的反馈
        function showFeedback() {
            const copyStatus = document.getElementById("copyStatus");
            copyStatus.style.display = "inline";
            setTimeout(() => {
                copyStatus.style.display = "none";
            }, 1500);
        }
        // 初始加载时立即更新
		updateTime();
        // 每秒更新一次
        setInterval(updateTime, 1000);
        // 绑定点击事件
        const copyButton = document.getElementById("copyButton");
        copyButton.addEventListener("click", handleCopy);

});

// <!--        // 初始加载时立即更新-->
// <!--        updateTime();-->
// <!--        // 每隔500毫秒更新一次-->
// <!--        setInterval(updateTime, 500);-->
//document.addEventListener('DOMContentLoaded', function() {
//         const forms = document.querySelectorAll('form');
//         forms.forEach(form => {
//                form.addEventListener('submit', async function(e) {
//                    e.preventDefault();
//                    showLoading();
//                    try {
//                        const formData = new FormData(this);
//                        const response = await fetch(this.action, {
//                            method: this.method,
//                            body: formData
//                        });
//                        // 解析返回的 JSON 响应
//                        const responseData = await response.json();
//                        if (response.ok) {
//                             console.log('成功', responseData);  // 打印返回的 JSON 数据
//                        } else {
//                            throw new Error('失败');
//                        }
//                    } catch (error) {
//                        alert(error.message);
//                    } finally {
//                        hideLoading();
//                    }
//                });
//            });
//        });
//
//function showLoading() {
//            document.getElementById('loadingOverlay').style.display = 'flex';
//        }
//
//function hideLoading() {
//            document.getElementById('loadingOverlay').style.display = 'none';
//        }

// 等待 DOM 加载完成
document.addEventListener('DOMContentLoaded', function() {
    const input = document.getElementById('BuildProject');
    const form = document.getElementById('myForm');

    // 失焦校验
    input.addEventListener('blur', function() {
        validateProject(this);
    });

    // 输入时清除错误
    input.addEventListener('input', function() {
        clearError(this);
    });

    // 表单提交校验
    form.addEventListener('submit', function(event) {
        validateForm(event);
    });
});

// 校验函数（无需暴露到全局）
function validateProject(input) {
    const datalist = document.getElementById('JenkinsProjectList');
    const options = Array.from(datalist.querySelectorAll('option')).map(opt => opt.value);
    const errorSpan = document.getElementById('projectError');

    if (input.value && !options.includes(input.value)) {
        errorSpan.textContent = '⚠️ 请从下拉列表中选择有效的项目名称！';
        input.style.borderColor = 'red';
        return false;
    } else {
        errorSpan.textContent = '';
        input.style.borderColor = '#ccc';
        return true;
    }
}

function clearError(input) {
    const errorSpan = document.getElementById('projectError');
    if (errorSpan.textContent) {
        errorSpan.textContent = '';
        input.style.borderColor = '#ccc';
    }
}

function validateForm(event) {
    const input = document.getElementById('BuildProject');
    const isValid = validateProject(input);

    if (!isValid) {
        event.preventDefault();
        input.focus();
        return false;
    }

    if (!input.value.trim()) {
        document.getElementById('projectError').textContent = '⚠️ 请选择执行项目！';
        input.style.borderColor = 'red';
        input.focus();
        event.preventDefault();
        return false;
    }

    return true;
}