# faq/da.py
# FAQ 知识库数据访问层（DataAccess）
# 负责 SQLite 数据库的连接管理与 CRUD、模糊检索，并预留 RAG（embedding / 向量检索）扩展接口。

import os
import sqlite3
from contextlib import contextmanager

from tools.logs import logs


class FaqDataAccess:
    """FAQ 知识库数据访问对象。

    数据库文件为独立的 faq.db，与业务库 data.db 隔离。
    复用项目统一的 _connect() 上下文管理器与 logs 日志模式。
    """

    def __init__(self, db_path: str):
        self.db = db_path
        self.log = logs()
        # 确保数据库所在目录存在（打包后位于 %LOCALAPPDATA%）
        db_dir = os.path.dirname(os.path.abspath(self.db))
        if not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)

    # ---- 连接管理（沿用 gui_DA 的 _connect 模式）----
    @contextmanager
    def _connect(self):
        conn = sqlite3.connect(self.db)
        try:
            yield conn, conn.cursor()
        finally:
            conn.close()

    # ---- 建表 ----
    def create_database(self) -> None:
        try:
            with self._connect() as (conn, cursor):
                cursor.execute('''CREATE TABLE IF NOT EXISTS categories (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    name TEXT NOT NULL,
                                    parent_id INTEGER
                                )''')
                cursor.execute('''CREATE TABLE IF NOT EXISTS articles (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    category_id INTEGER,
                                    title TEXT NOT NULL,
                                    content_md TEXT,
                                    content_type TEXT DEFAULT 'text',
                                    created_at TEXT,
                                    updated_at TEXT,
                                    embedding BLOB
                                )''')
                conn.commit()
                self.log.write_log_info('FAQ 数据库初始化成功')
        except sqlite3.Error as e:
            self.log.write_log_error('FAQ 数据库初始化失败: ' + str(e))

    # ---- 分类 CRUD ----
    def add_category(self, name: str, parent_id: int | None = None) -> int:
        with self._connect() as (conn, cursor):
            cursor.execute(
                'INSERT INTO categories (name, parent_id) VALUES (?, ?)',
                (name, parent_id),
            )
            conn.commit()
            return cursor.lastrowid

    def get_categories(self) -> list[dict]:
        try:
            with self._connect() as (conn, cursor):
                cursor.execute('SELECT id, name, parent_id FROM categories ORDER BY id')
                rows = cursor.fetchall()
                return [
                    {'id': r[0], 'name': r[1], 'parent_id': r[2]}
                    for r in rows
                ]
        except sqlite3.Error as e:
            self.log.write_log_error('读取分类失败: ' + str(e))
            return []

    def get_category_id_by_name(self, name: str) -> int | None:
        with self._connect() as (conn, cursor):
            cursor.execute('SELECT id FROM categories WHERE name = ?', (name,))
            row = cursor.fetchone()
            return row[0] if row else None

    def delete_category(self, category_id: int) -> int:
        """删除分类及其下所有条目（级联简单实现）。"""
        with self._connect() as (conn, cursor):
            cursor.execute('DELETE FROM articles WHERE category_id = ?', (category_id,))
            cursor.execute('DELETE FROM categories WHERE id = ?', (category_id,))
            conn.commit()
            return cursor.rowcount

    def rename_category(self, category_id: int, new_name: str) -> int:
        """重命名分类。"""
        with self._connect() as (conn, cursor):
            cursor.execute(
                'UPDATE categories SET name = ? WHERE id = ?',
                (new_name, category_id),
            )
            conn.commit()
            return cursor.rowcount

    # ---- 条目 CRUD ----
    def add_article(self, category_id: int, title: str, content_md: str,
                    content_type: str = 'text') -> int:
        from datetime import datetime
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with self._connect() as (conn, cursor):
            cursor.execute(
                '''INSERT INTO articles (category_id, title, content_md, content_type, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?)''',
                (category_id, title, content_md, content_type, now, now),
            )
            conn.commit()
            return cursor.lastrowid

    def get_article(self, article_id: int) -> dict | None:
        try:
            with self._connect() as (conn, cursor):
                cursor.execute(
                    'SELECT id, category_id, title, content_md, content_type FROM articles WHERE id = ?',
                    (article_id,),
                )
                r = cursor.fetchone()
                if not r:
                    return None
                return {
                    'id': r[0], 'category_id': r[1], 'title': r[2],
                    'content_md': r[3], 'content_type': r[4],
                }
        except sqlite3.Error as e:
            self.log.write_log_error('读取条目失败: ' + str(e))
            return None

    def update_article(self, article_id: int, title: str, content_md: str,
                       content_type: str = 'text') -> int:
        """更新条目（标题、内容、类型），同步 updated_at。"""
        from datetime import datetime
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with self._connect() as (conn, cursor):
            cursor.execute(
                '''UPDATE articles
                   SET title = ?, content_md = ?, content_type = ?, updated_at = ?
                   WHERE id = ?''',
                (title, content_md, content_type, now, article_id),
            )
            conn.commit()
            return cursor.rowcount

    def delete_article(self, article_id: int) -> int:
        """删除单条条目。"""
        with self._connect() as (conn, cursor):
            cursor.execute('DELETE FROM articles WHERE id = ?', (article_id,))
            conn.commit()
            return cursor.rowcount

    def get_articles_by_category(self, category_id: int) -> list[dict]:
        try:
            with self._connect() as (conn, cursor):
                cursor.execute(
                    'SELECT id, title, content_type FROM articles WHERE category_id = ? ORDER BY id',
                    (category_id,),
                )
                return [
                    {'id': r[0], 'title': r[1], 'content_type': r[2]}
                    for r in cursor.fetchall()
                ]
        except sqlite3.Error as e:
            self.log.write_log_error('读取分类条目失败: ' + str(e))
            return []

    # ---- 检索 ----
    def search_keyword(self, keyword: str, limit: int = 50) -> list[dict]:
        """关键词模糊检索（标题 + 正文 LIKE）。"""
        if not keyword:
            return []
        like = '%' + keyword + '%'
        try:
            with self._connect() as (conn, cursor):
                cursor.execute(
                    '''SELECT a.id, a.title, a.content_md, a.content_type, c.name
                       FROM articles a
                       LEFT JOIN categories c ON a.category_id = c.id
                       WHERE a.title LIKE ? OR a.content_md LIKE ?
                       ORDER BY a.id LIMIT ?''',
                    (like, like, limit),
                )
                results = []
                for r in cursor.fetchall():
                    content = r[2] or ''
                    # 生成简短摘要（去除换行，截取前 60 字）
                    summary = content.replace('\n', ' ').strip()
                    summary = summary[:60] + ('…' if len(summary) > 60 else '')
                    results.append({
                        'id': r[0], 'title': r[1], 'content': content,
                        'content_type': r[3], 'category': r[4] or '未分类',
                        'summary': summary,
                    })
                return results
        except sqlite3.Error as e:
            self.log.write_log_error('FAQ 检索失败: ' + str(e))
            return []

    # ---- RAG 扩展接口（预留）----
    def embedding(self, text: str) -> list[float]:
        """后期接入大模型生成文本向量；当前未实现。

        接入示例（伪代码）：
            import openai
            resp = openai.Embedding.create(input=text, model='text-embedding-3-small')
            return resp['data'][0]['embedding']
        """
        raise NotImplementedError('embedding 待接入大模型（RAG 扩展）')

    def vector_search(self, vec: list[float], top_k: int = 5) -> list[dict]:
        """基于向量相似度检索；当前未实现。

        接入示例（伪代码）：取出 articles.embedding（BLOB 反序列化为向量），
        计算余弦相似度，返回 top_k 条最相似结果。
        """
        raise NotImplementedError('vector_search 待实现（RAG 扩展）')
