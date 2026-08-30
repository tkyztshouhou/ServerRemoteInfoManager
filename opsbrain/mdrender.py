# opsbrain/mdrender.py
# 轻量 Markdown 渲染器：将 Markdown 文本渲染到 tk.Text。
# 支持：标题、引用、有序/无序列表、代码块（带复制/另存按钮）、行内代码、
#       粗体、斜体、分隔线、普通段落。
# 思考内容的折叠由调用方以独立控件呈现，本模块只负责正文渲染。

import re
import tkinter as tk


CODE_OPEN_RE = re.compile(r'^```(\w+)?\s*$')


class MarkdownRenderer:
    """将 Markdown 文本渲染到给定的 tk.Text 组件。"""

    def __init__(self, text_widget: tk.Text, on_copy_code=None, on_save_code=None):
        self.text = text_widget
        self.on_copy_code = on_copy_code
        self.on_save_code = on_save_code

    # ---------------- 公共接口 ----------------
    def render(self, md_text: str):
        """清空并一次性渲染整段 markdown。"""
        self.text.configure(state=tk.NORMAL)
        self.text.delete('1.0', tk.END)
        self._render_body(md_text or '')
        self.text.configure(state=tk.DISABLED)

    def append(self, md_text: str):
        """增量追加（用于流式渲染尾部的增量片段）。"""
        self.text.configure(state=tk.NORMAL)
        self._render_body(md_text, at_end=True)
        self.text.configure(state=tk.DISABLED)

    # ---------------- 解析 ----------------
    def _render_body(self, md_text: str, at_end: bool = False):
        lines = md_text.split('\n')
        i, n = 0, len(lines)
        first_block = True
        while i < n:
            line = lines[i]
            stripped = line.strip()

            # 代码块
            m = CODE_OPEN_RE.match(stripped)
            if m and stripped.startswith('```'):
                lang = m.group(1) or ''
                code_lines = []
                i += 1
                while i < n and not lines[i].strip().startswith('```'):
                    code_lines.append(lines[i])
                    i += 1
                i += 1  # 跳过结束 ```
                self._insert_code_block('\n'.join(code_lines), lang)
                first_block = False
                continue

            # 标题
            if re.match(r'^#{1,6}\s', stripped):
                level = len(stripped.split(' ', 1)[0])
                content = stripped.split(' ', 1)[1]
                self.text.insert(tk.END, '', 'h%d' % min(level, 4))
                self._inline(content)
                self.text.insert(tk.END, '\n', 'h%d' % min(level, 4))
                first_block = False
                i += 1
                continue

            # 分隔线
            if re.match(r'^(\*\*\*|---|___)\s*$', stripped):
                self.text.insert(tk.END, '─' * 30 + '\n', 'hr')
                first_block = False
                i += 1
                continue

            # 引用
            if stripped.startswith('>'):
                quote_buf = []
                while i < n and lines[i].strip().startswith('>'):
                    quote_buf.append(lines[i].strip().lstrip('>').strip())
                    i += 1
                self.text.insert(tk.END, '', 'quote')
                self._inline(' '.join(quote_buf))
                self.text.insert(tk.END, '\n', 'quote')
                first_block = False
                continue

            # 列表
            if re.match(r'^(\s*[-*+]\s)', stripped) or re.match(r'^\s*\d+\.\s', stripped):
                list_buf = []
                ordered = re.match(r'^\s*\d+\.\s', stripped) is not None
                while i < n and (re.match(r'^(\s*[-*+]\s)', lines[i].strip())
                                 or re.match(r'^\s*\d+\.\s', lines[i].strip())):
                    item = re.sub(r'^(\s*[-*+]\s|\s*\d+\.\s)', '', lines[i].strip())
                    list_buf.append((ordered, item))
                    i += 1
                for idx, (o, item) in enumerate(list_buf):
                    bullet = ('%d. ' % (idx + 1)) if o else '• '
                    self.text.insert(tk.END, '    ' + bullet, 'li')
                    self._inline(item)
                    self.text.insert(tk.END, '\n', 'li')
                self.text.insert(tk.END, '\n')
                first_block = False
                continue

            # 空行
            if stripped == '':
                if not first_block:
                    self.text.insert(tk.END, '\n')
                first_block = True
                i += 1
                continue

            # 普通段落（聚合连续普通行）
            para = [stripped]
            i += 1
            while i < n and lines[i].strip() != '' \
                    and not lines[i].strip().startswith('#') \
                    and not lines[i].strip().startswith('>') \
                    and not lines[i].strip().startswith('```') \
                    and not re.match(r'^(\s*[-*+]\s|\s*\d+\.\s)', lines[i].strip()) \
                    and not re.match(r'^(\*\*\*|---|___)\s*$', lines[i].strip()):
                para.append(lines[i].strip())
                i += 1
            self._inline(' '.join(para))
            self.text.insert(tk.END, '\n\n', 'p')
            first_block = False

    # ---------------- 代码块（带工具栏） ----------------
    def _insert_code_block(self, code: str, lang: str):
        self.text.insert(tk.END, '\n')
        start = self.text.index(tk.END)
        self.text.insert(tk.END, code + '\n')
        end = self.text.index(tk.END)
        self.text.tag_add('codeblock', start, end)

        bar = tk.Frame(self.text, bg='#EEF1F4', relief='flat')
        tk.Label(bar, text=(lang or 'code'), bg='#EEF1F4', fg='#888',
                 font=('Microsoft YaHei', 8)).pack(side=tk.LEFT, padx=4)
        tk.Button(bar, text='复制', width=5, relief='flat', bg='#E0E5EA',
                  font=('Microsoft YaHei', 8),
                  command=lambda c=code: self._do_copy(c)).pack(side=tk.RIGHT, padx=2)
        tk.Button(bar, text='另存为', width=6, relief='flat', bg='#E0E5EA',
                  font=('Microsoft YaHei', 8),
                  command=lambda c=code, l=lang: self._do_save(c, l)).pack(side=tk.RIGHT, padx=2)
        self.text.window_create(tk.END, window=bar)
        self.text.insert(tk.END, '\n\n')

    # ---------------- 行内语法 ----------------
    def _inline(self, text: str):
        """解析行内语法（行内码、粗体、斜体）并直接以带 tag 的方式插入到 tk.Text。

        使用非贪婪正则切分文本为「纯文本段」与「特殊段」，分别插入并打 tag。
        """
        pattern = re.compile(r'(`[^`]+`|\*\*[^*]+\*\*|(?<!\*)\*[^*]+\*(?!\*))')
        pos = 0
        for m in pattern.finditer(text):
            if m.start() > pos:
                self.text.insert(tk.END, text[pos:m.start()], 'p')
            tok = m.group(0)
            if tok.startswith('`') and tok.endswith('`'):
                self.text.insert(tk.END, tok[1:-1], 'inlinecode')
            elif tok.startswith('**'):
                self.text.insert(tk.END, tok[2:-2], 'bold')
            else:  # *italic*
                self.text.insert(tk.END, tok[1:-1], 'italic')
            pos = m.end()
        if pos < len(text):
            self.text.insert(tk.END, text[pos:], 'p')

    def _do_copy(self, code: str):
        if self.on_copy_code:
            self.on_copy_code(code)

    def _do_save(self, code: str, lang: str):
        if self.on_save_code:
            self.on_save_code(code, lang)
