# 工具
# \tools\tool.py

import datetime
import os
import threading
import time

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
    def run_mstsc(self,ip,port):
        import subprocess
        # 命令行调用mstsc 连接远程服务器
        cmd = f'mstsc /v:{ip}:{port}'
        # 运行命令
        subprocess.call(cmd)
        return True
    
    # 打开浏览器
    def open_browser(self,url):
        import webbrowser
        webbrowser.open(url)
        return True
    








