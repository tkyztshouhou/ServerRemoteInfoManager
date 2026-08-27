import tkinter as tk
from Object.infoServer import InfoServer
from tools.logs import logs

'''
    @author: LiuShan
    @date: 2024
    @description:程序入口
'''

log = logs()

log.write_log(' 程序启动 ')
root = tk.Tk()
InfoServer(root)
root.mainloop()