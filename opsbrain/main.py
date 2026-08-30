# opsbrain/main.py
# 运维智脑入口层：解析用户数据目录得到 aichat.db 路径，单例打开/复用聊天窗口，异常兜底日志。

import os

from tools.logs import logs


def _resolve_chat_db_path() -> str:
    """解析独立聊天库路径（%LOCALAPPDATA%/ServerRemoteInfoManager/aichat.db）。"""
    local = os.getenv('LOCALAPPDATA')
    if local:
        base = local
    else:
        base = os.path.expanduser('~')
    data_dir = os.path.join(base, 'ServerRemoteInfoManager')
    if not os.path.exists(data_dir):
        os.makedirs(data_dir, exist_ok=True)
    return os.path.join(data_dir, 'aichat.db')


# 单例窗口引用
_window_instance = None


def open_ops_brain(master=None) -> None:
    """打开（或聚焦已存在的）运维智脑聊天窗口。"""
    global _window_instance
    log = logs()

    # 复用已打开的窗口
    if _window_instance is not None:
        try:
            if _window_instance.winfo_exists():
                _window_instance.deiconify()
                _window_instance.lift()
                _window_instance.focus_force()
                return
        except Exception:
            _window_instance = None

    try:
        from opsbrain.ui import OpsBrainWindow
        from opsbrain.da import ModelDAO, ChatDAO
        from opsbrain.service import ModelService, ChatService

        # 解析主库路径（与主程序 InfoServer.__init__ 逻辑一致）
        appdata = os.getenv('LOCALAPPDATA')
        if appdata:
            main_db = os.path.join(appdata, 'ServerRemoteInfoManager', 'data.db')
        else:
            main_db = os.path.join(os.path.expanduser('~'), 'ServerRemoteInfoManager', 'data.db')

        chat_db = _resolve_chat_db_path()

        model_dao = ModelDAO(main_db)
        model_dao.ensure_schema()
        chat_dao = ChatDAO(chat_db)
        chat_dao.ensure_schema()
        model_svc = ModelService(model_dao)
        chat_svc = ChatService(model_svc, chat_dao)

        _window_instance = OpsBrainWindow(master, model_svc, chat_svc)
        _window_instance.protocol('WM_DELETE_WINDOW', _on_close)
        _window_instance.mainloop() if False else None  # 不阻塞主程序
    except Exception as e:
        log.write_log_error('打开运维智脑失败: ' + str(e))
        import tkinter.messagebox as mb
        try:
            mb.showerror('错误', '运维智脑打开失败：' + str(e))
        except Exception:
            pass


def _on_close():
    global _window_instance
    if _window_instance is not None:
        try:
            _window_instance.destroy()
        except Exception:
            pass
        _window_instance = None
