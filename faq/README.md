# FAQ 知识库模块（faq/）

FAQ（常见问题知识库）功能模块，从主程序 `infoServer.py` 解耦，独立为 Python 包。
点击主窗口 FAQ 按钮（独立 Toplevel 窗口）打开，不破坏主界面布局。

## 目录结构

```
faq/
├── __init__.py       # 包导出（FAQServer / FaqUI）
├── da.py             # DataAccess 数据访问层（SQLite3 读写 + RAG 预留接口）
├── server.py         # 业务调度层（FAQServer：分类/条目 CRUD、异步检索）
├── ui.py             # 界面层（FaqWindow：树形导航 + 搜索 + Markdown 渲染）
├── main.py           # 程序入口（独立运行入口，供调试）
├── sample_data.py    # 示例分类与条目初始化数据
└── README.md         # 本文档
```

## 职责分离

- **DA（da.py）**：仅负责与 `faq.db` 的交互，不依赖 UI/线程。
  - `get_categories()` / `get_articles(category_id)` / `get_article(article_id)`
  - `add_category()` / `add_article()` / `update_article()` / `delete_*()`
  - **RAG 扩展预留**：`embedding(text)` 与 `vector_search(vec, top_k)` 为占位方法，
    后期可接入大模型/向量库实现语义检索，无需改动上层调用。
- **Server（server.py）**：业务编排。检索默认走 `LIKE` 关键词模糊匹配，
  通过 `threading` 守护线程执行，避免阻塞 UI；检索结果回调由调用方 `after()` 回填。
- **UI（ui.py）**：`FaqWindow(Toplevel)`。
  - 左侧 `ttk.Treeview` 树形分类导航（支持动态添加分类/子分类）。
  - 右侧上方搜索栏 + 结果列表，下方 Markdown 渲染区
    （`tkhtmlview.HTMLScrolledText`；库缺失时自动降级为纯 `Text` 文本）。
  - 支持 `text` / `sql` / `doc` 三种内容类型预览。
  - 新增/修改条目弹窗：grid 布局居中显示，含"保存/取消"按钮，
    保存后状态栏反馈，ESC 关闭放弃更改。

## 数据存储

- 独立 SQLite3 数据库 `faq.db`，位于 `%LOCALAPPDATA%/ServerRemoteInfoManager/`
  （与业务库 `data.db` 分离，互不干扰）。
- 表：`categories`（分类：id / name / parent_id）、`articles`
  （条目：id / category_id / title / content_md / content_type）。

## 检索与 RAG 扩展

- 当前：`server.search(keyword)` → DA 层 `LIKE '%kw%'` 模糊匹配标题与内容。
- 后期扩展向量检索：
  1. 实现 `DA.embedding(text)` 返回向量（调用本地/远程 Embedding 模型）。
  2. 在 `articles` 表增加 `embedding` 列存储向量（或独立向量库）。
  3. 用 `DA.vector_search(vec, top_k)` 替换/并联 `LIKE` 检索，`server.search`
     增加 `mode='vector'|'keyword'|'hybrid'` 参数，UI 无需大改。

## 打包注意

- `requirements.txt` 已声明 `markdown==3.5.1`、`tkhtmlview==0.0.9`。
- `build.spec` 的 `hiddenimports` 已加入 `'markdown'`、`'tkhtmlview'` 与
  `collect_submodules('faq')`，确保 PyInstaller 打包后导入正常。

## 运行 / 调试

```bash
python -m faq.main     # 独立启动 FAQ 窗口（调试用）
```
主程序集成入口：`infoServer.py` 的 `show_faq()` 调用 `faq.ui.FaqWindow`。
