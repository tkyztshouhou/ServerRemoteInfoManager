# 已知问题与待解决事项

> 本文档记录项目当前已知问题、未实现功能及代码质量问题，供迭代参考。

---

## 一、已修复 Bug

| # | 位置 | 问题描述 | 修复状态 |
|---|------|----------|----------|
| B1 | `gui_DA.py` | `destroy` 缺少括号 `()` → 所有"刷新"逻辑失效 | ✅ 已修复 |
| B2 | `gui_DA.py` | 同上，多处 `destroy` 调用 | ✅ 已修复 |
| B3 | `infoServer.py` | Text 控件取值带 `\n` 导致数据污染 | ✅ 已修复 |
| B4 | `gui_DA.py` | `delete_server` 操作顺序颠倒，删除后列表不更新 | ✅ 已修复 |
| B5 | `gui_DA.py` | `delete_group` 先删服务器再删分组，导致孤儿数据 | ✅ 已修复 |
| B6 | `infoServer.py` | `delete_group` 未刷新分组树 | ✅ 已修复 |
| B7 | `infoServer.py` | SSH 连接 `password` 取值错误（`values[5]` 应为 `get_server_password`） | ✅ 已修复 |
| B8 | `infoServer.py` | 编辑下拉框无"主机地址"选项，`host` 字段无法修改 | ✅ 已修复 |
| B9 | `infoServer.py` | 分组编辑分支 `conten_entry.config(textvariable=...)` 对 `tk.Text` 无效，抛出 `TclError` | ✅ 已修复 |
| B10 | `infoServer.py` | `finally` 块无条件关闭窗口，导致提示弹窗后立即消失 | ✅ 已修复 |
| B11 | `infoServer.py` | 编辑"分组"分支 `select_group_id` 可能为 `None`，导致 `TypeError` | ✅ 已修复 |
| B12 | `gui_DA.py` | 多处 `cursor.close()` 后再访问 `cursor.lastrowid` / `cursor.rowcount` | ✅ 已修复 |
| B13 | `gui_DA.py` | `exists` 方法使用 f-string 拼接表名（SQL 注入风险） | ✅ 已修复 |
| B14/B15 | `gui_DA.py` | `init_groups_data` 的 `finally` 块引用未定义的 `cursor`/`conn` | ✅ 已修复 |
| B16 | `infoServer.py` | RDP 分支 `port` 类型不一致（字符串 vs 整数） | ✅ 已修复 |
| B17 | `infoServer.py` | `search_servers` 先清空列表再搜索，搜索失败时列表空白 | ✅ 已修复 |
| B18 | `infoServer.py:23` | `tk.PhotoImage(file='./img/top.png')` 使用相对路径，若工作目录不在项目根目录则找不到图片 | ✅ 已修复：改用 `os.path.dirname(os.path.abspath(__file__))` 构造绝对路径 |
| B19 | `infoServer.py:24` | `DataAccess(os.path.join(os.getcwd(), 'data.db'))` 依赖 `os.getcwd()`，若从其他目录启动则数据库位置不可控 | ✅ 已修复：改用项目根目录绝对路径 |
| B20 | `infoServer.py:72, 80, 84` | `pack_propagate(1)` 注释说"禁止为1"，但实际 `1=True` 表示**允许**内部控件影响外层大小，注释与代码相反 | ✅ 已修复：修正注释说明 |
| B21 | `infoServer.py:106-107` | 搜索按钮被注释掉（`top_frame_button_6`），但搜索功能通过右上角搜索框实现，存在冗余注释代码 | ✅ 已修复：添加注释说明保留原因 |
| B22 | `tool.py:27` | `t.setDaemon(True)` 在 Python 3.10 中已弃用，应改用 `t.daemon = True` | ✅ 已修复：改为属性赋值 |
| B23 | `tool.py:63-64` | `is_ip` 方法内部 `import re` 和 `from tools.logs import logs` 每次调用都重新导入，应移到模块顶部 | ✅ 已修复：移到模块顶部 |
| B24 | `tool.py:68, 71` | `is_ip` 将"格式正确"记为 ERROR、"格式错误"记为 INFO，日志级别使用不当 | ✅ 已修复：格式正确用 INFO，格式错误用 ERROR |
| B25 | `logs.py:13-16` | `__init__` 中 `self.day` 在 `if` 分支（目录不存在）内赋值后创建文件，但 `else` 分支重复赋值并写入"DEBUG 日志文件存在"，导致每次实例化都写入调试行 | ✅ 已修复：简化初始化逻辑，移除调试行 |
| B26 | `logs.py` 全文 | 每次写日志都 `open` → `write` → `close`，高频写时性能差，且未使用 `with` 语句，异常时文件不关闭 | ✅ 已修复：使用 `with` 语句管理文件 |
| B27 | `gui_DA.py:41, 100, 146, 151` | 多处 `print()` 调试输出未清理，生产环境应移除或改为日志 | ✅ 已修复：移除所有 print() 调试输出 |
| B28 | `infoServer.py:635, 783, 788, 792, 797, 878, 884` | 多处 `print()` 调试输出未清理 | ✅ 已修复：移除所有 print() 调试输出 |
| B29 | `infoServer.py:20` | 窗口标题写死 `V1.0.20250124 Demo公测版`，版本号应从 `version.txt` 或配置读取 | ✅ 已修复：从 version.txt 动态读取版本号 |
| B30 | `infoServer.py:137` | `server_tree.heading('ip', text='域名')` 列名为 `ip` 但显示为"域名"，命名不一致 | ✅ 已修复：改为"IP地址" |
| B31 | `tool.py:10` + `logs.py:2` | `tool.py` 导入 `logs`，`logs.py` 导入 `too`，形成循环依赖，导致模块初始化失败 | ✅ 已修复：使用延迟导入，在函数内部导入依赖模块 |
| B32 | `infoServer.py:1079, 1092` | `tree_right_click` 和 `Stree_right_click` 调用 `import_group` 和 `import_server`，但这两个方法未定义 | ✅ 已修复：实现 `import_group`、`export_group`、`import_server`、`export_server` 方法 |
| B33 | `infoServer.py:1092-1096` | 服务器树右键菜单中"导入服务器"和"导出服务器"菜单项重复 | ✅ 已修复：删除重复的菜单项 |
| B34 | `infoServer.py:167` | 服务器树类型图标列表头的默认宽度（50px）与类型表头宽度不一致 | ✅ 已修复：统一为50px |
| B35 | `infoServer.py:156` | 服务器树缺少"状态"列，无法显示服务器连通性状态 | ✅ 已修复：在表头最后添加"状态"列，并更新所有插入代码 |
| B36 | `infoServer.py:500` | 系统设置窗口宽度不足（520px），工具路径和浏览按钮显示不完整 | ✅ 已修复：调整窗口宽度为600px |
| B37 | `infoServer.py:500` | 系统设置窗口宽度仍不足（600px），工具路径和浏览按钮显示不完整 | ✅ 已修复：调整窗口宽度为1200px |
| B38 | `infoServer.py:433` | 系统设置窗口保存设置后自动关闭，用户体验不佳 | ✅ 已修复：保存设置后不自动关闭窗口 |
| B39 | `tool.py:149` | SSH/VNC连接时报 AttributeError: 'too' object has no attribute 'db_path' | ✅ 已修复：为too类添加db_path属性，并在infoServer中传递 |
| B40 | `infoServer.py:507, 1360` | top_master硬编码宽度250且设置窗口误传1200作高度，geometry被覆盖为250x1200（又窄又高） | ✅ 已修复：top_master增加可选width参数，设置窗口固定为1000x700 |
| B41 | `tool.py:23` | thread_it 不支持关键字参数，SSH连接时 shell=True 报 TypeError | ✅ 已修复：签名增加 **kwargs 并透传给 Thread |
| B42 | `tool.py:150, 154-167` | run_ssh 工具类型判断值（'xterm'/'plink'等小写）与设置窗口保存的下拉框值（'XTerminal'/'PuTTY(plink)'等）不一致，导致任何选择都落入 else 分支执行 plink 报错 | ✅ 已修复：统一类型值映射，使用各工具独立路径，兼容旧版小写值；XTerminal 官方不支持命令行传参，回退系统 OpenSSH |
| B43 | `infoServer.py:441` | restore_defaults 默认 ssh_tool_type 存 'xterm'，与表单刷新值 'XTerminal' 不一致 | ✅ 已修复：统一为 'XTerminal' |
| B44 | `infoServer.py:441` | 设置窗口宽度 500px 仍偏宽，需缩小 100px | ✅ 已修复：改为 400px |
| B45 | `infoServer.py:363-397` | font_color、info_bg_color、search_bg_color 设置后未生效 | ✅ 已修复：apply_settings 增加三参数并实际应用到 Treeview/说明区/搜索框 |
| B46 | `tool.py:183-184` | XTerminal SSH 连接回退到系统 ssh 命令而非使用配置路径 | ✅ 已修复：XTerminal 使用配置路径直接启动，传入 ssh:// URL |
| B47 | `tool.py:148-186` | SSH 连接逻辑含不必要的超时判断，用户要求直接打开工具 | ✅ 已确认：run_ssh 本身无超时逻辑，保持直接打开 |
| B48 | `infoServer.py:393` | 搜索框背景色设置无效果 | ✅ 已修复：使用双重设置（config+configure）并强制刷新 |
| B49 | `tool.py:148-186` | SSH/VNC 连接失败时前端无提示 | ✅ 已修复：增加 callback 参数，在前端显示错误信息 |
| B50 | `infoServer.py:1310-1350` | 连接主机前缺少确认弹框 | ✅ 已修复：为 SSH/VNC/Radmin 连接添加确认弹框（RDP/URL 由 B59 补齐） |
| B51 | `tool.py:169-210` | SSH/VNC 连接启动失败时错误信息不友好 | ✅ 已修复：添加工具文件存在性检查，提供详细错误提示和解决方案 |
| B52 | `infoServer.py:edit_server` | 编辑主机时通过主机名查询数据库获取数据，存在同名主机时始终取到第一条记录，应获取实际选中的主机 | ✅ 已修复：直接从服务器树读取选中行数据，新增 `get_server_password_by_host` 按主机地址查询密码 |
| B53 | `infoServer.py:edit_server` | 编辑主机修改主机名时 `new_value` 在定义前被使用（`NameError` 被 except 吞掉），导致修改无法生效 | ✅ 已修复：重构为统一字段映射表，先读取输入值再校验，消除未定义引用 |
| B54 | `infoServer.py:edit_server` | 修改主机地址为纯数字（如 123）后，Treeview 将值自动转为 int，再次编辑时字符串拼接报 `TypeError: can only concatenate str (not "int") to str` | ✅ 已修复：树中取值统一 `str()` 转换 |
| B55 | `infoServer.py:groupTree_release/Stree_release` | 中键释放焦点偶发失效：仅监听 `Button-2` 且立即清除，被树控件内部选中逻辑覆盖 | ✅ 已修复：同时绑定 `Button-2`/`ButtonRelease-2`，`after(50)` 延迟清除 |
| B56 | `infoServer.py:_save_group_state` | 分组展开状态保存时调用了不存在的 `_save_child_state_by_group` 方法（异常被静默吞掉），且 JSON 键 int/str 类型不匹配导致恢复失败，第 2 级以下节点状态丢失 | ✅ 已修复：重写为 Treeview 层级递归遍历，统一字符串键，异常写入错误日志 |
| B57 | `infoServer.py:on_group_selection_change` | 仅当分组下有主机时才刷新服务器树，选中空分组时列表残留上一分组的内容 | ✅ 已修复：无条件清空并刷新，空分组显示空表格 |
| B58 | `infoServer.py:apply_settings` | 对 ttk.Treeview 使用 `configure(font=...)`，ttk 组件不支持 `-font` 选项，启动报 `unknown option "-font"`，且中断后续颜色设置 | ✅ 已修复：删除无效配置，字体经 `ttk.Style` 设置 |
| B59 | `infoServer.py:connect_server` | RDP/URL 类型连接无二次确认弹框（SSH/VNC/Radmin 已有） | ✅ 已修复：补齐确认弹框，五种连接类型齐全 |
| B60 | `tool.py:run_mstsc` | cmdkey 凭据目标格式错误（`TerminalServer:ip:port` 非法），且 shell=True 拼接命令时密码特殊字符被解析，报"添加凭据失败" | ✅ 已修复：改用 `TERMSRV/ip` 标准格式，列表形式传参，只写一条凭据 |
| B61 | `tool.py:run_mstsc` | RDP 连接在主线程执行 `subprocess.call`，双击连接时界面卡死 | ✅ 已修复：整体放入 `thread_it` 后台线程执行 |
| F3 | `infoServer.py:820-847` | Radmin 连接类型无对应分支 | ✅ 已修复：添加 run_radmin 方法并在 connect_server 中添加 Radmin 分支 |
| S1 | `infoServer.py:935` | 密码明文存储及日志泄露 | ✅ 已修复：对密码进行脱敏处理，避免日志中明文记录密码 |
| S2 | `infoServer.py:945` | 密码修改操作明文记录密码 | ✅ 已修复：对修改后的密码进行脱敏处理 |
| S4 | `infoServer.py:935-945` | 多处密码明文记录 | ✅ 已修复：对所有密码日志记录进行脱敏处理 |

