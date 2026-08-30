# opsbrain/service.py
# 运维智脑功能实现层
# 负责：模型配置业务（校验、密钥加解密与遮蔽）、会话业务（发消息、组装上下文、落库）、
#       AIClient（requests 流式/非流式调用、SSE 解析、错误分类）。
# 本层不直接访问 UI，仅向上提供可调用的方法与回调式结果回传。

import json
from datetime import datetime

import requests

from tools.secret import encrypt, decrypt, is_encrypted
from opsbrain.token import truncate_context, truncate_single, estimate_tokens
from opsbrain.da import ChatDAO


# ============================ 密钥处理 ============================

def mask_key(value: str) -> str:
    """界面展示用：保留前 4 后 4，中间以 **** 遮蔽；空值返回 '（未设置）'。"""
    if not value:
        return '（未设置）'
    if len(value) <= 8:
        return value[0] + '****' + value[-1]
    return value[:4] + '****' + value[-4:]


def safe_decrypt(api_key: str) -> str:
    """解密落库密钥；非密文（历史明文）原样返回；解密失败返回空串。"""
    if not api_key:
        return ''
    if is_encrypted(api_key):
        return decrypt(api_key)
    return api_key


def safe_encrypt(api_key: str) -> str:
    """加密密钥用于落库；空值存空；已是密文则原样保留（避免二次加密）。"""
    if not api_key:
        return ''
    if is_encrypted(api_key):
        return api_key
    return encrypt(api_key)


# ============================ 模型服务 ============================

class ModelService:
    """模型配置业务层（依赖 ModelDAO）。"""

    def __init__(self, model_dao):
        self.dao = model_dao

    def list_models(self, only_enabled: bool = False) -> list[dict]:
        rows = self.dao.list_models(only_enabled=only_enabled)
        # 不向外泄露密文：将 api_key 转为遮蔽展示
        for r in rows:
            r['api_key_masked'] = mask_key(safe_decrypt(r.get('api_key')))
        return rows

    def get_model(self, model_id: int) -> dict | None:
        r = self.dao.get_model(model_id)
        if r:
            r['api_key_masked'] = mask_key(safe_decrypt(r.get('api_key')))
        return r

    def save_model(self, data: dict, model_id: int | None = None) -> int:
        """新增或更新模型。data 中若含明文 api_key，则加密后落库。
        若 api_key 字段为 None 且为更新操作，则保留原值（不覆盖）。"""
        payload = dict(data)
        if 'api_key' in payload:
            raw = payload['api_key']
            if raw is None and model_id is not None:
                # 编辑时未改动密钥：从原记录取回密文
                old = self.dao.get_model(model_id)
                payload['api_key'] = old['api_key'] if old else ''
            else:
                payload['api_key'] = safe_encrypt(raw)
        if model_id is not None:
            self.dao.update_model(model_id, payload)
            return model_id
        return self.dao.add_model(payload)

    def delete_model(self, model_id: int) -> bool:
        return self.dao.delete_model(model_id)

    def reorder(self, ordered_ids: list[int]) -> bool:
        return self.dao.reorder(ordered_ids)

    @staticmethod
    def validate(data: dict) -> tuple[bool, str]:
        """校验模型配置必填项。返回 (是否通过, 错误信息)。"""
        name = (data.get('name') or '').strip()
        api_url = (data.get('api_url') or '').strip()
        model_name = (data.get('model_name') or '').strip()
        if not name:
            return False, '请填写模型名称（配置显示名）'
        if not api_url:
            return False, '请填写 API 地址'
        if not model_name:
            return False, '请填写模型名称（API model 参数）'
        try:
            t = float(data.get('temperature', 0.7))
            if not (0 <= t <= 2):
                return False, 'temperature 需在 0~2 之间'
        except (TypeError, ValueError):
            return False, 'temperature 必须为数字'
        try:
            mt = int(data.get('max_tokens', 4096))
            if mt <= 0:
                return False, 'max_tokens 必须为正数'
        except (TypeError, ValueError):
            return False, 'max_tokens 必须为整数'
        return True, ''


