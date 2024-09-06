import os
from tools.tool import too

'''
    日志记录
'''

class logs:
    def __init__(self):
        self.too = too()
        self.log_path = os.path.join(os.getcwd(), 'logs')
        if not os.path.exists(self.log_path):
            self.day = self.too.time_day()
            os.mkdir(self.log_path)
            self.log_file = open(os.path.join(self.log_path, self.day + 'log.txt'), 'w')
            self.log_file.close()
        else:
            self.day = self.too.time_day()
            self.time = self.too.time()
            self.log_file = open(os.path.join(self.log_path, self.day + 'log.txt'), 'a')
            self.log_file.write(self.time + " : ----- DEBUG 日志文件存在\n")
            self.log_file.close()
        
    # 写入日志
    def write_log(self, message):
        self.time = self.too.time()
        self.log_file = open(os.path.join(self.log_path, self.day + 'log.txt'), 'a')
        self.log_file.write(self.time + " : -----" + message + "\n")
        self.log_file.close()
    
    def write_log_error(self, message):
        self.time = self.too.time()
        self.log_file = open(os.path.join(self.log_path, self.day + 'log.txt'), 'a')
        self.log_file.write(self.time + " : ----- ERROR: " + message + "\n")
        self.log_file.close()
    
    def write_log_info(self, message):
        self.time = self.too.time()
        self.log_file = open(os.path.join(self.log_path, self.day + 'log.txt'), 'a')
        self.log_file.write(self.time + " : ----- INFO: " + message + "\n")
        self.log_file.close()