---

## 二、已知未修复问题

### 🔴 严重 Bug

> 暂无

### 🟡 中等 Bug

> 暂无

### 🟢 轻微 Bug

> 暂无

---

## 三、未实现功能

| # | 功能 | 位置 | 现状 |
|---|------|------|------|
| F1 | ~~SSH 连接~~ | `infoServer.py:827-835` / `tool.py:run_ssh` | ✅ **已实现** — 双击或右键 SSH 连接自动调用终端工具，支持 XTerminal、PuTTY、MobaXterm、FinalShell、Xshell |
| F2 | ~~VNC 连接~~ | `infoServer.py:836-841` / `tool.py:run_vnc` | ✅ **已实现** — 双击或右键 VNC 连接自动调用 vncviewer |
| F3 | Radmin 连接 | `infoServer.py:820-847` | ✅ **已实现** — 已添加 Radmin 连接分支 |
| F4 | 重命名分组 | `infoServer.py:647-655` | ❌ 仅判断是否选中分组，未实现实际重命名逻辑（`update_group` 方法在 DA 层已存在但未被调用） |
| F5 | 导入分组 | `infoServer.py:612` | ✅ **已实现** — 右键菜单"导入分组"已绑定 `import_group` 方法，支持从JSON文件导入分组数据 |
| F6 | 导出分组 | `infoServer.py:613` | ✅ **已实现** — 右键菜单"导出分组"已绑定 `export_group` 方法，支持将分组数据导出为JSON文件 |
| F7 | ~~编辑主机地址~~ | `infoServer.py:452` | ✅ **已修复**（B8）— 编辑下拉框已包含"主机地址"选项 |
| F8 | 编辑主机类型（conn_type） | `infoServer.py:452` | ❌ 编辑下拉框无"主机类型"选项，无法修改 conn_type 字段 |
| F9 | 批量添加主机 | README 声称支持 | ❌ 代码中无批量添加功能 |
| F10 | 导入导出 | README 声称支持 | ✅ **已实现** — 分组和服务器均支持JSON格式的导入导出功能 |
| F11 | 密码加密存储 | 全局 | ❌ 密码以明文存储在 `data.db` 中，无任何加密 |
| F12 | 窗口位置记忆 | 全局 | ❌ 窗口大小/位置不持久化，每次启动重置 |
| F13 | ESC 关闭弹窗 | `infoServer.py:50-51` | ❌ ESC 事件绑定被注释掉 |
| F14 | 分组双击查看主机 | `infoServer.py:184, 692-708` | ❌ `groupTree_click` 被注释，双击分组无反应（改为 `<<TreeviewSelect>>` 单击触发） |
| F15 | RDP 凭据异常残留清理 | `tool.py:run_mstsc` | ⚠️ 程序被强杀（断电/任务管理器结束进程）时，`finally` 不执行，凭据 `TERMSRV/ip` 可能残留在凭据管理器中；可手动 `cmdkey /delete:TERMSRV/ip` 清除（正常关闭远程桌面后均会自动清除） |

