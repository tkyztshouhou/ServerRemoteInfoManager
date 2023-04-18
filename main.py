# -*- coding: utf-8 -*-

import re
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from sqlite3 import Error
import time
import csv
import os
import threading
import subprocess
from datetime import datetime

import pythonping as pythonping

'''
   Time:2023
   Author:LiuS
   version: V0.1 
   Describe:A server remote information management tool developed by Tkinter
'''


# 多线程序
def thread_it(func, *args):
    '''将函数打包进线程'''
    # 创建
    t = threading.Thread(target=func, args=args)
    # 守护 !!!
    t.setDaemon(True)
    # 启动
    t.start()
    # 阻塞--卡死界面！
    # t.join()

# 创建主窗口
class RemoteDesktop:
    def __init__(self, master):
        self.master = master
        self.master.title("远程连接运维管理助手    V0.1    2023     【精品工程 精益求精】")
        self.master.geometry('1280x720+50+0')
        self.master.iconphoto(True, tk.PhotoImage(file='./img/top.png'))
        # self.master.config(bg='#FBF0DF')  # 设置背景颜色
        # 设置窗口宽高固定
        self.master.resizable(0, 0)
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

        self.create_widgets()
        self.create_database()
        self.show_servers_data()

        # 将列表控件绑定双击事件，以便实现编辑功能
        self.group_tree.bind('<Button-3>', self.show_group_menu)
        self.server_tree.bind('<Button-3>', self.show_server_menu)

    # 创建菜单栏
    # def create_menu(self):
    #     menu_bar = tk.Menu(self.master)
    #     # 添加分组菜单
    #     group_menu = tk.Menu(menu_bar, tearoff=0)
    #     group_menu.add_command(label='添加分组', command=self.add_server)
    #     group_menu.add_command(label='删除分组', command=self.add_server)
    #     menu_bar.add_cascade(label='分组', menu=group_menu)
    #     # 添加主机菜单
    #     server_menu = tk.Menu(menu_bar, tearoff=0)
    #     server_menu.add_command(label='添加主机', command=self.add_server)
    #     server_menu.add_command(label='编辑主机', command=self.edit_server)
    #     server_menu.add_command(label='删除主机', command=self.delete_server)
    #     menu_bar.add_cascade(label='主机', menu=server_menu)
    #     # 连接菜单
    #     connect_menu = tk.Menu(menu_bar, tearoff=0)
    #     connect_menu.add_command(label='远程桌面', command=self.add_server)
    #     connect_menu.add_command(label='radmin', command=self.add_server)
    #     connect_menu.add_command(label='Xshell', command=self.add_server)
    #     menu_bar.add_cascade(label='连接', menu=connect_menu)
    #     # 设置菜单
    #     setting_menu = tk.Menu(menu_bar, tearoff=0)
    #     setting_menu.add_command(label='系统选项', command=self.add_server)
    #     menu_bar.add_cascade(label='设置', menu=setting_menu)
    #     self.master.config(menu=menu_bar)

    # 创建主窗口
    def create_widgets(self):
        # 在此创建主窗口的控件
        # 创建菜单栏
        # self.create_menu()
        # 创建按钮功能区
        btn_frame = tk.Frame(self.master)
        btn_frame.pack(side=tk.TOP,fill=tk.X)
        self.tjfz_btn = tk.Button(btn_frame, bd=0,relief=tk.GROOVE, image=self.fz, command=self.add_login)
        self.tjfz_btn.pack(side=tk.LEFT,padx=15)
        self.scfz_btn = tk.Button(btn_frame, bd=0,relief=tk.GROOVE, image=self.scfz, command=self.delete_group)
        self.scfz_btn.pack(side=tk.LEFT,padx=15)
        self.tjzj_btn = tk.Button(btn_frame, bd=0,relief=tk.GROOVE, image=self.tjzj, command=self.top2_Gui)
        self.tjzj_btn.pack(side=tk.LEFT,padx=15)
        self.bjzj_btn = tk.Button(btn_frame, bd=0,relief=tk.GROOVE, image=self.bjzj, command=self.add_server)
        self.bjzj_btn.pack(side=tk.LEFT,padx=15)
        self.sczj_btn = tk.Button(btn_frame, bd=0,relief=tk.GROOVE, image=self.sczj, command=self.delete_server)
        self.sczj_btn.pack(side=tk.LEFT,padx=15)
        self.lj_btn = tk.Button(btn_frame, bd=0,relief=tk.GROOVE, image=self.lj, command=self.add_server)
        self.lj_btn.pack(side=tk.LEFT,padx=15)
        self.mstsc_btn = tk.Button(btn_frame, bd=0,relief=tk.GROOVE, image=self.mstsc, command=lambda: thread_it(self.openMstsc))
        self.mstsc_btn.pack(side=tk.LEFT,padx=15)
        self.radmin_btn = tk.Button(btn_frame, bd=0,relief=tk.GROOVE, image=self.radmin, command=self.add_server)
        self.radmin_btn.pack(side=tk.LEFT,padx=15)
        self.ssh_btn = tk.Button(btn_frame, bd=0,relief=tk.GROOVE, image=self.ssh, command=self.add_server)
        self.ssh_btn.pack(side=tk.LEFT,padx=15)
        self.sz_btn = tk.Button(btn_frame, bd=0,relief=tk.GROOVE, image=self.sz, command=self.add_server)
        self.sz_btn.pack(side=tk.LEFT,padx=15)

        # 创建分组、服务器列表、搜索、说明控件框架
        center_frame = tk.Frame(self.master)
        center_frame.pack(side=tk.LEFT,fill=tk.BOTH)

        # 创建分组树形结构
        group_frame = tk.Frame(center_frame)
        group_frame.pack(side=tk.LEFT,fill=tk.Y,padx=5, pady=5)
        self.group_tree = ttk.Treeview(group_frame,show='tree')
        self.group_tree.pack(side=tk.LEFT, fill=tk.Y)
        # self.group_tree.column('#0')

        # 创建滚动条
        scrollbar = ttk.Scrollbar(group_frame, orient=tk.VERTICAL, command=self.group_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.group_tree.configure(yscrollcommand=scrollbar.set)

        # 创建服务器列表
        server_frame = tk.Frame(center_frame)
        server_frame.pack(fill=tk.BOTH)
        self.server_tree = ttk.Treeview(server_frame, columns=('type', 'name', 'domain', 'port', 'account', 'status'),
                                        height=18,show='headings')
        self.server_tree.pack(side=tk.LEFT)
        self.server_tree.column('type', width=100, anchor='center')
        self.server_tree.column('name', width=210, anchor='center')
        self.server_tree.column('domain', width=170, anchor='center')
        self.server_tree.column('port', width=100, anchor='center')
        self.server_tree.column('account', width=160, anchor='center')
        self.server_tree.column('status', width=100, anchor='center')
        self.server_tree.heading('type', text='类型')
        self.server_tree.heading('name', text='名称')
        self.server_tree.heading('domain', text='域名/IP')
        self.server_tree.heading('port', text='端口')
        self.server_tree.heading('account', text='账号')
        self.server_tree.heading('status', text='状态')
        # self.server_tree.bind('', self.add_server())  # 绑定右键菜单事件
        # self.server_tree.bind('', self.edit_server)  # 绑定双击编辑事件
        self.server_tree.tag_configure('offline', background='#FF9999')  # 设置离线状态颜色
        self.server_tree.tag_configure('online', background='#99FF99')  # 设置在线状态颜色
        self.server_tree.tag_configure('unknown', background='#FFFF99')  # 设置未知状态颜色

        # 创建滚动条
        scrollbar = ttk.Scrollbar(server_frame, orient=tk.VERTICAL, command=self.server_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.server_tree.configure(yscrollcommand=scrollbar.set)

        # 创建搜索和说明
        so_frame = tk.Frame(center_frame)
        so_frame.pack(pady=5,fill=tk.BOTH)
        self.so = tk.Label(so_frame, text='请输入主机名字或者域名(IP)检索：')
        self.so.grid(row=0,column=0)
        self.sta = tk.Entry(so_frame, width=50)
        self.sta.grid(row=0,column=1)
        self.sota = tk.Button(so_frame,text="检索",width=10,command=self.search_servers)
        self.sota.grid(row=0,column=2)
        self.beizhu = tk.Label(so_frame, text='👇 其 他 信 息：')
        self.beizhu.grid(row=1,column=0)
        # 创建车站信息显示框
        self.station_info = tk.Label(so_frame, borderwidth = 1,relief="sunken",bg='white',fg='black',width=120,height=11,
                                     font=("微软雅黑", 9),text='')
        self.station_info.grid(row=4,column=0,columnspan=3)


        # 创建右侧远程功能选项区域
        rdpXx_frame = tk.Frame(self.master)
        rdpXx_frame.pack(side=tk.RIGHT,fill=tk.Y, pady=5)

        self.rdp_btn = tk.Button(rdpXx_frame, bd=0,width=220, image=self.rdp)
        self.rdp_btn.grid(row=1,column=0)
        self.ping_btn = tk.Button(rdpXx_frame, height=2,bd=2,font=("微软雅黑",12),
                                  text='在线检测', command=self.check_server_status)
        self.ping_btn.grid(row=2,column=0,pady=15)

        self.rlab2 = tk.Label(rdpXx_frame,text='👇 RDP 选项：',font=("微软雅黑",14))
        self.rlab2.grid(row=6,column=0,pady=10)


        # 创建状态栏
        # status_var = tk.StringVar()
        # status_var.set('就绪')
        # status_bar = tk.Label(self.master, textvariable=status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        # status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        # self.status_var = status_var
        # self.status_bar = status_bar
        # 创建数据库
        self.create_database()
        # 加载分组和主机列表
        self.load_group_list()
        # self.load_server_list()

    # 创建数据库
    def create_database(self):
        # 创建名为rdp_db的数据库，用于存储远程桌面连接数据
        try:
            self.conn = sqlite3.connect('rdp_db.db')
            self.cursor = self.conn.cursor()
            self.cursor.execute('''
                    CREATE TABLE IF NOT EXISTS servers (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        conn_type TEXT,
                        name TEXT NOT NULL,
                        host TEXT NOT NULL
                                  UNIQUE,
                        port INTEGER,
                        username TEXT,
                        password TEXT,
                        status TEXT,
                        ParentId INT
                    )
            ''')
            self.cursor.execute('''
                    CREATE TABLE  IF NOT EXISTS GroupTab (
                        id       INTEGER   PRIMARY KEY AUTOINCREMENT,
                        Name     CHAR (64) NOT NULL,
                        ParentId INT   NOT NULL
                    )
            ''')
            self.cursor.execute('''
                    CREATE TABLE  IF NOT EXISTS station_basic (
                        bureau_code  CHAR (1),
                        station_name VARCHAR (20),
                        info         VARCHAR (40) 
                    );
            ''')
        except Error as e:
            print('GroupTab 表已存在')
        finally:
            self.conn.close()

    # 显示数据库中的远程桌面连接数据
    def show_servers_data(self):
        # 显示数据库中的远程桌面连接数据到列表控件中
        try:
            self.conn = sqlite3.connect('rdp_db.db')
            self.cursor = self.conn.cursor()
            self.cursor.execute('SELECT conn_type, name, host, port, username FROM servers')
            rows = self.cursor.fetchall()
            for row in rows:
                self.server_tree.insert("", "end", values=row)
        except Error as e:
            messagebox.showerror("错误", e)
        finally:
            self.conn.close()

    # 添加远程桌面连接数据
    def add_server(self,conn_type, name, host, port, username, password, parent_id):
        # 获取需要添加的远程桌面连接数据
        # conn_type = conn_type
        # name = name
        # host = host
        # port = port
        # username = username
        # password = password
        # parent_id = parent_id

        # 将远程连接名称和主机名拼接作为数据表中的name字段
        # name = f"{name}({host})"

        # 将主机组名转化为数据库中的group_id
        try:
            self.conn = sqlite3.connect('rdp_db.db')
            self.cursor = self.conn.cursor()
            # self.cursor.execute(f"SELECT id FROM GroupTab WHERE name='{name}'")
            # group_id = self.cursor.fetchone()

            # if group_id:
            #     group_id = group_id[0]
            # else:
            #     # 如果该组名不存在，则新建该组并获取其id
            #     self.cursor.execute(f"INSERT INTO groups(name) VALUES('{group_name}')")
            #     self.cursor.execute(f"SELECT id FROM groups WHERE name='{group_name}'")
            #     group_id = self.cursor.fetchone()[0]

            # 将远程桌面连接数据存入数据库
            self.cursor.execute(
                f"INSERT INTO servers(conn_type, name, host, port, username, password, ParentId) VALUES('{conn_type}', '{name}', '{host}', {port}, '{username}', '{password}', '{parent_id}')")
            self.conn.commit()

            # 在列表控件中添加新数据
            server_data = (conn_type, name, host, port, username)
            self.server_tree.insert("", "end", values=server_data)
            messagebox.showinfo("提示", "添加成功！")
        except Error as e:
            messagebox.showerror("错误", e)
        finally:
            self.conn.close()

    # 编辑远程桌面连接数据
    def edit_server(self, event):
        # 获取被双击选中的远程桌面连接数据
        item = self.tree.selection()[0]
        selected_data = self.tree.item(item, "values")

        try:
            self.conn = sqlite3.connect('rdp_db.db')
            self.cursor = self.conn.cursor()
            self.cursor.execute(f"SELECT name FROM groups WHERE id={selected_data[0]}")
            group_name = self.cursor.fetchone()[0]
        except Error as e:
            messagebox.showerror("错误", e)
        finally:
            self.conn.close()

            # 将选中数据的值赋值给各控件
            self.combobox.set(group_name)
            self.conn_type_var.set(selected_data[1])
            name, host = selected_data[2].split("(")
            self.name_entry.delete(0, "end")
            self.name_entry.insert(0, name)
            self.host_entry.delete(0, "end")
            self.host_entry.insert(0, host[:-1])
            self.port_entry.delete(0, "end")
            self.port_entry.insert(0, selected_data[4])
            self.username_entry.delete(0, "end")
            self.username_entry.insert(0, selected_data[5])
            self.password_entry.delete(0, "end")
            self.password_entry.insert(0, selected_data[6])

            # 创建弹窗，让用户进行编辑操作
            edit_window = tk.Toplevel()
            edit_window.title("编辑远程桌面连接")
            edit_window.geometry("400x300")
            self.create_edit_widgets(edit_window)

            # 将原始数据的id和选中的行在列表中的索引保存下来，以便修改后更新列表
            self.edit_id = selected_data[0]
            self.edit_item = item

    def save_edited_server(self):
        # 获取修改后的远程桌面连接数据
        group_name = self.edit_combobox.get()
        conn_type = self.edit_conn_type_var.get()
        name = self.edit_name_entry.get()
        host = self.edit_host_entry.get()
        port = self.edit_port_entry.get()
        username = self.edit_username_entry.get()
        password = self.edit_password_entry.get()

        # 将修改后的远程桌面连接名称和主机名拼接作为数据表中的name字段
        name = f"{name}({host})"

        # 将主机组名转化为数据库中的group_id
        try:
            self.conn = sqlite3.connect('rdp_db.db')
            self.cursor = self.conn.cursor()
            self.cursor.execute(f"SELECT id FROM groups WHERE name='{group_name}'")
            group_id = self.cursor.fetchone()

            if group_id:
                group_id = group_id[0]
            else:
                # 如果该组名不存在，则新建该组并获取其id
                self.cursor.execute(f"INSERT INTO groups(name) VALUES('{group_name}')")
                self.cursor.execute(f"SELECT id FROM groups WHERE name='{group_name}'")
                group_id = self.cursor.fetchone()[0]

            # 更新数据库中的数据
            self.cursor.execute(
                f"UPDATE servers SET group_id={group_id}, conn_type='{conn_type}', name='{name}', host='{host}', port={port}, username='{username}', password='{password}' WHERE id={self.edit_id}")
            self.conn.commit()

            # 更新列表控件中的数据
            self.tree.item(self.edit_item, values=(group_id, conn_type, name, host, port, username, password))

            messagebox.showinfo("提示", "修改成功！")
        except Error as e:
            messagebox.showerror("错误", e)
        finally:
            self.conn.close()

    # 删除远程桌面连接数据
    def delete_server(self):
        # 获取被选中的远程桌面连接数据
        items = self.server_tree.focus()
        if not items:
            messagebox.showwarning("提示", "请选择需要删除的服务器数据！")
            return

        if messagebox.askyesno("确认", "确定要删除所选的服务器数据吗？"):
            # 获取当前选中的节点
            selected_item = self.server_tree.selection()
            try:
                self.conn = sqlite3.connect('rdp_db.db')
                self.cursor = self.conn.cursor()

                # 删除数据库中的数据
                for item in selected_item:
                    item_text = self.server_tree.item(selected_item,"values")
                    print(item)
                    # self.cursor.execute(f"DELETE FROM servers WHERE id={self.server_tree.item(item, 'values')[0]}")
                    self.cursor.execute(f"DELETE FROM servers WHERE host = '%s'"%(item_text[2]))


                self.conn.commit()

                # 删除列表控件中的数据
                self.server_tree.delete(items)

                messagebox.showinfo("提示", "删除成功！")
            except Error as e:
                messagebox.showerror("错误", e)
            except Exception as e:
                messagebox.showerror("错误", e)
            finally:
                self.conn.close()

    # 搜索远程桌面连接数据
    def search_servers(self):
        # 获取搜索关键字
        keyword = self.sta.get()
        if not keyword:
            # 如果关键字为空，则显示全部数据
            self.show_servers_data()
            return

        try:
            self.conn = sqlite3.connect('rdp_db.db')
            self.cursor = self.conn.cursor()
            self.cursor.execute("SELECT name FROM servers WHERE name LIKE '%s' "%(self.sta.get()))
            rows = self.cursor.fetchall()

            # 清空列表控件内容
            self.server_tree.delete(*self.group_tree.get_children())
        except Exception as e:
            messagebox.showerror("错误", e)
        finally:
            self.conn.close()

    # 显示分组右键菜单
    def show_group_menu(self, event):
        self.group_tree.focus()  # 聚焦分组树形结构
        self.group_menu = tk.Menu(self.master, tearoff=0)
        self.group_menu.add_command(label='添加分组',command=self.add_login)
        self.group_menu.add_command(label='删除分组',command=self.delete_group)
        self.group_menu.add_command(label='重命名分组')
        self.group_menu.add_separator()
        self.group_menu.add_command(label='导入分组')
        self.group_menu.add_command(label='导出分组')
        self.group_menu.post(event.x_root, event.y_root)  # 在鼠标位置显示菜单

    # 显示服务器右键菜单
    def show_server_menu(self, event):
        self.server_tree.focus()  # 聚焦服务器列表
        self.server_menu = tk.Menu(self.master, tearoff=0)
        self.server_menu.add_command(label='连接主机')
        self.server_menu.add_separator()
        self.server_menu.add_command(label='添加主机', command=self.top2_Gui)
        self.server_menu.add_command(label='编辑主机', command=self.edit_server)
        self.server_menu.add_command(label='删除主机', command=self.delete_server)
        self.server_menu.post(event.x_root, event.y_root)  # 在鼠标位置显示菜单

    # 加载分组列表
    def load_group_list(self):
        # 清空分组树形结构
        for item in self.group_tree.get_children():
            self.group_tree.delete(item)
        # 查询分组列表
        conn = sqlite3.connect('rdp_db.db')
        c = conn.cursor()
        c.execute("SELECT * FROM GroupTab")
        rows = c.fetchall()
        conn.close()
        # 添加分组到分组树形结构
        for row in rows:
            node_id = row[0]
            name = row[1]
            parent_id = row[2]
            parent = "" if parent_id == 0 else f"{parent_id}"
            self.group_tree.insert(parent, "end", node_id,image = self.folde, text=name)
    # 添加文件夹分组
    # def add_folder(self):
    #     # 获取当前选中的节点
    #     self.selected_item = self.group_tree.focus()
    #     # 如果没有选中节点，则默认添加到根节点
    #     if not self.selected_item:
    #         parent_id = 0
    #         # 创建窗口
    #         top = tk.Toplevel()
    #         top.title("添加分组")
    #         top.geometry('300x150+200+200')
    #         # 设置窗口宽高固定
    #         top.resizable(0, 0)
    #         lab1 = tk.Label(top, text="添加到分组：")
    #         lab1.pack()
    #         down_menu = tk.StringVar()
    #         down = ttk.Combobox(top, width=20,state='readonly', textvariable=down_menu)  # #创建下拉菜单
    #         # 下拉列表取值
    #         down["value"] = '根节点'
    #         down.current(0)
    #         down.pack()
    #         lab2 = tk.Label(top, text="分组名称：")
    #         lab2.pack()
    #         name_entry = tk.Entry(top, width=23)
    #         name_entry.pack()
    #         qt_btn = tk.Button(top, text="确定", command=lambda: self.add_new_node(name_entry.get()))
    #         qt_btn.pack()
    #     else:
    #         # 获取选中节点的ID
    #         # self.parent_id = self.item(self.selected_item)["id"]
    #         # self.seletc_name = self.item(self.selected_item, "values")
    #         # 创建窗口
    #         # 查询分组列表
    #         conn = sqlite3.connect('rdp_db.db')
    #         c = conn.cursor()
    #         c.execute("SELECT Name FROM GroupTab")
    #         groups = c.fetchall()
    #         conn.close()
    #         groups.append('根节点')
    #         top = tk.Toplevel()
    #         top.title("添加分组")
    #         top.geometry('300x150+200+200')
    #         # 设置窗口宽高固定
    #         top.resizable(0, 0)
    #         lab1 = tk.Label(top, text="添加到分组：")
    #         lab1.pack()
    #         down_menu = tk.StringVar()
    #         down = ttk.Combobox(top, width=20,state='readonly', textvariable=down_menu)  # #创建下拉菜单
    #         # 下拉列表取值
    #         down["value"] = groups
    #         down.current(0)
    #         down.pack()
    #         lab2 = tk.Label(top, text="分组名称：")
    #         lab2.pack()
    #         name_entry = tk.Entry(top, width=23)
    #         name_entry.pack()
    #         qt_btn = tk.Button(top, text="确定", command=lambda: self.add_new_node(name_entry.get()))
    #         qt_btn.pack()
    #
    # def add_new_node(self,name):
    #     if not self.selected_item:
    #         # 将新节点ID存储到数据库
    #         conn = sqlite3.connect("rdp_db.db")
    #         c = conn.cursor()
    #         c.execute("INSERT INTO GroupTab (Name, ParentId) VALUES (?, ?)", (name, 0))
    #         new_id = c.lastrowid
    #         conn.commit()
    #         conn.close()
    #     else :
    #         # 将新节点ID存储到数据库
    #         conn = sqlite3.connect("rdp_db.db")
    #         c = conn.cursor()
    #         c.execute("INSERT INTO GroupTab (Name, ParentId) VALUES (?, ?)", (name, 1))
    #         new_id = c.lastrowid
    #         conn.commit()
    #         conn.close()
    #     # 在当前选中节点下创建新节点
    #     selected_item = self.group_tree.focus()
    #     self.group_tree.insert(selected_item,"end",image = self.folde,text=name)

    # 添加分组按钮的回调函数

    # 创建添加分组界面
    # 添加分组界面
    # 添加分组界面
    def add_login(self):
        # 创建窗口
        self.top = tk.Toplevel()
        self.top.title("添加分组")
        self.top.geometry('250x50+400+80')
        # 设置窗口宽高固定
        self.top.resizable(0,0)
        lab2 = tk.Label(self.top, text="分组名称：")
        lab2.grid(row=0,column=1)
        name_entry = tk.Entry(self.top, width=23)
        name_entry.grid(row=0,column=2)
        qt_btn = tk.Button(self.top, text="确定", width=10,command=lambda: self.add_folder(name_entry.get()))
        qt_btn.grid(row=1,column=1,columnspan=2)

    # 添加分组
    def add_folder(self,name):
        try:
            self.top.destroy()
            # 获取当前选中的节点
            selected_item = self.group_tree.focus()
            # 如果没有选中节点，则默认添加到根节点
            if not selected_item:
                parent_id = 0
            else:
                # 获取选中节点的ID
                # parent_id = self.group_tree.item(selected_item)["id"]
                parent_id = selected_item
            if name == '':
                messagebox.showerror('错误', '分组名称不能为空！')
            else:
                # 查询分组是否已存在
                conn = sqlite3.connect('rdp_db.db')
                c = conn.cursor()
                c.execute("SELECT * FROM GroupTab WHERE Name=?", (name,))
                group = c.fetchone()
                if group:
                    messagebox.showerror('错误', '分组已存在！')
                else:
                    # 在treeview中添加新的节点
                    new_item = self.group_tree.insert(selected_item, "end",image = self.folde, text=name)
                    # 将新节点ID存储到数据库
                    conn = sqlite3.connect("rdp_db.db")
                    c = conn.cursor()
                    c.execute("INSERT INTO GroupTab (Name, ParentId) VALUES (?, ?)", (name, parent_id))
                    new_id = c.lastrowid
                    conn.commit()
                    conn.close()
                    # 设置新节点的ID属性
                    self.group_tree.set(new_item, "id", new_id)
        except Exception as e:
            print(e)
        finally:
            pass

    # 添加编辑主机GUI界面
    def top2_Gui(self):
        try:
            # 获取当前选中的节点
            selected_item = self.group_tree.focus()
            # 如果没有选中节点，则默认添加到根节点
            if not selected_item:
                parent_id = 0
            else:
                # 获取选中节点的ID
                # parent_id = self.group_tree.item(selected_item)["id"]
                parent_id = selected_item
            # 创建窗口
            self.top1 = tk.Toplevel()
            self.top1.title("新增主机")
            self.top1.geometry('260x180+400+40')
            # 设置窗口宽高固定
            self.top1.resizable(0,0)
            lab = tk.Label(self.top1, text="连接方式：")
            lab.grid(row=0,column=0)
            down_menu = tk.StringVar()
            down = ttk.Combobox(self.top1, width=20,state='readonly', textvariable=down_menu,values=['RDP','VNC','SSH'])  # #创建下拉菜单
            down.grid(row=0,column=1)
            lab2 = tk.Label(self.top1, text="主机名：")
            lab2.grid(row=2,column=0)
            name_entry = tk.Entry(self.top1, width=23)
            name_entry.grid(row=2,column=1)
            lab3 = tk.Label(self.top1, text="主机IP：")
            lab3.grid(row=3,column=0)
            ip_entry = tk.Entry(self.top1, width=23)
            ip_entry.grid(row=3,column=1)
            lab4 = tk.Label(self.top1, text="主机端口：")
            lab4.grid(row=4,column=0)
            port_entry = tk.Entry(self.top1, width=23)
            port_entry.grid(row=4,column=1)
            lab5 = tk.Label(self.top1, text="主机用户名：")
            lab5.grid(row=5,column=0)
            user_entry = tk.Entry(self.top1, width=23)
            user_entry.grid(row=5,column=1)
            lab6 = tk.Label(self.top1, text="远程密码：")
            lab6.grid(row=6,column=0)
            pwd_entry = tk.Entry(self.top1, width=23)
            pwd_entry.grid(row=6,column=1)
            qt_btn = tk.Button(self.top1, text="确定", width=10,command=lambda: self.add_server(
                                                                                              down.get(),
                                                                                              name_entry.get(),
                                                                                              ip_entry.get(),
                                                                                              port_entry.get(),
                                                                                              user_entry.get(),
                                                                                              pwd_entry.get(),
                                                                                              parent_id
                                                                                              ))
            qt_btn.grid(row=8,column=1,columnspan=1)

        except Exception as e:
            print(e)
        finally:
            pass

    # 检测主机连通状态
    def check_server_status(self):
        col_data = []
        for item in self.server_tree.get_children():
            values = self.server_tree.item(item)["values"]
            col_data.append(values[2])

            for ip in col_data:
                try:
                    # 执行ping命令
                    ping_process = pythonping.ping(ip, timeout=1, count=1)
                    # 判断Ping是否成功，成功为True，失败为False
                    success = ping_process.success()
                except pythonping.PingError as e:
                    # Ping失败，将结果设为False
                    success = False
                    # 输出Ping异常信息
                    print(f"Ping {ip} error: {e}")
                print(success)

                # 将新的数据插入到该行的最后一列中
                values.append(success)
                # 更新该行数据
                self.server_tree.item('',item,values=values)
            # self.server_tree.insert('', I001, values=('','','','','', success))  # 插入空值以占据第一列表头所在的位置

    # 运行远程桌面
    def openMstsc(self):
        os.system('C:\Windows\system32\mstsc.exe')

    # 删除分组
    def delete_group(self):
        try:
            # 获取被选中的远程桌面连接数据
            # items = self.group_tree.focus()
            # if not items:
            #     messagebox.showwarning("提示", "请选择需要删除的分组数据！")
            #     return

            item = self.group_tree.selection()[0]  # 获取当前选中的分组
            # if self.group_tree.item(item, 'values')[0] == 'group':  # 判断是否为分组
            group_name = self.group_tree.item(item, 'text')
            # 确认删除分组
            if messagebox.askokcancel('确认', '确定要删除分组及其下的主机吗？'):
                # 删除分组下的服务器
                conn = sqlite3.connect('rdp_db.db')
                c = conn.cursor()
                c.execute("select ParentId from GroupTab  WHERE Name = ?", (group_name,))
                id1 = c.fetchone()
                conn.commit()

                c.execute("DELETE FROM servers WHERE ParentId=?", (id1,))
                conn.commit()
                # 删除分组
                c.execute("DELETE FROM GroupTab WHERE Name=?", (group_name,))
                conn.commit()
                conn.close()
                messagebox.showinfo('提示', '删除分组成功！')
                self.load_group_list()
                self.show_servers_data()
        except Exception as e:
            messagebox.showerror("错误",e)
            print(e)
        finally:
            pass

root = tk.Tk()
RemoteDesktop(root)
root.mainloop()