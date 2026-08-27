
'''
   DA
'''
# \Object\DataAccess.py

import sqlite3
from contextlib import contextmanager
from tools.logs import logs

class DataAccess:
    def __init__(self, db_path):
        self.db = db_path              # 数据库路径
        self.log = logs()
        self.item_map = {}  # 用于存储 group_id 和 item id 的映射

    # Q5/Q7: 数据库连接上下文管理器，确保异常时连接一定关闭
    @contextmanager
    def _connect(self):
        conn = sqlite3.connect(self.db)
        try:
            yield conn, conn.cursor()
        finally:
            conn.close()

    # 创建数据库
    def create_database(self):
        try:
            with self._connect() as (conn, cursor):
                cursor.execute('''CREATE TABLE IF NOT EXISTS servers (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    conn_type TEXT,
                                    name TEXT,
                                    host TEXT,
                                    port INTEGER,
                                    username TEXT,
                                    password TEXT,
                                    parent_id INTEGER,
                                    server_info TEXT,
                                    foreign key(parent_id) references groups(id)
                                )''')
                cursor.execute('''CREATE TABLE IF NOT EXISTS groups (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    name TEXT,
                                    parent_id INTEGER
                                )''')
                cursor.execute('''CREATE TABLE IF NOT EXISTS settings (
                                    key TEXT PRIMARY KEY,
                                    value TEXT
                                )''')
                # 插入默认设置值
                # 任务2: 为每种SSH工具添加独立路径设置
                default_settings = [
                    ('ssh_tool_path_xterm', 'xterm'),
                    ('ssh_tool_path_plink', 'plink'),
                    ('ssh_tool_path_mobaxterm', 'MobaXterm.exe'),
                    ('ssh_tool_path_finalshell', 'finalshell.exe'),
                    ('ssh_tool_path_xshell', 'Xshell.exe'),
                    ('vnc_tool_path', 'vncviewer'),
                    ('default_username', ''),
                    ('default_password', ''),
                    ('default_ssh_port', '22'),
                    ('default_vnc_port', '5900'),
                    ('ui_font', 'Microsoft YaHei'),
                    ('ui_font_size', '10'),
                    ('ui_bg_color', '#F0F0F0'),
                    ('ui_font_color', '#000000'),  # 任务3: 字体颜色
                    ('ui_info_bg_color', '#FFFFFF'),  # 任务3: 服务器说明背景色
                    ('ui_search_bg_color', '#FFFFFF'),  # 任务3: 搜索框背景色
                    ('server_info_font_size', ''),  # F: 服务器说明字体大小（空表示使用全局字体大小）
                    ('server_info_font_color', ''),  # F: 服务器说明字体颜色（空表示使用全局字体颜色）
                    ('ssh_tool_type', 'xterm'),
                ]
                for key, value in default_settings:
                    cursor.execute('INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)', (key, value))
                conn.commit()
                # B27: 移除调试输出，保留日志记录
                self.log.write_log_info("数据库初始化成功")
        except sqlite3.Error as e:
            self.log.write_log_error("数据库初始化失败" + str(e))

    # 获取设置值
    def get_setting(self, key, default=''):
        try:
            with self._connect() as (conn, cursor):
                cursor.execute('SELECT value FROM settings WHERE key = ?', (key,))
                row = cursor.fetchone()
                return row[0] if row else default
        except sqlite3.Error as e:
            self.log.write_log_error('获取设置失败: ' + str(e))
            return default

    # 保存设置值
    def set_setting(self, key, value):
        try:
            with self._connect() as (conn, cursor):
                cursor.execute('INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)', (key, value))
                conn.commit()
                return True
        except sqlite3.Error as e:
            self.log.write_log_error('保存设置失败: ' + str(e))
            return False

    # 递归插入子节点 group_tree
    def insert_children(self, tree, folder_closed, folder_open, parent_group_id, cursor):
        # 查询指定 parent_id 的所有子节点
        cursor.execute("SELECT * FROM groups WHERE parent_id=?", (parent_group_id,))
        children = cursor.fetchall()

        for child in children:
            child_group_id, name, _ = child[:3]
            # 子节点默认折叠，使用folder_badge_plus.png图标
            item_id = tree.insert(self.item_map[parent_group_id], 'end', text=name, image=folder_closed, open=False)
            self.item_map[child_group_id] = item_id
            # 递归处理子节点的子节点
            self.insert_children(tree, folder_closed, folder_open, child_group_id, cursor)

    # 初始化组数据
    def init_groups_data(self, tree, folder_closed, folder_open):
        try:
            # 清空之前的树数据
            tree.delete(*tree.get_children())
            with self._connect() as (conn, cursor):
                cursor.execute("SELECT * FROM groups")
                results = cursor.fetchall()

                # 清空之前的映射表
                self.item_map.clear()
                # 插入顶级节点（默认全部展开）
                top_level_items = []
                for result in results:
                    group_id, name, parent_id = result[:3]
                    if parent_id is None:
                        # 根节点默认展开，使用folder_badge_plus.png图标
                        item_id = tree.insert('', 'end', text=name, image=folder_closed, open=True)
                        self.item_map[group_id] = item_id
                        top_level_items.append(group_id)
                # 递归插入子节点
                for group_id in top_level_items:
                    self.insert_children(tree, folder_closed, folder_open, group_id, cursor)
        except sqlite3.Error as e:
            # B27: 移除调试输出
            self.log.write_log_error(f"初始化组数据失败: {e}")

    # 初始化全部主机数据
    def init_servers_data(self, tree, icon_func=None):
        tree.delete(*tree.get_children())
        try:
            with self._connect() as (conn, cursor):
                cursor.execute("SELECT * FROM servers")
                results = cursor.fetchall()
                for r in results:
                    icon = icon_func(r[1]) if icon_func else None
                    tree.insert('', "end", image=icon if icon else '', values=(r[1], r[2], r[3], r[4], r[5], '********', ''))
                # B27: 移除调试输出，保留日志记录
                self.log.write_log_info("主机数据初始化成功")
        except sqlite3.Error as e:
            self.log.write_log_error("主机数据初始化失败" + str(e))

    # 检查主机名或者组名是否重复
    def exists(self, name, table):
        # 白名单校验表名，防止 SQL 注入
        allowed_tables = ('servers', 'groups')
        if table not in allowed_tables:
            self.log.write_log_error('exists 方法：非法表名 ' + str(table))
            return False
        try:
            with self._connect() as (conn, cursor):
                cursor.execute("SELECT * FROM " + table + " WHERE name=?", (name,))
                result = cursor.fetchone()
                return result is not None
        except sqlite3.Error as e:
            # B27: 移除调试输出
            self.log.write_log_error(f"检查主机名重复失败: {e}")
            return False

    # ip查重
    def ip_exists(self, host):
        try:
            with self._connect() as (conn, cursor):
                cursor.execute("SELECT * FROM servers WHERE host=?", (host,))
                result = cursor.fetchone()
                return result is not None
        except sqlite3.Error as e:
            # B27: 移除调试输出
            self.log.write_log_error(f"IP查重失败: {e}")
            return False

    # 添加服务器
    def add_server(self, conn_type, name, host, port, username, password, parent_id, server_info):
        with self._connect() as (conn, cursor):
            cursor.execute('INSERT INTO servers (conn_type, name, host, port, username, password, parent_id, server_info) VALUES (?, ?, ?, ?, ?, ?, ?,?)', (conn_type, name, host, port, username, password, parent_id, server_info))
            conn.commit()
            return cursor.lastrowid

    # 添加组
    def add_group(self, name, parent_id):
        try:
            with self._connect() as (conn, cursor):
                cursor.execute('INSERT INTO groups (name, parent_id) VALUES (?,?)', (name, parent_id))
                conn.commit()
                lastrowid = cursor.lastrowid
                self.log.write_log_info(f"组数据存入成功: {name}")
                return lastrowid
        except sqlite3.IntegrityError:
            return None

    #   删除服务器
    def delete_server(self, host):
        with self._connect() as (conn, cursor):
            cursor.execute('DELETE FROM servers WHERE host = ?', (host,))
            rowcount = cursor.rowcount
            conn.commit()
            return rowcount

    # 删除组 +父节点
    def del_group(self, parent_id):
        with self._connect() as (conn, cursor):
            cursor.execute('DELETE FROM groups WHERE parent_id = ?', (parent_id,))
            rowcount = cursor.rowcount
            conn.commit()
            return rowcount

    # 删除分组 + name
    def delete_group(self, name):
        with self._connect() as (conn, cursor):
            cursor.execute('DELETE FROM groups WHERE name = ?', (name,))
            rowcount = cursor.rowcount
            conn.commit()
            return rowcount

    # 清空所有分组
    def clear_groups(self):
        with self._connect() as (conn, cursor):
            cursor.execute('DELETE FROM groups')
            conn.commit()

    # 清空所有服务器
    def clear_servers(self):
        with self._connect() as (conn, cursor):
            cursor.execute('DELETE FROM servers')
            conn.commit()

    # 根据分组name返回分组id
    def get_group_id(self, name):
        with self._connect() as (conn, cursor):
            cursor.execute('SELECT id FROM groups WHERE name = ?', (name,))
            result = cursor.fetchone()
            return str(result[0]) if result else None

    # 检查分组下是否有主机 返回True表示有主机，False表示没有主机
    def check_group_has_servers(self, id):
        with self._connect() as (conn, cursor):
            cursor.execute('SELECT * FROM servers WHERE parent_id = ?', (id,))
            result = cursor.fetchone()
            return result is not None

    # 根据server name 返回server id
    def get_server_id(self, name):
        with self._connect() as (conn, cursor):
            cursor.execute('SELECT id FROM servers WHERE name = ?', (name,))
            result = cursor.fetchone()
            return str(result[0]) if result else None

    # 更新服务器信息
    def update_server(self, select_collu, content, host):
        # 安全地构建 SQL 更新语句
        set_clause = f"{select_collu} = ?"
        sql = f"UPDATE servers SET {set_clause} WHERE host = ?"
        with self._connect() as (conn, cursor):
            cursor.execute(sql, (content, host))
            rowcount = cursor.rowcount
            conn.commit()
            return rowcount

    # 根据name获取主机数据并返回
    def get_server_by_name(self, name):
        with self._connect() as (conn, cursor):
            cursor.execute('SELECT name,host,port,username,password FROM servers WHERE name = ?', (name,))
            server = cursor.fetchone()
            return server if server else None

    # 根据name返回主机password
    def get_server_password(self, name):
        with self._connect() as (conn, cursor):
            cursor.execute('SELECT password FROM servers WHERE name =?', (name,))
            result = cursor.fetchone()
            return result[0] if result else None

    # 根据host返回主机password
    def get_server_password_by_host(self, host):
        with self._connect() as (conn, cursor):
            cursor.execute('SELECT password FROM servers WHERE host =?', (host,))
            result = cursor.fetchone()
            return result[0] if result else None

    # 更新组信息
    def update_group(self, id, name):
        with self._connect() as (conn, cursor):
            cursor.execute('UPDATE groups SET name = ? WHERE id = ?', (name, id))
            rowcount = cursor.rowcount
            conn.commit()
            return rowcount

    # 搜索
    def search_servers(self, keyword, type, tree):
        with self._connect() as (conn, cursor):
            if type is True:
                cursor.execute('SELECT * FROM servers WHERE host LIKE ?', ('%' + keyword + '%',))
            else:
                cursor.execute('SELECT * FROM servers WHERE name LIKE ?', ('%' + keyword + '%',))
            servers = cursor.fetchall()

            for r in servers:
                tree.insert('', "end", image='', values=(r[1], r[2], r[3], r[4], r[5], r[6], ''))

            return servers

    # 根据name返回组焦点的id
    def get_group_focus_id(self, name):
        with self._connect() as (conn, cursor):
            cursor.execute('SELECT id FROM groups WHERE name = ?', (name,))
            result = cursor.fetchone()
            if result is None:
                return None
            return str(result[0])

    # id查组名称
    def get_group_name(self, id):
        with self._connect() as (conn, cursor):
            cursor.execute('SELECT name FROM groups WHERE id = ?', (id,))
            result = cursor.fetchone()
            return str(result[0])

    # 根据分组id查询server表中数据并返回
    def get_servers_by_group_id(self, id):
        with self._connect() as (conn, cursor):
            cursor.execute('SELECT * FROM servers WHERE parent_id = ?', (id,))
            servers = cursor.fetchall()
            return servers

    # 判断group_tree选中的节点id是否在groups表的parent_id列中
    def check_group_in_groups(self, id):
        with self._connect() as (conn, cursor):
            cursor.execute('SELECT parent_id FROM groups WHERE parent_id = ?', (id,))
            result = cursor.fetchone()
            return result is not None

    # get servers server_info
    def get_serverINFO_by_host(self, host):
        with self._connect() as (conn, cursor):
            cursor.execute('SELECT server_info FROM servers WHERE host = ?', (host,))
            result = cursor.fetchone()
            return result[0] if result else None