---

## 四、本次新增功能（2.1.20260825）

### 1. RDP 连接重构 —— Windows 凭据管理器方式
- 点击连接 RDP 主机：cmdkey 写入凭据（TERMSRV/ip）→ 执行 `mstsc /v ip:port` 一键登录 → 远程桌面关闭后自动删除凭据
- 列表形式传参，密码含 `&`/`|`/`<`/`>` 等特殊字符不再出错
- 后台线程执行，连接期间界面不卡死
- 不再生成含明文密码的 temp.rdp 临时文件（解决 S2/S5）

### 2. 编辑主机功能增强
- 新增输入校验：主机名非空+查重、主机地址非空+查重、端口号必须为数字、修改分组须先选中分组
- 未选中主机时提示"请先选中要修改的主机"
- 编辑成功后先更新 SQLite 再刷新服务器树
- 6 个重复 elif 分支重构为统一字段映射表（部分解决 Q4）

### 3. 鼠标中键释放焦点
- 分组树/服务器树范围内点击中键即取消当前选中并释放焦点
- 同时监听按下/释放事件，延迟 50ms 清除，确保不被树控件内部逻辑覆盖

### 4. 连接确认弹框补全
- RDP、URL 类型补齐二次确认弹框，五种连接类型（RDP/SSH/VNC/Radmin/URL）齐全

