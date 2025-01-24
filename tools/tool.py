# 工具
# \tools\tool.py

import datetime
import os
import subprocess
import threading
import time


'''
    @ Author: LiuShan
    @ Date: 2024.09.04
    @ Description: 工具类
'''

class too:
    def __init__(self):
        pass

    # 多线程序
    def thread_it(self,func, *args):
        '''将函数打包进线程'''
        # 创建
        t = threading.Thread(target=func, args=args)
        # 守护 !!!
        t.setDaemon(True)
        # 启动
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
        import re
        from tools.logs import logs
        self.log = logs()
        ip_re = re.compile(r'^((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$')
        if ip_re.match(ip):
            self.log.write_log_error('ip格式正确: ' + ip)
            return True
        else:
            self.log.write_log_info('ip格式错误: ' + ip)
            return False

    # 运行mstsc
    def run_mstsc(self, ip, port, username, password):
            # 获取当前项目目录
            current_dir = os.getcwd()
            
            # 生成临时的 RDP 文件路径
            rdp_file_path = os.path.join(current_dir, 'temp.rdp')
            
            # 写入RDP文件内容
            rdp_content = (
                f"full address:s:{ip}:{port}\n"  # IP地址和端口号
                f"username:s:{username}\n"      # 用户名
                f"password 51:s:{password}\n"   # 密码
                "prompt for credentials:i:0\n"  # 表示不提示输入凭据，直接使用 RDP 文件中的凭据
                "enablecredsspsupport:i:1\n"  # 启用凭据安全支持提供程序
                "screen mode id:i:2\n"  # 全屏
                "color depth:i:32\n"  # 颜色最高质量32位
                "use multimon:i:0\n"  # 不要将所有监视器用于远程会话
                "audio mode:i:2\n"      # 本地资源配置远程音频在远程计算机上播放
                "keyboard hook:i:2\n"  # 仅在全屏显示时应用windows组合键
                "redirectclipboard:i:1\n"  # 本地设备资源仅使用剪贴板
                "prompt credential once:i:1\n"  # 仅提示一次
                "authentication level:i:2\n"  # 高级服务器身份验证设置连接并不显示警告
                "disable wallpaper:i:1\n"   # 禁用桌面壁纸
                "disable full window drag:i:1\n"    
                "disable menu anims:i:1\n"  
                "disable themes:i:1\n"      
                "disable cursor setting:i:1\n"  
                # "bitmapcachepersistenable:i:1\n"    
                # "redirectprinters:i:1\n"    
                "redirectcomports:i:0\n"          # 重定向打印机
                "redirectsmartcards:i:1\n"      #   重定向智能卡
                "redirectserialports:i:0\n"      # 重定向串行端口
                "redirectparallelports:i:0\n"   # 重定向并行端口
                "redirectdevices:i:1\n"          # 重定向设备
                "redirectposdevices:i:0\n"       # 重定向POS设备
                "redirectdirectx:i:1\n"          # 重定向DirectX
                "redirectdirectxdesktop:i:1\n"      # 重定向DirectX桌面
                "redirectdirectxdesktopmode:i:1\n"  # 重定向DirectX桌面模式
                "redirectdirectxmode:i:1\n"          # 重定向DirectX模式
            )
            
            # 写入 RDP 文件
            with open(rdp_file_path, 'w', encoding='utf-8') as f:
                f.write(rdp_content)
            
            # 调试信息：打印RDP文件内容
            print(f"RDP文件内容:\n{rdp_content}")

            # 调用mstsc命令
            self.thread_it(self._run_mstsc, rdp_file_path)
    def _run_mstsc(self, rdp_file_path):
        try:
            subprocess.call(['mstsc', rdp_file_path])
        except Exception as e:
            print(f"调用mstsc命令时出错: {e}")
        finally:
            try:
                os.remove(rdp_file_path)
            except Exception as e:
                print(f"删除RDP文件时出错: {e}")
    '''
    def run_mstsc(self,ip,port,username,password):
        import subprocess
        # 命令行调用mstsc 连接远程服务器
        cmd = f'mstsc /v:{ip}:{port}'
        # 运行命令
        subprocess.call(cmd)
        return True
    '''
    # 打开浏览器
    def open_browser(self,url):
        import webbrowser
        webbrowser.open(url)
        return True
    








