# faq/ui.py
# FAQ 知识库界面层（独立 Toplevel 窗口）
# 左侧：树形分类导航（支持动态添加分类）
# 右侧上：搜索栏 + 结果列表
# 右侧下：Markdown 渲染区（tkhtmlview，缺失时降级纯文本）
# 检索走多线程（server.search_async），结果主线程回填，避免 UI 卡顿。

import os
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

# Markdown -> HTML 渲染（用户确认引入 tkhtmlview）
try:
    from markdown import markdown as md_to_html
    from tkhtmlview import HTMLScrolledText
    _HAVE_TKHTMLVIEW = True
except Exception:
    _HAVE_TKHTMLVIEW = False
    def md_to_html(text: str) -> str:
        # 降级：不渲染，直接转义换行
        return (text or '').replace('\n', '<br>')

from faq.server import FAQServer
from tools.logs import logs


# 视觉常量（沿用主程序风格）
BG = '#F0F0F0'
WHITE = '#FFFFFF'
PRIMARY = '#0078D4'
FONT = ('Microsoft YaHei', 10)
FONT_TITLE = ('Microsoft YaHei', 14, 'bold')
FONT_SUB = ('Microsoft YaHei', 11, 'bold')


class FaqWindow(tk.Toplevel):
    """FAQ 知识库独立窗口。"""

    def __init__(self, parent, db_path: str):
        super().__init__(parent)
        self.parent = parent
        self.title('FAQ 知识库')
        self.geometry('920x620')
        self.configure(bg=BG)
        self._img_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'img')

        self.log = logs()
        self.server = FAQServer(db_path)
        self.server.bind_root(self.parent)  # 注入主窗口用于线程安全调度

        self._selected_article_id = None
        self._cat_item_map = {}   # tree item id -> category id
        self._result_map = []      # 当前结果列表（与 Listbox 索引对应）

        self._build_ui()
        self._refresh_categories()
        self._render_placeholder()

    # ---------- UI 构建 ----------
    def _build_ui(self):
        # 顶部标题栏
        top = tk.Frame(self, bg=PRIMARY, height=46)
        top.pack(fill=tk.X)
        tk.Label(top, text='FAQ 知识库', font=FONT_TITLE, fg='white', bg=PRIMARY,
                 anchor='w', padx=12).pack(side=tk.LEFT)
        tk.Button(top, text='+ 添加分类', font=FONT, bg=WHITE, fg=PRIMARY,
                  relief='flat', command=self._on_add_category).pack(side=tk.RIGHT, padx=10, pady=8)

        # 主体：左右分栏
        body = tk.Frame(self, bg=BG)
        body.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # ---- 左侧：分类树 ----
        left = tk.Frame(body, bg=WHITE, width=220)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 8))
        left.pack_propagate(False)
        tk.Label(left, text='分类导航', font=FONT_SUB, bg=WHITE, anchor='w',
                 padx=8, pady=6).pack(fill=tk.X)
        self.tree = ttk.Treeview(left, show='tree', height=30)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=6, pady=4)
        self.tree.bind('<<TreeviewSelect>>', self._on_category_select)
        self.tree.bind('<Button-3>', self._on_tree_right_click)  # 右键添加子分类
        self._build_tree_menu()

        # ---- 右侧：搜索 + 列表 + 渲染 ----
        right = tk.Frame(body, bg=BG)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 搜索栏
        search_frame = tk.Frame(right, bg=BG)
        search_frame.pack(fill=tk.X, pady=(0, 6))
        tk.Label(search_frame, text='🔍', bg=BG, font=FONT).pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(search_frame, textvariable=self.search_var, font=FONT)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)
        self.search_entry.bind('<Return>', lambda e: self._on_search())
        tk.Button(search_frame, text='搜索', font=FONT, bg=PRIMARY, fg='white',
                  relief='flat', command=self._on_search).pack(side=tk.LEFT, padx=(4, 0))

        # 结果列表
        list_frame = tk.Frame(right, bg=WHITE, height=180)
        list_frame.pack(fill=tk.X, pady=(0, 6))
        list_frame.pack_propagate(False)
        self.result_list = tk.Listbox(list_frame, font=FONT, bg=WHITE,
                                      relief='flat', activestyle='none')
        self.result_list.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        self.result_list.bind('<<ListboxSelect>>', self._on_result_select)
        self.result_list.bind('<Button-3>', self._on_list_right_click)

        # 渲染/编辑区：上工具栏 + 下方 PanedWindow（左编辑框 / 右实时预览）
        render_frame = tk.Frame(right, bg=WHITE)
        render_frame.pack(fill=tk.BOTH, expand=True)
        toolbar = tk.Frame(render_frame, bg=WHITE)
        toolbar.pack(fill=tk.X, padx=8, pady=4)
        tk.Label(toolbar, text='内容（编辑后自动保存）', font=FONT_SUB, bg=WHITE,
                 anchor='w').pack(side=tk.LEFT)

        pane = tk.PanedWindow(render_frame, orient=tk.HORIZONTAL, bg=WHITE,
                              sashwidth=4, sashrelief='flat')
        pane.pack(fill=tk.BOTH, expand=True, padx=6, pady=4)

        # 左侧：编辑框（实时编辑 + 防抖自动保存）
        edit_sub = tk.Frame(pane, bg=WHITE)
        self.editor = tk.Text(edit_sub, font=FONT, bg=WHITE, relief='flat', wrap='word')
        self.editor.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        self.editor.bind('<KeyRelease>', self._on_editor_change)
        pane.add(edit_sub, width=420)

        # 右侧：实时预览
        preview_sub = tk.Frame(pane, bg=WHITE)
        if _HAVE_TKHTMLVIEW:
            self.render = HTMLScrolledText(preview_sub, font=FONT, background=WHITE)
            self.render.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        else:
            self.render = tk.Text(preview_sub, font=FONT, bg=WHITE, relief='flat', wrap='word')
            self.render.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
            self.render.config(state='disabled')
        pane.add(preview_sub, width=420)

        # 自动保存相关状态
        self._save_timer = None
        self._editing_article_id = None

        # 状态栏
        self.status = tk.Label(self, text='就绪', bg=BG, fg='#757575', font=('Microsoft YaHei', 9),
                               anchor='w', padx=10)
        self.status.pack(fill=tk.X, side=tk.BOTTOM)

        # ESC 关闭窗口
        self.bind('<Escape>', lambda e: self.destroy())

    def _build_tree_menu(self):
        self._tree_menu = tk.Menu(self, tearoff=0)
        self._tree_menu.add_command(label='添加子分类', command=self._on_add_subcategory)
        self._tree_menu.add_command(label='重命名分类', command=self._on_rename_category)
        self._tree_menu.add_command(label='删除分类', command=self._on_delete_category)

    def _build_list_menu(self):
        self._list_menu = tk.Menu(self, tearoff=0)
        self._list_menu.add_command(label='新增条目', command=self._on_add_article)
        self._list_menu.add_command(label='修改条目', command=self._on_edit_article)
        self._list_menu.add_command(label='删除条目', command=self._on_delete_article)

    # ---------- 数据刷新 ----------
    def _refresh_categories(self):
        self.tree.delete(*self.tree.get_children())
        self._cat_item_map.clear()
        cats = self.server.get_categories()
        # 仅展示顶级（parent_id 为空）
        for c in cats:
            if c['parent_id'] is None or c['parent_id'] == '':
                iid = self.tree.insert('', 'end', text=c['name'])
                self._cat_item_map[iid] = c['id']
        # 子分类挂到父节点（按插入顺序，简单两层级）
        for c in cats:
            pid = c['parent_id']
            if pid:
                parent_iid = self._find_tree_iid_by_cat_id(pid)
                if parent_iid:
                    iid = self.tree.insert(parent_iid, 'end', text=c['name'])
                    self._cat_item_map[iid] = c['id']

    def _find_tree_iid_by_cat_id(self, cat_id):
        for iid, cid in self._cat_item_map.items():
            if cid == cat_id:
                return iid
        return None

    # ---------- 事件处理 ----------
    def _on_category_select(self, event):
        sel = self.tree.selection()
        if not sel:
            return
        cat_id = self._cat_item_map.get(sel[0])
        if cat_id is None:
            return
        arts = self.server.get_articles_by_category(cat_id)
        self._result_map = [
            {'id': a['id'], 'title': a['title'], 'content_type': a['content_type'],
             'summary': a['title'], 'category': ''}
            for a in arts
        ]
        self._fill_result_list(self._result_map)
        # 切换分类后若当前分类无条目，清空预览区，避免残留上一分类内容
        if not arts:
            self._clear_render()
            self._selected_article_id = None
        self.status.config(text=f'分类下共 {len(arts)} 条')

    def _on_search(self):
        keyword = self.search_var.get().strip()
        if not keyword:
            messagebox.showinfo('提示', '请输入检索关键词')
            return
        self.status.config(text='检索中…')
        self.result_list.delete(0, tk.END)
        self.result_list.insert(tk.END, '（检索中…）')
        self.server.search_async(
            keyword,
            on_start=None,
            on_done=self._on_search_done,
        )

    def _on_search_done(self, results):
        self._result_map = results
        self._fill_result_list(results)
        self.status.config(text=f'检索完成：共 {len(results)} 条结果')

    def _fill_result_list(self, results):
        self.result_list.delete(0, tk.END)
        if not results:
            self.result_list.insert(tk.END, '（无匹配结果）')
            return
        for r in results:
            label = f"[{r.get('content_type','text')}] {r.get('title','')}"
            if r.get('category'):
                label += f"  —— {r.get('category')}"
            self.result_list.insert(tk.END, label)

    def _on_result_select(self, event):
        sel = self.result_list.curselection()
        if not sel:
            return
        idx = sel[0]
        if idx >= len(self._result_map):
            return
        item = self._result_map[idx]
        self._selected_article_id = item.get('id')
        # 优先用列表中的 content（检索结果已带 content），否则按 id 再查
        content = item.get('content')
        ctype = item.get('content_type', 'text')
        if content is None and self._selected_article_id:
            full = self.server.get_article(self._selected_article_id)
            if full:
                content = full.get('content_md', '')
                ctype = full.get('content_type', 'text')
        # 传入 article_id 使编辑器进入可编辑态并支持自动保存
        self._render_content(content or '', ctype, article_id=self._selected_article_id)

    def _render_content(self, content, ctype, article_id=None):
        """渲染内容：右侧预览 + 左侧编辑器（若有关联条目 id 则进入可编辑态）。"""
        html = self._to_html(content, ctype)
        if _HAVE_TKHTMLVIEW:
            self.render.set_html(html)
        else:
            self.render.config(state='normal')
            self.render.delete('1.0', tk.END)
            self.render.insert('1.0', content)
            self.render.config(state='disabled')

        # 编辑器：仅在有关联条目时加载并可编辑
        self.editor.delete('1.0', tk.END)
        if article_id is not None:
            self._editing_article_id = article_id
            self.editor.insert('1.0', content or '')
            self.editor.config(state='normal')
            self.status.config(text='可编辑：修改后自动保存')
        else:
            self._editing_article_id = None
            self.editor.config(state='disabled')

    def _to_html(self, content, ctype):
        if ctype == 'sql':
            # SQL 用等宽代码块展示
            esc = (content or '').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            return f'<pre style="background:#f5f5f5;padding:8px;font-family:Consolas,monospace;">{esc}</pre>'
        if ctype == 'doc':
            # 文档类型按 Markdown 渲染
            return md_to_html(content or '')
        # 默认 text / markdown
        return md_to_html(content or '')

    # ---------- 编辑 / 自动保存 ----------
    def _on_editor_change(self, event=None):
        """编辑框内容变化：防抖自动保存（800ms 内无新输入才提交）。"""
        if self._editing_article_id is None:
            return
        if self._save_timer is not None:
            self.after_cancel(self._save_timer)
        self._save_timer = self.after(800, self._auto_save)
        self.status.config(text='编辑中…')

    def _auto_save(self):
        self._save_timer = None
        if self._editing_article_id is None:
            return
        content = self.editor.get('1.0', 'end').rstrip('\n')
        # 标题沿用现有（自动保存仅保存正文；标题修改走"修改条目"对话框）
        full = self.server.get_article(self._editing_article_id)
        if not full:
            return
        try:
            self.server.update_article(
                self._editing_article_id, full['title'], content, full['content_type'])
            # 实时刷新预览
            html = self._to_html(content, full['content_type'])
            if _HAVE_TKHTMLVIEW:
                self.render.set_html(html)
            else:
                self.render.config(state='normal')
                self.render.delete('1.0', tk.END)
                self.render.insert('1.0', content)
                self.render.config(state='disabled')
            self.status.config(text='已自动保存 ✓')
            self.log.write_log_info('FAQ 自动保存条目 id=' + str(self._editing_article_id))
        except Exception as e:
            self.status.config(text='自动保存失败: ' + str(e))

    def _clear_render(self):
        self.editor.delete('1.0', tk.END)
        self.editor.config(state='disabled')
        self._editing_article_id = None
        if _HAVE_TKHTMLVIEW:
            self.render.set_html('')
        else:
            self.render.config(state='normal')
            self.render.delete('1.0', tk.END)
            self.render.config(state='disabled')

    def _render_placeholder(self):
        self._render_content('# 欢迎使用 FAQ 知识库\n\n- 左侧选择分类，或上方输入关键词检索\n- 支持 **Markdown**、`SQL`、文档 三种内容预览\n- 检索在后台线程执行，不阻塞界面', 'text', article_id=None)

    # ---------- 分类管理 ----------
    def _on_add_category(self):
        name = simpledialog.askstring('添加分类', '请输入分类名称：', parent=self)
        if not name:
            return
        self.server.add_category(name.strip())
        self._refresh_categories()
        self.log.write_log_info('FAQ 添加分类: ' + name)

    def _on_tree_right_click(self, event):
        sel = self.tree.selection()
        if sel:
            self._tree_menu.post(event.x_root, event.y_root)

    def _on_add_subcategory(self):
        sel = self.tree.selection()
        if not sel:
            return
        parent_id = self._cat_item_map.get(sel[0])
        name = simpledialog.askstring('添加子分类', '请输入子分类名称：', parent=self)
        if not name:
            return
        self.server.add_category(name.strip(), parent_id)
        self._refresh_categories()

    def _on_delete_category(self):
        sel = self.tree.selection()
        if not sel:
            return
        cat_id = self._cat_item_map.get(sel[0])
        if cat_id is None:
            return
        if not messagebox.askyesno('确认', '删除该分类及其下所有条目？', parent=self):
            return
        self.server.delete_category(cat_id)
        self._refresh_categories()

    def _on_rename_category(self):
        sel = self.tree.selection()
        if not sel:
            return
        cat_id = self._cat_item_map.get(sel[0])
        if cat_id is None:
            return
        old_name = self.tree.item(sel[0])['text']
        new_name = simpledialog.askstring('重命名分类', '请输入新分类名称：',
                                          initialvalue=old_name, parent=self)
        if not new_name or new_name.strip() == old_name:
            return
        self.server.rename_category(cat_id, new_name.strip())
        self._refresh_categories()
        self.log.write_log_info('FAQ 重命名分类: ' + old_name + ' -> ' + new_name)

    # ---------- 条目管理 ----------
    def _on_list_right_click(self, event):
        # 只要列表区域有右键就弹出菜单（无结果时仍允许"新增条目"）
        self._build_list_menu()
        has_selection = bool(self.result_list.curselection()) and self._result_map
        self._list_menu.entryconfig('修改条目', state='normal' if has_selection else 'disabled')
        self._list_menu.entryconfig('删除条目', state='normal' if has_selection else 'disabled')
        self._list_menu.post(event.x_root, event.y_root)

    def _current_category_id(self):
        """返回当前选中的分类 id（用于新增条目时归属）。"""
        sel = self.tree.selection()
        if sel:
            return self._cat_item_map.get(sel[0])
        return None

    def _on_add_article(self):
        cat_id = self._current_category_id()
        if cat_id is None:
            messagebox.showinfo('提示', '请先在左侧选择一个分类', parent=self)
            return
        self._open_article_dialog('新增条目', cat_id)

    def _on_edit_article(self):
        sel = self.result_list.curselection()
        if not sel or sel[0] >= len(self._result_map):
            return
        art_id = self._result_map[sel[0]].get('id')
        if art_id is None:
            return
        full = self.server.get_article(art_id)
        if not full:
            return
        self._open_article_dialog('修改条目', full['category_id'], article=full)

    def _open_article_dialog(self, title, category_id, article=None):
        """新增/修改条目对话框。"""
        dlg = tk.Toplevel(self)
        dlg.title(title)
        dlg.geometry('560x520')
        dlg.configure(bg=BG)
        dlg.transient(self)
        dlg.grab_set()
        # 居中显示在 FAQ 主窗口中央（而非默认左上角）
        dlg.update_idletasks()
        px, py = self.winfo_rootx(), self.winfo_rooty()
        pw, ph = self.winfo_width(), self.winfo_height()
        x = px + (pw - 560) // 2
        y = py + (ph - 520) // 2
        dlg.geometry('+{}+{}'.format(max(x, 0), max(y, 0)))

        # grid 布局：内容区行可拉伸，按钮行固定高度，保证按钮始终可见
        dlg.grid_columnconfigure(0, weight=1)
        dlg.grid_rowconfigure(5, weight=1)

        tk.Label(dlg, text='标题', font=FONT, bg=BG, anchor='w').grid(row=0, column=0, sticky='ew', padx=12, pady=(10, 2))
        title_var = tk.StringVar(value=article['title'] if article else '')
        tk.Entry(dlg, textvariable=title_var, font=FONT).grid(row=1, column=0, sticky='ew', padx=12)

        tk.Label(dlg, text='类型', font=FONT, bg=BG, anchor='w').grid(row=2, column=0, sticky='ew', padx=12, pady=(8, 2))
        type_var = tk.StringVar(value=article['content_type'] if article else 'text')
        ttk.Combobox(dlg, textvariable=type_var, font=FONT,
                     values=['text', 'sql', 'doc'], state='readonly').grid(row=3, column=0, sticky='ew', padx=12)

        tk.Label(dlg, text='内容（Markdown / SQL / 文档）', font=FONT, bg=BG, anchor='w').grid(row=4, column=0, sticky='ew', padx=12, pady=(8, 2))
        text_frame = tk.Frame(dlg, bg=BG)
        text_frame.grid(row=5, column=0, sticky='nsew', padx=12, pady=(2, 6))
        text_area = tk.Text(text_frame, font=FONT, bg=WHITE, relief='flat', wrap='word')
        text_area.pack(fill=tk.BOTH, expand=True)
        text_area.insert('1.0', article['content_md'] if article else '')

        def on_save():
            t = title_var.get().strip()
            c = text_area.get('1.0', 'end').rstrip('\n')
            ct = type_var.get()
            if not t:
                messagebox.showinfo('提示', '标题不能为空', parent=dlg)
                return
            if article:
                self.server.update_article(article['id'], t, c, ct)
                self.log.write_log_info('FAQ 修改条目: ' + t)
                self.status.config(text='已保存修改：' + t)
            else:
                self.server.add_article(category_id, t, c, ct)
                self.log.write_log_info('FAQ 新增条目: ' + t)
                self.status.config(text='已新增条目：' + t)
            dlg.destroy()
            self._refresh_current_list()

        btn_frame = tk.Frame(dlg, bg=BG)
        btn_frame.grid(row=6, column=0, sticky='ew', padx=12, pady=(0, 10))
        tk.Button(btn_frame, text='保存', font=FONT, bg=PRIMARY, fg='white',
                  relief='flat', command=on_save).pack(side=tk.RIGHT, padx=4)
        tk.Button(btn_frame, text='取消', font=FONT, bg=WHITE, fg='#333333',
                  relief='flat', command=dlg.destroy).pack(side=tk.RIGHT, padx=4)

        # 明确放弃更改：ESC 关闭对话框（不保存）
        dlg.bind('<Escape>', lambda e: dlg.destroy())

    def _refresh_current_list(self):
        """刷新当前结果列表（分类选中态或检索结果均刷新）。"""
        sel = self.tree.selection()
        if sel:
            self._on_category_select(None)
        else:
            # 无分类选中时，保留原列表但刷新选中条目信息
            pass

    def _on_delete_article(self):
        sel = self.result_list.curselection()
        if not sel or sel[0] >= len(self._result_map):
            return
        art_id = self._result_map[sel[0]].get('id')
        if art_id is None:
            return
        if not messagebox.askyesno('确认', '确定删除该条目？', parent=self):
            return
        self.server.delete_article(art_id)
        self.log.write_log_info('FAQ 删除条目 id=' + str(art_id))
        # 从结果列表移除并清空预览
        del self._result_map[sel[0]]
        self._fill_result_list(self._result_map)
        self._clear_render()
        self._selected_article_id = None
