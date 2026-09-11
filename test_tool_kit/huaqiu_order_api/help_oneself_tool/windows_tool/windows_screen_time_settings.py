# -*- coding: utf-8 -*-
"""
windows_screen_time_settings.py
===============================
设置 Windows 屏幕关闭(超时)时间为 1 分钟。

实现原理:
    调用 Windows 自带的 powercfg 命令修改当前电源方案的屏幕超时时间:
        powercfg /change monitor-timeout-ac <分钟>   # 接通电源(AC)时
        powercfg /change monitor-timeout-dc <分钟>   # 使用电池(DC)时

依赖:
    仅支持 Windows 系统, 无需安装第三方库。

用法:
    直接运行即可, 默认设置为 1 分钟:
        python windows_screen_time_settings.py
    也可通过命令行参数自定义分钟数:
        python windows_screen_time_settings.py 5
"""

import ctypes
import subprocess
import sys


# 默认屏幕关闭时间(分钟)
DEFAULT_MINUTES = 1


def is_admin() -> bool:
    """检测当前进程是否具有管理员权限。

    修改电源方案中的屏幕超时时间属于系统级设置,
    powercfg /change 通常需要管理员权限才能生效。

    Returns:
        bool: True 表示拥有管理员权限, False 表示没有。
    """
    try:
        # IsUserAnAdmin() 返回 1 表示是管理员, 0 表示不是
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False


def elevate_to_admin() -> None:
    """以管理员权限重新启动当前脚本(触发 UAC 弹窗)。

    使用 ShellExecuteW + "runas" 动词请求系统提权,
    提权后新进程会替代当前进程继续执行脚本逻辑。
    若用户取消 UAC 弹窗, 脚本将无法继续, 直接退出。
    """
    params = " ".join(sys.argv[1:])  # 保留原命令行参数(如自定义分钟数)
    # nShow = 1 表示正常显示窗口
    result = ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, f'"{__file__}" {params}', None, 1
    )
    # ShellExecuteW 返回值 > 32 表示执行成功
    if result <= 32:
        print(f"[错误] 请求管理员权限失败, 错误码: {result}, 请右键“以管理员身份运行”本脚本。")
        sys.exit(1)
    sys.exit(0)  # 提权成功则退出当前非管理员进程, 由新进程执行


def set_screen_timeout(minutes: int) -> bool:
    """通过 powercfg 设置屏幕关闭时间为指定分钟数。

    分别修改接通电源(AC)和电池供电(DC)两种场景的超时时间。

    Args:
        minutes: 屏幕超时分钟数(整数, >= 0, 0 表示永不关闭)。

    Returns:
        bool: 两个设置是否全部成功。
    """
    commands = [
        ["powercfg", "/change", "monitor-timeout-ac", str(minutes)],
        ["powercfg", "/change", "monitor-timeout-dc", str(minutes)],
    ]
    all_ok = True
    for cmd in commands:
        try:
            # creationflags=0 默认窗口; 通过 shell=False 直接执行可执行文件
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding="gbk",  # powercfg 中文系统输出为 GBK 编码
                timeout=15,
            )
            if result.returncode == 0:
                print(f"[成功] {cmd[2]} 已设置为 {minutes} 分钟")
            else:
                all_ok = False
                print(
                    f"[失败] 执行 {' '.join(cmd)} 出错:\n"
                    f"       {result.stderr.strip() or result.stdout.strip()}"
                )
        except FileNotFoundError:
            all_ok = False
            print("[错误] 未找到 powercfg 命令, 请确认当前系统为 Windows。")
        except subprocess.TimeoutExpired:
            all_ok = False
            print(f"[超时] 命令 {' '.join(cmd)} 执行超时。")
    return all_ok


def get_current_screen_timeout() -> str:
    """查询当前电源方案的屏幕超时时间(毫秒), 用于验证设置是否生效。

    Returns:
        str: 查询到的超时时间原文; 查询失败时返回空字符串。
    """
    try:
        # VIDEOIDLE 是"关闭显示器"电源设置的别名, 查询其当前 AC/DC 值
        result = subprocess.run(
            ["powercfg", "/query", "SCHEME_CURRENT", "SUB_VIDEO", "VIDEOIDLE"],
            capture_output=True,
            text=True,
            encoding="gbk",
            timeout=15,
        )
        if result.returncode == 0:
            # 提取所有 "当前交流电源设置索引" / "当前直流电源设置索引" 行的数值(单位毫秒)
            lines = []
            for line in result.stdout.splitlines():
                if "当前" in line and "设置索引" in line:
                    lines.append(line.strip())
            return "\n".join(lines)
    except Exception:
        pass
    return ""


def main() -> None:
    """主流程: 权限检查 -> 提权 -> 设置超时时间 -> 验证结果。"""
    # 1. 解析命令行参数(可选): 第一个参数为分钟数
    minutes = DEFAULT_MINUTES
    if len(sys.argv) > 1:
        try:
            minutes = int(sys.argv[1])
            if minutes < 0:
                raise ValueError
        except ValueError:
            print(f"[错误] 参数必须为非负整数, 收到: {sys.argv[1]}")
            print(f"       用法: python {__file__.split(chr(92))[-1]} [分钟数]")
            sys.exit(1)

    print(f"准备将 Windows 屏幕关闭时间设置为 {minutes} 分钟 ...")

    # 2. 权限检查: powercfg /change 需要管理员权限
    if not is_admin():
        print("[提示] 当前未以管理员身份运行, 正在请求提权 ...")
        elevate_to_admin()
        # elevate_to_admin 内部会退出当前进程, 正常不会执行到这里

    # 3. 执行设置
    success = set_screen_timeout(minutes)
    if not success:
        print("[结论] 设置未完全成功, 请检查上述错误信息。")
        sys.exit(1)

    # 4. 查询当前值进行验证(期望为 minutes * 60000 毫秒)
    current = get_current_screen_timeout()
    if current:
        print("[验证] 当前电源方案的实际配置(毫秒):")
        print(current)
    else:
        print("[提示] 无法读取当前配置用于验证, 可手动执行 powercfg /query 检查。")

    print(f"[完成] 屏幕关闭时间已设置为 {minutes} 分钟。")


if __name__ == "__main__":
    main()
