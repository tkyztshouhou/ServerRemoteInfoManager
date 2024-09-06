
'''
    DA
'''
# \Object\DataAccess.py

import sqlite3
from tools.logs import logs

class DataAccess:
    def __init__(self, db_path):
        self.db = db_path              # 数据库路径
        self.log = logs()

    # 创建数据库
    def create_database(self):  
        try:
            conn = sqlite3.connect(self.db)
            cursor = conn.cursor()                  
            cursor.execute('''CREATE TABLE IF NOT EXISTS servers (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                conn_type TEXT,
                                name TEXT,
                                host TEXT,
                                port int,
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

            conn.commit()
            cursor.close()
            print("数据库初始化成功")
            self.log.write_log_info("数据库初始化成功")
        except sqlite3.Error as e:
            print('创建数据库失败：', e)
            self.log.write_log_error("数据库初始化失败" + str(e))
    

    # 初始化组数据
    def init_groups_data(self,tree,images):
        try:
            conn = sqlite3.connect(self.db)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM groups")
            results = cursor.fetchall()
            # 递归函数，用来渲染给定父节点下的所有子节点
            def render_subnodes(parent_node, nodes_dict, images):
                """递归函数，用来渲染给定父节点下的所有子节点"""
                print(f"{parent_node}")
                if parent_node in nodes_dict:
                    print(f"Rendering subnodes for parent: {parent_node}")
                    for group_id, name in nodes_dict[parent_node]:
                        child_node = tree.insert(parent_node, 'end', text=name, open=True, image=images)
                        print(f"Inserted child node: {child_node} with name: {name}")
                        render_subnodes(child_node, nodes_dict, images)  # 继续深入下一个层次
            # 创建一个字典来存储每个节点的记录和其对应的所有子节点
            nodes_dict = {}

            for result in results:
                group_id, name, parent_id = result[:3]
                if parent_id not in nodes_dict:
                    nodes_dict[parent_id] = []
                nodes_dict[parent_id].append((group_id, name))

            # 打印 nodes_dict 以检查数据是否正确
            print("Nodes Dict:", nodes_dict)

            # 开始渲染树状结构
            # 先处理顶级节点（parent_id 是 None 的）
            for group_id, name in nodes_dict.get(None, []):
                top_node = tree.insert('', 'end', text=name, open=True, image=images)

                # 接着递归处理所有的子节点
                render_subnodes(top_node, nodes_dict, images)
                    
        except Exception as e:
            print(f"Error: {e}")
        finally:
            cursor.close()
            conn.close()
    # 初始化全部主机数据
    def init_servers_data(self,tree):
        tree.delete(*tree.get_children())
        try:
            conn = sqlite3.connect(self.db)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM servers")
            results = cursor.fetchall()
            for r in results:
                tree.insert('', "end",values=(r[1],r[2],r[3],r[4],r[5],r[6]))
            cursor.close()
            conn.close()
            print("主机数据初始化成功")
            self.log.write_log_info("主机数据初始化成功")
        except Exception as e:
            print("主机数据初始化失败" + str(e))
            self.log.write_log_error("主机数据初始化失败" + str(e))
    # 检查主机名或者组名是否重复
    def exists(self, name,table):
        try:
            conn = sqlite3.connect(self.db)
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM {table} WHERE name=?", (name,))
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            return result is not None
        except Exception as e:
            print(e)
            return False

    # ip查重
    def ip_exists(self, host):
        try:
            conn = sqlite3.connect(self.db)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM servers WHERE host=?", (host,))
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            return result is not None
        except Exception as e:
            print(e)
            return False

    # 添加服务器
    def add_server(self, conn_type, name, host, port, username, password, parent_id,server_info):
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO servers (conn_type, name, host, port, username, password, parent_id,server_info) VALUES (?, ?, ?, ?, ?, ?, ?,?)', (conn_type, name, host, port, username, password, parent_id,server_info))
        conn.commit()
        cursor.close()
        return cursor.lastrowid
    
    # 添加组
    def add_group(self, name,parent_id):
        try:
            conn = sqlite3.connect(self.db)
            print("链接成功")
            cursor = conn.cursor()
            cursor.execute('INSERT INTO groups (name, parent_id) VALUES (?,?)', (name, parent_id))
            conn.commit()
            cursor.close()
            print("组数据存入成功")
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            return None
        finally:
            conn.close()
    
    #   删除服务器
    def delete_server(self, host):
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM servers WHERE host = ?', (host,))
        conn.commit()
        cursor.close()
        return cursor.rowcount
    
    # 删除组 +父节点
    def del_group(self, parent_id):
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM groups WHERE parent_id = ?', (parent_id,))
        conn.commit()
        cursor.close()
        return cursor.rowcount

    # 删除分组 + name
    def delete_group(self, name):
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM groups WHERE name = ?', (name,))
        conn.commit()
        cursor.close()
        return cursor.rowcount

    # 根据分组name返回分组id
    def get_group_id(self, name):
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM groups WHERE name = ?', (name,))
        result = cursor.fetchone()
        cursor.close()
        return str(result[0]) if result else None

    # 检查分组下是否有主机 返回True表示有主机，False表示没有主机
    def check_group_has_servers(self, id):
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM servers WHERE parent_id = ?', (id,))
        result = cursor.fetchone()
        cursor.close()
        return result is not None
    
    # 根据server name 返回server id
    def get_server_id(self, name):
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM servers WHERE name = ?', (name,))
        result = cursor.fetchone()
        cursor.close()
        return str(result[0]) if result else None

    # 更新服务器信息
    def update_server(self, select_collu,content,host):
        # 安全地构建 SQL 更新语句
        set_clause = f"{select_collu} = ?"
        sql = f"UPDATE servers SET {set_clause} WHERE host = ?"
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()
        cursor.execute(sql, (content, host))
        conn.commit()
        cursor.close()
        return cursor.rowcount
    
    # 根据name获取主机数据并返回
    def get_server_by_name(self, name):
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()
        cursor.execute('SELECT name,host,port,username,password FROM servers WHERE name = ?', (name,))
        server = cursor.fetchone()
        cursor.close()
        return server if server else None
    
    # 根据name返回主机password
    def get_server_password(self, name):
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()
        cursor.execute('SELECT password FROM servers WHERE name =?', (name,))
        password = cursor.fetchone()
        cursor.close()
        return password if password else None 

    # 更新组信息
    def update_group(self, id, name):
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()
        cursor.execute('UPDATE groups SET name = ? WHERE id = ?', (name, id))
        conn.commit()
        cursor.close()
        return cursor.rowcount
    
    # 搜索
    def search_servers(self, keyword,type,tree):
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()
        if type == True:
            cursor.execute('SELECT * FROM servers WHERE host LIKE ?', ('%' + keyword + '%',))
        elif type == False:
            cursor.execute('SELECT * FROM servers WHERE name LIKE ?', ('%' + keyword + '%',))
        servers = cursor.fetchall()
        
        for r in servers:
            tree.insert('', "end",values=(r[1],r[2],r[3],r[4],r[5]))
        cursor.close()
        return servers
    

    # 根据name返回组焦点的id
    def get_group_focus_id(self,name):
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM groups WHERE name = ?', (name,))
        result = cursor.fetchone()
        cursor.close()
        if result is None:
            return None
        return str(result[0])
    
    # id查组名称
    def get_group_name(self,id):
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()
        cursor.execute('SELECT name FROM groups WHERE id = ?', (id,))
        result = cursor.fetchone()
        cursor.close()
        return str(result[0])
    
    # 根据分组id查询server表中数据并返回
    def get_servers_by_group_id(self, id):
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM servers WHERE parent_id = ?', (id,))
        servers = cursor.fetchall()
        cursor.close()
        return servers
    
    # 判断group_tree选中的节点id是否在groups表的parent_id列中
    def check_group_in_groups(self, id):
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()
        cursor.execute('SELECT parent_id FROM groups WHERE parent_id = ?', (id,))
        result = cursor.fetchone()
        cursor.close()
        return result is not None
    
    # get servers server_info
    def get_serverINFO_by_host(self, host):
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()
        cursor.execute('SELECT server_info FROM servers WHERE host = ?', (host,))
        result = cursor.fetchone()
        cursor.close()
        return result[0] if result else None
    


