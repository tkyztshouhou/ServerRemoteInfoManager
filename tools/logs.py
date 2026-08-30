import os

'''
    日志记录
'''

class logs:
    def __init__(self, user_data_dir=None):
        # 延迟导入 Tool 类，避免循环导入
        from tools.tool import Tool
        self.too = Tool()
        # 日志目录：优先使用用户可写数据目录（打包后 Program Files 只读）
        if user_data_dir:
            self.log_path = os.path.join(user_data_dir, 'logs')
        else:
            # 未显式传入时回退到 %LOCALAPPDATA%/ServerRemoteInfoManager/logs，
            # 避免落到 C:\Program Files\...（只读）导致 PermissionError（B74）
            appdata = os.getenv('LOCALAPPDATA') or os.path.expanduser('~')
            self.log_path = os.path.join(appdata, 'ServerRemoteInfoManager', 'logs')
        # B25: 简化初始化逻辑，移除重复赋值和调试行
        if not os.path.exists(self.log_path):
            os.makedirs(self.log_path, exist_ok=True)
        self.day = self.too.time_day()
        self.log_file_path = os.path.join(self.log_path, self.day + 'log.txt')
        # 确保日志文件存在
        if not os.path.exists(self.log_file_path):
            with open(self.log_file_path, 'w'):
                pass
        
    # 写入日志 - B26: 使用 with 语句管理文件，确保异常时文件正确关闭
    def write_log(self, message):
        log_line = f"{self.too.time()} : ----- {message}\n"
        with open(self.log_file_path, 'a', encoding='utf-8') as f:
            f.write(log_line)
    
    def write_log_error(self, message):
        log_line = f"{self.too.time()} : ----- ERROR: {message}\n"
        with open(self.log_file_path, 'a', encoding='utf-8') as f:
            f.write(log_line)
    
    def write_log_info(self, message):
        log_line = f"{self.too.time()} : ----- INFO: {message}\n"
        with open(self.log_file_path, 'a', encoding='utf-8') as f:
            f.write(log_line)

