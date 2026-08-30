# opsbrain/token.py
# 上下文长度控制模块（零新增依赖，字符加权估算）。
#
# 策略：
#   - CJK（中日韩统一表意文字）按 1.5 字符/token 估算；其余字符按 4 字符/token 估算。
#   - 输入预算 = max_tokens * (1 - reserve_ratio)，reserve_ratio 预留给模型输出。
#   - 上下文超出预算时优先丢弃最早的历史轮次；单条仍超出则尾部硬截断。

import re

_CJK_RE = re.compile(r'[\u4e00-\u9fff\u3000-\u303f\uff00-\uffef]')


def estimate_tokens(text: str) -> int:
    """估算文本 token 数（整数，向上取整）。"""
    if not text:
        return 0
    cjk = len(_CJK_RE.findall(text))
    other = len(text) - cjk
    # CJK 约 1.5 字符/token，其他约 4 字符/token
    return int((cjk / 1.5) + (other / 4) + 0.999)


def estimate_messages_tokens(messages: list[dict]) -> int:
    """估算一组消息的总 token（含 role 标识的少量开销）。"""
    total = 0
    for msg in messages:
        total += estimate_tokens(msg.get('content', '') or '')
        if msg.get('thinking'):
            total += estimate_tokens(msg['thinking'])
        total += 4  # role / 结构开销
    return total


def input_budget(max_tokens: int, reserve_ratio: float = 0.25) -> int:
    """计算允许留给输入的最大 token 数。"""
    if max_tokens <= 0:
        return 4096
    return int(max_tokens * (1 - reserve_ratio))


def truncate_context(messages: list[dict], max_tokens: int) -> tuple[list[dict], bool]:
    """按 token 预算裁剪历史消息。

    优先保留末尾（最新）的消息，丢弃最早的轮次；若最新单条仍超预算则尾部硬截断。
    返回 (裁剪后消息列表, 是否发生过截断)。
    """
    budget = input_budget(max_tokens)
    truncated = False

    # 从末尾向前累加，超出预算则丢弃头部
    kept: list[dict] = []
    used = 0
    for msg in reversed(messages):
        cost = estimate_tokens(msg.get('content', '') or '') + \
               (estimate_tokens(msg['thinking']) if msg.get('thinking') else 0) + 4
        if used + cost > budget and kept:
            truncated = True
            break
        kept.insert(0, msg)
        used += cost

    # 若最新单条仍超出，对其做尾部截断
    if kept:
        last = kept[-1]
        last_cost = estimate_tokens(last.get('content', '') or '')
        if last_cost > budget:
            kept[-1] = dict(last)
            kept[-1]['content'] = _tail_truncate(last.get('content', ''), budget)
            truncated = True

    return kept, truncated


def _tail_truncate(text: str, budget_tokens: int) -> str:
    """按预算对单条文本做尾部硬截断（保留开头）。"""
    limit = max(int(budget_tokens * 4 * 0.9), 100)
    if len(text) <= limit:
        return text
    return text[:limit] + '\n\n[内容过长已自动截断]'


def truncate_single(text: str, max_tokens: int, reserve_ratio: float = 0.25) -> tuple[str, bool]:
    """对单条用户输入按预算做尾部截断，返回 (文本, 是否截断)。"""
    budget = input_budget(max_tokens, reserve_ratio)
    limit = max(int(budget * 4 * 0.9), 100)
    if len(text) <= limit:
        return text, False
    return text[:limit] + '\n\n[输入过长已自动截取]', True
