import os
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import colorchooser
from Object.gui_DA import *
from tools.logs import logs
from tools.tool import too
from PIL import Image, ImageDraw, ImageFont, ImageTk


'''
    @ Author: LiuShan
    @ Date: 2024.09.04
    @ Description: 主机运维管理工具类
'''

# 创建主窗口
class infoServer:
    def __init__(self, master):
        self.master = master    # 窗口
        # 从 version.txt 读取版本号
        try:
            version_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'version.txt')
            with open(version_path, 'r') as f:
                version = f.read().strip()
        except Exception:
            version = 'V1.0.20250124'
        self.master.title(f"主机运维管理工具    {version} -LiuShan")
        self.master.geometry('1280x720+50+0')   #将该行代码修改为分辨率可自定义调整窗口大小
        self.master.resizable(width=True, height=True)
        # B18: 使用绝对路径加载图标，避免工作目录不在项目根目录时找不到图片
        self._img_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'img')
        self.master.iconphoto(True, tk.PhotoImage(file=os.path.join(self._img_dir, 'top.png')))
        # B19: 使用项目根目录绝对路径，避免 os.getcwd() 依赖启动目录
        self._project_root = os.path.dirname(os.path.abspath(__file__))
        self.db_path = os.path.join(self._project_root, 'data.db')
        self.db = DataAccess(self.db_path)
        self.log = logs()
        self.too = too(self.db_path)
        

        # 创建图片 - B18: 使用绝对路径
        self.fz = tk.PhotoImage(file=os.path.join(self._img_dir, 'fz.png'))
        self.scfz = tk.PhotoImage(file=os.path.join(self._img_dir, 'scfz.png'))
        self.tjzj = tk.PhotoImage(file=os.path.join(self._img_dir, 'tjzj.png'))
        self.bjzj = tk.PhotoImage(file=os.path.join(self._img_dir, 'bjzj.png'))
        self.sczj = tk.PhotoImage(file=os.path.join(self._img_dir, 'sczj.png'))
        self.lj = tk.PhotoImage(file=os.path.join(self._img_dir, 'lj.png'))
        self.mstsc = tk.PhotoImage(file=os.path.join(self._img_dir, 'mstsc.png'))
        self.radmin = tk.PhotoImage(file=os.path.join(self._img_dir, 'radmin.png'))
        self.ssh = tk.PhotoImage(file=os.path.join(self._img_dir, 'ssh.png'))
        self.sz = tk.PhotoImage(file=os.path.join(self._img_dir, 'sz.png'))
        self.rdp = tk.PhotoImage(file=os.path.join(self._img_dir, 'rdp.png'))
        self.folde = tk.PhotoImage(file=os.path.join(self._img_dir, 'FolderEmpty16x16.png'))
        self.folde_open = tk.PhotoImage(file=os.path.join(self._img_dir, 'FolderOpen16x16.png'))
        # Font Awesome 图标（由 _init_fa_icons 动态生成）
        self._fa_icons = {}
        self._fa_font = None

        self.create_widgets()   # 初始化控件
        self.create_database()  # 初始化数据库

        self._init_fa_icons()
        self.init_groups_data()
        self.init_server_data()
        self.load_settings()

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
        self.left_frame.pack_propagate(1)               # 允许内部控件影响外层控件大小 (1=True)
        self.right_frame = tk.Frame(self.master, bg='#F0F0F0')
        self.right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True,padx=10, pady=10)
        self.right_frame.pack_propagate(0)

        # top
        self.top_frame = tk.Frame(self.top, bg='#F0F0F0')
        self.top_frame.pack(side=tk.LEFT, fill=tk.Y)     # 填充 横向
        self.top_frame.pack_propagate(1)                # 允许内部控件影响外层控件大小 (1=True)

        self.top_R = tk.Frame(self.top, bg='#F0F0F0')
        self.top_R.pack(side=tk.LEFT, fill=tk.Y)     # 填充 横向
        self.top_R.pack_propagate(1)                # 允许内部控件影响外层控件大小 (1=True)

        # 创建右侧服务器列表框架，右侧区域分为上下两部分，上方显示服务器信息，下方显示服务器详细信息
        self.right_frame_top = tk.Frame(self.right_frame, bg='#F0F0F0') # 填充 纵向
        self.right_frame_top.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.right_frame_top.pack_propagate(0)                  # 禁止内部控件影响外层控件大小 (0=False)

        self.right_frame_bottom = tk.Frame(self.right_frame, bg='#F0F0F0')  # 填充 纵向
        self.right_frame_bottom.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True,pady=5)
        self.right_frame_bottom.pack_propagate(0)                    # 禁止内部控件影响外层控件大小 (0=False)
        
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
        # B21: 搜索按钮已注释掉，保留注释代码以便后续恢复
        # self.top_frame_button_6 = tk.Button(self.top_frame,  bd=0, image=self.sz, compound=tk.LEFT, bg='#F0F0F0',  command=self.search_servers)
        # self.top_frame_button_6.pack(side=tk.LEFT, padx=30,pady=10)
        self.top_frame_button_7 = tk.Button(self.top_frame,  bd=0, image=self.mstsc, compound=tk.LEFT, bg='#F0F0F0',  command=lambda:self.too.thread_it(self.too.open_mstsc))
        self.top_frame_button_7.pack(side=tk.LEFT, padx=30,pady=1)

        # 设置按钮（sz.png）
        self.top_frame_button_8 = tk.Button(self.top_frame,  bd=0, image=self.sz, compound=tk.LEFT, bg='#F0F0F0',  command=self.open_settings)
        self.top_frame_button_8.pack(side=tk.LEFT, padx=30,pady=1)

        # 创建分组列表
        self.group_tree = ttk.Treeview(self.left_frame,show='tree')
        self.group_tree.pack(side = tk.LEFT,fill=tk.Y, expand=True)   # 填充 纵向 边距10
        # 绑定展开/折叠事件，持久化状态
        self.group_tree.bind('<<TreeviewOpen>>', self._save_group_state)
        self.group_tree.bind('<<TreeviewClose>>', self._save_group_state)

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
                                        columns=('type', 'name', 'ip', 'port', 'username', 'password', 'status'),
                                        show=['tree', 'headings'],
                                        height=30, style='Treeview')

        self.server_tree.heading('type', text='类型')
        self.server_tree.heading('name', text='主机名')
        # B30: 列名 ip 与显示文本"域名"不一致，改为"IP地址"
        self.server_tree.heading('ip', text='IP地址')
        self.server_tree.heading('port', text='端口')
        self.server_tree.heading('username', text='用户名')
        self.server_tree.heading('password', text='密码')
        self.server_tree.heading('status', text='状态')

        self.server_tree.column('type', width=50, anchor='center')
        self.server_tree.column('name', width=250, anchor='center')
        self.server_tree.column('ip', width=100, anchor='center')
        self.server_tree.column('port', width=50, anchor='center')
        self.server_tree.column('username', width=70, anchor='center')
        self.server_tree.column('password', width=100, anchor='center')
        self.server_tree.column('status', width=50, anchor='center')

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
        self.server_tree.bind("<Double-1>" ,lambda event: self.connect_server(event))

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
            # 任务1: 使用FontAwesome图标替代旧的文件夹图标
            self.db.init_groups_data(self.group_tree, self._fa_icons.get('folder_close'), self._fa_icons.get('folder_open'))
            self.restore_group_state()
            self.log.write_log_info('组数据初始化成功')
        except Exception as e:
            self.log.write_log_error('外层调用组数据初始化失败' + str(e))

    def _save_group_state(self, event=None):
        """保存分组展开/折叠状态"""
        try:
            import json
            state = {}
            for item in self.group_tree.get_children():
                state[item] = self.group_tree.item(item)['open']
                self._save_child_state(item, state)
            self.db.set_setting('group_expand_state', json.dumps(state))
        except Exception:
            pass

    def _save_child_state(self, parent_id, state):
        """递归保存子节点展开状态"""
        for child in self.group_tree.get_children(parent_id):
            state[child] = self.group_tree.item(child)['open']
            self._save_child_state(child, state)

    def restore_group_state(self):
        """恢复分组展开/折叠状态"""
        try:
            import json
            raw = self.db.get_setting('group_expand_state')
            if not raw:
                return
            state = json.loads(raw)
            for item_id, is_open in state.items():
                if self.group_tree.exists(item_id):
                    self.group_tree.item(item_id, open=is_open)
        except Exception:
            pass

    # 初始化主机数据
    def init_server_data(self):
        try:
            self.db.init_servers_data(self.server_tree, self._get_server_icons)
            self.log.write_log_info('主机数据初始化成功')
        except Exception as e:
            self.log.write_log_error(str(e))

    def _init_fa_icons(self):
        """初始化 Font Awesome 图标，生成 PNG 缓存"""
        try:
            fa_path = os.path.join(os.path.dirname(__file__), '..', 'img',
                                   'fontawesome-free-6.4.0-web', 'webfonts', 'fa-solid-900.ttf')
            fa_path = os.path.normpath(fa_path)
            self._fa_font = ImageFont.truetype(fa_path, 16)
            # 颜色定义
            colors = {
                'SSH':   '#2196F3',   # 蓝色
                'VNC':   '#FF5722',   # 橙红
                'URL':   '#4CAF50',   # 绿色
                'Radmin':'#9C27B0',   # 紫色
                'RDP':   '#FF9800',   # 橙色
            }
            # Unicode 码点（Font Awesome 6.4.0 solid）
            icons = {
                'SSH':   '\uf120',   # terminal
                'VNC':   '\uf108',   # desktop
                'URL':   '\uf0c1',   # link
                'Radmin':'\uf108',   # desktop（同 VNC，颜色区分）
                'RDP':   '\uf2d2',   # window-maximize
            }
            for conn_type, char in icons.items():
                img = Image.new('RGBA', (22, 22), (0, 0, 0, 0))
                draw = ImageDraw.Draw(img)
                draw.text((0, 0), char, font=self._fa_font, fill=colors[conn_type])
                self._fa_icons[conn_type] = ImageTk.PhotoImage(img)
            # 默认图标（RDP）
            self._fa_icons['default'] = self._fa_icons.get('RDP')

            # 任务1: 初始化分组树展开/折叠图标
            # 折叠状态：fa-folder (uf00b) - 棕色
            img_folder_close = Image.new('RGBA', (20, 20), (0, 0, 0, 0))
            draw_folder_close = ImageDraw.Draw(img_folder_close)
            draw_folder_close.text((0, 0), '\uf00b', font=self._fa_font, fill='#8B4513')
            self._fa_icons['folder_close'] = ImageTk.PhotoImage(img_folder_close)

            # 展开状态：fa-folder-open (uf00c) - 棕色
            img_folder_open = Image.new('RGBA', (20, 20), (0, 0, 0, 0))
            draw_folder_open = ImageDraw.Draw(img_folder_open)
            draw_folder_open.text((0, 0), '\uf00c', font=self._fa_font, fill='#D2691E')
            self._fa_icons['folder_open'] = ImageTk.PhotoImage(img_folder_open)

            self.log.write_log_info('Font Awesome 图标初始化成功')
        except Exception as e:
            self.log.write_log_error('Font Awesome 图标初始化失败: ' + str(e))

    def _get_server_icons(self, conn_type):
        """根据连接类型返回对应的 tk.PhotoImage 图标，失败时返回 None"""
        return self._fa_icons.get(conn_type)

    # 加载设置并应用界面样式
    def load_settings(self):
        try:
            font_name = self.db.get_setting('ui_font', 'Microsoft YaHei')
            font_size = int(self.db.get_setting('ui_font_size', '10'))
            bg_color = self.db.get_setting('ui_bg_color', '#F0F0F0')
            self.master.configure(bg=bg_color)
            self.top.configure(bg=bg_color)
            self.left_frame.configure(bg=bg_color)
            self.right_frame.configure(bg=bg_color)
            self.right_frame_top.configure(bg=bg_color)
            self.right_frame_bottom.configure(bg=bg_color)
            self.top_frame.configure(bg=bg_color)
            self.top_R.configure(bg=bg_color)
            self.lable1.configure(bg=bg_color, font=(font_name, font_size))
            self.search_label.configure(bg=bg_color, font=(font_name, font_size))
            font_color = self.db.get_setting('ui_font_color', '#333333')
            info_bg_color = self.db.get_setting('ui_info_bg_color')
            search_bg_color = self.db.get_setting('ui_search_bg_color')
            self.apply_settings(font_name, font_size, bg_color,
                                font_color=font_color, info_bg_color=info_bg_color,
                                search_bg_color=search_bg_color)
            self.log.write_log_info('设置加载成功')
        except Exception as e:
            self.log.write_log_error('加载设置失败: ' + str(e))

    def apply_settings(self, font_name, font_size, bg_color,
                       font_color='#333333', info_bg_color=None, search_bg_color=None):
        """将字体和背景颜色应用到分组树和服务器树"""
        try:
            # 更新主窗口背景
            self.master.configure(bg=bg_color)
            for child in self.master.winfo_children():
                if isinstance(child, tk.Frame):
                    child.configure(bg=bg_color)

            # 更新 Treeview 样式
            style = ttk.Style()
            style.configure('Treeview', font=(font_name, int(font_size)),
                            background=bg_color, foreground=font_color,
                            fieldbackground=bg_color)
            style.configure('Treeview.Heading', font=(font_name, int(font_size), 'bold'),
                            background=bg_color, foreground=font_color)

            # 更新分组树和服务器树
            self.group_tree.configure(font=(font_name, int(font_size)))
            self.server_tree.configure(font=(font_name, int(font_size)))

            # 应用服务器说明区背景色
            if info_bg_color is not None:
                self.right_frame_bottom.configure(bg=info_bg_color)
                self.lable1.configure(bg=info_bg_color)
                self.server_info.configure(bg=info_bg_color, fg=font_color)

            # 应用搜索框背景色
            if search_bg_color is not None:
                # 强制设置背景色和前景色
                self.search_entry.config(bg=search_bg_color, fg=font_color)
                self.search_entry.configure(bg=search_bg_color, fg=font_color)
                # 尝试强制刷新
                self.search_entry.update()
                # 同时更新搜索标签颜色
                self.search_label.configure(bg=search_bg_color, fg=font_color)

            self.log.write_log_info('界面样式已更新')
        except Exception as e:
            self.log.write_log_error('应用设置失败: ' + str(e))

    def apply_all_settings(self, ssh_tool_type, ssh_paths, vnc_path, default_user, default_pass,
                           ssh_port, vnc_port, font_name, font_size, bg_color,
                           font_color, info_bg_color, search_bg_color):
        """保存并立即应用所有设置（含界面样式）"""
        self.db.set_setting('ssh_tool_type', ssh_tool_type)
        # 任务2: 保存每种SSH工具的独立路径
        for tool_type, path in ssh_paths.items():
            self.db.set_setting(f'ssh_tool_path_{tool_type}', path)
        self.db.set_setting('vnc_tool_path', vnc_path)
        self.db.set_setting('default_username', default_user)
        self.db.set_setting('default_password', default_pass)
        self.db.set_setting('default_ssh_port', ssh_port)
        self.db.set_setting('default_vnc_port', vnc_port)
        self.db.set_setting('ui_font', font_name)
        self.db.set_setting('ui_font_size', font_size)
        self.db.set_setting('ui_bg_color', bg_color)
        # 任务3: 保存颜色设置
        self.db.set_setting('ui_font_color', font_color)
        self.db.set_setting('ui_info_bg_color', info_bg_color)
        self.db.set_setting('ui_search_bg_color', search_bg_color)
        self.apply_settings(font_name, font_size, bg_color,
                            font_color=font_color, info_bg_color=info_bg_color,
                            search_bg_color=search_bg_color)
        self.log.write_log_info('设置已保存并立即生效')

    # 打开设置对话框
    def open_settings(self):
        def save_settings():
            ssh_tool_type = combo_ssh_tool.get()
            # 任务2: 收集所有SSH工具路径
            ssh_paths = {
                'xterm': entry_ssh_xterm.get(),
                'plink': entry_ssh_plink.get(),
                'mobaxterm': entry_ssh_mobaxterm.get(),
                'finalshell': entry_ssh_finalshell.get(),
                'xshell': entry_ssh_xshell.get(),
            }
            vnc_path = entry_vnc_path.get()
            default_user = entry_default_user.get()
            default_pass = entry_default_pass.get()
            ssh_port = entry_ssh_port.get()
            vnc_port = entry_vnc_port.get()
            font_name = combo_font.get()
            font_size = combo_font_size.get()
            bg_color = entry_bg_color.get()
            # 任务3: 收集颜色设置
            font_color = entry_font_color.get()
            info_bg_color = entry_info_bg_color.get()
            search_bg_color = entry_search_bg_color.get()
            preview_label.configure(bg=bg_color)

            self.apply_all_settings(ssh_tool_type, ssh_paths, vnc_path, default_user, default_pass,
                                    ssh_port, vnc_port, font_name, font_size, bg_color,
                                    font_color, info_bg_color, search_bg_color)
            messagebox.showinfo('提示', '设置已保存并立即生效')

        def restore_defaults():
            """恢复所有设置为初始默认值"""
            if not messagebox.askyesno('确认', '确定要恢复所有设置为默认值吗？\n此操作将清除所有自定义配置。'):
                return

            defaults = {
                'ssh_tool_type': 'XTerminal',
                'ssh_tool_path_xterm': 'xterm',
                'ssh_tool_path_plink': 'plink',
                'ssh_tool_path_mobaxterm': 'MobaXterm.exe',
                'ssh_tool_path_finalshell': 'finalshell.exe',
                'ssh_tool_path_xshell': 'Xshell.exe',
                'vnc_tool_path': 'vncviewer',
                'default_username': '',
                'default_password': '',
                'default_ssh_port': '22',
                'default_vnc_port': '5900',
                'ui_font': 'Microsoft YaHei',
                'ui_font_size': '10',
                'ui_bg_color': '#F0F0F0',
                'ui_font_color': '#000000',
                'ui_info_bg_color': '#FFFFFF',
                'ui_search_bg_color': '#FFFFFF',
            }
            for key, value in defaults.items():
                self.db.set_setting(key, value)

            # 刷新表单
            combo_ssh_tool.set('XTerminal')
            entry_ssh_xterm.delete(0, tk.END)
            entry_ssh_xterm.insert(0, 'xterm')
            entry_ssh_plink.delete(0, tk.END)
            entry_ssh_plink.insert(0, 'plink')
            entry_ssh_mobaxterm.delete(0, tk.END)
            entry_ssh_mobaxterm.insert(0, 'MobaXterm.exe')
            entry_ssh_finalshell.delete(0, tk.END)
            entry_ssh_finalshell.insert(0, 'finalshell.exe')
            entry_ssh_xshell.delete(0, tk.END)
            entry_ssh_xshell.insert(0, 'Xshell.exe')
            entry_vnc_path.delete(0, tk.END)
            entry_vnc_path.insert(0, 'vncviewer')
            entry_default_user.delete(0, tk.END)
            entry_default_pass.delete(0, tk.END)
            entry_ssh_port.delete(0, tk.END)
            entry_ssh_port.insert(0, '22')
            entry_vnc_port.delete(0, tk.END)
            entry_vnc_port.insert(0, '5900')
            combo_font.set('Microsoft YaHei')
            combo_font_size.set('10')
            entry_bg_color.delete(0, tk.END)
            entry_bg_color.insert(0, '#F0F0F0')
            # 任务3: 恢复颜色设置
            entry_font_color.delete(0, tk.END)
            entry_font_color.insert(0, '#000000')
            entry_info_bg_color.delete(0, tk.END)
            entry_info_bg_color.insert(0, '#FFFFFF')
            entry_search_bg_color.delete(0, tk.END)
            entry_search_bg_color.insert(0, '#FFFFFF')
            preview_label.configure(bg='#F0F0F0')

            # 立即应用到主窗口
            self.apply_settings('Microsoft YaHei', 10, '#F0F0F0',
                                font_color='#333333', info_bg_color='#F0F0F0',
                                search_bg_color='#FFFFFF')
            messagebox.showinfo('提示', '已恢复为默认设置')
            self.log.write_log_info('已恢复默认设置')

        settings_win = tk.Toplevel(self.master)
        settings_win.title('系统设置')
        settings_win.geometry('400x650')
        settings_win.configure(bg='#F0F0F0')
        settings_win.transient(self.master)
        settings_win.grab_set()
        # 居中定位（宽度400，高度650）
        self.top_master(settings_win, 650, 400)

        notebook = ttk.Notebook(settings_win)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Tab 1: 连接工具
        tab1 = tk.Frame(notebook, bg='#F0F0F0')
        notebook.add(tab1, text='连接工具')
        tk.Label(tab1, text='SSH 工具：', bg='#F0F0F0', font=('Microsoft YaHei', 10)).place(x=20, y=30)
        combo_ssh_tool = ttk.Combobox(tab1,
                                      values=['XTerminal', 'PuTTY(plink)', 'MobaXterm', 'FinalShell', 'Xshell'],
                                      width=20, font=('Microsoft YaHei', 10))
        combo_ssh_tool.place(x=20, y=55)

        # 任务2: 为每种SSH工具添加独立路径设置
        tk.Label(tab1, text='SSH工具路径：', bg='#F0F0F0', font=('Microsoft YaHei', 10)).place(x=20, y=100)
        entry_ssh_xterm = tk.Entry(tab1, width=35, font=('Microsoft YaHei', 10))
        entry_ssh_xterm.place(x=20, y=125)
        btn_ssh_xterm_browse = tk.Button(tab1, text='浏览...', font=('Microsoft YaHei', 9),
                                         command=lambda: _browse_path(entry_ssh_xterm))
        btn_ssh_xterm_browse.place(x=330, y=122)

        entry_ssh_plink = tk.Entry(tab1, width=35, font=('Microsoft YaHei', 10))
        entry_ssh_plink.place(x=20, y=160)
        btn_ssh_plink_browse = tk.Button(tab1, text='浏览...', font=('Microsoft YaHei', 9),
                                         command=lambda: _browse_path(entry_ssh_plink))
        btn_ssh_plink_browse.place(x=330, y=157)

        entry_ssh_mobaxterm = tk.Entry(tab1, width=35, font=('Microsoft YaHei', 10))
        entry_ssh_mobaxterm.place(x=20, y=195)
        btn_ssh_mobaxterm_browse = tk.Button(tab1, text='浏览...', font=('Microsoft YaHei', 9),
                                             command=lambda: _browse_path(entry_ssh_mobaxterm))
        btn_ssh_mobaxterm_browse.place(x=330, y=192)

        entry_ssh_finalshell = tk.Entry(tab1, width=35, font=('Microsoft YaHei', 10))
        entry_ssh_finalshell.place(x=20, y=230)
        btn_ssh_finalshell_browse = tk.Button(tab1, text='浏览...', font=('Microsoft YaHei', 9),
                                              command=lambda: _browse_path(entry_ssh_finalshell))
        btn_ssh_finalshell_browse.place(x=330, y=227)

        entry_ssh_xshell = tk.Entry(tab1, width=35, font=('Microsoft YaHei', 10))
        entry_ssh_xshell.place(x=20, y=265)
        btn_ssh_xshell_browse = tk.Button(tab1, text='浏览...', font=('Microsoft YaHei', 9),
                                          command=lambda: _browse_path(entry_ssh_xshell))
        btn_ssh_xshell_browse.place(x=330, y=262)

        tk.Label(tab1, text='VNC 工具路径：', bg='#F0F0F0', font=('Microsoft YaHei', 10)).place(x=20, y=300)
        entry_vnc_path = tk.Entry(tab1, width=35, font=('Microsoft YaHei', 10))
        entry_vnc_path.place(x=20, y=325)
        btn_vnc_browse = tk.Button(tab1, text='浏览...', font=('Microsoft YaHei', 9),
                                   command=lambda: _browse_path(entry_vnc_path))
        btn_vnc_browse.place(x=330, y=322)

        # Tab 2: 连接参数
        tab2 = tk.Frame(notebook, bg='#F0F0F0')
        notebook.add(tab2, text='连接参数')
        tk.Label(tab2, text='默认用户名：', bg='#F0F0F0', font=('Microsoft YaHei', 10)).place(x=20, y=30)
        entry_default_user = tk.Entry(tab2, width=35, font=('Microsoft YaHei', 10))
        entry_default_user.place(x=20, y=55)
        tk.Label(tab2, text='默认密码：', bg='#F0F0F0', font=('Microsoft YaHei', 10)).place(x=20, y=90)
        entry_default_pass = tk.Entry(tab2, width=35, show='*', font=('Microsoft YaHei', 10))
        entry_default_pass.place(x=20, y=115)
        tk.Label(tab2, text='默认 SSH 端口：', bg='#F0F0F0', font=('Microsoft YaHei', 10)).place(x=20, y=150)
        entry_ssh_port = tk.Entry(tab2, width=15, font=('Microsoft YaHei', 10))
        entry_ssh_port.place(x=20, y=175)
        tk.Label(tab2, text='默认 VNC 端口：', bg='#F0F0F0', font=('Microsoft YaHei', 10)).place(x=20, y=210)
        entry_vnc_port = tk.Entry(tab2, width=15, font=('Microsoft YaHei', 10))
        entry_vnc_port.place(x=20, y=235)

        # Tab 3: 界面设置
        tab3 = tk.Frame(notebook, bg='#F0F0F0')
        notebook.add(tab3, text='界面设置')
        tk.Label(tab3, text='字体：', bg='#F0F0F0', font=('Microsoft YaHei', 10)).place(x=20, y=30)
        combo_font = ttk.Combobox(tab3, values=['Microsoft YaHei', 'SimSun', 'SimHei', 'Arial'],
                                   width=20, font=('Microsoft YaHei', 10))
        combo_font.place(x=20, y=55)
        tk.Label(tab3, text='字体大小：', bg='#F0F0F0', font=('Microsoft YaHei', 10)).place(x=20, y=90)
        combo_font_size = ttk.Combobox(tab3, values=['9', '10', '11', '12', '14'],
                                        width=10, font=('Microsoft YaHei', 10))
        combo_font_size.place(x=20, y=115)
        tk.Label(tab3, text='背景颜色：', bg='#F0F0F0', font=('Microsoft YaHei', 10)).place(x=20, y=150)
        entry_bg_color = tk.Entry(tab3, width=10, font=('Microsoft YaHei', 10))
        entry_bg_color.place(x=20, y=175)
        btn_color_picker = tk.Button(tab3, text='取色', font=('Microsoft YaHei', 9),
                                     command=lambda: _pick_color(entry_bg_color, preview_label))
        btn_color_picker.place(x=105, y=170)
        preview_label = tk.Label(tab3, bg='#F0F0F0', width=15, height=3, relief='solid', bd=1)
        preview_label.place(x=145, y=170)
        tk.Label(tab3, text='（颜色预览）', bg='#F0F0F0', font=('Microsoft YaHei', 9), fg='#888888').place(x=220, y=185)

        # 任务3: 添加颜色设置
        tk.Label(tab3, text='字体颜色：', bg='#F0F0F0', font=('Microsoft YaHei', 10)).place(x=20, y=220)
        entry_font_color = tk.Entry(tab3, width=10, font=('Microsoft YaHei', 10))
        entry_font_color.place(x=20, y=245)
        btn_font_color_picker = tk.Button(tab3, text='取色', font=('Microsoft YaHei', 9),
                                          command=lambda: _pick_color(entry_font_color, preview_font_color))
        btn_font_color_picker.place(x=105, y=240)
        preview_font_color = tk.Label(tab3, bg='#000000', width=15, height=3, relief='solid', bd=1)
        preview_font_color.place(x=145, y=240)
        tk.Label(tab3, text='（颜色预览）', bg='#F0F0F0', font=('Microsoft YaHei', 9), fg='#888888').place(x=220, y=255)

        tk.Label(tab3, text='服务器说明背景色：', bg='#F0F0F0', font=('Microsoft YaHei', 10)).place(x=20, y=290)
        entry_info_bg_color = tk.Entry(tab3, width=10, font=('Microsoft YaHei', 10))
        entry_info_bg_color.place(x=20, y=315)
        btn_info_bg_picker = tk.Button(tab3, text='取色', font=('Microsoft YaHei', 9),
                                       command=lambda: _pick_color(entry_info_bg_color, preview_info_bg))
        btn_info_bg_picker.place(x=105, y=310)
        preview_info_bg = tk.Label(tab3, bg='#FFFFFF', width=15, height=3, relief='solid', bd=1)
        preview_info_bg.place(x=145, y=310)
        tk.Label(tab3, text='（颜色预览）', bg='#F0F0F0', font=('Microsoft YaHei', 9), fg='#888888').place(x=220, y=325)

        tk.Label(tab3, text='搜索框背景色：', bg='#F0F0F0', font=('Microsoft YaHei', 10)).place(x=20, y=360)
        entry_search_bg_color = tk.Entry(tab3, width=10, font=('Microsoft YaHei', 10))
        entry_search_bg_color.place(x=20, y=385)
        btn_search_bg_picker = tk.Button(tab3, text='取色', font=('Microsoft YaHei', 9),
                                         command=lambda: _pick_color(entry_search_bg_color, preview_search_bg))
        btn_search_bg_picker.place(x=105, y=380)
        preview_search_bg = tk.Label(tab3, bg='#FFFFFF', width=15, height=3, relief='solid', bd=1)
        preview_search_bg.place(x=145, y=380)
        tk.Label(tab3, text='（颜色预览）', bg='#F0F0F0', font=('Microsoft YaHei', 9), fg='#888888').place(x=220, y=395)

        # 加载现有设置值
        combo_ssh_tool.set(self.db.get_setting('ssh_tool_type', 'XTerminal'))
        # 任务2: 加载每种SSH工具的路径
        entry_ssh_xterm.insert(0, self.db.get_setting('ssh_tool_path_xterm', 'xterm'))
        entry_ssh_plink.insert(0, self.db.get_setting('ssh_tool_path_plink', 'plink'))
        entry_ssh_mobaxterm.insert(0, self.db.get_setting('ssh_tool_path_mobaxterm', 'MobaXterm.exe'))
        entry_ssh_finalshell.insert(0, self.db.get_setting('ssh_tool_path_finalshell', 'finalshell.exe'))
        entry_ssh_xshell.insert(0, self.db.get_setting('ssh_tool_path_xshell', 'Xshell.exe'))
        entry_vnc_path.insert(0, self.db.get_setting('vnc_tool_path', 'vncviewer'))
        entry_default_user.insert(0, self.db.get_setting('default_username', ''))
        entry_default_pass.insert(0, self.db.get_setting('default_password', ''))
        entry_ssh_port.insert(0, self.db.get_setting('default_ssh_port', '22'))
        entry_vnc_port.insert(0, self.db.get_setting('default_vnc_port', '5900'))
        combo_font.set(self.db.get_setting('ui_font', 'Microsoft YaHei'))
        combo_font_size.set(self.db.get_setting('ui_font_size', '10'))
        entry_bg_color.insert(0, self.db.get_setting('ui_bg_color', '#F0F0F0'))
        # 任务3: 加载颜色设置
        entry_font_color.insert(0, self.db.get_setting('ui_font_color', '#000000'))
        entry_info_bg_color.insert(0, self.db.get_setting('ui_info_bg_color', '#FFFFFF'))
        entry_search_bg_color.insert(0, self.db.get_setting('ui_search_bg_color', '#FFFFFF'))
        preview_label.configure(bg=entry_bg_color.get())
        preview_font_color.configure(bg=entry_font_color.get())
        preview_info_bg.configure(bg=entry_info_bg_color.get())
        preview_search_bg.configure(bg=entry_search_bg_color.get())

        # 底部按钮
        btn_frame = tk.Frame(settings_win, bg='#F0F0F0')
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=20, pady=15)
        tk.Button(btn_frame, text='恢复默认', font=('Microsoft YaHei', 10),
                  bg='#FF9800', fg='white', command=restore_defaults).pack(side=tk.RIGHT, padx=5)
        tk.Button(btn_frame, text='保存', font=('Microsoft YaHei', 10),
                  bg='#4CAF50', fg='white', command=save_settings).pack(side=tk.RIGHT, padx=5)
        tk.Button(btn_frame, text='取消', font=('Microsoft YaHei', 10),
                  bg='#f0f0f0', command=settings_win.destroy).pack(side=tk.RIGHT, padx=5)

        def _browse_path(entry):
            import tkinter.filedialog
            path = tkinter.filedialog.askopenfilename(title='选择工具路径')
            if path:
                entry.delete(0, tk.END)
                entry.insert(0, path)

        def _pick_color(entry, preview):
            """打开颜色选择器，选择后更新输入框和预览"""
            result = colorchooser.askcolor(title='选择背景颜色')
            if result[1]:
                entry.delete(0, tk.END)
                entry.insert(0, result[1])
                preview.configure(bg=result[1])

    # 添加主机window
    def add_server_window(self):
        def add_server ():
            conn_type = down.get()
            name = name_entry.get()
            host = host_entry.get()
            port = port_entry.get()
            username = user_entry.get()
            password = passwd_entry.get()
            server_info = info_text.get("1.0", tk.END).rstrip("\n")

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
                self.server_tree.delete(*self.server_tree.get_children())
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
                    if self.db.exists(new_value,'servers'):
                        messagebox.showinfo('提示', '主机名已存在')
                        self.log.write_log_error('主机名已存在，添加失败')
                        return
                    if1 = 'name'
                    new_value = conten_entry.get("1.0", tk.END).rstrip("\n")
                    self.db.update_server(if1,new_value,host)
                    # 刷新server_tree数据
                    self.server_tree.delete(*self.server_tree.get_children())
                    self.init_server_data()
                    messagebox.showinfo('提示', '编辑成功')
                    self.log.write_log_info('主机:' + host + '编辑成功,主机名修改为:' + new_value)
                    self.top.destroy()
                    return
                elif select_collu == '主机地址':
                    new_value = conten_entry.get("1.0", tk.END).rstrip("\n")
                    self.db.update_server('host', new_value, host)
                    # 刷新server_tree数据（host已变，重新加载）
                    self.server_tree.delete(*self.server_tree.get_children())
                    self.init_server_data()
                    # 更新host变量，供后续日志使用
                    host = new_value
                    messagebox.showinfo('提示', '编辑成功')
                    self.log.write_log_info('主机:' + host + '编辑成功,主机地址修改为:' + host)
                    self.top.destroy()
                    return
                elif select_collu == '端口号':
                    if2 = 'port'
                    new_value = conten_entry.get("1.0", tk.END).rstrip("\n")
                    self.db.update_server(if2,new_value,host)
                    self.server_tree.delete(*self.server_tree.get_children())
                    self.init_server_data()
                    messagebox.showinfo('提示', '编辑成功')
                    self.log.write_log_info('主机:' + host + '编辑成功,端口号修改为:' + new_value)
                    self.top.destroy()
                    return
                elif select_collu == '用户名':
                    if3 = 'username'
                    new_value = conten_entry.get("1.0", tk.END).rstrip("\n")
                    self.db.update_server(if3,new_value,host)
                    self.server_tree.delete(*self.server_tree.get_children())
                    self.init_server_data()
                    messagebox.showinfo('提示', '编辑成功')
                    self.log.write_log_info('主机:' + host + '编辑成功,用户名修改为:' + new_value)
                    self.top.destroy()
                    return
                elif select_collu == '密码':
                    if4 = 'password'
                    new_value = conten_entry.get("1.0", tk.END).rstrip("\n")
                    self.db.update_server(if4,new_value,host)
                    self.server_tree.delete(*self.server_tree.get_children())
                    self.init_server_data()
                    messagebox.showinfo('提示', '编辑成功')
                    # 安全修复：密码脱敏处理
                    masked_new_value = new_value[:2] + '*' * (len(new_value) - 2) if len(new_value) > 2 else '*' * len(new_value)
                    self.log.write_log_info('主机:' + host + '编辑成功,密码修改为:' + masked_new_value)
                    self.top.destroy()
                    return
                elif select_collu == '分组':
                    if select_group_id is None:
                        messagebox.showinfo('提示', '未选择分组,请选择分组')
                        self.log.write_log_error('未选择分组，编辑主机信息失败')
                        return
                    conten_entry.delete("1.0", tk.END)
                    conten_entry.insert(tk.END, "修改分组无需输入内容")
                    if5 = 'parent_id'
                    self.db.update_server(if5, int(select_group_id), host)
                    self.server_tree.delete(*self.server_tree.get_children())
                    self.init_server_data()
                    messagebox.showinfo('提示', '编辑成功')
                    self.log.write_log_info('主机:' + host + '编辑成功,分组修改为:' + str(select_group_id))
                    self.top.destroy()
                    return
                elif select_collu == '服务器说明':
                    if6 = 'server_info'
                    new_value = conten_entry.get("1.0", tk.END).rstrip("\n")
                    self.db.update_server(if6,new_value,host)
                    self.server_tree.delete(*self.server_tree.get_children())
                    self.init_server_data()
                    messagebox.showinfo('提示', '编辑成功')
                    self.log.write_log_info('主机:' + host + '编辑成功,服务器说明修改为:' + new_value)
                    self.top.destroy()
                    return
                else:
                    messagebox.showinfo('提示', '不支持的操作')
                    self.log.write_log_error('编辑失败')
            except Exception as e:
                self.log.write_log_error('服务器编辑失败' + str(e))
            
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
        # 安全修复：密码脱敏处理，避免日志泄露
        masked_password = password[:2] + '*' * (len(password) - 2) if len(password) > 2 else '*' * len(password)
        self.log.write_log_info('主机名：' + name + ',主机ip : ' + host + '端口号：' + str(port) + '用户名：' + username + '密码：' + masked_password)
        self.top = tk.Toplevel()
        self.top.title("编辑主机")
        self.top_master(self.top,300)
        # 锁定焦点
        # self.top.grab_set()
        self.top.resizable(0,0)
        lab1 = tk.Label(self.top, text="请选择要修改的内容：")
        lab1.pack()
        down = ttk.Combobox(self.top, values=['主机名', '主机地址','端口号','用户名','密码','分组','服务器说明'],state='readonly', width=20)
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
            self.db.delete_server(host)
            self.log.write_log_info('主机: ' + host + '删除成功')
            # 刷新server_tree数据
            self.server_tree.delete(*self.server_tree.get_children())
            self.init_server_data()
            
    # 新建分组界面
    def add_folder_window(self):
        # B28: 移除调试输出
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
        if not messagebox.askokcancel('删除分组', '确定删除分组？'):
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
                self.log.write_log_info('分组下存在主机，删除分组失败')
                messagebox.showerror('错误', '分组下存在主机，删除失败！')
                return
            else:
                self.log.write_log_info('该分组下不存在主机,分组删除成功' + str(parent_id) + "," + name)
                self.db.delete_group(name)
                # 刷新group_tree数据
                self.group_tree.delete(*self.group_tree.get_children())
                self.init_groups_data()

    # 搜索服务器
    def search_servers(self):
        content = self.search_entry.get()
        if content == '':
            messagebox.showerror('错误', '请输入要搜索的内容！')
        else:
            flag = self.too.is_ip(content)
            # 先搜索，成功后再清空并填充结果
            servers = self.db.search_servers(content, flag, self.server_tree)
            if servers is not None:
                self.server_tree.delete(*self.server_tree.get_children())
                for r in servers:
                    icon = self._get_server_icons(r[1])
                    self.server_tree.insert('', "end", image=icon if icon else '', values=(r[1], r[2], r[3], r[4], r[5], r[6], ''))

    # 分组右键事件
    def tree_right_click(self, event):
        self.group_tree.focus()  # 聚焦分组树形结构
        self.group_menu = tk.Menu(self.master, tearoff=0)
        self.group_menu.add_command(label='添加分组',command=self.add_folder_window)
        self.group_menu.add_command(label='删除分组',command=self.delete_group)
        self.group_menu.add_command(label='重命名分组',command=self.rename_group)
        self.group_menu.add_separator()
        self.group_menu.add_command(label='导入分组',command=self.import_group)
        self.group_menu.add_command(label='导出分组',command=self.export_group)        
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
        self.server_menu.add_command(label='导入服务器',command=self.import_server)
        self.server_menu.add_command(label='导出服务器',command=self.export_server)
        self.server_menu.add_separator()
        self.server_menu.add_command(label='显示全部主机',command=self.init_server_data)

        self.server_menu.post(event.x_root, event.y_root)   # 在鼠标位置显示菜单
    # group_tree 释放焦点事件
    def groupTree_release(self,event):
        # B28: 移除调试输出
        # 取消选中
        self.group_tree.selection_remove(self.group_tree.focus())
        # group_tree焦点设为空
        self.group_tree.focus("")

    # server_tree 释放焦点事件
    def Stree_release(self,event):
        # B28: 移除调试输出
        # 取消选中
        self.server_tree.selection_remove(self.server_tree.focus())
        # server_tree焦点设为空
        self.server_tree.focus("")

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

    # 任务：实现导入/导出分组和服务器功能
    def import_group(self):
        """导入分组数据"""
        try:
            import json
            from tkinter import filedialog
            file_path = filedialog.askopenfilename(
                title='选择分组导入文件',
                filetypes=[('JSON文件', '*.json'), ('所有文件', '*.*')],
                defaultextension='.json'
            )
            if not file_path:
                return
            with open(file_path, 'r', encoding='utf-8') as f:
                groups_data = json.load(f)
            # 清空现有分组
            self.db.clear_groups()
            # 导入分组
            for group in groups_data:
                self.db.add_group(group['name'], group.get('parent_id'))
            # 刷新分组树
            self.init_groups_data()
            messagebox.showinfo('成功', '分组导入成功！')
            self.log.write_log_info('分组导入成功')
        except Exception as e:
            messagebox.showerror('错误', f'导入分组失败：{str(e)}')
            self.log.write_log_error(f'导入分组失败：{e}')

    def export_group(self):
        """导出分组数据"""
        try:
            import json
            from tkinter import filedialog
            # 查询所有分组
            conn = sqlite3.connect(self.db.db)
            cursor = conn.cursor()
            cursor.execute('SELECT id, name, parent_id FROM groups')
            groups_data = cursor.fetchall()
            cursor.close()
            conn.close()
            # 转换为列表
            groups_list = [{'name': g[1], 'parent_id': g[2]} for g in groups_data]
            # 保存文件
            file_path = filedialog.asksaveasfilename(
                title='保存分组文件',
                defaultextension='.json',
                filetypes=[('JSON文件', '*.json'), ('所有文件', '*.*')],
                initialfile='groups_export.json'
            )
            if not file_path:
                return
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(groups_list, f, ensure_ascii=False, indent=4)
            messagebox.showinfo('成功', '分组导出成功！')
            self.log.write_log_info('分组导出成功')
        except Exception as e:
            messagebox.showerror('错误', f'导出分组失败：{str(e)}')
            self.log.write_log_error(f'导出分组失败：{e}')

    def import_server(self):
        """导入服务器数据"""
        try:
            import json
            from tkinter import filedialog
            file_path = filedialog.askopenfilename(
                title='选择服务器导入文件',
                filetypes=[('JSON文件', '*.json'), ('所有文件', '*.*')],
                defaultextension='.json'
            )
            if not file_path:
                return
            with open(file_path, 'r', encoding='utf-8') as f:
                servers_data = json.load(f)
            # 清空现有服务器
            self.db.clear_servers()
            # 导入服务器
            for server in servers_data:
                self.db.add_server(
                    server['conn_type'],
                    server['name'],
                    server['host'],
                    server['port'],
                    server['username'],
                    server['password'],
                    server.get('parent_id'),
                    server.get('server_info', '')
                )
            # 刷新服务器树
            self.init_servers_data()
            messagebox.showinfo('成功', '服务器导入成功！')
            self.log.write_log_info('服务器导入成功')
        except Exception as e:
            messagebox.showerror('错误', f'导入服务器失败：{str(e)}')
            self.log.write_log_error(f'导入服务器失败：{e}')

    def export_server(self):
        """导出服务器数据"""
        try:
            import json
            from tkinter import filedialog
            # 查询所有服务器
            conn = sqlite3.connect(self.db.db)
            cursor = conn.cursor()
            cursor.execute('SELECT conn_type, name, host, port, username, password, parent_id, server_info FROM servers')
            servers_data = cursor.fetchall()
            cursor.close()
            conn.close()
            # 转换为列表
            servers_list = [
                {
                    'conn_type': s[0],
                    'name': s[1],
                    'host': s[2],
                    'port': s[3],
                    'username': s[4],
                    'password': s[5],
                    'parent_id': s[6],
                    'server_info': s[7]
                }
                for s in servers_data
            ]
            # 保存文件
            file_path = filedialog.asksaveasfilename(
                title='保存服务器文件',
                defaultextension='.json',
                filetypes=[('JSON文件', '*.json'), ('所有文件', '*.*')],
                initialfile='servers_export.json'
            )
            if not file_path:
                return
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(servers_list, f, ensure_ascii=False, indent=4)
            messagebox.showinfo('成功', '服务器导出成功！')
            self.log.write_log_info('服务器导出成功')
        except Exception as e:
            messagebox.showerror('错误', f'导出服务器失败：{str(e)}')
            self.log.write_log_error(f'导出服务器失败：{e}')
           
    # 连接主机
    def connect_server(self,event=None):
        self.log.write_log_info('事件触发：连接主机')
        #获取选择的主机信息
        selected_item = self.server_tree.focus()
        if selected_item == '':
            messagebox.showerror('错误', '请选择要连接的主机！')
            self.log.write_log_error('未选择主机，连接失败')
            return
        connect_type = self.server_tree.item(selected_item)['values'][0]
        if connect_type == 'RDP':
            name = self.server_tree.item(selected_item)['values'][1]
            host = self.server_tree.item(selected_item)['values'][2]
            port = str(self.server_tree.item(selected_item)['values'][3])
            username = self.server_tree.item(selected_item)['values'][4]
            password = self.server_tree.item(selected_item)['values'][5]
            self.too.run_mstsc(host, port, username, password)
        elif connect_type == 'SSH':
            name = self.server_tree.item(selected_item)['values'][1]
            host = self.server_tree.item(selected_item)['values'][2]
            port = str(self.server_tree.item(selected_item)['values'][3])
            username = self.server_tree.item(selected_item)['values'][4]
            password = self.db.get_server_password(name)
            
            # 任务3：添加连接确认弹框
            confirm_msg = f"确认连接到主机：\n\n主机名：{name}\n地址：{host}:{port}\n类型：SSH\n用户名：{username}"
            result = messagebox.askyesno('确认连接', confirm_msg)
            if not result:
                self.log.write_log_info('用户取消SSH连接')
                return
            
            self.too.run_ssh(host, port, username, password, callback=self.show_connection_error)
            self.log.write_log_info('SSH连接: ' + host + ' 端口:' + port + ' 用户:' + username)
        elif connect_type == 'VNC':
            host = self.server_tree.item(selected_item)['values'][2]
            port = str(self.server_tree.item(selected_item)['values'][3])
            vnc_tool = self.db.get_setting('vnc_tool_path', 'vncviewer')
            
            # 任务3：添加连接确认弹框
            confirm_msg = f"确认连接到主机：\n\n地址：{host}:{port}\n类型：VNC"
            result = messagebox.askyesno('确认连接', confirm_msg)
            if not result:
                self.log.write_log_info('用户取消VNC连接')
                return
            
            self.too.run_vnc(host, port, callback=self.show_connection_error)
            self.log.write_log_info('VNC连接: ' + host + ' 端口:' + port)
        elif connect_type == 'Radmin':
            host = self.server_tree.item(selected_item)['values'][2]
            port = str(self.server_tree.item(selected_item)['values'][3])
            
            # 任务3：添加连接确认弹框
            confirm_msg = f"确认连接到主机：\n\n地址：{host}:{port}\n类型：Radmin"
            result = messagebox.askyesno('确认连接', confirm_msg)
            if not result:
                self.log.write_log_info('用户取消Radmin连接')
                return
            
            self.too.run_radmin(host, port, callback=self.show_connection_error)
            self.log.write_log_info('Radmin连接: ' + host + ' 端口:' + port)
        elif connect_type == 'URL':
            host = self.server_tree.item(selected_item)['values'][2]
            # username = self.server_tree.item(selected_item)['values'][4]
            self.too.thread_it(self.too.open_browser,host)
        else:
            messagebox.showerror('错误', '不支持的连接类型，请联系系统管理员！')

    def show_connection_error(self, error_msg):
        """显示连接错误信息"""
        messagebox.showerror('连接失败', error_msg)
                                                                                                                   
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
            # B28: 移除调试输出
            self.server_info.update()

    # group_tree焦点变更事件
    def on_group_selection_change(self, event):
        selected_item  = self.group_tree.selection()
        # B28: 移除调试输出
        if selected_item:
            item = self.group_tree.item(selected_item)
            group_name = item['text']
            group_id = self.db.get_group_id(group_name)
            if self.db.check_group_has_servers(group_id):
                self.server_tree.delete(*self.server_tree.get_children())
                res = self.db.get_servers_by_group_id(group_id)
                for r in res:
                    icon = self._get_server_icons(r[1])
                    self.server_tree.insert('', 'end', image=icon if icon else '', values=(r[1], r[2], r[3], r[4], r[5], r[6], ''))


    # self.top的位置 添加主机用
    def top_master(self,top,height,width=250):
        # 获取主窗口的位置和尺寸
        master_x = self.master.winfo_rootx()
        master_y = self.master.winfo_rooty()
        master_width = self.master.winfo_width()
        master_height = self.master.winfo_height()

        # 设置弹出窗口的大小
        popup_width = width
        popup_height = height

        # 计算弹出窗口的中心位置
        popup_x = master_x + (master_width // 2) - (popup_width // 2)
        popup_y = master_y + (master_height // 2) - (popup_height // 2)
        # 设置弹出窗口的大小和位置
        return top.geometry(f'{popup_width}x{popup_height}+{popup_x}+{popup_y}')
    


