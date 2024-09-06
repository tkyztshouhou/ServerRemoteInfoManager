import os
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from Object.gui_DA import *
from tools.logs import logs
from tools.tool import too


'''
    @ Author: LiuShan
    @ Date: 2024.09.04
    @ Description: 服务器运维管理工具类
'''

# 创建主窗口
class infoServer:
    def __init__(self, master):
        self.master = master    # 窗口
        self.master.title("服务器运维管理工具    V1.0.20240906  Demo公测版 -Liu")
        self.master.geometry('1280x720+50+0')   #将该行代码修改为分辨率可自定义调整窗口大小
        self.master.resizable(width=True, height=True)
        self.master.iconphoto(True, tk.PhotoImage(file='./img/top.png'))
        self.db = DataAccess(os.path.join(os.getcwd(), 'data.db'))
        self.log = logs()
        self.too = too()
        

        # 创建图片
        self.fz = tk.PhotoImage(file='./img/fz.png')
        self.scfz = tk.PhotoImage(file='./img/scfz.png')
        self.tjzj = tk.PhotoImage(file='./img/tjzj.png')
        self.bjzj = tk.PhotoImage(file='./img/bjzj.png')
        self.sczj = tk.PhotoImage(file='./img/sczj.png')
        self.lj = tk.PhotoImage(file='./img/lj.png')
        self.mstsc = tk.PhotoImage(file='./img/mstsc.png')
        self.radmin = tk.PhotoImage(file='./img/radmin.png')
        self.ssh = tk.PhotoImage(file='./img/ssh.png')
        self.sz = tk.PhotoImage(file='./img/sz.png')
        self.rdp = tk.PhotoImage(file='./img/rdp.png')
        self.folde = tk.PhotoImage(file='./img/FolderEmpty16x16.png')

        self.create_widgets()   # 初始化控件
        self.create_database()  # 初始化数据库

        self.init_groups_data()
        self.init_server_data()
        
        
        # master绑定esc事件
        # self.master.bind('<Escape>', lambda event: self.top.destroy())

        self.log.write_log_info("程序初始化成功")

    # 创建主窗口
    '''
        初始化控件
    '''
    def create_widgets(self):
        def update_width(event):
            # 获取当前窗口的宽度
            window_width = event.width
            # 设置左侧部件的宽度为窗口宽度的1/4
            self.left_frame.config(width=window_width // 4)

        # 一级框架
        self.top = tk.Frame(self.master, bg='#F0F0F0')
        self.top.pack(side=tk.TOP, fill=tk.X)

        self.left_frame = tk.Frame(self.master, bg='#F0F0F0')
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y,padx=10, pady=10)   # 填充 纵向
        self.left_frame.pack_propagate(1)               # 禁止内部控件影响外层控件大小 默认为1 禁止为0
        self.right_frame = tk.Frame(self.master, bg='#F0F0F0')
        self.right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True,padx=10, pady=10)
        self.right_frame.pack_propagate(0)

        # top
        self.top_frame = tk.Frame(self.top, bg='#F0F0F0')
        self.top_frame.pack(side=tk.LEFT, fill=tk.Y)     # 填充 横向
        self.top_frame.pack_propagate(1)                # 禁止内部控件影响外层控件大小 默认为1 禁止为0

        self.top_R = tk.Frame(self.top, bg='#F0F0F0')
        self.top_R.pack(side=tk.LEFT, fill=tk.Y)     # 填充 横向
        self.top_R.pack_propagate(1)                # 禁止内部控件影响外层控件大小 默认为1 禁止为0

        # 创建右侧服务器列表框架，右侧区域分为上下两部分，上方显示服务器信息，下方显示服务器详细信息
        self.right_frame_top = tk.Frame(self.right_frame, bg='#F0F0F0') # 填充 纵向
        self.right_frame_top.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.right_frame_top.pack_propagate(0)                  # 禁止内部控件影响外层控件大小 默认为1 禁止为0

        self.right_frame_bottom = tk.Frame(self.right_frame, bg='#F0F0F0')  # 填充 纵向
        self.right_frame_bottom.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True,pady=5)
        self.right_frame_bottom.pack_propagate(0)                    # 禁止内部控件影响外层控件大小 默认为1 禁止为0
        
        # 初始化btn按钮
        self.top_frame_button_1 = tk.Button(self.top_frame,  bd=0,image=self.fz, compound=tk.LEFT, bg='#F0F0F0', command=self.add_folder_window)
        self.top_frame_button_1.pack(side=tk.LEFT, padx=30,pady=10)
        self.top_frame_button_2 = tk.Button(self.top_frame,  bd=0, image=self.tjzj, compound=tk.LEFT, bg='#F0F0F0', command=self.add_server_window)
        self.top_frame_button_2.pack(side=tk.LEFT, padx=30,pady=10)
        self.top_frame_button_3 = tk.Button(self.top_frame,  bd=0, image=self.bjzj, compound=tk.LEFT, bg='#F0F0F0',  command=self.edit_server)
        self.top_frame_button_3.pack(side=tk.LEFT, padx=30,pady=10)
        self.top_frame_button_4 = tk.Button(self.top_frame,  bd=0, image=self.sczj, compound=tk.LEFT, bg='#F0F0F0',  command=self.delete_server)
        self.top_frame_button_4.pack(side=tk.LEFT, padx=30,pady=10)
        self.top_frame_button_5 = tk.Button(self.top_frame,  bd=0, image=self.scfz, compound=tk.LEFT, bg='#F0F0F0',  command=self.delete_group)
        self.top_frame_button_5.pack(side=tk.LEFT, padx=30,pady=10)
        # self.top_frame_button_6 = tk.Button(self.top_frame,  bd=0, image=self.sz, compound=tk.LEFT, bg='#F0F0F0',  command=self.search_servers)
        # self.top_frame_button_6.pack(side=tk.LEFT, padx=30,pady=10)
        self.top_frame_button_7 = tk.Button(self.top_frame,  bd=0, image=self.mstsc, compound=tk.LEFT, bg='#F0F0F0',  command=lambda:self.too.thread_it(self.too.open_mstsc))

        self.top_frame_button_7.pack(side=tk.LEFT, padx=30,pady=1)

        # 创建分组列表
        self.group_tree = ttk.Treeview(self.left_frame,show='tree')
        self.group_tree.pack(side = tk.LEFT,fill=tk.Y, expand=True)   # 填充 纵向 边距10

        # 添加滚动条
        group_scrollbar = ttk.Scrollbar(self.left_frame, orient=tk.VERTICAL, command=self.group_tree.yview)
        group_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.group_tree.configure(yscrollcommand=group_scrollbar.set)

        # 创建样式
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Treeview', rowheight=25)
        style.map('Treeview', background=[('selected', 'gray')], foreground=[('selected', 'white')])
        style.configure('Treeview.Heading', font=('Microsoft YaHei',10))

        # 创建主机列表
        self.server_tree = ttk.Treeview(self.right_frame_top, 
                                        columns=('type','name', 'ip', 'port', 'username',
                                                 'password', 'remark'), show='headings',
                                                   height=30,
                                                    style='Treeview')
        
        self.server_tree.heading('type', text='类型')
        self.server_tree.heading('name', text='主机名')
        self.server_tree.heading('ip', text='域名')
        self.server_tree.heading('port', text='端口')
        self.server_tree.heading('username', text='用户名')
        self.server_tree.heading('password', text='密码')
        self.server_tree.heading('remark', text='状态')
    
        self.server_tree.column('type', width=10, anchor='center')
        self.server_tree.column('name', width=250, anchor='center')
        self.server_tree.column('ip', width=100, anchor='center')
        self.server_tree.column('port', width=20, anchor='center')
        self.server_tree.column('username', width=70, anchor='center')
        self.server_tree.column('password', width=50, anchor='center')
        self.server_tree.column('remark', width=10, anchor='center')

        self.server_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)


        # 添加滚动条
        server_scrollbar = ttk.Scrollbar(self.right_frame_top, orient=tk.VERTICAL, command=self.server_tree.yview)
        server_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.server_tree.configure(yscrollcommand=server_scrollbar.set)

        # 创建搜索框
        self.search_label = tk.Label(self.top_R, text="主机名或域名搜索：")
        self.search_label.pack(side=tk.LEFT,padx=1)
        self.search_entry = tk.Entry(self.top_R, width=20,border=2)
        self.search_entry.pack(side=tk.LEFT,padx=1)
        self.search_btn = tk.Button(self.top_R, text="搜索", width=10,command=self.search_servers)
        self.search_btn.pack(side=tk.LEFT,padx=1)

        # 创建右侧服务器详细信息框架
        self.lable1 = tk.Label(self.right_frame_bottom, text="服务器说明：",bg='#F0F0F0',font=('微软雅黑',10))
        self.lable1.pack(side=tk.TOP,fill=tk.X)
        # self.server_info = tk.LabelFrame(self.right_frame_bottom,bg='#F0F0F0' )     # bg='#F0F0F0'
        # self.server_info.pack(fill=tk.BOTH, expand=True)
        self.server_info = tk.Text(self.right_frame_bottom)

        self.server_info.pack(side=tk.LEFT,fill = tk.BOTH,expand=True)
        # 添加滚动条
        info_Scrollbar = ttk.Scrollbar(self.right_frame_bottom, orient=tk.VERTICAL, command=self.server_info.yview)
        info_Scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.server_info.configure(yscrollcommand=info_Scrollbar.set)
        
        #绑定窗口改变事件
        self.master.bind('<Configure>', update_width)

        # 左键双击事件
        # self.group_tree.bind("<Double-1>", self.groupTree_click)
        # self.server_tree.bind("<Double-1>" ,lambda event: self.connect_server(event))

        # server_tree焦点变更事件
        self.server_tree.bind("<<TreeviewSelect>>", self.on_selection_change)
        self.group_tree.bind("<<TreeviewSelect>>", self.on_group_selection_change)

        # 绑定中键事件 取消焦点
        self.group_tree.bind("<Button-2>", self.groupTree_release)
        self.server_tree.bind("<Button-2>", self.Stree_release)

        # 右键事件
        self.group_tree.bind("<Button-3>", self.tree_right_click)
        self.server_tree.bind("<Button-3>", self.Stree_right_click)


        self.log.write_log_info('控件初始化成功')

    # 创建数据库
    def create_database(self):
        try:
            self.db.create_database()
        except Exception as e:
            self.log.write_log_error(str(e))

    # 初始化组数据
    def init_groups_data(self):
        try:
            self.db.init_groups_data(self.group_tree,self.folde)
            self.log.write_log_info('组数据初始化成功')
        except Exception as e:
            self.log.write_log_error('外层调用组数据初始化失败' + str(e))

    # 初始化主机数据
    def init_server_data(self):
        try:
            self.db.init_servers_data(self.server_tree)
            self.log.write_log_info('主机数据初始化成功')
        except Exception as e:
            self.log.write_log_error(str(e))

    # 添加主机window
    def add_server_window(self):
        def add_server ():
            conn_type = down.get()
            name = name_entry.get()
            host = host_entry.get()
            port = port_entry.get()
            username = user_entry.get()
            password = passwd_entry.get()
            server_info = info_text.get("1.0", tk.END)

            selectItem_groupTree = self.group_tree.focus()                              # 获取选中的分组id
            selectTree_name = self.group_tree.item(selectItem_groupTree)['text']         # 获取选中的分组名称
            select_group_id = self.db.get_group_focus_id(selectTree_name)
            # 判断self.group_tree.focus()是否为空

            if select_group_id is None:
                messagebox.showinfo('提示', '请选择分组')
                self.log.write_log_error('未选择分组，添加失败')
                return
            if not name:
                messagebox.showinfo('提示', '主机名不能为空')
                self.log.write_log_error('主机名不能为空，添加失败')
                return
            if not host:
                messagebox.showinfo('提示', '主机地址不能为空')
                self.log.write_log_error('主机地址不能为空，添加失败')
                return
            if self.db.exists(name,'server'):
                messagebox.showinfo('提示', '主机名已存在')
                self.log.write_log_error('主机名已存在，添加失败')
                return
            if self.db.ip_exists(host):
               messagebox.showinfo('提示', '主机地址已存在')
               self.log.write_log_error('主机地址已存在，添加失败')
               return
            try:
                self.db.add_server(conn_type,name,host,port,username,password,select_group_id,server_info)
                # 刷新server_tree数据
                self.server_tree.destroy
                self.init_server_data()
                # self.top.destroy()
                messagebox.showinfo('提示', '添加成功')
                self.log.write_log_info('服务器：主机名:'+ name +'，ip地址：'+ host+ ',端口:'+ port+ 
                                        '，用户名：' + username+ ',密码：'+ password + ',说明： '+ server_info+ '添加成功' )

            except Exception as e:
                self.log.write_log_error('服务器添加失败' + str(e))
                return
        self.log.write_log_info('事件触发：添加主机window')
        self.top = tk.Toplevel()
        self.top.title("添加主机")
        # self.top.geometry('250x450+400+80')
        self.top_master(self.top,450)
        # 锁定焦点
        # self.top.grab_set()
        # 设置窗口宽高固定
        self.top.resizable(0,0)
        # 窗口置顶
        # self.top.attributes('-topmost', 1)
        lab1 = tk.Label(self.top, text="主机类型：")
        lab1.pack()
        down = ttk.Combobox(self.top, values=['SSH', 'RDP','VNC','Radmin','URL'],state='readonly', width=20)
        down.current(0)
        down.pack()
        lab2 = tk.Label(self.top, text="主机名：")
        lab2.pack()
        name_entry = tk.Entry(self.top, width=23)
        name_entry.pack()
        lab3 = tk.Label(self.top, text="主机地址：")
        lab3.pack()
        host_entry = tk.Entry(self.top, width=23)
        host_entry.pack()
        lab4 = tk.Label(self.top, text="端口：")
        lab4.pack()
        port_entry = tk.Entry(self.top, width=23)
        port_entry.pack()
        lab5 = tk.Label(self.top, text="用户名：")
        lab5.pack()
        user_entry = tk.Entry(self.top, width=23)
        user_entry.pack()
        lab6 = tk.Label(self.top, text="密码：")
        lab6.pack()
        passwd_entry = tk.Entry(self.top, width=23)
        passwd_entry.pack()
        info_lab = tk.Label(self.top, text="服务器说明：")
        info_lab.pack()
        info_text = tk.Text(self.top, height=4, width=23)
        info_text.pack()

        btn = tk.Button(self.top, text="确定", width=10,command=add_server) 
                                                                                    
        btn.pack(pady='5')
        btn2 = tk.Button(self.top, text="取消", width=10,command=self.top.destroy)
        btn2.pack(pady='5')
        
    # 编辑服务器
    def edit_server(self):
        def edit_da():
            select_collu = down.get()
            name = server_info[0]
            host = server_info[1]
           
            server_id = self.db.get_server_id(name)
            selectItem_groupTree = self.group_tree.focus()                              # 获取选中的分组id
            selectTree_name = self.group_tree.item(selectItem_groupTree)['text']         # 获取选中的分组名称
            select_group_id = self.db.get_group_focus_id(selectTree_name)

            # if not name:
            #     messagebox.showinfo('提示', '主机名不能为空')
            #     self.log.write_log_error('主机名不能为空，添加失败')
            #     return
            # if not host:
            #     messagebox.showinfo('提示', '主机地址不能为空')
            #     self.log.write_log_error('主机地址不能为空，添加失败')
            #     return

            try:
                if select_collu == '主机名':
                    if self.db.exists(name,'server'):
                        messagebox.showinfo('提示', '主机名已存在')
                        self.log.write_log_error('主机名已存在，添加失败')
                        return
                    if1 = 'name'
                    self.db.update_server(if1,conten_entry.get("1.0", tk.END),host)
                    # 刷新server_tree数据
                    self.server_tree.destroy
                    self.init_server_data()
                    messagebox.showinfo('提示', '编辑成功')
                    self.log.write_log_info('主机:' + host + '编辑成功,主机名修改为:' + conten_entry.get("1.0", tk.END))
                    self.top.destroy()
                    return
                elif select_collu == '端口号':
                    if2 = 'port'
                    self.db.update_server(if2,conten_entry.get("1.0", tk.END),host)
                    self.server_tree.destroy
                    self.init_server_data()
                    messagebox.showinfo('提示', '编辑成功')
                    self.log.write_log_info('主机:' + host + '编辑成功,端口号修改为:' + conten_entry.get("1.0", tk.END))
                    self.top.destroy()
                    return
                elif select_collu == '用户名':
                    if3 = 'username'
                    self.db.update_server(if3,conten_entry.get("1.0", tk.END),host)
                    self.server_tree.destroy
                    self.init_server_data()
                    messagebox.showinfo('提示', '编辑成功')
                    self.log.write_log_info('主机:' + host + '编辑成功,用户名修改为:' + conten_entry.get("1.0", tk.END))
                    self.top.destroy()
                    return
                elif select_collu == '密码':
                    if4 = 'password'
                    self.db.update_server(if4,conten_entry.get("1.0", tk.END),host)
                    self.server_tree.destroy
                    self.init_server_data()
                    messagebox.showinfo('提示', '编辑成功')
                    self.log.write_log_info('主机:' + host + '编辑成功,密码修改为:' + conten_entry.get("1.0", tk.END))
                    self.top.destroy()
                    return
                elif select_collu == '分组':
                    if select_group_id is None:
                        messagebox.showinfo('提示', '未选择分组,请选择分组')
                        self.log.write_log_error('未选择分组，编辑主机信息失败')
                        return
                    conten_entry.config(textvariable="修改分组无需输入内容")
                    if5 = 'parent_id'
                    self.db.update_server(if5,select_group_id,host)
                    self.server_tree.destroy
                    self.init_server_data()
                    messagebox.showinfo('提示', '编辑成功')
                    self.log.write_log_info('主机:' + host + '编辑成功,分组修改为:' + select_group_id)
                    self.top.destroy()
                    return
                elif select_collu == '服务器说明':
                    if6 = 'server_info'
                    self.db.update_server(if6,conten_entry.get("1.0", tk.END),host)
                    self.server_tree.destroy
                    self.init_server_data()
                    messagebox.showinfo('提示', '编辑成功')
                    self.log.write_log_info('主机:' + host + '编辑成功,服务器说明修改为:' + conten_entry.get("1.0", tk.END))
                    self.top.destroy()
                    return
                else:
                    messagebox.showinfo('提示', '不支持的操作')
                    self.log.write_log_error('编辑失败')
            except Exception as e:
                self.log.write_log_error('服务器编辑失败' + str(e))
                return
            finally:
                self.top.destroy()
            
        self.log.write_log_info('事件触发：编辑主机信息')
        selected_item = self.server_tree.focus()
        if not selected_item:
            messagebox.showerror("Error", "请选择一个服务器")
            return
        
        item_values = self.server_tree.item(selected_item).get('values')
        if not item_values or len(item_values) < 2:
            messagebox.showerror("Error", "服务器信息不完整")
            return

        selectServerTreeName = self.server_tree.item(selected_item)['values'][1]

        if not isinstance(selectServerTreeName, str):
            raise ValueError("selectServerTreeName 必须是字符串类型")

        server_info = self.db.get_server_by_name(selectServerTreeName)
        if server_info is None:
            # 处理未找到的情况，例如显示错误消息
            messagebox.showerror("Error", f"服务器{selected_item} {selectServerTreeName} {server_info} 未找到")
            return
        
        name = server_info[0]
        host = server_info[1]
        port = server_info[2]
        username = server_info[3]
        password = server_info[4]
        self.log.write_log_info('主机名：' + name + ',主机ip : ' + host + '端口号：' + str(port) + '用户名：' + username + '密码：' + password)
        self.top = tk.Toplevel()
        self.top.title("编辑主机")
        self.top_master(self.top,300)
        # 锁定焦点
        # self.top.grab_set()
        self.top.resizable(0,0)
        lab1 = tk.Label(self.top, text="请选择要修改的内容：")
        lab1.pack()
        down = ttk.Combobox(self.top, values=['主机名', '端口号','用户名','密码','分组','服务器说明'],state='readonly', width=20)
        down.current(0)
        down.pack()
        lab2 = tk.Label(self.top, text="修改为：")
        lab2.pack()
        conten_entry = tk.Text(self.top, height=10, width=23)
        conten_entry.pack()


        btn = tk.Button(self.top, text="确定", width=10,command=edit_da)
        btn.pack(pady='5')
        btn2 = tk.Button(self.top, text="取消", width=10,command=self.top.destroy)
        btn2.pack(pady='5')

    # 删除服务器
    def delete_server(self):
        self.log.write_log_info('事件触发：删除主机')
        if self.server_tree.focus() == "":
            messagebox.showerror("Error", "请选择一个服务器")
            return
        # 获取当前选中的host
        host = self.server_tree.item(self.server_tree.focus())['values'][2]
        # 再次确认是否删除
        if messagebox.askyesno("警告", "确定删除主机" + host + "吗？"):
            self.log.write_log_info('主机: ' + host + '删除成功')
            self.server_tree.destroy
            self.init_server_data()
            self.db.delete_server(host)
            
    # 新建分组界面
    def add_folder_window(self):
        print("--" + self.group_tree.focus() +"--")
        self.log.write_log_info('事件触发：新建分组')
        self.top = tk.Toplevel()
        self.top.title("添加分组")
        self.top_master(self.top,200)
        # 锁定焦点
        self.top.grab_set()
        # 设置窗口宽高固定
        self.top.resizable(0,0)
        # 窗口置顶
        self.top.attributes('-topmost', 1)
        lab1 = tk.Label(self.top, text="添加位置：")
        lab1.pack()
        
        if self.group_tree.focus() == "":
            down = ttk.Combobox(self.top, values=['根节点'],state = 'readonly', width=20) 
        else:
            selected_text = self.group_tree.item(self.group_tree.focus())['text']
            down = ttk.Combobox(self.top, values=[selected_text],state='readonly', width=20)
            # down = ttk.Combobox(self.top, values=[self.group_tree.item(self.group_tree.focus())['text']],state='readonly', width=20)
        down.current(0)
        down.pack()
        lab2 = tk.Label(self.top, text="分组名称：")
        lab2.pack()
        name_entry = tk.Entry(self.top, width=23)
        name_entry.pack()
        qt_btn = tk.Button(self.top, text="确定", width=10,command=lambda: self.add_folder(name_entry.get(),
                                                                                            down.get()
                                                                                            )
                                                                                            )
        qt_btn.pack(pady='5')
        qx_btn = tk.Button(self.top, text="取消", width=10,command=self.top.destroy)
        qx_btn.pack(pady='5')

    # 新建分组
    def add_folder(self,name,local):
        try:
            if local == '根节点':
                self.log.write_log_info(local + '等于根节点，分组添加到根节点')
                parent_id = None
            else:
                selected_item = self.group_tree.focus()
                selected_item_name = self.group_tree.item(selected_item)['text']
                selected_item_id = self.db.get_group_id(selected_item_name)
                self.log.write_log_info('添加到当前节点下 : ' +  selected_item_name + ' ' + str(selected_item_id))
                parent_id = selected_item_id
            if name == '':
                messagebox.showerror('错误', '分组名称不能为空！')
                return

            # 查询分组是否已存在
            flag = self.db.exists(name, "groups")
            if flag:
                messagebox.showerror('错误', '分组已存在！')
                return

            # 将新节点ID存储到数据库
            self.db.add_group(name, parent_id)

            # 刷新分组列表
            self.group_tree.delete(*self.group_tree.get_children())
            self.init_groups_data()
            self.log.write_log_info('分组添加成功')

        except Exception as e:
            messagebox.showerror('错误', f'添加分组失败: {str(e)}')
            self.log.write_log_error(f'添加分组失败: {str(e)}')
        finally:
            self.top.destroy()
    # 删除分组
    def delete_group(self):
        self.log.write_log_info('事件触发：删除分组')
        # 警告确认
        if messagebox.askokcancel('删除分组', '确定删除分组？'):
            pass
        else:
            return
        selected_item = self.group_tree.focus()
        if selected_item == '':
            messagebox.showerror('错误', '请选择要删除的分组！')
            self.log.write_log_error('未选择分组，删除失败')
            return
        else:
            # 获取选中节点的ID
            selected_item_name = self.group_tree.item(selected_item)['text']
            parent_id = self.db.get_group_focus_id(selected_item_name)
            flag_group = self.db.check_group_in_groups(parent_id)
            if flag_group:
                messagebox.showerror('错误', '该分组下存在二级分组，删除失败！')
                return
            # 获取parent_id节点名字
            name = self.group_tree.item(selected_item)['text']
            self.log.write_log_info('删除的分组名是：' + name)
            # get当前分组id
            id = self.db.get_group_id(name)
            # 判断分组下是否有主机
            flag = self.db.check_group_has_servers(id)
            if flag:
                if messagebox.askokcancel('删除分组', '分组下存在主机，确定删除分组？'):
                    self.log.write_log_info('分组下存在主机，删除分组失败')
                    messagebox.showerror('错误', '分组下存在主机，删除失败！')
                    return
            else:
                self.log.write_log_info('该分组下不存在主机,分组删除成功' + parent_id + "," + name)
                print("删除的分组是： " + name)
                self.group_tree.delete(selected_item)
                self.db.delete_group(name)
                
                self.group_tree.destroy         # 刷新self.group_tree     

    # 搜索服务器
    def search_servers(self):
        content = self.search_entry.get()
        if content == '':
            messagebox.showerror('错误', '请输入要搜索的内容！')
        else:
            flag = self.too.is_ip(content)
            # 情况self.server_tree数据
            self.server_tree.delete(*self.server_tree.get_children())
            self.db.search_servers(content,flag,self.server_tree)

    # 分组右键事件
    def tree_right_click(self, event):
        self.group_tree.focus()  # 聚焦分组树形结构
        self.group_menu = tk.Menu(self.master, tearoff=0)
        self.group_menu.add_command(label='添加分组',command=self.add_folder_window)
        self.group_menu.add_command(label='删除分组',command=self.delete_group)
        self.group_menu.add_command(label='重命名分组',command=self.rename_group)
        self.group_menu.add_separator()
        self.group_menu.add_command(label='导入分组')
        self.group_menu.add_command(label='导出分组')        
        self.group_menu.post(event.x_root, event.y_root)  # 在鼠标位置显示菜单
    # 主机右键事件
    def Stree_right_click(self, event):
        self.server_tree.focus()    # 聚焦主机树形结构
        self.server_menu = tk.Menu(self.master, tearoff=0)
        self.server_menu.add_command(label='连接主机',command=lambda:self.too.thread_it(self.connect_server))
        self.server_menu.add_separator()
        self.server_menu.add_command(label='添加主机',command=self.add_server_window)
        self.server_menu.add_command(label='编辑主机',command=self.edit_server)
        self.server_menu.add_command(label='删除主机',command=self.delete_server)
        self.server_menu.add_separator()
        self.server_menu.add_command(label='显示全部主机',command=self.init_server_data)

        self.server_menu.post(event.x_root, event.y_root)   # 在鼠标位置显示菜单
    # group_tree 释放焦点事件
    def groupTree_release(self,event):
        print("--" + self.group_tree.focus() + "--")
        # 取消选中
        self.group_tree.selection_remove(self.group_tree.focus())
        # group_tree焦点设为空
        self.group_tree.focus("")
        print("--" + self.group_tree.focus() + "--")

    # server_tree 释放焦点事件
    def Stree_release(self,event):
        print("--" + self.server_tree.focus() + "--")
        # 取消选中
        self.server_tree.selection_remove(self.server_tree.focus())
        # server_tree焦点设为空
        self.server_tree.focus("")
        print("--" + self.server_tree.focus() + "--")

    # 重命名分组    
    def rename_group(self):
        self.log.write_log_info('事件触发：重命名分组')
        # 判断是否选中分组
        if self.group_tree.focus() == '':
            messagebox.showerror('错误', '请选择要重命名的分组！')
            self.log.write_log_error('未选择分组，重命名失败')
            return
        else:
            pass
           
    # 连接主机
    def connect_server(self):
        self.log.write_log_info('事件触发：连接主机')
        #获取选择的主机信息
        selected_item = self.server_tree.focus()
        if selected_item == '':
            messagebox.showerror('错误', '请选择要连接的主机！')
            self.log.write_log_error('未选择主机，连接失败')
            return
        connect_type = self.server_tree.item(selected_item)['values'][0]
        if connect_type == 'RDP':
            # name = self.server_tree.item(selected_item)['values'][1]
            host = self.server_tree.item(selected_item)['values'][2]
            port = self.server_tree.item(selected_item)['values'][3]
            # username = self.server_tree.item(selected_item)['values'][4]
            # password = self.db.get_server_password(name)
            self.too.run_mstsc(host,port)
        elif connect_type == 'SSH':
            host = self.server_tree.item(selected_item)['values'][2]
            port = self.server_tree.item(selected_item)['values'][3]
            username = self.server_tree.item(selected_item)['values'][4]
            password = self.db.get_server_password
            pass
        elif connect_type == 'VNC':
            host = self.server_tree.item(selected_item)['values'][2]
            port = self.server_tree.item(selected_item)['values'][3]
            pass
        elif connect_type == 'URL':
            host = self.server_tree.item(selected_item)['values'][2]
            # username = self.server_tree.item(selected_item)['values'][4]
            self.too.thread_it(self.too.open_browser,host)
        else:
            messagebox.showerror('错误', '不支持的连接类型，请联系系统管理员！')
                                                                                                                   
    # group_tree左键双击事件
    # def groupTree_click(self, event):
    #     self.server_tree.delete(*self.server_tree.get_children())
    #     self.log.write_log_info('事件触发：groupTree_click')
    #     # 获取group_tree的focus
    #     selected_item = self.group_tree.focus()
    #     if selected_item == '':
    #         messagebox.showerror('错误', '请选择要查看的分组！')
    #     else:
    #         # 获取parent_id节点名字
    #         name = self.group_tree.item(selected_item)['text']
    #         self.log.write_log_info('查看的分组名是：' + name)
    #         # get当前分组id
    #         id = self.db.get_group_id(name)
    #         res = self.db.get_servers_by_group_id(id)
    #         # 插入到server_tree中
    #         for r in res:
    #             self.server_tree.insert('', 'end',values=(r[1],r[2],r[3],r[4],r[5]))

    # server_tree焦点变更事件
    def on_selection_change(self, event):
        selected_item  = self.server_tree.selection()
        if selected_item:
            item = self.server_tree.item(selected_item)
            sever_host = item['values'][2]
            server_info = self.db.get_serverINFO_by_host(sever_host)
            self.server_info.delete(1.0, tk.END)
            self.server_info.insert(tk.END, server_info)
            # 刷新server_info
            print(self.server_info.get(1.0, tk.END))   
            self.server_info.update()

    # group_tree焦点变更事件
    def on_group_selection_change(self, event):
        selected_item  = self.group_tree.selection()
        print(selected_item)
        if selected_item:
            item = self.group_tree.item(selected_item)
            group_name = item['text']
            group_id = self.db.get_group_id(group_name)
            if self.db.check_group_has_servers(group_id):
                self.server_tree.delete(*self.server_tree.get_children())
                res = self.db.get_servers_by_group_id(group_id)
                for r in res:
                    self.server_tree.insert('', 'end',values=(r[1],r[2],r[3],r[4],r[5],r[6]))


    # self.top的位置 添加主机用
    def top_master(self,top,height):
        # 获取主窗口的位置和尺寸
        master_x = self.master.winfo_rootx()
        master_y = self.master.winfo_rooty()
        master_width = self.master.winfo_width()
        master_height = self.master.winfo_height()

        # 设置弹出窗口的大小
        popup_width = 250
        popup_height = height

        # 计算弹出窗口的中心位置
        popup_x = master_x + (master_width // 2) - (popup_width // 2)
        popup_y = master_y + (master_height // 2) - (popup_height // 2)
        # 设置弹出窗口的大小和位置
        return top.geometry(f'{popup_width}x{popup_height}+{popup_x}+{popup_y}')
    