# ============================ AI 客户端 ============================

class AIClientError(Exception):
    """AI 调用异常，携带分类类型便于 UI 给出可操作提示。"""

    def __init__(self, message: str, kind: str = 'unknown'):
        super().__init__(message)
        self.kind = kind  # 'connection' | 'auth' | 'timeout' | 'parse' | 'http' | 'unknown'


class AIClient:
    """大模型 API 客户端（OpenAI 兼容接口，支持流式与非流式）。"""

    def __init__(self, model: dict, timeout: tuple = (10, 60)):
        self.model = model
        self.timeout = timeout
        self.model_id = model.get('id')
        self.api_url = (model.get('api_url') or '').rstrip('/')
        self.model_name = model.get('model_name') or ''
        self.api_key = safe_decrypt(model.get('api_key'))
        self.temperature = float(model.get('temperature', 0.7))
        self.max_tokens = int(model.get('max_tokens', 4096))
        self.supports_stream = bool(model.get('supports_stream', True))

    def _build_payload(self, messages: list[dict]) -> dict:
        return {
            'model': self.model_name,
            'messages': messages,
            'temperature': self.temperature,
            'max_tokens': self.max_tokens,
            'stream': self.supports_stream,
        }

    def _headers(self) -> dict:
        h = {'Content-Type': 'application/json'}
        if self.api_key:
            h['Authorization'] = 'Bearer ' + self.api_key
        return h

    def _endpoint(self) -> str:
        # 兼容以 /chat/completions 结尾或未结尾两种写法
        if self.api_url.endswith('/chat/completions'):
            return self.api_url
        return self.api_url + '/chat/completions'

    def chat(self, messages: list[dict], on_delta=None, on_thinking=None,
             cancel_event=None) -> dict:
        """发起对话。

        流式：逐块回调 on_delta(text_delta) / on_thinking(thinking_delta)；
        非流式：一次性返回。返回 {'content':..., 'thinking':...}。
        cancel_event 为 threading.Event，置位时中断流式读取。
        """
        payload = self._build_payload(messages)
        try:
            resp = requests.post(
                self._endpoint(), headers=self._headers(),
                data=json.dumps(payload), stream=self.supports_stream,
                timeout=self.timeout,
            )
        except requests.exceptions.Timeout:
            raise AIClientError('请求超时，请检查网络或 API 地址', 'timeout')
        except requests.exceptions.ConnectionError:
            raise AIClientError('连接失败，请检查 API 地址与网络', 'connection')
        except requests.exceptions.RequestException as e:
            raise AIClientError('请求异常：' + str(e), 'connection')

        if resp.status_code == 401:
            raise AIClientError('鉴权失败（401），请检查 API Key', 'auth')
        if resp.status_code != 200:
            body = resp.text[:300]
            raise AIClientError('API 返回错误 %d：%s' % (resp.status_code, body), 'http')

        try:
            if self.supports_stream:
                return self._parse_stream(resp, on_delta, on_thinking, cancel_event)
            return self._parse_once(resp)
        except AIClientError:
            raise
        except Exception as e:
            raise AIClientError('响应解析失败：' + str(e), 'parse')

    @staticmethod
    def _extract_delta(obj: dict) -> tuple[str, str]:
        """从一段 choices[0].delta 中提取内容与思考。返回 (content, reasoning)。"""
        choice = (obj.get('choices') or [{}])[0]
        delta = choice.get('delta') or {}
        content = delta.get('content') or ''
        # 兼容性：部分模型在 delta 中给出 reasoning_content
        reasoning = delta.get('reasoning_content') or delta.get('thinking') or ''
        return content, reasoning

    def _parse_stream(self, resp, on_delta, on_thinking, cancel_event) -> dict:
        content_buf = []
        thinking_buf = []
        for raw in resp.iter_lines(decode_unicode=False):
            if cancel_event is not None and cancel_event.is_set():
                resp.close()
                break
            if not raw:
                continue
            line = raw.decode('utf-8', errors='replace').strip()
            if not line or not line.startswith('data:'):
                continue
            data_str = line[len('data:'):].strip()
            if data_str == '[DONE]':
                break
            try:
                obj = json.loads(data_str)
            except json.JSONDecodeError:
                continue
            content, reasoning = self._extract_delta(obj)
            if reasoning:
                thinking_buf.append(reasoning)
                if on_thinking:
                    on_thinking(reasoning)
            if content:
                content_buf.append(content)
                if on_delta:
                    on_delta(content)
        return {'content': ''.join(content_buf), 'thinking': ''.join(thinking_buf)}

    @staticmethod
    def _parse_once(resp) -> dict:
        obj = resp.json()
        choice = (obj.get('choices') or [{}])[0]
        message = choice.get('message') or {}
        content = message.get('content') or ''
        reasoning = message.get('reasoning_content') or message.get('thinking') or ''
        # 归一化 <think> 标签（非流式也兼容）
        content, tagged_think = _split_think_tag(content)
        if not reasoning and tagged_think:
            reasoning = tagged_think
        return {'content': content, 'thinking': reasoning}