### 5. 分组展开状态全层级持久化
- 按 Treeview 层级递归遍历保存/恢复，任意深度的分组节点状态均可记录
- 统一字符串键，规避 JSON 序列化 int/str 类型不一致问题

### 6. 界面设置实时生效
- 服务器说明（Text）、搜索框（Entry）背景色保存后立即应用
- 组件创建时直接从 settings 表读取已存颜色值
- "恢复默认"后界面立即刷新；两个组件默认背景色改为白色

### 7. 分组树图标更换
- 折叠状态：`img/folder_badge_plus.png`（24x24）
- 展开状态：`img/folder.png`（24x24）
- 根节点/子节点统一样式，保留 > 箭头指示（关闭向右/打开向下）

---

## 五、代码兼容性问题（Python 3.10.11 升级相关）

| # | 位置 | 问题 | 建议 |
|---|------|------|------|
| C1 | `tool.py:27` | `t.setDaemon(True)` 在 Python 3.10 已弃用，3.12 将移除 | 改为 `t.daemon = True` |
| C2 | `tool.py:63` | `import re` 在方法内部，Python 3.10 虽支持但不符合 PEP 8 | 移到模块顶部 |
| C3 | `infoServer.py:72, 80, 84` | `pack_propagate(1)` 中 `1` 作为布尔值 | 改为 `pack_propagate(True)` 更清晰 |
| C4 | `infoServer.py:282, 449, 491` | `resizable(0, 0)` 中 `0` 作为布尔值 | 改为 `resizable(False, False)` |
| C5 | `gui_DA.py:26` | `port int` 应为 `port INTEGER` | SQL 语法虽兼容但不规范 |
| C6 | `infoServer.py:5` | `from Object.gui_DA import *` 通配符导入 | 建议改为 `from Object.gui_DA import DataAccess` |
| C7 | 全局 | 相对路径 `./img/xxx.png` 依赖工作目录 | 建议使用 `os.path.dirname(__file__)` 构造绝对路径 |
| C8 | `version.txt` | 版本信息仍为 `1.0.20240906`，与代码标题 `1.0.20250124` 不一致 | 同步更新 version.txt |

