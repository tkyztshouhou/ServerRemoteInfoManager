# faq/server.py
# FAQ 知识库业务/检索调度层
# 持有 DataAccess，封装多线程异步检索，避免阻塞 Tkinter 主线程。

import threading

from faq.da import FaqDataAccess
from tools.logs import logs


class FAQServer:
    """业务逻辑与检索调度。

    UI 通过本类与数据层交互；检索使用 daemon 线程异步执行，
    结果通过主线程 after() 回调回填，保证 UI 不卡顿。
    """

    def __init__(self, db_path: str):
        self.da = FaqDataAccess(db_path)
        self.log = logs()
        # 创建表（幂等）
        self.da.create_database()

    # ---- 分类 / 条目 业务封装 ----
    def add_category(self, name: str, parent_id: int | None = None) -> int:
        return self.da.add_category(name, parent_id)

    def get_categories(self) -> list[dict]:
        return self.da.get_categories()

    def add_article(self, category_id: int, title: str, content_md: str,
                    content_type: str = 'text') -> int:
        return self.da.add_article(category_id, title, content_md, content_type)

    def get_article(self, article_id: int) -> dict | None:
        return self.da.get_article(article_id)

    def get_articles_by_category(self, category_id: int) -> list[dict]:
        return self.da.get_articles_by_category(category_id)

    def delete_category(self, category_id: int) -> int:
        return self.da.delete_category(category_id)

    def rename_category(self, category_id: int, new_name: str) -> int:
        return self.da.rename_category(category_id, new_name)

    # ---- 条目 业务封装 ----
    def update_article(self, article_id: int, title: str, content_md: str,
                       content_type: str = 'text') -> int:
        return self.da.update_article(article_id, title, content_md, content_type)

    def delete_article(self, article_id: int) -> int:
        return self.da.delete_article(article_id)

    # ---- 多线程检索 ----
    def search_async(self, keyword: str, on_done: callable, on_start: callable = None) -> None:
        """在 daemon 线程执行模糊检索，结束后在主线程回调 on_done(results)。

        :param keyword: 检索关键词
        :param on_done: 主线程回调，签名 on_done(results: list[dict])
        :param on_start: 检索开始前的主线程回调（用于显示"检索中…"）
        """
        if on_start:
            on_start()

        def worker():
            try:
                results = self.da.search_keyword(keyword)
            except Exception as e:
                self.log.write_log_error('FAQ 检索异常: ' + str(e))
                results = []
            # 回到主线程回填 UI
            self._schedule(on_done, results)

        t = threading.Thread(target=worker, daemon=True)
        t.start()

    def _schedule(self, callback: callable, *args):
        """将结果回调调度回主线程（Tkinter 线程安全）。"""
        try:
            import tkinter as tk
            # 通过 Tk 的 after 把回调排入主线程事件循环
            # 这里借助全局 root 引用（由 UI 层注入）若不可用则降级为直接调用
            root = getattr(self, '_root', None)
            if root is not None:
                root.after(0, callback, *args)
            else:
                callback(*args)
        except Exception:
            callback(*args)

    def bind_root(self, root) -> None:
        """注入 Tk 主窗口引用，用于线程安全的 after() 调度。"""
        self._root = root
