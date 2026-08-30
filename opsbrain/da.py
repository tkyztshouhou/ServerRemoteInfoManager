# opsbrain/da.py
# 运维智脑数据访问层（DataAccess）
# 负责 SQLite 数据库的连接管理与 CRUD，不含业务判断与 UI 逻辑。
# 模型配置操作主库 data.db 的 ai_models 表；会话/消息操作独立库 aichat.db。
# 复用项目统一的 _connect() 上下文管理器与 tools.logs 日志模式。

import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime

from tools.logs import logs


def _now() -> str:
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


class ModelDAO:
    """模型配置数据访问对象（操作主库 ai_models 表）。

    密钥字段 api_key 由上层负责加解密，DA 层只做透明存取。
    """

    def __init__(self, db_path: str):
        self.db = db_path
        self.log = logs()
        db_dir = os.path.dirname(os.path.abspath(self.db))
        if not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)

    @contextmanager
    def _connect(self):
        conn = sqlite3.connect(self.db)
        try:
            yield conn, conn.cursor()
        finally:
            conn.close()

    def ensure_schema(self) -> None:
        try:
            with self._connect() as (conn, cursor):
                cursor.execute('''CREATE TABLE IF NOT EXISTS ai_models (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    name TEXT NOT NULL,
                                    api_url TEXT NOT NULL,
                                    api_key TEXT,
                                    model_name TEXT NOT NULL,
                                    temperature REAL DEFAULT 0.7,
                                    max_tokens INTEGER DEFAULT 4096,
                                    supports_stream INTEGER DEFAULT 1,
                                    description TEXT,
                                    sort_order INTEGER DEFAULT 0,
                                    enabled INTEGER DEFAULT 1,
                                    created_at TEXT,
                                    updated_at TEXT
                                )''')
                conn.commit()
                self.log.write_log_info('运维智脑模型表初始化成功')
        except sqlite3.Error as e:
            self.log.write_log_error('运维智脑模型表初始化失败: ' + str(e))

    # ---- 模型 CRUD ----
    def list_models(self, only_enabled: bool = False) -> list[dict]:
        try:
            with self._connect() as (conn, cursor):
                sql = ('SELECT id, name, api_url, api_key, model_name, temperature, '
                       'max_tokens, supports_stream, description, sort_order, enabled '
                       'FROM ai_models')
                if only_enabled:
                    sql += ' WHERE enabled = 1'
                sql += ' ORDER BY sort_order ASC, id ASC'
                cursor.execute(sql)
                return [self._row_to_model(r) for r in cursor.fetchall()]
        except sqlite3.Error as e:
            self.log.write_log_error('读取模型列表失败: ' + str(e))
            return []

    def get_model(self, model_id: int) -> dict | None:
        try:
            with self._connect() as (conn, cursor):
                cursor.execute(
                    'SELECT id, name, api_url, api_key, model_name, temperature, '
                    'max_tokens, supports_stream, description, sort_order, enabled '
                    'FROM ai_models WHERE id = ?',
                    (model_id,),
                )
                r = cursor.fetchone()
                return self._row_to_model(r) if r else None
        except sqlite3.Error as e:
            self.log.write_log_error('读取模型失败: ' + str(e))
            return None

    def add_model(self, data: dict) -> int:
        now = _now()
        with self._connect() as (conn, cursor):
            cursor.execute(
                '''INSERT INTO ai_models
                   (name, api_url, api_key, model_name, temperature, max_tokens,
                    supports_stream, description, sort_order, enabled, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (
                    data.get('name', ''),
                    data.get('api_url', ''),
                    data.get('api_key'),
                    data.get('model_name', ''),
                    float(data.get('temperature', 0.7)),
                    int(data.get('max_tokens', 4096)),
                    1 if data.get('supports_stream', True) else 0,
                    data.get('description', ''),
                    int(data.get('sort_order', 0)),
                    1 if data.get('enabled', True) else 0,
                    now, now,
                ),
            )
            conn.commit()
            return cursor.lastrowid

    def update_model(self, model_id: int, data: dict) -> bool:
        now = _now()
        with self._connect() as (conn, cursor):
            cursor.execute(
                '''UPDATE ai_models
                   SET name = ?, api_url = ?, api_key = ?, model_name = ?, temperature = ?,
                       max_tokens = ?, supports_stream = ?, description = ?,
                       sort_order = ?, enabled = ?, updated_at = ?
                   WHERE id = ?''',
                (
                    data.get('name', ''),
                    data.get('api_url', ''),
                    data.get('api_key'),
                    data.get('model_name', ''),
                    float(data.get('temperature', 0.7)),
                    int(data.get('max_tokens', 4096)),
                    1 if data.get('supports_stream', True) else 0,
                    data.get('description', ''),
                    int(data.get('sort_order', 0)),
                    1 if data.get('enabled', True) else 0,
                    now, model_id,
                ),
            )
            conn.commit()
            return cursor.rowcount > 0

    def delete_model(self, model_id: int) -> bool:
        with self._connect() as (conn, cursor):
            cursor.execute('DELETE FROM ai_models WHERE id = ?', (model_id,))
            conn.commit()
            return cursor.rowcount > 0

    def reorder(self, ordered_ids: list[int]) -> bool:
        """按传入的顺序重置 sort_order（0,1,2,...）。"""
        with self._connect() as (conn, cursor):
            for idx, mid in enumerate(ordered_ids):
                cursor.execute(
                    'UPDATE ai_models SET sort_order = ? WHERE id = ?',
                    (idx, mid),
                )
            conn.commit()
            return True

    @staticmethod
    def _row_to_model(r) -> dict:
        return {
            'id': r[0], 'name': r[1], 'api_url': r[2], 'api_key': r[3],
            'model_name': r[4], 'temperature': r[5], 'max_tokens': r[6],
            'supports_stream': bool(r[7]), 'description': r[8],
            'sort_order': r[9], 'enabled': bool(r[10]),
        }


class ChatDAO:
    """会话与消息数据访问对象（操作独立库 aichat.db）。"""

    def __init__(self, chat_db_path: str):
        self.db = chat_db_path
        self.log = logs()
        db_dir = os.path.dirname(os.path.abspath(self.db))
        if not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)

    @contextmanager
    def _connect(self):
        conn = sqlite3.connect(self.db)
        try:
            yield conn, conn.cursor()
        finally:
            conn.close()

    def ensure_schema(self) -> None:
        try:
            with self._connect() as (conn, cursor):
                cursor.execute('''CREATE TABLE IF NOT EXISTS chat_sessions (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    title TEXT NOT NULL,
                                    model_id INTEGER,
                                    model_name TEXT,
                                    created_at TEXT,
                                    updated_at TEXT
                                )''')
                cursor.execute('''CREATE TABLE IF NOT EXISTS chat_messages (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    session_id INTEGER NOT NULL,
                                    role TEXT NOT NULL,
                                    content TEXT,
                                    thinking TEXT,
                                    created_at TEXT
                                )''')
                conn.commit()
                self.log.write_log_info('运维智脑聊天库初始化成功')
        except sqlite3.Error as e:
            self.log.write_log_error('运维智脑聊天库初始化失败: ' + str(e))

    # ---- 会话 CRUD ----
    def create_session(self, title: str, model_id: int, model_name: str) -> int:
        now = _now()
        with self._connect() as (conn, cursor):
            cursor.execute(
                '''INSERT INTO chat_sessions (title, model_id, model_name, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?)''',
                (title, model_id, model_name, now, now),
            )
            conn.commit()
            return cursor.lastrowid

    def list_sessions(self) -> list[dict]:
        try:
            with self._connect() as (conn, cursor):
                cursor.execute(
                    'SELECT id, title, model_id, model_name, created_at, updated_at '
                    'FROM chat_sessions ORDER BY updated_at DESC, id DESC'
                )
                return [
                    {
                        'id': r[0], 'title': r[1], 'model_id': r[2],
                        'model_name': r[3], 'created_at': r[4], 'updated_at': r[5],
                    }
                    for r in cursor.fetchall()
                ]
        except sqlite3.Error as e:
            self.log.write_log_error('读取会话列表失败: ' + str(e))
            return []

    def get_session(self, session_id: int) -> dict | None:
        try:
            with self._connect() as (conn, cursor):
                cursor.execute(
                    'SELECT id, title, model_id, model_name, created_at, updated_at '
                    'FROM chat_sessions WHERE id = ?',
                    (session_id,),
                )
                r = cursor.fetchone()
                return {
                    'id': r[0], 'title': r[1], 'model_id': r[2],
                    'model_name': r[3], 'created_at': r[4], 'updated_at': r[5],
                } if r else None
        except sqlite3.Error as e:
            self.log.write_log_error('读取会话失败: ' + str(e))
            return None

    def rename_session(self, session_id: int, title: str) -> bool:
        now = _now()
        with self._connect() as (conn, cursor):
            cursor.execute(
                'UPDATE chat_sessions SET title = ?, updated_at = ? WHERE id = ?',
                (title, now, session_id),
            )
            conn.commit()
            return cursor.rowcount > 0

    def touch_session(self, session_id: int) -> None:
        now = _now()
        with self._connect() as (conn, cursor):
            cursor.execute(
                'UPDATE chat_sessions SET updated_at = ? WHERE id = ?',
                (now, session_id),
            )
            conn.commit()

    def delete_session(self, session_id: int) -> bool:
        """删除会话并级联删除其全部消息（同一事务）。"""
        with self._connect() as (conn, cursor):
            cursor.execute('DELETE FROM chat_messages WHERE session_id = ?', (session_id,))
            cursor.execute('DELETE FROM chat_sessions WHERE id = ?', (session_id,))
            conn.commit()
            return True

    # ---- 消息 CRUD ----
    def add_message(self, session_id: int, role: str, content: str,
                    thinking: str = '') -> int:
        now = _now()
        with self._connect() as (conn, cursor):
            cursor.execute(
                '''INSERT INTO chat_messages (session_id, role, content, thinking, created_at)
                   VALUES (?, ?, ?, ?, ?)''',
                (session_id, role, content, thinking, now),
            )
            conn.commit()
            return cursor.lastrowid

    def list_messages(self, session_id: int) -> list[dict]:
        try:
            with self._connect() as (conn, cursor):
                cursor.execute(
                    'SELECT id, role, content, thinking, created_at '
                    'FROM chat_messages WHERE session_id = ? ORDER BY id ASC',
                    (session_id,),
                )
                return [
                    {
                        'id': r[0], 'role': r[1], 'content': r[2] or '',
                        'thinking': r[3] or '', 'created_at': r[4],
                    }
                    for r in cursor.fetchall()
                ]
        except sqlite3.Error as e:
            self.log.write_log_error('读取消息失败: ' + str(e))
            return []
