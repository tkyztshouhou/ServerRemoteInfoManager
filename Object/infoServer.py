import os
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import colorchooser
from Object.gui_DA import *
from tools.logs import logs
from tools.tool import too
from PIL import Image, ImageDraw, ImageFont, ImageTk
import threading
import subprocess
import platform
import queue
import re


'''
    @ Author: LiuShan
    @ Date: 2024.09.04
    @ Description: 主机运维管理工具类
'''

# 创建主窗口
class infoServer:
    def __init__(self, master):
        self.master = master    # 窗口
        # 从 version.txt 读取版本号（VSVersionInfo 格式则提取 FileVersion 字段）
        version = ''
        try:
            version_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'version.txt')
            with open(version_path, 'r', encoding='utf-8') as f:
                content = f.read()
            m = re.search(r"StringStruct\('FileVersion',\s*'([^']+)'\)", content)
            if m:
                version = 'V' + m.group(1)
            else:
                version = content.strip()
                # 非纯版本号文本（多行或过长）不使用
                if '\n' in version or len(version) > 32:
                    version = ''
        except Exception:
            version = ''
        if not version:
            version = 'V2.2.20260825'
        self.master.title(f"主机运维管理工具    {version} -LiuShan")
        self.master.geometry('1366x768+50+0')   #将该行代码修改为分辨率可自定义调整窗口大小
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
        self._load_window_state()

        # master绑定esc事件
        self.master.bind('<Escape>', lambda event: self._close_top_window())
        # 绑定窗口关闭事件，保存窗口位置
        self.master.protocol("WM_DELETE_WINDOW", self._on_close)

        # F15: 清理可能残留的 RDP 凭据
        self.too.cleanup_rdp_credentials()

        self.log.write_log_info("程序初始化成功")

    # F12: 保存窗口位置和大小
    def _save_window_state(self):
        try:
            geom = self.master.geometry()
            # 解析 geometry 字符串，格式如 "1366x768+50+0"
            parts = geom.split('+')
            size_part = parts[0]
            width, height = size_part.split('x')
            x = parts[1] if len(parts) > 1 else '0'
            y = parts[2] if len(parts) > 2 else '0'

            self.db.set_setting('last_window_x', str(x))
            self.db.set_setting('last_window_y', str(y))
            self.db.set_setting('last_window_width', str(width))
            self.db.set_setting('last_window_height', str(height))
            self.log.write_log_info(f'窗口位置已保存: {geom}')
        except Exception as e:
            self.log.write_log_error(f'保存窗口位置失败: {e}')

    def _load_window_state(self):
        try:
            last_x = self.db.get_setting('last_window_x', '50')
            last_y = self.db.get_setting('last_window_y', '0')
            last_w = self.db.get_setting('last_window_width', '1366')
            last_h = self.db.get_setting('last_window_height', '768')
            self.master.geometry(f'{last_w}x{last_h}+{last_x}+{last_y}')
            self.log.write_log_info(f'已恢复窗口位置: {last_w}x{last_h}+{last_x}+{last_y}')
        except Exception as e:
            self.log.write_log_error(f'加载窗口位置失败: {e}')

    def _on_close(self):
        """窗口关闭时保存窗口位置和大小"""
        self._save_window_state()
        self.master.destroy()

    def _close_top_window(self):
        """关闭当前打开的弹窗"""
        for win in list(self.master.winfo_children()):
            if isinstance(win, tk.Toplevel):
                win.destroy()

    # 创建主窗口
    '''
        初始化控件
    '''
    def create_widgets(self):
        # 记录上一次设置的左侧宽度，避免重复触发
        self._last_left_width = None

        def update_width(event):
            # 关键修复：<Configure> 事件会从子控件向祖先冒泡，
            # 若不过滤，left_frame.config 又会触发自身 Configure 冒泡回 master，
            # 形成无限重排死循环（主线程 100% CPU、界面卡死只能强杀）。
            # 只处理主窗口自身的尺寸变化事件。
            if event.widget is not self.master:
                return
            window_width = event.width
            new_width = window_width // 4
            # 宽度未变化则跳过，避免无意义的重排
            if self._last_left_width == new_width:
                return
            self._last_left_width = new_width
            self.left_frame.config(width=new_width)

        # 一级框架
        self.top = tk.Frame(self.master, bg='#F0F0F0')
        self.top.pack(side=tk.TOP, fill=tk.X)

        self.left_frame = tk.Frame(self.master, bg='#F0F0F0')
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y,padx=10, pady=10)   # 填充 纵向
        self.left_frame.pack_propagate(1)               # 允许内部控件影响外层控件大小 (1=True)
        self.right_frame = tk.Frame(self.master, bg='#F0F0F0')
        self.right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True,padx=10, pady=10)
        self.right_frame.pack_propagate(0)

        # top（保持原始背景色 #F0F0F0，不跟随全局背景变化，避免按钮图片突兀）
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
        
        # 配置自定义滚动条样式
        style.configure('Custom.Vertical.TScrollbar', troughcolor='#F0F0F0', arrowcolor='#333333')
        style.configure('Custom.Horizontal.TScrollbar', troughcolor='#F0F0F0', arrowcolor='#333333')

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

        self.server_tree.column('#0', width=13, anchor='center')
        self.server_tree.column('type', width=50, anchor='center')
        self.server_tree.column('name', width=250, anchor='center')
        self.server_tree.column('ip', width=250, anchor='center')
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
        
        # 从settings表中读取存储的颜色值
        search_bg_color = self.db.get_setting('ui_search_bg_color', '#FFFFFF')
        font_color = self.db.get_setting('ui_font_color', '#333333')
        self.log.write_log_info(f'组件创建时设置搜索框颜色 - 背景色: {search_bg_color}, 字体色: {font_color}')
        self.search_entry.configure(bg=search_bg_color, fg=font_color)

        # 创建左右布局容器（左侧说明自然窄、右侧配置扩展占满剩余宽度）
        self.new_container = tk.Frame(self.right_frame_bottom, bg='#F0F0F0')
        self.new_container.pack(fill=tk.BOTH, expand=True)
        
        # 左侧容器 - 服务器说明（自然宽度，不扩展，保持较窄）
        self.left_container = tk.Frame(self.new_container, bg='#F0F0F0')
        self.left_container.pack(side=tk.LEFT, fill=tk.BOTH)
        
        # 右侧容器 - 功能区域（扩展占满剩余宽度）
        self.right_container = tk.Frame(self.new_container, bg='#F0F0F0')
        self.right_container.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # 左侧：服务器说明
        self.lable1 = tk.Label(self.left_container, text="服务器说明：",bg='#F0F0F0',font=('微软雅黑',10))
        self.lable1.pack(side=tk.TOP,fill=tk.X)
        self.server_info = tk.Text(self.left_container)
        self.server_info.pack(side=tk.LEFT,fill=tk.BOTH,expand=True)
        # 添加滚动条
        info_Scrollbar = ttk.Scrollbar(self.left_container, orient=tk.VERTICAL, command=self.server_info.yview)
        info_Scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.server_info.configure(yscrollcommand=info_Scrollbar.set)
        
        # 从settings表中读取存储的颜色值
        info_bg_color = self.db.get_setting('ui_info_bg_color', '#FFFFFF')
        font_color = self.db.get_setting('ui_font_color', '#333333')
        self.log.write_log_info(f'组件创建时设置Text组件颜色 - 背景色: {info_bg_color}, 字体色: {font_color}')
        self.server_info.configure(bg=info_bg_color, fg=font_color)
        
        # 右侧：上方 - 按钮容器（Ping检测 + FAQ 左右排列，两侧与中间边距均衡）
        self.top_btn_container = tk.Frame(self.right_container, bg='#F0F0F0')
        self.top_btn_container.pack(side=tk.TOP, fill=tk.X, pady=(20, 8))
        
        # Ping检测按钮（左，左侧外边距与右侧一致、与FAQ间距一致）
        self.ping_btn = tk.Button(self.top_btn_container, text="Ping检测", width=15, height=2, 
                                 command=self.ping_all_servers, bg='#2196F3', fg='white')
        self.ping_btn.pack(side=tk.LEFT, padx=(25, 10))
        
        # FAQ按钮（右，右侧外边距与左侧一致）
        try:
            self.faq_image = tk.PhotoImage(file="img/btn-faqzsk.png")
            self.faq_btn = tk.Button(self.top_btn_container, image=self.faq_image, command=self.show_faq, 
                                    width=191, height=45, borderwidth=0)
            self.faq_btn.pack(side=tk.RIGHT, padx=(10, 25))
        except Exception as e:
            # 如果图片不存在，使用文字按钮
            self.faq_btn = tk.Button(self.top_btn_container, text="FAQ知识库", command=self.show_faq, 
                                    width=15, height=2, bg='#4CAF50', fg='white')
            self.faq_btn.pack(side=tk.RIGHT, padx=(10, 25))
            self.log.write_log_error(f'FAQ图片加载失败: {e}')
        
        # 右侧：下方 - 远程桌面高级选项（占满剩余全部高度，不再需要滚动）
        self.rdp_frame = tk.Frame(self.right_container, bg='#F0F0F0')
        self.rdp_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=5)
        # 直接作为内容容器承载所有选项控件（高度足够，不滚动）
        self.rdp_inner = self.rdp_frame
        
        # 创建远程桌面高级选项UI
        self.create_rdp_options_ui()
        
        # 加载保存的设置
        self.load_rdp_settings()
        
        #绑定窗口改变事件
        self.master.bind('<Configure>', update_width)

        # 左键双击事件
        # self.group_tree.bind("<Double-1>", self.groupTree_click)
        self.server_tree.bind("<Double-1>" ,lambda event: self.connect_server(event))

        # server_tree焦点变更事件
        self.server_tree.bind("<<TreeviewSelect>>", self.on_selection_change)
        self.group_tree.bind("<<TreeviewSelect>>", self.on_group_selection_change)

        # 绑定中键事件（按下+释放） 取消焦点
        self.group_tree.bind("<Button-2>", self.groupTree_release)
        self.group_tree.bind("<ButtonRelease-2>", self.groupTree_release)
        self.server_tree.bind("<Button-2>", self.Stree_release)
        self.server_tree.bind("<ButtonRelease-2>", self.Stree_release)

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
            # 所有节点都使用folder_badge_plus.png图标
            self.db.init_groups_data(self.group_tree, self._fa_icons.get('folder_close'), self._fa_icons.get('folder_close'))
            self.restore_group_state()
            self.log.write_log_info('组数据初始化成功')
        except Exception as e:
            self.log.write_log_error('外层调用组数据初始化失败' + str(e))

    def _save_group_state(self, event=None):
        """保存分组展开/折叠状态（递归保存所有层级节点）"""
        try:
            import json
            state = {}
            # 构建 item_id -> group_id 的反向映射
            item_to_group = {iid: gid for gid, iid in self.db.item_map.items()}

            def save_item(item_id):
                gid = item_to_group.get(item_id)
                if gid is not None:
                    # 统一用字符串键，避免JSON序列化/反序列化的int/str类型不一致问题
                    state[str(gid)] = self.group_tree.item(item_id)['open']
                # 递归保存所有子节点
                for child in self.group_tree.get_children(item_id):
                    save_item(child)

            for root in self.group_tree.get_children():
                save_item(root)

            self.db.set_setting('group_expand_state', json.dumps(state))
        except Exception as e:
            self.log.write_log_error('保存分组展开状态失败: ' + str(e))

    def restore_group_state(self):
        """恢复分组展开/折叠状态（递归恢复所有层级节点）"""
        try:
            import json
            raw = self.db.get_setting('group_expand_state')
            if not raw:
                return
            state = json.loads(raw)  # 键为字符串形式的group_id
            # 构建 item_id -> group_id 的反向映射
            item_to_group = {iid: gid for gid, iid in self.db.item_map.items()}

            def restore_item(item_id):
                gid = item_to_group.get(item_id)
                if gid is not None and str(gid) in state:
                    self.group_tree.item(item_id, open=state[str(gid)])
                # 递归恢复所有子节点
                for child in self.group_tree.get_children(item_id):
                    restore_item(child)

            for root in self.group_tree.get_children():
                restore_item(root)
        except Exception as e:
            self.log.write_log_error('恢复分组展开状态失败: ' + str(e))

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
            # 折叠状态：使用 folder_badge_plus.png
            img_path = os.path.join(os.path.dirname(__file__), '..', 'img', 'folder_badge_plus.png')
            img_path = os.path.normpath(img_path)
            self.log.write_log_info(f'加载关闭状态图标: {img_path}')
            img_folder_close = Image.open(img_path)
            img_folder_close = img_folder_close.resize((24, 24), Image.Resampling.LANCZOS)
            self._fa_icons['folder_close'] = ImageTk.PhotoImage(img_folder_close)

            # 展开状态：使用 folder.png
            img_path = os.path.join(os.path.dirname(__file__), '..', 'img', 'folder.png')
            img_path = os.path.normpath(img_path)
            self.log.write_log_info(f'加载打开状态图标: {img_path}')
            img_folder_open = Image.open(img_path)
            img_folder_open = img_folder_open.resize((24, 24), Image.Resampling.LANCZOS)
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
            self.log.write_log_info('开始加载设置...')
            font_name = self.db.get_setting('ui_font', 'Microsoft YaHei')
            font_size = int(self.db.get_setting('ui_font_size', '10'))
            bg_color = self.db.get_setting('ui_bg_color', '#F0F0F0')
            font_color = self.db.get_setting('ui_font_color', '#333333')
            info_bg_color = self.db.get_setting('ui_info_bg_color')
            search_bg_color = self.db.get_setting('ui_search_bg_color')
            # F: 加载服务器说明字体设置
            server_info_font_size = self.db.get_setting('server_info_font_size')
            server_info_font_color = self.db.get_setting('server_info_font_color')

            self.log.write_log_info(f'加载的颜色设置 - 字体: {font_name}, 大小: {font_size}, 背景色: {bg_color}, 字体色: {font_color}')
            self.log.write_log_info(f'服务器说明背景色: {info_bg_color}, 搜索框背景色: {search_bg_color}')
            self.log.write_log_info(f'服务器说明字体大小: {server_info_font_size}, 颜色: {server_info_font_color}')

            self.master.configure(bg=bg_color)
            self.top.configure(bg=bg_color)
            self.left_frame.configure(bg=bg_color)
            self.right_frame.configure(bg=bg_color)
            self.right_frame_top.configure(bg=bg_color)
            self.right_frame_bottom.configure(bg=bg_color)
            self.top_frame.configure(bg=bg_color)
            self.top_R.configure(bg=bg_color)
            # 主机名搜索label与服务器说明label背景不跟随界面背景色变化，保持原始色
            self.lable1.configure(bg='#F0F0F0', font=(font_name, font_size))
            self.search_label.configure(bg='#F0F0F0', font=(font_name, font_size))

            self.apply_settings(font_name, font_size, bg_color,
                                font_color=font_color, info_bg_color=info_bg_color,
                                search_bg_color=search_bg_color,
                                server_info_font_size=server_info_font_size,
                                server_info_font_color=server_info_font_color)
            self.log.write_log_info('设置加载成功')
        except Exception as e:
            self.log.write_log_error('加载设置失败: ' + str(e))

    def apply_settings(self, font_name, font_size, bg_color,
                       font_color='#333333', info_bg_color=None, search_bg_color=None,
                       server_info_font_size=None, server_info_font_color=None):
        """将字体和背景颜色应用到分组树和服务器树"""
        try:
            self.log.write_log_info(f'apply_settings被调用 - 字体: {font_name}, 大小: {font_size}, 背景色: {bg_color}')
            self.log.write_log_info(f'应用的颜色设置 - 字体色: {font_color}, 服务器说明背景色: {info_bg_color}, 搜索框背景色: {search_bg_color}')

            # 如果没有指定服务器说明背景色，使用白色作为默认值
            if info_bg_color is None:
                info_bg_color = '#FFFFFF'
            # 如果没有指定搜索框背景色，使用白色作为默认值
            if search_bg_color is None:
                search_bg_color = '#FFFFFF'

            self.log.write_log_info(f'使用默认颜色 - 服务器说明背景色: {info_bg_color}, 搜索框背景色: {search_bg_color}')

            # 更新主窗口背景
            self.master.configure(bg=bg_color)
            for child in self.master.winfo_children():
                if isinstance(child, tk.Frame):
                    child.configure(bg=bg_color)
            # 顶部按钮区整体保持原始背景色，不跟随界面背景变化，避免按钮图片突兀
            try:
                self.top.configure(bg='#F0F0F0')
                self.top_frame.configure(bg='#F0F0F0')
                self.top_R.configure(bg='#F0F0F0')
            except Exception:
                pass

            # 更新 Treeview 样式（ttk.Treeview 的字体只能通过 Style 设置，不支持 -font 选项）
            style = ttk.Style()
            style.configure('Treeview', font=(font_name, int(font_size)),
                            background=bg_color, foreground=font_color,
                            fieldbackground=bg_color)
            style.configure('Treeview.Heading', font=(font_name, int(font_size), 'bold'),
                            background=bg_color, foreground=font_color)

            # 应用服务器说明区背景色和字体
            if info_bg_color is not None:
                self.log.write_log_info(f'应用服务器说明区背景色: {info_bg_color}')
                # 构建 Text 组件的标签字体配置
                tag_font = (font_name, int(font_size), 'normal')
                tag_foreground = font_color

                # 如果有自定义服务器说明字体设置，使用这些设置
                if server_info_font_size is not None:
                    try:
                        tag_font = (font_name, int(server_info_font_size), 'normal')
                    except (ValueError, TypeError):
                        pass
                if server_info_font_color is not None and server_info_font_color.strip():
                    tag_foreground = server_info_font_color

                self.server_info.configure(bg=info_bg_color, fg=tag_foreground)
                self.server_info.config(bg=info_bg_color, fg=tag_foreground)
                # 使用 tag 配置字体和颜色
                self.server_info.tag_configure('default', font=tag_font, foreground=tag_foreground)
                self.log.write_log_info(f'Text组件字体已设置为: {tag_font}, 颜色: {tag_foreground}')
                # 重新插入现有内容以应用新 tag
                current_text = self.server_info.get('1.0', tk.END).rstrip('\n')
                self.server_info.delete('1.0', tk.END)
                if current_text:
                    self.server_info.insert('1.0', current_text, 'default')
                # 强制刷新Text组件
                self.server_info.update_idletasks()
                self.master.after(50, lambda: self.server_info.update_idletasks())
                self.log.write_log_info(f'Text组件背景色已设置为: {info_bg_color}')
                # 更新滚动条样式
                for widget in self.right_frame_bottom.winfo_children():
                    if isinstance(widget, ttk.Scrollbar):
                        widget.configure(style='Custom.Vertical.TScrollbar')
                        # 动态更新滚动条颜色
                        style = ttk.Style()
                        style.configure('Custom.Vertical.TScrollbar', troughcolor=info_bg_color, arrowcolor=font_color)

            # 应用搜索框背景色
            if search_bg_color is not None:
                self.log.write_log_info(f'应用搜索框背景色: {search_bg_color}')
                # 更新搜索框容器背景色
                # self.top_R.configure(bg=search_bg_color)
                # Entry组件需要特殊处理
                self.search_entry.config(bg=search_bg_color, fg=font_color)
                self.search_entry.configure(bg=search_bg_color, fg=font_color)
                # 更新搜索标签颜色
                # self.search_label.configure(bg=search_bg_color, fg=font_color)
                # 强制刷新搜索框
                self.search_entry.update_idletasks()
                # self.search_label.update_idletasks()
                self.log.write_log_info(f'Entry组件背景色已设置为: {search_bg_color}')
                # 强制刷新整个界面
                self.top_R.update_idletasks()

            self.log.write_log_info('界面样式已更新')
            
            # 保持新容器区域为中性灰背景，不跟随全局背景色变化：
            # 左侧服务器说明区、右侧配置区及其内部容器/标题标签均固定 #F0F0F0
            for _w in (self.new_container, self.left_container, self.right_container,
                       self.ping_frame, self.faq_frame, self.rdp_frame, self.rdp_inner,
                       self.rdp_canvas):
                try:
                    _w.configure(bg='#F0F0F0')
                except Exception:
                    pass
            try:
                self.lable1.configure(bg='#F0F0F0')
            except Exception:
                pass
            try:
                self.title_label.configure(bg='#F0F0F0')
            except Exception:
                pass
            
            # 强制刷新Text和Entry组件
            self.refresh_text_component()
            self.refresh_entry_component()
            
            # 强制刷新整个界面
            self.master.update_idletasks()
            self.master.after(100, lambda: self.master.update_idletasks())
            
        except Exception as e:
            self.log.write_log_error('应用设置失败: ' + str(e))
    
    def force_refresh_ui(self):
        """强制刷新整个界面"""
        try:
            # 更新所有组件
            self.master.update_idletasks()

            # 重新加载并应用所有设置
            font_name = self.db.get_setting('ui_font', 'Microsoft YaHei')
            font_size = self.db.get_setting('ui_font_size', '10')
            bg_color = self.db.get_setting('ui_bg_color', '#F0F0F0')
            font_color = self.db.get_setting('ui_font_color', '#333333')
            info_bg_color = self.db.get_setting('ui_info_bg_color', '#F0F0F0')
            search_bg_color = self.db.get_setting('ui_search_bg_color', '#F0F0F0')
            server_info_font_size = self.db.get_setting('server_info_font_size')
            server_info_font_color = self.db.get_setting('server_info_font_color')

            # 应用所有设置
            self.apply_settings(font_name, font_size, bg_color,
                              font_color=font_color, info_bg_color=info_bg_color,
                              search_bg_color=search_bg_color,
                              server_info_font_size=server_info_font_size or None,
                              server_info_font_color=server_info_font_color or None)
            
            # 强制刷新Text和Entry组件
            self.refresh_text_component()
            self.refresh_entry_component()
            
            self.log.write_log_info('界面已强制刷新')
        except Exception as e:
            self.log.write_log_error('强制刷新界面失败: ' + str(e))
    
    def refresh_text_component(self):
        """强制刷新Text组件"""
        try:
            info_bg_color = self.db.get_setting('ui_info_bg_color', '#F0F0F0')
            font_color = self.db.get_setting('ui_font_color', '#333333')
            font_name = self.db.get_setting('ui_font', 'Microsoft YaHei')
            font_size = int(self.db.get_setting('ui_font_size', '10'))
            server_info_font_size = self.db.get_setting('server_info_font_size')
            server_info_font_color = self.db.get_setting('server_info_font_color')

            self.log.write_log_info(f'刷新Text组件 - 背景色: {info_bg_color}, 字体色: {font_color}')

            # 构建 Text 组件的标签字体配置
            tag_font = (font_name, font_size, 'normal')
            tag_foreground = font_color

            # 如果有自定义服务器说明字体设置，使用这些设置
            if server_info_font_size:
                try:
                    tag_font = (font_name, int(server_info_font_size), 'normal')
                except (ValueError, TypeError):
                    pass
            if server_info_font_color and server_info_font_color.strip():
                tag_foreground = server_info_font_color

            # 强制设置Text组件背景色和前景色
            self.server_info.configure(bg=info_bg_color, fg=tag_foreground)
            self.server_info.config(bg=info_bg_color, fg=tag_foreground)
            # 配置 tag 以应用字体和颜色
            self.server_info.tag_configure('default', font=tag_font, foreground=tag_foreground)
            # 重新插入现有内容以应用新 tag
            current_text = self.server_info.get('1.0', tk.END).rstrip('\n')
            self.server_info.delete('1.0', tk.END)
            if current_text:
                self.server_info.insert('1.0', current_text, 'default')

            # 强制刷新Text组件
            self.server_info.update_idletasks()
            self.server_info.update()
            self.master.after(50, lambda: self.server_info.update_idletasks())

            self.log.write_log_info('Text组件刷新成功')
        except Exception as e:
            self.log.write_log_error('刷新Text组件失败: ' + str(e))
    
    def refresh_entry_component(self):
        """强制刷新Entry组件"""
        try:
            search_bg_color = self.db.get_setting('ui_search_bg_color', '#F0F0F0')
            font_color = self.db.get_setting('ui_font_color', '#333333')
            
            self.log.write_log_info(f'刷新Entry组件 - 背景色: {search_bg_color}, 字体色: {font_color}')
            
            # 强制设置Entry组件颜色
            self.search_entry.config(bg=search_bg_color, fg=font_color)
            self.search_entry.configure(bg=search_bg_color, fg=font_color)
            
            # 强制刷新Entry组件
            self.search_entry.update_idletasks()
            self.search_entry.update()
            
            self.log.write_log_info('Entry组件刷新成功')
        except Exception as e:
            self.log.write_log_error('刷新Entry组件失败: ' + str(e))

    def apply_all_settings(self, ssh_tool_type, ssh_paths, vnc_path, default_user, default_pass,
                           ssh_port, vnc_port, font_name, font_size, bg_color,
                           font_color, info_bg_color, search_bg_color,
                           server_info_font_size=None, server_info_font_color=None):
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
        # F: 保存服务器说明字体设置
        if server_info_font_size is not None:
            self.db.set_setting('server_info_font_size', str(server_info_font_size))
        if server_info_font_color is not None:
            self.db.set_setting('server_info_font_color', server_info_font_color)
        self.apply_settings(font_name, font_size, bg_color,
                            font_color=font_color, info_bg_color=info_bg_color,
                            search_bg_color=search_bg_color,
                            server_info_font_size=server_info_font_size,
                            server_info_font_color=server_info_font_color)

        # 确保界面完全刷新
        self.force_refresh_ui()

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
            server_info_font_size = entry_server_info_font_size.get().strip()
            server_info_font_color = entry_server_info_font_color.get().strip()
            preview_label.configure(bg=bg_color)

            self.apply_all_settings(ssh_tool_type, ssh_paths, vnc_path, default_user, default_pass,
                                    ssh_port, vnc_port, font_name, font_size, bg_color,
                                    font_color, info_bg_color, search_bg_color,
                                    server_info_font_size=server_info_font_size or None,
                                    server_info_font_color=server_info_font_color or None)
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
                'server_info_font_size': '',
                'server_info_font_color': '',
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
            entry_server_info_font_size.delete(0, tk.END)
            entry_server_info_font_color.delete(0, tk.END)
            preview_label.configure(bg='#F0F0F0')

            # 立即应用到主窗口
            self.apply_settings('Microsoft YaHei', 10, '#F0F0F0',
                                font_color='#333333', info_bg_color='#FFFFFF',
                                search_bg_color='#FFFFFF')
            
            # 强制刷新界面
            self.force_refresh_ui()
            
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

        # 分隔线 - 区分全局设置和服务器说明设置
        separator = tk.Label(tab3, text='──────────────────────────────────────────────',
                             font=('Microsoft YaHei', 9), fg='#888888')
        separator.place(x=20, y=425)
        tk.Label(tab3, text='【服务器说明字体设置】', bg='#F0F0F0',
                 font=('Microsoft YaHei', 10, 'bold'), fg='#4CAF50').place(x=20, y=440)

        # 服务器说明字体大小
        tk.Label(tab3, text='字体大小：', bg='#F0F0F0', font=('Microsoft YaHei', 10)).place(x=20, y=470)
        entry_server_info_font_size = tk.Entry(tab3, width=8, font=('Microsoft YaHei', 10))
        entry_server_info_font_size.place(x=100, y=467)

        # 服务器说明字体颜色
        tk.Label(tab3, text='字体颜色：', bg='#F0F0F0', font=('Microsoft YaHei', 10)).place(x=20, y=500)
        entry_server_info_font_color = tk.Entry(tab3, width=10, font=('Microsoft YaHei', 10))
        entry_server_info_font_color.place(x=100, y=497)
        btn_server_info_color_picker = tk.Button(tab3, text='取色', font=('Microsoft YaHei', 9),
                                                  command=lambda: _pick_color(entry_server_info_font_color, preview_server_info_color))
        btn_server_info_color_picker.place(x=185, y=492)
        preview_server_info_color = tk.Label(tab3, bg='#333333', width=15, height=3, relief='solid', bd=1)
        preview_server_info_color.place(x=225, y=492)
        tk.Label(tab3, text='（颜色预览）', bg='#F0F0F0', font=('Microsoft YaHei', 9), fg='#888888').place(x=300, y=507)

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
        # F: 加载服务器说明字体设置
        server_info_font_size_val = self.db.get_setting('server_info_font_size')
        server_info_font_color_val = self.db.get_setting('server_info_font_color')
        if server_info_font_size_val:
            entry_server_info_font_size.insert(0, server_info_font_size_val)
        if server_info_font_color_val:
            entry_server_info_font_color.insert(0, server_info_font_color_val)
            preview_server_info_color.configure(bg=server_info_font_color_val)
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
        self.log.write_log_info('事件触发：编辑主机信息')
        # 1. 先从servertree获取当前选中的item的server信息
        selected_item = self.server_tree.focus()
        if not selected_item:
            messagebox.showerror('提示', '请先选中要修改的主机')
            return
        
        item_values = self.server_tree.item(selected_item).get('values')
        if not item_values or len(item_values) < 6:
            messagebox.showerror("提示", "服务器信息不完整")
            return
        
        # 树中数据显示格式：[连接类型, 主机名, 主机地址, 端口号, 用户名, 密码]
        # 注意：Treeview会把纯数字值自动转成int，必须统一转换为str
        current_name = str(item_values[1])      # 主机名（显示名称）
        current_host = str(item_values[2])      # 主机地址（用于数据库定位）
        current_port = str(item_values[3])      # 端口号
        current_username = str(item_values[4])  # 用户名
        
        # 从数据库获取密码（按host查询确保唯一性；数据库无记录时回退到树中值）
        current_password = self.db.get_server_password_by_host(current_host)
        if current_password is None:
            current_password = str(item_values[5]) if len(item_values) > 5 else ''
        if current_password is None:
            current_password = ''
        
        # 安全修复：密码脱敏处理
        masked_password = current_password[:2] + '*' * (len(current_password) - 2) if len(current_password) > 2 else '*' * len(current_password)
        self.log.write_log_info('主机名：' + current_name + ',主机ip : ' + current_host + '端口号：' + str(current_port) + '用户名：' + current_username + '密码：' + masked_password)
        
        def edit_da():
            # 2. 根据编辑主机的下拉框判断要修改的字段
            select_collu = down.get()
            host = current_host

            try:
                # 分组编辑：需要从分组树获取当前选中的分组
                select_group_id = None
                if select_collu == '分组':
                    selectItem_groupTree = self.group_tree.focus()
                    if not selectItem_groupTree:
                        messagebox.showinfo('提示', '请先在左侧分组树中选择分组')
                        return
                    selectTree_name = self.group_tree.item(selectItem_groupTree)['text']
                    select_group_id = self.db.get_group_focus_id(selectTree_name)
                    if select_group_id is None:
                        messagebox.showinfo('提示', '未选择分组,请选择分组')
                        self.log.write_log_error('未选择分组，编辑主机信息失败')
                        return

                # 读取用户输入的新值
                new_value = conten_entry.get("1.0", tk.END).rstrip("\n")

                # 字段映射：下拉框选项 -> 数据库字段名
                field_map = {
                    '主机名': 'name',
                    '主机地址': 'host',
                    '端口号': 'port',
                    '用户名': 'username',
                    '密码': 'password',
                    '主机类型': 'conn_type',
                    '服务器说明': 'server_info',
                }

                if select_collu == '分组':
                    field = 'parent_id'
                    value = int(select_group_id)
                    display_value = str(select_group_id)
                elif select_collu in field_map:
                    field = field_map[select_collu]
                    value = new_value
                    display_value = new_value
                    # 主机名：非空 + 查重
                    if select_collu == '主机名':
                        if not value:
                            messagebox.showinfo('提示', '主机名不能为空')
                            self.log.write_log_error('主机名不能为空，编辑失败')
                            return
                        if value != current_name and self.db.exists(value, 'servers'):
                            messagebox.showinfo('提示', '主机名已存在')
                            self.log.write_log_error('主机名已存在，编辑失败')
                            return
                    # 主机地址：非空 + 查重
                    elif select_collu == '主机地址':
                        if not value:
                            messagebox.showinfo('提示', '主机地址不能为空')
                            self.log.write_log_error('主机地址不能为空，编辑失败')
                            return
                        if value != current_host and self.db.ip_exists(value):
                            messagebox.showinfo('提示', '主机地址已存在')
                            self.log.write_log_error('主机地址已存在，编辑失败')
                            return
                    # 端口号：必须是数字
                    elif select_collu == '端口号':
                        if not value.isdigit():
                            messagebox.showinfo('提示', '端口号必须是数字')
                            self.log.write_log_error('端口号必须是数字，编辑失败')
                            return
                else:
                    messagebox.showinfo('提示', '不支持的操作')
                    self.log.write_log_error('编辑失败：不支持的操作')
                    return

                # 3. 更新sqlite
                self.db.update_server(field, value, host)

                # 4. 刷新servertree界面（从数据库重新加载，立即反映修改）
                self.server_tree.delete(*self.server_tree.get_children())
                self.init_server_data()

                messagebox.showinfo('提示', '编辑成功')
                # 日志记录（密码脱敏）
                if select_collu == '密码':
                    masked_new = value[:2] + '*' * (len(value) - 2) if len(value) > 2 else '*' * len(value)
                    self.log.write_log_info('主机:' + host + '编辑成功,密码修改为:' + masked_new)
                else:
                    self.log.write_log_info('主机:' + host + '编辑成功,' + select_collu + '修改为:' + display_value)
                self.top.destroy()
            except Exception as e:
                messagebox.showerror('错误', '编辑失败：' + str(e))
                self.log.write_log_error('服务器编辑失败' + str(e))
            
        # 创建编辑主机窗口
        self.top = tk.Toplevel()
        self.top.title("编辑主机")
        self.top_master(self.top, 300)
        # 锁定焦点
        self.top.grab_set()
        self.top.resizable(0, 0)
        lab1 = tk.Label(self.top, text="请选择要修改的内容：")
        lab1.pack(pady=5)
        down = ttk.Combobox(self.top, values=['主机名', '主机地址','端口号','用户名','密码','主机类型','分组','服务器说明'],state='readonly', width=20)
        down.current(0)
        down.pack()

        # 主机类型标签和输入框
        lab2 = tk.Label(self.top, text="修改为：")
        lab2.pack(pady=5)
        conten_entry = tk.Text(self.top, height=5, width=23)
        conten_entry.pack()

        # 当选择"主机类型"时，显示类型选择对话框
        def on_type_select():
            selected = down.get()
            if selected == '主机类型':
                # 创建类型选择弹窗
                type_win = tk.Toplevel(self.top)
                type_win.title("选择主机类型")
                type_win.grab_set()
                type_win.resizable(0, 0)
                type_win.configure(bg='#F0F0F0')

                current_type = item_values[0] if len(item_values) > 0 else 'SSH'
                selected_type = [current_type]

                def confirm_type():
                    new_type = combo_type.get()
                    if new_type in ['SSH', 'RDP', 'VNC', 'Radmin', 'URL']:
                        self.db.update_server('conn_type', new_type, current_host)
                        self.server_tree.delete(*self.server_tree.get_children())
                        self.init_server_data()
                        messagebox.showinfo('提示', f'主机类型已修改为: {new_type}')
                        self.log.write_log_info(f'主机:{current_host} 主机类型修改为: {new_type}')
                        self.top.destroy()
                    type_win.destroy()

                tk.Label(type_win, text="请选择连接类型：", bg='#F0F0F0', font=('Microsoft YaHei', 10)).pack(pady=10)
                combo_type = ttk.Combobox(type_win, values=['SSH', 'RDP', 'VNC', 'Radmin', 'URL'], state='readonly', width=15)
                combo_type.set(current_type)
                combo_type.pack(pady=5)

                btn_confirm = tk.Button(type_win, text="确定", width=8, command=confirm_type)
                btn_confirm.pack(side=tk.LEFT, padx=10, pady=10)
                btn_cancel = tk.Button(type_win, text="取消", width=8, command=type_win.destroy)
                btn_cancel.pack(side=tk.RIGHT, padx=10, pady=10)
                return False
            return True

        down.bind('<<ComboboxSelected>>', lambda e: on_type_select())

        btn = tk.Button(self.top, text="确定", width=10, command=edit_da)
        btn.pack(pady=5)
        btn2 = tk.Button(self.top, text="取消", width=10, command=self.top.destroy)
        btn2.pack(pady=5)

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
                    self.server_tree.insert('', "end", image=icon if icon else '', values=(r[1], r[2], r[3], r[4], r[5], '********', ''))

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
        self.server_menu.add_separator()
        self.server_menu.add_command(label='显示密码',command=self.show_password)

        self.server_menu.post(event.x_root, event.y_root)   # 在鼠标位置显示菜单

    def show_password(self):
        """显示选中行的密码"""
        selected_item = self.server_tree.focus()
        if not selected_item:
            messagebox.showinfo('提示', '请先选中要查看密码的主机')
            return
        item_values = self.server_tree.item(selected_item)['values']
        if not item_values or len(item_values) < 3:
            messagebox.showerror('错误', '服务器信息不完整')
            return
        host = str(item_values[2])  # 主机地址
        password = self.db.get_server_password_by_host(host)
        if password is None:
            password = ''
        # 更新当前行的密码列
        new_values = list(item_values)
        new_values[5] = password
        self.server_tree.item(selected_item, values=tuple(new_values))
        self.log.write_log_info('主机 ' + host + ' 密码已显示')
    # group_tree 释放焦点事件
    def groupTree_release(self,event):
        # 延迟执行清除操作，确保覆盖Treeview内部的选中处理
        self.group_tree.after(50, self._clear_group_tree_selection)

    def _clear_group_tree_selection(self):
        # 获取当前所有选中的项并全部取消选中
        selection = self.group_tree.selection()
        if selection:
            self.group_tree.selection_remove(*selection)
        # group_tree焦点设为空
        self.group_tree.focus("")

    # server_tree 释放焦点事件
    def Stree_release(self,event):
        # 延迟执行清除操作，确保覆盖Treeview内部的选中处理
        self.server_tree.after(50, self._clear_server_tree_selection)

    def _clear_server_tree_selection(self):
        # 获取当前所有选中的项并全部取消选中
        selection = self.server_tree.selection()
        if selection:
            self.server_tree.selection_remove(*selection)
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

        # 获取当前分组信息
        selected_item = self.group_tree.focus()
        old_name = self.group_tree.item(selected_item)['text']
        group_id = self.db.get_group_id(old_name)

        # 创建重命名弹窗
        self.top = tk.Toplevel()
        self.top.title("重命名分组")
        self.top_master(self.top, 150)
        self.top.grab_set()
        self.top.resizable(0, 0)

        lab1 = tk.Label(self.top, text="新分组名称：")
        lab1.pack(pady=10)
        name_entry = tk.Entry(self.top, width=20)
        name_entry.pack()
        name_entry.insert(0, old_name)
        name_entry.select_range(0, tk.END)
        name_entry.focus()

        def confirm_rename():
            new_name = name_entry.get().strip()
            if not new_name:
                messagebox.showerror('错误', '分组名称不能为空！')
                return
            if new_name == old_name:
                self.top.destroy()
                return
            # 检查分组是否已存在
            if self.db.exists(new_name, "groups"):
                messagebox.showerror('错误', '分组已存在！')
                return
            # 更新数据库
            self.db.update_group(group_id, new_name)
            self.log.write_log_info(f'分组 "{old_name}" 重命名为 "{new_name}" 成功')
            # 刷新分组树
            self.init_groups_data()
            # 更新item_map映射（item_map 在 db 对象中）
            # 注意：init_groups_data() 会清除 item_map，所以重命名后无需手动维护映射
            self.top.destroy()

        btn = tk.Button(self.top, text="确定", width=8, command=confirm_rename)
        btn.pack(side=tk.LEFT, padx=10, pady=5)
        btn2 = tk.Button(self.top, text="取消", width=8, command=self.top.destroy)
        btn2.pack(side=tk.RIGHT, padx=10, pady=5)

        # 绑定回车键确认
        self.top.bind('<Return>', lambda e: confirm_rename())
        self.top.bind('<Escape>', lambda e: self.top.destroy())

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
            password = self.db.get_server_password_by_host(host)
            if not password:
                password = ''
            
            # 添加连接确认弹框
            confirm_msg = f"确认连接到主机：\n\n主机名：{name}\n地址：{host}:{port}\n类型：RDP\n用户名：{username}"
            result = messagebox.askyesno('确认连接', confirm_msg)
            if not result:
                self.log.write_log_info('用户取消RDP连接')
                return
            
            self.too.run_mstsc(host, port, username, password)
            self.log.write_log_info('RDP连接: ' + host + ' 端口:' + port + ' 用户:' + username)
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
            name = self.server_tree.item(selected_item)['values'][1]
            host = self.server_tree.item(selected_item)['values'][2]
            
            # 添加连接确认弹框
            confirm_msg = f"确认打开URL：\n\n主机名：{name}\n地址：{host}\n类型：URL"
            result = messagebox.askyesno('确认连接', confirm_msg)
            if not result:
                self.log.write_log_info('用户取消URL连接')
                return
            
            self.too.thread_it(self.too.open_browser, host)
            self.log.write_log_info('URL连接: ' + host)
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
            server_info_text = self.db.get_serverINFO_by_host(sever_host)
            # 先配置tag再插入，确保字体/颜色立即生效
            font_name = self.db.get_setting('ui_font', 'Microsoft YaHei')
            font_size = int(self.db.get_setting('ui_font_size', '10'))
            font_color = self.db.get_setting('ui_font_color', '#333333')
            server_info_font_size = self.db.get_setting('server_info_font_size')
            server_info_font_color = self.db.get_setting('server_info_font_color')
            tag_font = (font_name, font_size, 'normal')
            tag_fg = font_color
            if server_info_font_size:
                try:
                    tag_font = (font_name, int(server_info_font_size), 'normal')
                except (ValueError, TypeError):
                    pass
            if server_info_font_color and server_info_font_color.strip():
                tag_fg = server_info_font_color
            self.server_info.tag_configure('default', font=tag_font, foreground=tag_fg)
            self.server_info.configure(fg=tag_fg)
            self.server_info.config(fg=tag_fg)
            self.server_info.delete('1.0', tk.END)
            self.server_info.insert('1.0', server_info_text, 'default')
            # B28: 移除调试输出
            self.server_info.update()
            self.master.after(50, lambda: self.server_info.update_idletasks())

    # group_tree焦点变更事件
    def on_group_selection_change(self, event):
        selected_item  = self.group_tree.selection()
        # B28: 移除调试输出
        if selected_item:
            item = self.group_tree.item(selected_item)
            group_name = item['text']
            group_id = self.db.get_group_id(group_name)
            # 无论分组下是否有主机，都先清空服务器树（无主机时显示空表格）
            self.server_tree.delete(*self.server_tree.get_children())
            res = self.db.get_servers_by_group_id(group_id)
            for r in res:
                icon = self._get_server_icons(r[1])
                self.server_tree.insert('', 'end', image=icon if icon else '', values=(r[1], r[2], r[3], r[4], r[5], '********', ''))


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

    # Ping检测功能
    def ping_all_servers(self):
        """遍历servertree中的所有主机，执行ping检测并更新状态列（后台线程执行，不阻塞界面）"""
        try:
            # 防止重复点击
            if getattr(self, '_ping_running', False):
                return
            self._ping_running = True
            self.ping_btn.config(state='disabled', text='检测中...')
            
            # 获取所有主机项（仅复制 iid 与主机地址，避免在线程中操作 Tk 对象）
            items = self.server_tree.get_children()
            if not items:
                messagebox.showinfo('提示', '没有可检测的主机')
                self.ping_btn.config(state='normal', text='Ping检测')
                self._ping_running = False
                return
            
            # 创建进度提示
            progress_window = tk.Toplevel(self.master)
            progress_window.title('Ping检测进度')
            progress_window.geometry('300x100')
            progress_window.resizable(False, False)
            progress_window.transient(self.master)
            progress_window.grab_set()
            
            # 居中显示
            master_x = self.master.winfo_rootx()
            master_y = self.master.winfo_rooty()
            master_width = self.master.winfo_width()
            master_height = self.master.winfo_height()
            popup_x = master_x + (master_width // 2) - 150
            popup_y = master_y + (master_height // 2) - 50
            progress_window.geometry(f'300x100+{popup_x}+{popup_y}')
            
            tk.Label(progress_window, text='正在检测主机连通性...', font=('Microsoft YaHei', 10)).pack(pady=10)
            progress_label = tk.Label(progress_window, text='0/0', font=('Microsoft YaHei', 10))
            progress_label.pack()
            
            # 收集主机地址（仅字符串），供后台线程使用
            hosts = []
            for item in items:
                vals = self.server_tree.item(item)['values']
                if vals and len(vals) >= 3:
                    hosts.append((item, str(vals[2])))
                else:
                    hosts.append((item, ''))
            
            total = len(hosts)
            result_queue = queue.Queue()
            
            def worker():
                """后台线程：执行所有 ping 检测，结果放入队列"""
                for idx, (item, host) in enumerate(hosts):
                    if not host:
                        result_queue.put((idx, item, False, '地址为空'))
                        continue
                    # 从 URL 中提取可 ping 的主机名（如 https://www.baidu.com -> www.baidu.com）
                    ping_host = self._extract_ping_host(host)
                    try:
                        if platform.system().lower() == 'windows':
                            cmd = ['ping', '-n', '1', '-w', '1000', ping_host]
                        else:
                            cmd = ['ping', '-c', '1', '-W', '1', ping_host]
                        result = subprocess.run(cmd, capture_output=True, text=True, timeout=2)
                        is_online = result.returncode == 0
                        result_queue.put((idx, item, is_online, host))
                    except Exception as e:
                        result_queue.put((idx, item, False, host))
                # 哨兵：检测结束
                result_queue.put((None, None, None, None))
            
            def poll_queue():
                """主线程轮询队列，更新 UI（不阻塞）"""
                try:
                    while True:
                        msg = result_queue.get_nowait()
                        idx, item, is_online, host = msg
                        if idx is None:
                            # 全部完成
                            progress_window.destroy()
                            self.ping_btn.config(state='normal', text='Ping检测')
                            self._ping_running = False
                            messagebox.showinfo('完成', '所有主机检测完成')
                            return
                        # 更新状态列
                        cur_vals = list(self.server_tree.item(item)['values'])
                        while len(cur_vals) < 7:
                            cur_vals.append('')
                        status_text = '✓' if is_online else '✗'
                        cur_vals[6] = status_text
                        self.server_tree.item(item, values=tuple(cur_vals))
                        progress_label.config(text=f'{idx + 1}/{total} - 检测 {host}')
                        self.log.write_log_info(f'主机 {host} ping检测结果: {"正常" if is_online else "异常"}')
                except queue.Empty:
                    pass
                # 继续轮询
                self.master.after(100, poll_queue)
            
            # 启动后台线程
            t = threading.Thread(target=worker, daemon=True)
            t.start()
            # 启动主线程轮询
            self.master.after(100, poll_queue)
            
        except Exception as e:
            self.log.write_log_error(f'Ping检测失败: {e}')
            messagebox.showerror('错误', f'Ping检测失败: {e}')
            self.ping_btn.config(state='normal', text='Ping检测')
            self._ping_running = False

    @staticmethod
    def _extract_ping_host(raw_host):
        """从输入中提取可用于 ping 的主机名/IP。
        支持：纯 IP、域名、带协议头的 URL（http://、https://）、带端口（host:port）等。
        """
        h = (raw_host or '').strip()
        if not h:
            return ''
        # 去除协议头
        if '://' in h:
            h = h.split('://', 1)[1]
        # 去除路径、查询参数
        for sep in ['/', '?', '#']:
            if sep in h:
                h = h.split(sep, 1)[0]
        # 去除端口（IPv6 暂不特殊处理）
        if ':' in h:
            h = h.split(':', 1)[0]
        # 去除用户信息 user@host
        if '@' in h:
            h = h.split('@', 1)[1]
        return h.strip()

    # FAQ知识库功能（暂不实现）
    def show_faq(self):
        """显示FAQ知识库（功能暂不实现）"""
        messagebox.showinfo('提示', 'FAQ知识库功能正在开发中，敬请期待！')
        self.log.write_log_info('用户点击了FAQ知识库按钮')
    
    # 创建远程桌面高级选项UI
    def create_rdp_options_ui(self):
        """创建远程桌面高级选项UI容器（网格布局，一行多个选项）"""
        # 标题（上下边距小、字体小）
        title_label = tk.Label(self.rdp_inner, text="远程桌面高级选项", 
                              font=('Microsoft YaHei', 10, 'bold'), bg='#F0F0F0')
        title_label.pack(pady=(2, 8))
        
        # 创建选项容器（3列网格，列权重拉伸填满宽度避免空白）
        options_frame = tk.Frame(self.rdp_inner, bg='#F0F0F0')
        options_frame.pack(fill=tk.X, padx=10)
        options_frame.columnconfigure(0, weight=1)
        options_frame.columnconfigure(1, weight=1)
        options_frame.columnconfigure(2, weight=1)
        
        # 第0行：远程音频位置 | 远程桌面分辨率（分辨率跨2列占满右侧）
        # 远程音频位置
        audio_frame = tk.Frame(options_frame, bg='#F0F0F0')
        tk.Label(audio_frame, text="远程音频：", anchor='w', 
                font=('Microsoft YaHei', 10), bg='#F0F0F0').pack(side=tk.LEFT)
        self.audio_var = tk.StringVar(value="local")
        audio_combo = ttk.Combobox(audio_frame, textvariable=self.audio_var, 
                                  values=["本地", "远程"], width=8, state='readonly')
        audio_combo.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        audio_combo.bind('<<ComboboxSelected>>', lambda e: self.save_rdp_settings())
        audio_frame.grid(row=0, column=0, sticky='ew', padx=5, pady=5)
        
        # 远程桌面分辨率（跨2列，占满右侧宽度）
        resolution_frame = tk.Frame(options_frame, bg='#F0F0F0')
        tk.Label(resolution_frame, text="分辨率：", anchor='w', 
                font=('Microsoft YaHei', 10), bg='#F0F0F0').pack(side=tk.LEFT)
        self.resolution_var = tk.StringVar(value="1024x768")
        resolution_combo = ttk.Combobox(resolution_frame, textvariable=self.resolution_var, 
                                       values=["640x480", "800x600", "1024x768", "1280x720", 
                                              "1366x768", "1920x1080", "自定义"], 
                                       width=10, state='readonly')
        resolution_combo.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        resolution_frame.grid(row=0, column=1, columnspan=2, sticky='ew', padx=5, pady=5)
        
        # 第1行：启用剪贴板 | 全屏模式 | 映射本地驱动器（三个一行）
        self.clipboard_var = tk.BooleanVar(value=True)
        clipboard_check = tk.Checkbutton(options_frame, text="启用剪贴板", 
                                       variable=self.clipboard_var, 
                                       command=self.save_rdp_settings,
                                       font=('Microsoft YaHei', 10), bg='#F0F0F0', anchor='w')
        clipboard_check.grid(row=1, column=0, sticky='ew', padx=5, pady=5)
        
        self.fullscreen_var = tk.BooleanVar(value=False)
        fullscreen_check = tk.Checkbutton(options_frame, text="全屏模式", 
                                         variable=self.fullscreen_var, 
                                         command=self.save_rdp_settings,
                                         font=('Microsoft YaHei', 10), bg='#F0F0F0', anchor='w')
        fullscreen_check.grid(row=1, column=1, sticky='ew', padx=5, pady=5)
        
        self.drive_var = tk.BooleanVar(value=False)
        drive_check = tk.Checkbutton(options_frame, text="映射本地驱动器", 
                                    variable=self.drive_var, 
                                    command=self.save_rdp_settings,
                                    font=('Microsoft YaHei', 10), bg='#F0F0F0', anchor='w')
        drive_check.grid(row=1, column=2, sticky='ew', padx=5, pady=5)
        
        # 自定义分辨率输入框（初始隐藏，跟随分辨率行下方）
        self.custom_resolution_frame = tk.Frame(options_frame, bg='#F0F0F0')
        tk.Label(self.custom_resolution_frame, text="自定义：", 
                font=('Microsoft YaHei', 10), bg='#F0F0F0').pack(side=tk.LEFT)
        self.custom_resolution_entry = tk.Entry(self.custom_resolution_frame, width=10)
        self.custom_resolution_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.custom_resolution_frame.grid(row=3, column=1, sticky='ew', padx=5, pady=6)
        self.custom_resolution_frame.grid_remove()  # 默认隐藏
        
        # 当选择"自定义"时显示输入框
        def on_resolution_change(event):
            if self.resolution_var.get() == "自定义":
                self.custom_resolution_frame.grid()
            else:
                self.custom_resolution_frame.grid_remove()
                self.save_rdp_settings()
        
        resolution_combo.bind('<<ComboboxSelected>>', on_resolution_change)
        
        # 保存按钮
        save_btn = tk.Button(self.rdp_inner, text="保存设置", command=self.save_rdp_settings,
                            bg='#4CAF50', fg='white', width=10)
        save_btn.pack(pady=(2, 6))
    
    # 加载远程桌面设置
    def load_rdp_settings(self):
        """从数据库加载远程桌面设置"""
        try:
            # 从数据库读取设置
            audio_setting = self.db.get_setting('rdp_audio', 'local')
            clipboard_setting = self.db.get_setting('rdp_clipboard', '1') == '1'
            drive_setting = self.db.get_setting('rdp_drive', '0') == '1'
            fullscreen_setting = self.db.get_setting('rdp_fullscreen', '0') == '1'
            resolution_setting = self.db.get_setting('rdp_resolution', '1024x768')
            
            # 设置控件值
            self.audio_var.set(audio_setting)
            self.clipboard_var.set(clipboard_setting)
            self.drive_var.set(drive_setting)
            self.fullscreen_var.set(fullscreen_setting)
            self.resolution_var.set(resolution_setting)
            
            self.log.write_log_info('远程桌面设置加载成功')
            
        except Exception as e:
            self.log.write_log_error(f'加载远程桌面设置失败: {e}')
            # 使用默认值
            self.audio_var.set('local')
            self.clipboard_var.set(True)
            self.drive_var.set(False)
            self.fullscreen_var.set(False)
            self.resolution_var.set('1024x768')
    
    # 保存远程桌面设置
    def save_rdp_settings(self):
        """保存远程桌面设置到数据库"""
        try:
            # 获取设置值
            audio_value = self.audio_var.get()
            clipboard_value = '1' if self.clipboard_var.get() else '0'
            drive_value = '1' if self.drive_var.get() else '0'
            fullscreen_value = '1' if self.fullscreen_var.get() else '0'
            resolution_value = self.resolution_var.get()
            
            # 如果是自定义分辨率，使用输入框的值
            if resolution_value == "自定义":
                custom_resolution = self.custom_resolution_entry.get().strip()
                if custom_resolution and re.match(r'^\d+x\d+$', custom_resolution):
                    resolution_value = custom_resolution
                else:
                    messagebox.showwarning('警告', '请输入有效的自定义分辨率（格式：宽度x高度）')
                    return
            
            # 保存到数据库
            self.db.set_setting('rdp_audio', audio_value)
            self.db.set_setting('rdp_clipboard', clipboard_value)
            self.db.set_setting('rdp_drive', drive_value)
            self.db.set_setting('rdp_fullscreen', fullscreen_value)
            self.db.set_setting('rdp_resolution', resolution_value)
            
            self.log.write_log_info('远程桌面设置保存成功')
            
        except Exception as e:
            self.log.write_log_error(f'保存远程桌面设置失败: {e}')
            messagebox.showerror('错误', f'保存设置失败: {e}')
    


