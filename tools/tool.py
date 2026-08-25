# 工具
# \tools\tool.py

import datetime
import os
import subprocess
import threading
import time
import re


'''
    @ Author: LiuShan
    @ Date: 2024.09.04
    @ Description: 工具类
'''

class too:
    def __init__(self, db_path=None):
        self.db_path = db_path

    # 多线程序
    def thread_it(self,func, *args, **kwargs):
        '''将函数打包进线程'''
        # 创建
        t = threading.Thread(target=func, args=args, kwargs=kwargs)
        # B22: 使用 daemon 属性替代已废弃的 setDaemon()
        t.daemon = True
        t.start()
        # 阻塞--卡死界面！
        # t.join()

    # 打开mstsc
    def open_mstsc(self):
        try:
            os.startfile('mstsc.exe')
        except:
            pass
        
    # 分组控件鼠标右键菜单
    def show_menu(self,event, menu): 
        menu.post(event.x_root, event.y_root)   # 显示菜单
        menu.grab_set() # 菜单获取焦点
        menu.grab_release() # 菜单释放焦点
        menu.bind("<Leave>", lambda e: menu.unpost())   # 鼠标离开菜单时隐藏菜单
        menu.bind("<FocusOut>", lambda e: menu.unpost())    # 菜单失去焦点时隐藏菜单
        menu.bind("<Button-1>", lambda e: menu.unpost())    # 鼠标单击菜单时隐藏菜单
        menu.bind("<Button-2>", lambda e: menu.unpost())    # 鼠标双击菜单时隐藏菜单

    def time(self):
        # 使用datetime获取当前时间，并将时间格式化为YY-MM-DD HH:MM:SS格式返回
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def time_day(self):
        # 使用datetime获取当前时间，并将时间格式化为YY-MM-DD格式返回
        return datetime.datetime.now().strftime("%Y-%m-%d")
    
    def sleep(self,interval):
        return time.sleep(interval)
    
    # 正则匹配是否是ip
    def is_ip(self,ip):
        # B23: 延迟导入 logs 类，避免循环导入
        from tools.logs import logs
        self.log = logs()
        ip_re = re.compile(r'^((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$')
        if ip_re.match(ip):
            # B24: 格式正确使用 INFO，格式错误使用 WARNING
            self.log.write_log_info('ip格式正确: ' + ip)
            return True
        else:
            self.log.write_log_error('ip格式错误: ' + ip)
            return False

    # 运行mstsc
    def run_mstsc(self, ip, port, username, password):
        """使用 Windows 凭据管理器运行远程桌面连接（在线程中执行，避免阻塞界面）"""
        self.thread_it(self._run_mstsc_with_credential, ip, port, username, password)

    def _run_mstsc_with_credential(self, ip, port, username, password):
        """通过 cmdkey 写入凭据管理器 -> mstsc 连接 -> 关闭后清除凭据"""
        # RDP 凭据目标：TERMSRV/ip（不带端口，凭据按服务器区分）
        target = f"TERMSRV/{ip}"
        try:
            # 添加凭据到 Windows 凭据管理器（列表形式传参，避免密码特殊字符被 shell 解析）
            result = subprocess.run(
                ['cmdkey', '/generic:' + target, '/user:' + str(username), '/pass:' + str(password)],
                capture_output=True, text=True
            )
            if result.returncode != 0:
                print(f"添加凭据失败，无法连接 {ip}:{port}")
                return False

            # 启动 mstsc 连接（阻塞直到远程桌面关闭）
            subprocess.call(['mstsc', '/v', f'{ip}:{port}'])
            return True
        except Exception as e:
            print(f"运行mstsc时出错: {e}")
            return False
        finally:
            # 连接结束（或异常）后，清除刚刚添加的凭据
            try:
                subprocess.run(['cmdkey', '/delete:' + target], capture_output=True, text=True)
            except Exception:
                pass
    '''
    def run_mstsc(self,ip,port,username,password):
        import subprocess
        # 命令行调用mstsc 连接远程服务器
        cmd = f'mstsc /v:{ip}:{port}'
        # 运行命令
        subprocess.call(cmd)
        return True
    '''
    # 运行SSH（支持多种终端工具）
    def run_ssh(self, host, port, username, password, callback=None):
        """根据配置的 SSH 工具类型执行连接，支持 XTerminal、PuTTY(plink)、MobaXterm、FinalShell、Xshell"""
        from Object.gui_DA import DataAccess
        da = DataAccess(self.db_path)
        ssh_tool_type = da.get_setting('ssh_tool_type') or 'XTerminal'

        # 兼容旧版本保存的小写工具类型值
        legacy_map = {
            'xterm': 'XTerminal', 'plink': 'PuTTY(plink)', 'mobaxterm': 'MobaXterm',
            'finalshell': 'FinalShell', 'xshell': 'Xshell',
        }
        ssh_tool_type = legacy_map.get(ssh_tool_type, ssh_tool_type)

        # 工具类型 -> 独立路径设置键（与设置窗口保存的键名一致）
        path_keys = {
            'XTerminal': 'ssh_tool_path_xterm',
            'PuTTY(plink)': 'ssh_tool_path_plink',
            'MobaXterm': 'ssh_tool_path_mobaxterm',
            'FinalShell': 'ssh_tool_path_finalshell',
            'Xshell': 'ssh_tool_path_xshell',
        }
        tool_path = da.get_setting(path_keys.get(ssh_tool_type, 'ssh_tool_path_xterm'), '')

        try:
            if ssh_tool_type == 'PuTTY(plink)':
                tool = tool_path or 'plink'
                cmd = f'"{tool}" -P {port} -l {username} -pw {password} {host}'
            elif ssh_tool_type == 'MobaXterm':
                tool = tool_path or 'MobaXterm.exe'
                cmd = f'"{tool}" -ssh {username}@{host}:{port}'
            elif ssh_tool_type == 'FinalShell':
                tool = tool_path or 'finalshell.exe'
                cmd = f'"{tool}" -h {host} -p {port} -u {username} -pw {password}'
            elif ssh_tool_type == 'Xshell':
                tool = tool_path or 'Xshell.exe'
                cmd = f'"{tool}" -url ssh://{username}:{password}@{host}:{port}'
            else:
                # XTerminal：使用配置的工具路径直接启动，传入 ssh:// URL
                tool = tool_path or 'XTerminal.exe'
                cmd = f'"{tool}" "ssh://{username}@{host}:{port}"'

            # 检查工具文件是否存在
            import os
            if not os.path.exists(tool):
                error_msg = f"SSH连接失败：工具文件不存在\n\n工具路径：{tool}\n\n请检查工具路径是否正确，或重新配置SSH工具路径。"
                print(error_msg)
                if callback:
                    callback(error_msg)
                return False

            self.thread_it(subprocess.Popen, cmd, shell=True)
            return True
        except Exception as e:
            # 提供更友好的错误信息
            if "不是内部或外部命令" in str(e) or "not found" in str(e):
                error_msg = f"SSH连接失败：工具无法启动\n\n错误：{e}\n\n请检查工具路径是否正确，或重新配置SSH工具路径。"
            elif "权限" in str(e) or "permission" in str(e):
                error_msg = f"SSH连接失败：权限不足\n\n错误：{e}\n\n请检查工具文件的访问权限。"
            else:
                error_msg = f"SSH连接失败：{e}"
            
            print(error_msg)
            if callback:
                callback(error_msg)
            return False

    # 运行VNC（vncviewer）
    def run_vnc(self, host, port, callback=None):
        """调用 vncviewer 进行 VNC 连接"""
        try:
            # 检查工具文件是否存在
            import os
            vncviewer_path = 'vncviewer'
            if not os.path.exists(vncviewer_path):
                error_msg = f"VNC连接失败：工具文件不存在\n\n工具路径：{vncviewer_path}\n\n请确保系统已安装VNC客户端，或重新配置VNC工具路径。"
                print(error_msg)
                if callback:
                    callback(error_msg)
                return False

            addr = f"{host}:{port}"
            cmd = ['vncviewer', addr]
            self.thread_it(subprocess.Popen, cmd)
            return True
        except Exception as e:
            # 提供更友好的错误信息
            if "不是内部或外部命令" in str(e) or "not found" in str(e):
                error_msg = f"VNC连接失败：工具无法启动\n\n错误：{e}\n\n请确保系统已安装VNC客户端，或重新配置VNC工具路径。"
            elif "权限" in str(e) or "permission" in str(e):
                error_msg = f"VNC连接失败：权限不足\n\n错误：{e}\n\n请检查工具文件的访问权限。"
            else:
                error_msg = f"VNC连接失败：{e}"
            
            print(error_msg)
            if callback:
                callback(error_msg)
            return False

    # 运行Radmin连接
    def run_radmin(self, host, port, callback=None):
        """调用 Radmin 进行远程连接"""
        try:
            # 检查工具文件是否存在
            import os
            radmin_path = 'radmin.exe'
            if not os.path.exists(radmin_path):
                error_msg = f"Radmin连接失败：工具文件不存在\n\n工具路径：{radmin_path}\n\n请确保系统已安装Radmin客户端，或重新配置Radmin工具路径。"
                print(error_msg)
                if callback:
                    callback(error_msg)
                return False

            # Radmin连接命令：radmin.exe /connect:地址:端口
            cmd = f'"{radmin_path}" /connect:{host}:{port}'
            self.thread_it(subprocess.Popen, cmd, shell=True)
            return True
        except Exception as e:
            # 提供更友好的错误信息
            if "不是内部或外部命令" in str(e) or "not found" in str(e):
                error_msg = f"Radmin连接失败：工具无法启动\n\n错误：{e}\n\n请确保系统已安装Radmin客户端，或重新配置Radmin工具路径。"
            elif "权限" in str(e) or "permission" in str(e):
                error_msg = f"Radmin连接失败：权限不足\n\n错误：{e}\n\n请检查工具文件的访问权限。"
            else:
                error_msg = f"Radmin连接失败：{e}"
            
            print(error_msg)
            if callback:
                callback(error_msg)
            return False

    # 打开浏览器
    def open_browser(self,url):
        import webbrowser
        webbrowser.open(url)
        return True
    








