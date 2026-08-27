# faq/main.py
# FAQ 知识库程序入口（供主程序调用）

import os

from faq.sample_data import ensure_sample_data
from faq.ui import FaqWindow
from tools.logs import logs


def _default_faq_db_path() -> str:
    """FAQ 数据库路径：%LOCALAPPDATA%/ServerRemoteInfoManager/faq.db。"""
    appdata = os.getenv('LOCALAPPDATA') or os.path.expanduser('~')
    user_data_dir = os.path.join(appdata, 'ServerRemoteInfoManager')
    if not os.path.exists(user_data_dir):
        os.makedirs(user_data_dir, exist_ok=True)
    return os.path.join(user_data_dir, 'faq.db')


def open_faq(parent) -> None:
    """打开 FAQ 知识库 Toplevel 窗口（供主程序 infoServer.show_faq 调用）。

    :param parent: Tk 主窗口（tk.Tk 或 tk.Toplevel），用于作为父窗口与线程调度
    """
    log = logs()
    try:
        db_path = _default_faq_db_path()
        # 首次启动预置示例数据
        ensure_sample_data(db_path)
        # 单例：避免重复打开
        for w in parent.winfo_children():
            if isinstance(w, FaqWindow):
                w.lift()
                w.focus_force()
                return
        FaqWindow(parent, db_path)
        log.write_log_info('打开 FAQ 知识库窗口')
    except Exception as e:
        log.write_log_error('打开 FAQ 知识库失败: ' + str(e))