def _split_think_tag(text: str) -> tuple[str, str]:
    """提取 <think>...</think> 内容（支持多段，取首尾拼接）。"""
    if '<think>' not in text:
        return text, ''
    import re
    thinks = re.findall(r'<think>(.*?)</think>', text, flags=re.DOTALL)
    cleaned = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()
    return cleaned, '\n'.join(t.strip() for t in thinks if t.strip())


# ============================ 会话服务 ============================

class ChatService:
    """会话业务层（依赖 ModelService 与 ChatDAO）。"""

    def __init__(self, model_service: ModelService, chat_dao: ChatDAO):
        self.model_svc = model_service
        self.chat_dao = chat_dao

    def new_session(self, model_id: int) -> int:
        model = self.model_svc.get_model(model_id)
        title = '新会话 ' + datetime.now().strftime('%m-%d %H:%M')
        return self.chat_dao.create_session(title, model_id, model['model_name'])

    def list_sessions(self) -> list[dict]:
        return self.chat_dao.list_sessions()

    def load_messages(self, session_id: int) -> list[dict]:
        return self.chat_dao.list_messages(session_id)

    def rename_session(self, session_id: int, title: str) -> bool:
        return self.chat_dao.rename_session(session_id, title.strip() or '未命名会话')

    def delete_session(self, session_id: int) -> bool:
        return self.chat_dao.delete_session(session_id)

    def send(self, session_id: int, model_id: int, user_text: str,
             on_delta=None, on_thinking=None, on_done=None,
             on_error=None, cancel_event=None) -> None:
        """发送一条用户消息并触发 AI 回复（阻塞，由调用方放到后台线程）。

        回调均在调用方线程触发，UI 需自行切换到主线程刷新。
        """
        model = self.model_svc.get_model(model_id)
        if model is None:
            if on_error:
                on_error(AIClientError('模型配置不存在', 'unknown'))
            return

        # 1. 落库用户消息
        self.chat_dao.add_message(session_id, 'user', user_text)

        # 2. 组装上下文并截断
        history = self.chat_dao.list_messages(session_id)
        # history 含刚写入的 user 消息；转换为 API messages
        api_messages = [{'role': m['role'], 'content': m['content']} for m in history]
        api_messages, _truncated = truncate_context(api_messages, model['max_tokens'])

        # 3. 调用模型
        try:
            client = AIClient(model)
            result = client.chat(
                api_messages,
                on_delta=on_delta, on_thinking=on_thinking,
                cancel_event=cancel_event,
            )
        except AIClientError as e:
            if on_error:
                on_error(e)
            return

        # 4. 落库助手回复
        self.chat_dao.add_message(
            session_id, 'assistant', result['content'], result['thinking']
        )
        self.chat_dao.touch_session(session_id)
        if on_done:
            on_done(result)


# 对外暴露的便捷函数：单条文本截断（UI 提交前调用）
def prepare_user_input(text: str, max_tokens: int) -> tuple[str, bool]:
    return truncate_single(text, max_tokens)
