# opsbrain/ui.py
# 运维智脑聊天窗口 UI 层（tkinter）
# 会话列表 + 消息滚动区 + 输入区 + 模型单选框（动态生成）；
# 调用 service 层完成发消息、流式渲染、停止生成；不直接访问数据库。

import threading
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog

from opsbrain.mdrender import MarkdownRenderer
from opsbrain.service import prepare_user_input, AIClientError

PRIMARY = '#9C27B0'
PRIMARY_LIGHT = '#E1BEE7'
USER_BUBBLE = '#E3F2FD'
ASSIST_BUBBLE = '#FFFFFF'
BG = '#F5F6F8'
CODE_BG = '#F0F2F5'


class OpsBrainWindow(tk.Toplevel):
    def __init__(self, master, model_svc, chat_svc):
        super().__init__(master)
        self.model_svc = model_svc
        self.chat_svc = chat_svc
        self.title('运维智脑')
        self.geometry('1100x760')
        self.configure(bg=BG)
        self._center()

        self.current_session_id = None
        self.cancel_event = None          # 流式取消标志
        self.generating = False
        self._auto_scroll = True

        self._build_layout()
        self._load_sessions()
        self._refresh_models()

        # 默认新建一个会话
        if not self.sessions:
            self._new_session()

    # ---------------- 布局 ----------------
    def _center(self):
        self.update_idletasks()
        w, h = 1100, 760
        x = (self.winfo_screenwidth() - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry('%dx%d+%d+%d' % (w, h, x, y))

    def _build_layout(self):
        # 左侧会话栏
        left = tk.Frame(self, width=240, bg='#FFFFFF', relief='solid', bd=1)
        left.pack(side=tk.LEFT, fill=tk.Y)
        left.pack_propagate(False)

        tk.Button(left, text='+ 新建会话', bg=PRIMARY, fg='white',
                  font=('Microsoft YaHei', 11, 'bold'), relief='flat',
                  command=self._new_session).pack(fill=tk.X, padx=12, pady=12)

        self.session_list = tk.Listbox(left, bg='#FFFFFF', relief='flat',
                                       font=('Microsoft YaHei', 10),
                                       activestyle='none',
                                       selectbackground=PRIMARY_LIGHT,
                                       selectforeground='#4A148C')
        self.session_list.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))
        self.session_list.bind('<Double-Button-1>', lambda e: self._switch_session())
        self.session_list.bind('<Button-3>', self._on_session_right_click)

        # 右侧主区
        right = tk.Frame(self, bg=BG)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 顶部标题栏
        top = tk.Frame(right, bg='#FFFFFF', relief='solid', bd=0, height=46)
        top.pack(fill=tk.X)
        top.pack_propagate(False)
        self.title_label = tk.Label(top, text='运维智脑', bg='#FFFFFF',
                                    font=('Microsoft YaHei', 13, 'bold'), fg=PRIMARY)
        self.title_label.pack(side=tk.LEFT, padx=16)
        self.model_tag = tk.Label(top, text='', bg='#FFFFFF', fg='#888',
                                  font=('Microsoft YaHei', 10))
        self.model_tag.pack(side=tk.LEFT, padx=8)
        tk.Button(top, text='重命名', bg='#F0F0F0', relief='flat',
                  font=('Microsoft YaHei', 9),
                  command=self._rename_session).pack(side=tk.RIGHT, padx=8)

        # 消息滚动区（Canvas + 内部 Frame）
        self.msg_canvas = tk.Canvas(right, bg=BG, highlightthickness=0)
        self.msg_canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=6)
        self.msg_inner = tk.Frame(self.msg_canvas, bg=BG)
        self.msg_canvas.create_window((0, 0), window=self.msg_inner, anchor='nw')
        self.msg_canvas.bind('<Configure>', self._on_canvas_configure)
        self.msg_inner.bind('<Configure>', self._on_inner_configure)
        self.msg_canvas.bind('<MouseWheel>', self._on_mousewheel)

        # 底部输入区
        bottom = tk.Frame(right, bg='#FFFFFF')
        bottom.pack(fill=tk.X, side=tk.BOTTOM)

        self.input_box = tk.Text(bottom, height=5, bg='#FFFFFF', relief='solid', bd=1,
                                 font=('Microsoft YaHei', 10), wrap='word',
                                 padx=8, pady=6)
        self.input_box.pack(fill=tk.X, padx=12, pady=(10, 4))
        self.input_box.bind('<Control-Return>', lambda e: self._send())
        self.input_box.bind('<Shift-Return>', lambda e: None)  # 允许换行

        # 模型单选框区（动态）
        self.model_frame = tk.Frame(bottom, bg='#FFFFFF')
        self.model_frame.pack(fill=tk.X, padx=12)
        self.model_var = tk.StringVar()

        # 发送/停止按钮
        btn_row = tk.Frame(bottom, bg='#FFFFFF')
        btn_row.pack(fill=tk.X, padx=12, pady=(4, 10))
        self.send_btn = tk.Button(btn_row, text='发送 (Ctrl+Enter)', bg=PRIMARY, fg='white',
                                  font=('Microsoft YaHei', 10, 'bold'), relief='flat',
                                  width=18, command=self._send)
        self.send_btn.pack(side=tk.RIGHT, padx=4)
        self.stop_btn = tk.Button(btn_row, text='停止', bg='#BDBDBD', fg='white',
                                  font=('Microsoft YaHei', 10), relief='flat',
                                  width=10, state=tk.DISABLED, command=self._stop)
        self.stop_btn.pack(side=tk.RIGHT, padx=4)
        self.hint_label = tk.Label(btn_row, text='', bg='#FFFFFF', fg='#F44336',
                                   font=('Microsoft YaHei', 9))
        self.hint_label.pack(side=tk.LEFT)

    # ---------------- 会话列表 ----------------
    def _load_sessions(self):
        self.sessions = self.chat_svc.list_sessions()
        self.session_list.delete(0, tk.END)
        for s in self.sessions:
            self.session_list.insert(tk.END, '%s  ·  %s' % (s['title'], s['updated_at'][5:16]))
        if self.sessions:
            self.session_list.selection_set(0)
            self._switch_session()

    def _new_session(self):
        models = self.model_svc.list_models(only_enabled=True)
        if not models:
            messagebox.showwarning('提示', '请先在「系统设置-连接参数」中配置 AI 模型')
            return
        mid = models[0]['id']
        sid = self.chat_svc.new_session(mid)
        self._load_sessions()
        # 选中新建的会话
        for idx, s in enumerate(self.sessions):
            if s['id'] == sid:
                self.session_list.selection_set(idx)
                self.session_list.see(idx)
                break
        self._switch_session()

    def _switch_session(self):
        sel = self.session_list.curselection()
        if not sel:
            return
        idx = sel[0]
        if idx >= len(self.sessions):
            return
        self.current_session_id = self.sessions[idx]['id']
        s = self.sessions[idx]
        self.title_label.config(text=s['title'])
        self._render_history()

    def _rename_session(self):
        if self.current_session_id is None:
            return
        cur = next((s for s in self.sessions if s['id'] == self.current_session_id), None)
        if not cur:
            return
        new = simpledialog.askstring('重命名会话', '会话标题：', initialvalue=cur['title'])
        if new and new.strip():
            self.chat_svc.rename_session(self.current_session_id, new.strip())
            self._load_sessions()

    def _on_session_right_click(self, event):
        idx = self.session_list.nearest(event.y)
        if idx < 0 or idx >= len(self.sessions):
            return
        self.session_list.selection_clear(0, tk.END)
        self.session_list.selection_set(idx)
        self.session_list.see(idx)
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label='重命名', command=self._rename_session)
        menu.add_command(label='删除', command=self._delete_session)
        menu.tk_popup(event.x_root, event.y_root)

    def _delete_session(self):
        if self.current_session_id is None:
            return
        if not messagebox.askyesno('确认', '确定删除该会话及其全部消息？'):
            return
        self.chat_svc.delete_session(self.current_session_id)
        self.current_session_id = None
        self._load_sessions()
        self._clear_messages()

    # ---------------- 消息渲染 ----------------
    def _clear_messages(self):
        for w in self.msg_inner.winfo_children():
            w.destroy()

    def _render_history(self):
        self._clear_messages()
        if self.current_session_id is None:
            return
        msgs = self.chat_svc.load_messages(self.current_session_id)
        for m in msgs:
            if m['role'] == 'user':
                self._add_user_bubble(m['content'])
            else:
                self._add_assistant_bubble(m['content'], m['thinking'])

    def _add_user_bubble(self, text):
        row = tk.Frame(self.msg_inner, bg=BG)
        row.pack(fill=tk.X, pady=6, padx=8)
        spacer = tk.Frame(row, width=120, bg=BG)
        spacer.pack(side=tk.LEFT, expand=True)
        bubble = tk.Frame(row, bg=USER_BUBBLE, relief='solid', bd=1)
        bubble.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=4)
        lbl = tk.Label(bubble, text=text, bg=USER_BUBBLE, justify='left',
                       font=('Microsoft YaHei', 10), wraplength=560, padx=10, pady=8)
        lbl.pack(anchor='e')
        self._scroll_to_bottom()

    def _add_assistant_bubble(self, content, thinking='', stream=False):
        row = tk.Frame(self.msg_inner, bg=BG)
        row.pack(fill=tk.X, pady=6, padx=8)
        bubble = tk.Frame(row, bg=ASSIST_BUBBLE, relief='solid', bd=1)
        bubble.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)

        # 思考折叠区
        if thinking:
            self._add_thinking(bubble, thinking)

        text = tk.Text(bubble, bg=ASSIST_BUBBLE, relief='flat', height=2,
                       font=('Microsoft YaHei', 10), wrap='word',
                       padx=10, pady=8, state=tk.DISABLED)
        text.pack(fill=tk.X, expand=True)
        self._configure_tags(text)
        renderer = MarkdownRenderer(text, on_copy_code=self._copy_code,
                                    on_save_code=self._save_code)
        renderer.render(content)
        self._fit_text_height(text)
        # 复制全文按钮
        tk.Button(bubble, text='复制全文', bg='#F0F0F0', relief='flat',
                  font=('Microsoft YaHei', 8),
                  command=lambda c=content: self._copy_code(c)).pack(anchor='e', padx=8, pady=(0, 6))
        self._scroll_to_bottom()
        return renderer

    def _add_thinking(self, parent, thinking_text):
        frame = tk.Frame(parent, bg='#F3E5F5', relief='solid', bd=1)
        frame.pack(fill=tk.X, padx=8, pady=(6, 2))
        header = tk.Frame(frame, bg='#F3E5F5')
        header.pack(fill=tk.X)
        arrow = tk.Label(header, text='▾', bg='#F3E5F5', fg='#7B1FA2',
                         font=('Microsoft YaHei', 9))
        arrow.pack(side=tk.LEFT, padx=4)
        tk.Label(header, text='思考过程', bg='#F3E5F5', fg='#7B1FA2',
                 font=('Microsoft YaHei', 9, 'italic')).pack(side=tk.LEFT)
        body = tk.Label(frame, text=thinking_text, bg='#F3E5F5', fg='#555',
                        font=('Microsoft YaHei', 9), justify='left', wraplength=560,
                        padx=8, pady=4)
        body.pack(fill=tk.X)

        def toggle():
            if body.winfo_viewable():
                body.pack_forget()
                arrow.config(text='▸')
            else:
                body.pack(fill=tk.X)
                arrow.config(text='▾')

        header.bind('<Button-1>', lambda e: toggle())
        arrow.bind('<Button-1>', lambda e: toggle())

    def _configure_tags(self, text):
        text.tag_configure('h1', font=('Microsoft YaHei', 14, 'bold'), foreground='#212121')
        text.tag_configure('h2', font=('Microsoft YaHei', 13, 'bold'), foreground='#212121')
        text.tag_configure('h3', font=('Microsoft YaHei', 12, 'bold'), foreground='#212121')
        text.tag_configure('h4', font=('Microsoft YaHei', 11, 'bold'), foreground='#212121')
        text.tag_configure('p', font=('Microsoft YaHei', 10), foreground='#212121')
        text.tag_configure('quote', font=('Microsoft YaHei', 10, 'italic'), foreground='#616161')
        text.tag_configure('li', font=('Microsoft YaHei', 10), foreground='#212121')
        text.tag_configure('hr', foreground='#BDBDBD')
        text.tag_configure('codeblock', background=CODE_BG, font=('Consolas', 9),
                           foreground='#212121', relief='flat', spacing1=4, spacing3=4)
        text.tag_configure('inlinecode', background=CODE_BG, font=('Consolas', 9),
                           foreground='#C2185B')
        text.tag_configure('bold', font=('Microsoft YaHei', 10, 'bold'), foreground='#212121')
        text.tag_configure('italic', font=('Microsoft YaHei', 10, 'italic'), foreground='#212121')

    def _fit_text_height(self, text):
        text.update_idletasks()
        lines = int(text.index('end-1c').split('.')[0])
        text.configure(height=min(max(lines, 2), 40))

    # ---------------- 模型单选框（动态） ----------------
    def _refresh_models(self):
        for w in self.model_frame.winfo_children():
            w.destroy()
        self.models = self.model_svc.list_models(only_enabled=True)
        if not self.models:
            self.model_var.set('')
            self.hint_label.config(text='请先在系统设置中配置模型')
            self.send_btn.config(state=tk.DISABLED)
            return
        self.hint_label.config(text='')
        self.send_btn.config(state=tk.NORMAL)
        default = self.models[0]
        self.model_var.set(str(default['id']))
        for m in self.models:
            rb = tk.Radiobutton(self.model_frame, text=m['name'],
                                variable=self.model_var, value=str(m['id']),
                                bg='#FFFFFF', font=('Microsoft YaHei', 10),
                                activebackground='#FFFFFF', cursor='hand2')
            rb.pack(side=tk.LEFT, padx=8)
            if m.get('description'):
                self._add_tooltip(rb, m['description'])

    def _add_tooltip(self, widget, text):
        def enter(e):
            x, y = e.x_root + 10, e.y_root + 10
            tip = tk.Toplevel(self)
            tip.wm_overrideredirect(True)
            tip.geometry('+%d+%d' % (x, y))
            tk.Label(tip, text=text, bg='#333', fg='white',
                     font=('Microsoft YaHei', 9), padx=8, pady=4,
                     wraplength=260, justify='left').pack()
            widget._tip = tip
        def leave(e):
            if hasattr(widget, '_tip'):
                widget._tip.destroy()
                del widget._tip
        widget.bind('<Enter>', enter)
        widget.bind('<Leave>', leave)

    def _selected_model(self):
        mid = self.model_var.get()
        if not mid:
            return None
        return next((m for m in self.models if str(m['id']) == mid), None)

    # ---------------- 发送 / 停止 ----------------
    def _send(self):
        if self.generating:
            return
        if self.current_session_id is None:
            self._new_session()
            if self.current_session_id is None:
                return
        model = self._selected_model()
        if model is None:
            messagebox.showwarning('提示', '请先选择模型')
            return
        user_text = self.input_box.get('1.0', tk.END).strip()
        if not user_text:
            return
        # 输入长度检测与截取
        truncated_text, was_cut = prepare_user_input(user_text, model['max_tokens'])
        if was_cut:
            self.hint_label.config(text='输入过长已自动截取')
        else:
            self.hint_label.config(text='')
        self.input_box.delete('1.0', tk.END)

        # 展示用户消息
        self._add_user_bubble(truncated_text)

        # 创建助手气泡并准备流式渲染
        renderer, text_w = self._create_streaming_bubble()
        self.generating = True
        self.send_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.cancel_event = threading.Event()

        # 后台线程请求
        thread = threading.Thread(
            target=self._run_request,
            args=(renderer, text_w, model, truncated_text),
            daemon=True,
        )
        thread.start()

    def _create_streaming_bubble(self):
        row = tk.Frame(self.msg_inner, bg=BG)
        row.pack(fill=tk.X, pady=6, padx=8)
        bubble = tk.Frame(row, bg=ASSIST_BUBBLE, relief='solid', bd=1)
        bubble.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)
        text = tk.Text(bubble, bg=ASSIST_BUBBLE, relief='flat', height=2,
                       font=('Microsoft YaHei', 10), wrap='word',
                       padx=10, pady=8, state=tk.DISABLED)
        text.pack(fill=tk.X, expand=True)
        self._configure_tags(text)
        renderer = MarkdownRenderer(text, on_copy_code=self._copy_code,
                                    on_save_code=self._save_code)
        return renderer, text

    def _run_request(self, renderer, text_w, model, user_text):
        # 收集流式增量
        content_buf = []
        thinking_buf = []
        think_appended = [False]

        def on_delta(delta):
            content_buf.append(delta)
            self.after(0, self._append_stream, text_w, renderer, ''.join(content_buf))

        def on_thinking(delta):
            thinking_buf.append(delta)
            if not think_appended[0]:
                think_appended[0] = True
                self.after(0, self._ensure_thinking, text_w, ''.join(thinking_buf))
            else:
                self.after(0, self._append_thinking, text_w, ''.join(thinking_buf))

        def on_done(result):
            self.after(0, self._finalize_stream, text_w, renderer,
                       result['content'], result['thinking'])

        def on_error(err):
            self.after(0, self._on_error, err)

        try:
            self.chat_svc.send(
                self.current_session_id, model['id'], user_text,
                on_delta=on_delta, on_thinking=on_thinking,
                on_done=on_done, on_error=on_error,
                cancel_event=self.cancel_event,
            )
        except Exception as e:
            self.after(0, self._on_error, AIClientError(str(e)))

    def _append_stream(self, text_w, renderer, full_text):
        # 增量重渲染整段（轻量场景可接受）
        renderer.render(full_text)
        self._fit_text_height(text_w)
        self._scroll_to_bottom()

    def _ensure_thinking(self, text_w, thinking_text):
        self._add_thinking(text_w.master, thinking_text)

    def _append_thinking(self, text_w, thinking_text):
        # 更新已有思考区文本
        for child in text_w.master.winfo_children():
            if isinstance(child, tk.Frame) and child.cget('bg') == '#F3E5F5':
                for sub in child.winfo_children():
                    if isinstance(sub, tk.Frame):  # header
                        continue
                    if isinstance(sub, tk.Label):
                        sub.config(text=thinking_text)
                break

    def _finalize_stream(self, text_w, renderer, content, thinking):
        renderer.render(content)
        if thinking and not any(isinstance(c, tk.Frame) and c.cget('bg') == '#F3E5F5'
                                for c in text_w.master.winfo_children()):
            self._add_thinking(text_w.master, thinking)
        self._fit_text_height(text_w)
        self._scroll_to_bottom()
        self._end_generating()

    def _on_error(self, err):
        msg = getattr(err, 'message', str(err))
        kind = getattr(err, 'kind', 'unknown')
        hint = {
            'connection': '连接失败，请检查 API 地址与网络',
            'auth': '鉴权失败，请检查 API Key',
            'timeout': '请求超时，请稍后重试',
            'http': 'API 返回错误',
            'parse': '响应解析失败',
        }.get(kind, '调用失败')
        self._add_user_bubble('⚠️ %s：%s' % (hint, msg))
        self._end_generating()

    def _stop(self):
        if self.cancel_event:
            self.cancel_event.set()
        self._end_generating()

    def _end_generating(self):
        self.generating = False
        self.send_btn.config(state=tk.NORMAL if self.models else tk.DISABLED)
        self.stop_btn.config(state=tk.DISABLED)
        self._load_sessions()

    # ---------------- 代码操作 ----------------
    def _copy_code(self, code):
        self.clipboard_clear()
        self.clipboard_append(code)
        self.hint_label.config(text='已复制到剪贴板')
        self.after(2000, lambda: self.hint_label.config(text=''))

    def _save_code(self, code, lang):
        ext_map = {'python': '.py', 'py': '.py', 'javascript': '.js', 'js': '.js',
                   'bash': '.sh', 'shell': '.sh', 'java': '.java', 'go': '.go',
                   'cpp': '.cpp', 'c': '.c', 'json': '.json', 'html': '.html',
                   'sql': '.sql', 'xml': '.xml', 'yaml': '.yaml', 'yml': '.yml'}
        ext = ext_map.get((lang or '').lower(), '.txt')
        path = filedialog.asksaveasfilename(defaultextension=ext,
                                            filetypes=[('代码文件', '*%s' % ext), ('全部', '*.*')])
        if path:
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(code)
                self.hint_label.config(text='已保存：' + path)
                self.after(2000, lambda: self.hint_label.config(text=''))
            except Exception as e:
                messagebox.showerror('保存失败', str(e))

    # ---------------- 滚动 ----------------
    def _on_canvas_configure(self, event):
        self.msg_canvas.itemconfig('all', width=event.width)
        self.msg_canvas.configure(scrollregion=self.msg_canvas.bbox('all'))

    def _on_inner_configure(self, event):
        self.msg_canvas.configure(scrollregion=self.msg_canvas.bbox('all'))

    def _on_mousewheel(self, event):
        self.msg_canvas.yview_scroll(int(-1 * (event.delta / 120)), 'units')

    def _scroll_to_bottom(self):
        self.msg_canvas.update_idletasks()
        self.msg_canvas.yview_moveto(1.0)
