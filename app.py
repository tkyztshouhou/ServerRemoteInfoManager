import tkinter as tk
from Object.infoServer import infoServer
from tools.logs import logs

'''
    @author: LiuShan
    @date: 2024
    @description:程序入口
'''

log = logs()

log.write_log(' 程序启动 ')
root = tk.Tk()
infoServer(root)
root.mainloop()