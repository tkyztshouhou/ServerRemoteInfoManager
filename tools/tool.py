# 工具
# \tools\tool.py

import datetime
import os
import subprocess
import sys
import threading
import time
import re


'''
    @ Author: LiuShan
    @ Date: 2024.09.04
    @ Description: 工具类
'''

def _hidden_console_kwargs():
    """构造 subprocess 的隐藏控制台参数，避免 GUI 程序拉起控制台程序时闪现黑色命令行窗口

    程序打包为 GUI（console=False）运行时，父进程没有控制台，Windows 会为
    cmdkey.exe 等控制台子系统程序自动创建一个新的控制台窗口，表现为黑框一闪而过。

    返回可直接解包传给 subprocess.run/call/Popen 的 kwargs；非 Windows 平台返回空字典。
    """
    if not sys.platform.startswith('win'):
        return {}
    kwargs = {}
    # Python 3.7+ 提供 CREATE_NO_WINDOW（0x08000000），不创建控制台
    creationflags = getattr(subprocess, 'CREATE_NO_WINDOW', 0)
    startupinfo = None
    try:
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        si.wShowWindow = 0  # SW_HIDE
        startupinfo = si
    except Exception:
        startupinfo = None
    if creationflags:
        kwargs['creationflags'] = creationflags
    if startupinfo is not None:
        kwargs['startupinfo'] = startupinfo
    return kwargs