---

## 六、代码质量问题

| # | 类别 | 问题描述 |
|---|------|----------|
| Q1 | 命名 | `too` 类名应为 `Tool`（类名应大写） |
| Q2 | 命名 | `infoServer` 类名应为 `InfoServer`（类名应大写） |
| Q3 | 命名 | `edit_da`、`add_server`（内部函数）命名风格不统一 |
| Q4 | 重复代码 | ~~`edit_da` 中 6 个 `elif` 分支结构几乎相同~~ ✅ **已重构**（2.1 版）：统一为字段映射表 + 单一更新/刷新流程；`gui_DA.py` 各方法仍存在重复的连接管理模式 |
| Q5 | 重复代码 | `gui_DA.py` 每个方法都重复 `sqlite3.connect` → `cursor` → `execute` → `close` 模式，应提取上下文管理器 |
| Q6 | 异常处理 | 多处 `except Exception as e` 过于宽泛，吞掉所有异常（注：2.1 版分组状态保存/恢复已改为写错误日志而非静默） |
| Q7 | 资源管理 | `gui_DA.py` 未使用 `with` 语句管理数据库连接，异常时连接不关闭 |
| Q8 | 调试代码 | ~~`infoServer.py` 和 `gui_DA.py` 中大量 `print()` 未清理~~ ✅ **已清理**（B27/B28） |
| Q9 | 注释 | `pack_propagate` 注释与代码行为相反（见 B20，已修复） |
| Q10 | 死代码 | `infoServer.py:692-708` `groupTree_click` 整个方法被注释 |
| Q11 | 死代码 | `Object/testInfoserver.py` 是早期原型，未接入主程序，应归档或删除 |
| Q12 | 死代码 | `Object/gui_DA -20240905.py` 是旧版备份，应使用 git 管理而非保留文件副本 |
| Q13 | 类型安全 | ~~`server_tree.item(...)['values'][1]` 取值后未做类型转换~~ ✅ **已修复**（B54）：树中取值统一 `str()` 转换 |

