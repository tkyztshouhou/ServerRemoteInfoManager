---
name: 修复 ISSUES.md 轻微 Bug
overview: 修复 ISSUES.md 中"轻微 Bug"部分列出的所有问题（B18-B30），包括路径问题、注释错误、废弃 API、日志问题、调试代码清理等。
todos:
  - id: fix-paths
    content: "修复 B18/B19: 将相对路径改为基于 __file__ 的绝对路径（infoServer.py）"
    status: completed
  - id: fix-comments
    content: "修复 B20/B21: 修正 pack_propagate 注释并删除冗余搜索按钮注释代码"
    status: completed
    dependencies:
      - fix-paths
  - id: fix-tool-deprecated
    content: "修复 B22: 将 setDaemon 改为 daemon 属性赋值（tool.py）"
    status: completed
    dependencies:
      - fix-comments
  - id: fix-tool-imports
    content: "修复 B23/B24: 将导入移到模块顶部并修正 is_ip 日志级别（tool.py）"
    status: completed
    dependencies:
      - fix-tool-deprecated
  - id: fix-logs
    content: "修复 B25/B26: 重构 logs.py，统一 day 赋值并使用 with 语句管理文件"
    status: completed
    dependencies:
      - fix-tool-imports
  - id: fix-prints
    content: "修复 B27/B28: 清理 gui_DA.py 和 infoServer.py 中的 print() 调试输出"
    status: completed
    dependencies:
      - fix-logs
  - id: fix-column-name
    content: "修复 B30: 将 server_tree 列名\"域名\"改为\"IP地址\""
    status: completed
    dependencies:
      - fix-prints
  - id: update-issues
    content: 更新 ISSUES.md，标记所有修复的 Bug 状态
    status: completed
    dependencies:
      - fix-column-name
---

## 需求分析

修复 ISSUES.md 中列出的所有轻微 Bug（B18-B30），共 13 个问题：

### 待修复 Bug 列表

| # | 位置 | 问题描述 |
| --- | --- | --- |
| B18 | `infoServer.py:32` | `tk.PhotoImage(file='./img/top.png')` 使用相对路径，工作目录不在项目根目录时找不到图片 |
| B19 | `infoServer.py:33` | `DataAccess(os.path.join(os.getcwd(), 'data.db'))` 依赖 `os.getcwd()`，从其他目录启动则数据库位置不可控 |
| B20 | `infoServer.py:86, 94, 98, 103, 107` | `pack_propagate(1)` 注释说"禁止为1"，但实际 `1=True` 表示**允许**内部控件影响外层大小，注释与代码相反 |
| B21 | `infoServer.py:120-121` | 搜索按钮被注释掉（`top_frame_button_6`），但搜索功能通过右上角搜索框实现，存在冗余注释代码 |
| B22 | `tool.py:27` | `t.setDaemon(True)` 在 Python 3.10 中已弃用，应改用 `t.daemon = True` |
| B23 | `tool.py:63-64` | `is_ip` 方法内部 `import re` 和 `from tools.logs import logs` 每次调用都重新导入，应移到模块顶部 |
| B24 | `tool.py:68, 71` | `is_ip` 将"格式正确"记为 ERROR、"格式错误"记为 INFO，日志级别使用不当 |
| B25 | `logs.py:13-22` | `__init__` 中 `self.day` 在 `if` 分支内赋值后创建文件，但 `else` 分支重复赋值并写入"DEBUG 日志文件存在"，导致每次实例化都写入调试行 |
| B26 | `logs.py` 全文 | 每次写日志都 `open` → `write` → `close`，高频写时性能差，且未使用 `with` 语句，异常时文件不关闭 |
| B27 | `gui_DA.py:60, 63, 131, 154, 157, 175, 189, 206, 212` | 多处 `print()` 调试输出未清理 |
| B28 | `infoServer.py:806, 959, 964, 968, 973, 1054, 1060` | 多处 `print()` 调试输出未清理 |
| B30 | `infoServer.py:156` | `server_tree.heading('ip', text='域名')` 列名为 `ip` 但显示为"域名"，命名不一致 |


### 修复目标

- 保持原有代码风格和项目结构不变
- 修复后确保功能正常，不引入新问题
- 清理调试代码，提升代码质量

## 技术方案

### 技术栈

- Python 3.10
- Tkinter (GUI)
- SQLite (数据库)
- PIL (图像处理)

### 修复策略

#### 1. 路径问题修复 (B18, B19)

**根因**: 使用相对路径依赖工作目录，从其他目录启动时找不到文件或数据库。
**方案**: 使用 `os.path.dirname(os.path.abspath(__file__))` 构造项目根目录绝对路径，所有资源路径基于此计算。

```python
# 项目根目录
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 图片路径
img_path = os.path.join(PROJECT_ROOT, 'img', 'top.png')
# 数据库路径
db_path = os.path.join(PROJECT_ROOT, 'data.db')
```

#### 2. 注释修正 (B20)

**根因**: 注释与实际行为相反，`pack_propagate(1)` 表示允许内部控件影响外层大小。
**方案**: 修正注释为"允许内部控件影响外层控件大小"。

#### 3. 删除冗余代码 (B21)

**根因**: 搜索按钮已注释掉，但搜索功能通过右上角搜索框实现，注释代码无意义。
**方案**: 删除 `top_frame_button_6` 的注释代码块。

#### 4. 废弃 API 修复 (B22)

**根因**: `setDaemon()` 在 Python 3.10 已弃用，3.12 将移除。
**方案**: 改为属性赋值 `t.daemon = True`。

#### 5. 导入优化 (B23)

**根因**: 方法内部导入导致每次调用都重新加载模块，违反 PEP 8。
**方案**: 将 `import re` 和 `from tools.logs import logs` 移到模块顶部。

#### 6. 日志级别修正 (B24)

**根因**: IP 格式正确应记为 INFO，格式错误应记为 WARNING 或 ERROR。
**方案**: 交换日志级别，格式正确用 `write_log_info`，格式错误用 `write_log_error`。

#### 7. 日志类重构 (B25, B26)

**根因**:

- B25: `self.day` 在 if/else 分支都赋值，且每次实例化都写入调试行
- B26: 每次写日志都 open/close，性能差且异常时文件不关闭

**方案**:

- 重构 `__init__`，统一 `self.day` 赋值，删除调试行写入
- 使用 `with` 语句管理文件操作，确保异常时正确关闭

#### 8. 清理 print() 调试输出 (B27, B28)

**根因**: 开发过程中遗留的调试代码未清理。
**方案**: 删除所有 `print()` 语句，保留已有的日志记录。

#### 9. 列名修正 (B30)

**根因**: 列名 `ip` 与显示文本"域名"不一致。
**方案**: 将表头文本改为"IP地址"，与列名语义一致。

## Agent Extensions

### SubAgent

- **code-explorer**
- Purpose: 探索代码库，确认所有需要修改的文件和位置
- Expected outcome: 精确定位所有 Bug 的所在行号和上下文