class Tool:
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

    # 读取 settings 表配置（sqlite 直连，避免与 Object.gui_DA 相互依赖）
    def _get_setting(self, key, default=''):
        if not self.db_path or not os.path.exists(self.db_path):
            return default
        try:
            import sqlite3
            conn = sqlite3.connect(self.db_path)
            try:
                cur = conn.cursor()
                cur.execute('SELECT value FROM settings WHERE key = ?', (key,))
                row = cur.fetchone()
                return row[0] if row else default
            finally:
                conn.close()
        except Exception:
            return default

    # F15/S6: 清理残留的 RDP 凭据
    def cleanup_rdp_credentials(self):
        """启动时扫描并清理凭据管理器中已删除服务器的 RDP 孤儿凭据

        S6：程序被强杀时连接后的 finally 不执行，TERMSRV/ip 凭据会残留。
        本方法在启动时扫描全部 TERMSRV 凭据，删除数据库中已不存在主机的凭据；
        可通过 settings 表 `rdp_cred_cleanup = 0` 关闭该自动清理。
        """
        try:
            # S6: 自动清理开关（默认开启）
            if str(self._get_setting('rdp_cred_cleanup', '1')) != '1':
                return True

            # 获取所有 TERMSRV 凭据（隐藏控制台窗口，避免黑框闪烁）
            result = subprocess.run(
                ['cmdkey', '/list'],
                capture_output=True, text=True, check=False,
                **_hidden_console_kwargs()
            )
            if result.returncode != 0:
                return False

            output = result.stdout
            # 解析 TERMSRV 凭据
            target_ips = []
            for line in output.splitlines():
                line = line.strip()
                if line.startswith('Target: TERMSRV/'):
                    ip = line.split('TERMSRV/')[1].strip()
                    target_ips.append(ip)

            if not target_ips:
                return True

            # 查询数据库中存在的服务器主机地址
            import sqlite3
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT host FROM servers')
            existing_hosts = [row[0] for row in cursor.fetchall()]
            cursor.close()
            conn.close()
            existing_set = set(str(h) for h in existing_hosts)

            # 清除已不存在服务器的凭据
            cleaned = []
            for ip in target_ips:
                if ip not in existing_set:
                    try:
                        subprocess.run(
                            ['cmdkey', '/delete:TERMSRV/' + ip],
                            capture_output=True, text=True, check=False,
                            **_hidden_console_kwargs()
                        )
                        cleaned.append(ip)
                    except Exception:
                        pass

            if cleaned:
                print(f"[F15] 已清理 {len(cleaned)} 个残留 RDP 凭据: {cleaned}")
            return True
        except Exception as e:
            print(f"[F15] 清理 RDP 凭据失败: {e}")
            return False

    # F15/S6: 清理残留的临时 .rdp 文件
    def cleanup_temp_rdp_files(self, min_age_seconds=3600):
        """删除系统临时目录中本程序生成的 mstsc_*.rdp 残留文件

        程序被强杀时连接结束的 finally 不执行，临时 .rdp 文件会残留。
        仅删除超过 min_age_seconds（默认 1 小时）的文件，避免影响正在进行的连接。
        该文件不含密码，残留主要泄露主机地址与用户名。
        """
        import tempfile
        import time
        try:
            tmp_dir = tempfile.gettempdir()
            now = time.time()
            removed = []
            for name in os.listdir(tmp_dir):
                if not (name.startswith('mstsc_') and name.endswith('.rdp')):
                    continue
                path = os.path.join(tmp_dir, name)
                try:
                    if now - os.path.getmtime(path) < min_age_seconds:
                        continue
                    os.remove(path)
                    removed.append(name)
                except Exception:
                    pass
            if removed:
                print(f"[F15] 已清理 {len(removed)} 个残留的临时 .rdp 文件")
            return True
        except Exception as e:
            print(f"[F15] 清理临时 .rdp 文件失败: {e}")
            return False

    # 运行mstsc
    def run_mstsc(self, ip, port, username, password):
        """使用 Windows 凭据管理器运行远程桌面连接（在线程中执行，避免阻塞界面）"""
        self.thread_it(self._run_mstsc_with_credential, ip, port, username, password)

    def _run_mstsc_with_credential(self, ip, port, username, password):
        """通过 cmdkey 写入凭据 -> 生成临时 .rdp 文件 -> mstsc 连接 -> 关闭后清理凭据与临时文件

        流程：
          1. 连接前先清理凭据管理器中与本次主机相关的凭据，避免残留冲突
          2. 将用户名/密码写入 Windows 凭据管理器（TERMSRV/ip）
          3. 根据远程桌面高级选项生成临时 .rdp 文件
          4. 执行 mstsc 打开该 .rdp（阻塞直到远程桌面会话关闭）
          5. 会话关闭后自动删除凭据并删除临时 .rdp 文件
        """
        import sqlite3
        import tempfile

        # 凭据目标：TERMSRV/ip（不带端口，凭据按服务器区分）
        target = f"TERMSRV/{ip}"
        tmp_rdp = None
        try:
            # ---- 1. 连接前清理与本次主机相关的凭据（避免密码冲突/残留） ----
            try:
                subprocess.run(['cmdkey', '/delete:' + target],
                               capture_output=True, text=True, check=False,
                               **_hidden_console_kwargs())
            except Exception:
                pass

            # ---- 2. 读取远程桌面高级选项 ----
            audio = 'local'
            clipboard = '1'
            drive = '0'
            fullscreen = '0'
            resolution = '1024x768'
            if self.db_path:
                try:
                    conn = sqlite3.connect(self.db_path)
                    cur = conn.cursor()
                    cur.execute('SELECT value FROM settings WHERE key = ?', ('rdp_audio',))
                    row = cur.fetchone()
                    if row:
                        audio = row[0]
                    cur.execute('SELECT value FROM settings WHERE key = ?', ('rdp_clipboard',))
                    row = cur.fetchone()
                    if row:
                        clipboard = row[0]
                    cur.execute('SELECT value FROM settings WHERE key = ?', ('rdp_drive',))
                    row = cur.fetchone()
                    if row:
                        drive = row[0]
                    cur.execute('SELECT value FROM settings WHERE key = ?', ('rdp_fullscreen',))
                    row = cur.fetchone()
                    if row:
                        fullscreen = row[0]
                    cur.execute('SELECT value FROM settings WHERE key = ?', ('rdp_resolution',))
                    row = cur.fetchone()
                    if row:
                        resolution = row[0]
                    cur.close()
                    conn.close()
                except Exception as e:
                    print(f"读取远程桌面设置失败，使用默认值: {e}")

            # 解析分辨率（格式 宽度x高度）
            desktopwidth, desktopheight = 1024, 768
            if resolution and 'x' in str(resolution):
                try:
                    w, h = str(resolution).lower().split('x')
                    desktopwidth = int(w)
                    desktopheight = int(h)
                except Exception:
                    desktopwidth, desktopheight = 1024, 768

            # 音频位置映射：本地 -> 在本地计算机播放(audiomode 0)；远程 -> 在远程播放(audiomode 1)
            audiomode = 0 if str(audio).lower() in ('local', '本地') else 1
            redirect_clipboard = 1 if str(clipboard) == '1' else 0
            drive_storedirect = '*' if str(drive) == '1' else ''
            screen_mode = 2 if str(fullscreen) == '1' else 1

            # ---- 3. 生成临时 .rdp 文件 ----
            rdp_lines = [
                'full address:s:' + f'{ip}:{port}',
                'username:s:' + str(username),
                'prompt for credentials:i:0',
                'audiomode:i:' + str(audiomode),
                'redirectclipboard:i:' + str(redirect_clipboard),
                'drivestoredirect:s:' + drive_storedirect,
                'screen mode id:i:' + str(screen_mode),
                'desktopwidth:i:' + str(desktopwidth),
                'desktopheight:i:' + str(desktopheight),
                'authentication level:i:2',
                'allow desktop composition:i:1',
                'allow font smoothing:i:1',
            ]
            fd, tmp_path = tempfile.mkstemp(suffix='.rdp', prefix='mstsc_')
            with os.fdopen(fd, 'w', encoding='utf-8') as f:
                f.write('\n'.join(rdp_lines) + '\n')
            tmp_rdp = tmp_path

            # ---- 4. 写入凭据到 Windows 凭据管理器（列表形式传参，避免密码特殊字符被 shell 解析） ----
            add_result = subprocess.run(
                ['cmdkey', '/generic:' + target, '/user:' + str(username), '/pass:' + str(password)],
                capture_output=True, text=True, check=False,
                **_hidden_console_kwargs()
            )
            if add_result.returncode != 0:
                print(f"添加凭据失败，无法连接 {ip}:{port}")
                return False

            # 启动 mstsc 打开临时 .rdp（阻塞直到远程桌面会话关闭）
            # mstsc 是 GUI 程序，不能附加 STARTUPINFO(SW_HIDE)，否则远程桌面窗口会被隐藏
            subprocess.call(['mstsc', tmp_rdp])
            return True
        except Exception as e:
            print(f"运行mstsc时出错: {e}")
            return False
        finally:
            # ---- 5. 会话关闭（或异常）后，清理凭据与临时文件 ----
            try:
                subprocess.run(['cmdkey', '/delete:' + target],
                               capture_output=True, text=True, check=False,
                               **_hidden_console_kwargs())
            except Exception:
                pass
            if tmp_rdp and os.path.exists(tmp_rdp):
                try:
                    os.remove(tmp_rdp)
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

            # shell=True 会拉起 cmd，隐藏其控制台窗口避免黑框闪烁；
            # PuTTY(plink) 本身是控制台程序，需要显示终端窗口保持可见，故不隐藏
            popen_kwargs = {} if ssh_tool_type == 'PuTTY(plink)' else _hidden_console_kwargs()
            self.thread_it(subprocess.Popen, cmd, shell=True, **popen_kwargs)
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
            # vncviewer 是 GUI 程序，不能附加 SW_HIDE（同 mstsc 的 B68 修正）
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
            # radmin.exe 是 GUI 程序，不能附加 SW_HIDE（同 mstsc 的 B68 修正）
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
    