---

## 七、安全风险

| # | 风险 | 说明 | 状态 |
|---|------|------|------|
| S1 | 密码明文存储 | `servers.password` 明文存入 sqlite | ⚠️ 未解决（日志已脱敏）。建议使用 `cryptography` 库加密，或至少使用 base64 + 盐值混淆 |
| S2 | ~~RDP 文件含明文密码~~ | ~~`tool.py:86` 将密码明文写入 `temp.rdp`~~ | ✅ **已解决**（2.1 版）：RDP 改用 Windows 凭据管理器，不再生成临时文件 |
| S3 | SQL 注入 | `gui_DA.py:110` 表名通过 f-string 拼接 | ⚠️ 已加白名单校验（B13），建议进一步参数化 |
| S4 | ~~日志泄露敏感信息~~ | ~~`infoServer.py` 日志中记录用户名和密码~~ | ✅ **已解决**：日志中密码已脱敏（S1/S2/S4） |
| S5 | ~~临时文件竞态~~ | ~~`tool.py:80` `temp.rdp` 写在固定路径，多实例并发时互相覆盖~~ | ✅ **已解决**（2.1 版）：不再使用临时文件 |
| S6 | RDP 凭据残留 | 程序被强杀时 `finally` 不执行，`TERMSRV/ip` 凭据可能残留在系统凭据管理器 | ⚠️ 低风险：正常关闭远程桌面均会自动清除；可启动时主动扫描清理残留凭据（待规划） |

---

## 八、优先修复建议

### P0（立即修复，影响基本功能）
1. **S1**：密码明文存储（唯一剩余的 P0 级安全风险；日志脱敏和临时文件问题已解决）

### P1（近期修复，影响体验）
2. **F4**：重命名分组功能补全
3. **F8**：编辑下拉框补充"主机类型"选项
4. **F15/S6**：RDP 凭据残留扫描清理（程序启动时检查并清理孤儿凭据）
5. **F12**：窗口位置记忆

### P2（中期优化）
6. **Q5**：重复代码抽象（数据库连接上下文管理器）
7. **Q7**：数据库连接改用 `with` 上下文管理器
8. **C7**：相对路径改绝对路径
9. **F9**：批量添加主机
10. **F11**：密码加密存储

---

*本文档随项目迭代持续更新。*
