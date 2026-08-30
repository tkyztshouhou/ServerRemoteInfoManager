# 已知问题与待解决事项

> 本文档记录项目当前已知问题、功能实现状态与代码质量问题，供迭代参考。

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
| B62 | `infoServer.py:run_mstsc` | RDP 连接复用历史残留凭据（TERMSRV/ip），旧密码与当前主机密码不一致时登录失败且难以排查 | ✅ 已修复（2.2 版）：连接前先 `cmdkey /delete:TERMSRV/ip` 清理本次主机相关旧凭据 |
| B63 | `infoServer.py:服务器树` | 密码列直接明文展示，界面共享/截屏场景泄露密码 | ✅ 已修复（2.2 版）：默认显示 `*********`，右键菜单"显示密码"按需查看当前行明文 |
| B64 | `infoServer.py:右侧功能区` | 远程桌面高级选项内容高度超出可用区域，出现轻微上下滚动 | ✅ 已修复：右侧改为上下结构（Ping+FAQ 同容器左右排列），高级选项区占满剩余高度，不再滚动 |
| B65 | `infoServer.py:版本读取` | version.txt 为 UTF-8 编码的 VSVersionInfo 多行格式（含 © 字符），代码用默认 GBK 打开抛 `UnicodeDecodeError` 被 except 吞掉，窗口标题长期回退 fallback 旧版本号 | ✅ 已修复（2.2 版）：UTF-8 编码打开并用正则提取 `FileVersion` 字段，fallback 更新为 V2.2.20260825 |
| B66 | `infoServer.py` | 顶部未 `import re`，`save_rdp_settings` 自定义分辨率校验 `re.match` 时抛 `NameError`（被 except 捕获提示"保存设置失败"），自定义分辨率无法保存 | ✅ 已修复（2.2 版）：顶部补充 `import re` |
| B67 | `tool.py:run_mstsc` | 连接 RDP 时连续 `cmdkey` 调用（清理/写入/删除）弹出黑色命令行窗口并闪烁：程序以 GUI 方式打包（`console=False`），父进程无控制台，Windows 会为 `cmdkey.exe` 等控制台子系统程序自动新建控制台 | ✅ 已修复：新增 `_hidden_console_kwargs()`，为 Windows 下**控制台**子进程（`cmdkey` 及 `shell=True` 拉起 cmd 的场景）附加 `CREATE_NO_WINDOW` + `STARTF_USESHOWWINDOW(SW_HIDE)`；**注意**：`SW_HIDE` 仅适用于控制台程序，GUI 程序（如 `mstsc`）误用会隐藏其主窗口（见 **B68**）；PuTTY(plink) 为控制台程序，保持窗口可见 |
| B68 | `tool.py:_run_mstsc_with_credential` | **B67 回归**：`_hidden_console_kwargs()`（含 `STARTUPINFO.wShowWindow=SW_HIDE`）被错误应用到 `mstsc.exe`（GUI 程序），导致点击 RDP 连接后远程桌面窗口被整体隐藏、看似「打不开」 | ✅ 已修复（4.1.20260830）：启动 `mstsc` 时移除隐藏参数（`subprocess.call(['mstsc', tmp_rdp])`），仅保留 `cmdkey` 的隐藏参数，凭据清理/写入不再黑框闪烁，且远程桌面窗口正常显示 |
| B69 | `gui_DA.py:set_setting` | **S1 加密重构回归**：`set_setting(key, value)` 内部 SQL 参数误写为未定义的 `stored`（`NameError`），导致所有「远程桌面高级选项」保存（启用剪贴板/全屏/映射驱动器/分辨率等）报错「保存设置失败: name 'stored' is not defined」 | ✅ 已修复（4.1.20260830）：将参数名改回 `value`，与 `add_server` 中 `stored_password` 的命名误用脱钩 |
| B70 | `infoServer.py:export_group / export_server` | **S1 加密重构回归**：`export_server` 改写时直接 `sqlite3.connect(self.db.db)` 但文件顶部未 `import sqlite3`，导致「导出分组」「导出服务器」均报错「name 'sqlite3' is not defined」 | ✅ 已修复（4.2.20260830）：在 `Object/infoServer.py` 顶部补充 `import sqlite3` |
| B71 | `infoServer.py:import_server` | **import/export 功能回归**：`import_server` 导入成功后刷新服务器树时误调用 `self.init_servers_data()`（该方法不存在，UI 层方法名为 `init_server_data`），报错 `InfoServer object has no attribute 'init_servers_data'` | ✅ 已修复（4.3.20260830）：改回正确的 `self.init_server_data()` |
| B72 | `tool.py:_run_vnc_with_radmin` / `_run_vnc_viewer` | **B67 同类回归**：B67 修复 mstsc 时只改了 `run_mstsc`，但 `vncviewer` 与 `radmin.exe` 同为 GUI 程序，仍被 `_hidden_console_kwargs()`（SW_HIDE）隐藏，连接后窗口不出现 | ✅ 已修复（4.4.20260830）：移除两者的隐藏参数，仅 `cmdkey`/SSH-`cmd` 等控制台程序保留隐藏 |
| B73 | `infoServer.py:export_server` / `import_server` | **数据损坏隐患（初版修复方向有误）**：初版改为「导出保留密文」仅适合同机同用户，跨机器/跨用户导入会解密失败导致密码置空 | ⚠️ 4.4 初版方案不适用跨机器；**4.5 修正为导出明文 + 导入重新加密**（见 **B76**） |
| B74 | `tools/logs.py` / `gui_DA.py:25` | **安装到 Program Files 后启动崩溃**：`logs()` 在多处未传入 `user_data_dir`（`app.py`、`gui_DA.DataAccess`、`tool.py`、`opsbrain/da.py`、`faq/ui.py`），回退到 `程序目录/../logs`，只读目录写入触发 `PermissionError: [WinError 5] 拒绝访问`；`DataAccess.__init__` 同样 `logs()` 无目录 | ✅ 已修复（4.5.20260830）：`logs()` 未传 `user_data_dir` 时默认回退到 `%LOCALAPPDATA%/ServerRemoteInfoManager/logs`，彻底避开 Program Files 只读目录 |
| B75 | `infoServer.py:export_group` | **分组导出缺少 id**：仅导出 `name`/`parent_id`，导入时重新分配 id，导致 `server.parent_id` 指向错乱 | ✅ 已修复（4.5.20260830）：导出保留 `id` 与 `parent_id`，导入时按 id 重建父子关系 |
| B76 | `infoServer.py:export_server` | **跨机器迁移密码丢失**：B73 初版导出密文，换机器/换用户后 DPAPI/Fernet 无法解密、密码置空 | ✅ 已修复（4.5.20260830）：`export_server` 解密为明文写入 JSON（保留安全确认弹窗），`import_server` 经 `add_server` 在目标机重新加密，跨机器/跨用户迁移正常 |
| B77 | `infoServer.py:import_group` / `import_server` | **导入 id 漂移**：分组表/服务器表使用 `AUTOINCREMENT`，导入时按导出 id 显式插入却未重置 `sqlite_sequence`，导致新序列与现有 max id 冲突（如导出 id=4 但当前序列已到 6，导入后新增分组拿到 id=6 与导出错乱、server.parent_id 指向错误） | ✅ 已修复（4.6.20260830）：新增 `import_group_replace` / `import_server_replace`，导入前 `DELETE` 全表并 `DELETE FROM sqlite_sequence WHERE name=...` 重置自增序列，再严格按导出 id 恢复，后续自动新增 id 紧接其后无漂移 |
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

## 三、功能清单与实现状态

> **2026-08-30 全量核实**：本节原"未实现功能"清单已逐项对照当前代码复核——F1~F8、F10~F13、F15、F16 **全部已实现**；F9、F14 经评估确定**无需开发**，已从列表移入下方「已关闭（无需开发）」小节。当前**未实现功能列表为空**，故本节更名为"功能清单与实现状态"。

| # | 功能 | 位置 | 状态 | 核实说明（2026-08-30） |
|---|------|------|------|------------------------|
| F1 | SSH 连接 | `tool.py:run_ssh` / `infoServer.py:connect_server` | ✅ **已完成** | `connect_server` 的 SSH 分支读取用户名密码后调用 `Tool.run_ssh`，支持 XTerminal / PuTTY(plink) / MobaXterm / FinalShell / Xshell 五种工具与独立路径配置 |
| F2 | VNC 连接 | `tool.py:run_vnc` / `infoServer.py:1884` | ✅ **已完成** | `connect_server` 的 VNC 分支调用 `Tool.run_vnc(host, port, callback=...)`，启动 vncviewer 并在失败时回调弹窗提示 |
| F3 | Radmin 连接 | `tool.py:run_radmin` / `infoServer.py:1909` | ✅ **已完成** | `connect_server` 的 Radmin 分支调用 `Tool.run_radmin`，命令为 `radmin.exe /connect:host:port` |
| F4 | 重命名分组 | `infoServer.py:1636 rename_group` | ✅ **已完成** | 原记录为 ❌（仅判断选中、未调 `update_group`），现已核实：分组右键菜单"重命名分组"（`infoServer.py:1566`）绑定 `rename_group`，方法内弹出重命名对话框并调用 `db.update_group(group_id, new_name)`（`infoServer.py:1677`）后刷新分组树，功能完整可用 |
| F5 | 导入分组 | `infoServer.py:1695 import_group` | ✅ **已完成** | 分组右键菜单"导入分组"（`1568`）绑定 `import_group`，从 JSON 文件导入分组数据并刷新分组树 |
| F6 | 导出分组 | `infoServer.py:1722 export_group` | ✅ **已完成** | 分组右键菜单"导出分组"（`1569`）绑定 `export_group`，将分组数据导出为 JSON 文件 |
| F7 | 编辑主机地址 | `infoServer.py:1291 字段映射表` | ✅ **已完成** | 编辑弹窗字段映射表含 `'主机地址': 'host'`（B8 修复），并带非空校验与地址查重 |
| F8 | 编辑主机类型（conn_type） | `infoServer.py:1292 字段映射表` | ✅ **已完成** | 原记录为 ❌（下拉框无该选项），现已核实：字段映射表含 `'主机类型': 'conn_type'`，编辑弹窗可直接修改；另有服务器右键"修改主机类型"入口调用 `db.update_server('conn_type', ...)`（`infoServer.py:1390`） |
| F10 | 导入导出 | `infoServer.py:1695/1722/1750/1786` | ✅ **已完成** | 分组与服务器各有一对导入/导出：`import_group`/`export_group`、`import_server`/`export_server`，均为 JSON 格式；服务器导出前含明文密码风险确认，导入时密码自动加密 |
| F11 | 密码加密存储 | `tools/secret.py` / `Object/gui_DA.py` | ✅ **已完成** | 新增 `tools/secret.py`：Windows 走系统 DPAPI，其余环境回退 Fernet；`servers.password` 与 `settings.default_password` 加密入库，首次启动自动迁移历史明文（详见「七（续）」S1） |
| F12 | 窗口位置记忆 | `infoServer.py:113/131 _save/_load_window_state` | ✅ **已完成** | 原记录为 ❌（不持久化），现已核实：`_save_window_state` 解析 geometry 并写入 settings（`last_window_x/y/width/height`），`_load_window_state` 启动时 `geometry()` 恢复；由 `WM_DELETE_WINDOW` → `_on_close`（`infoServer.py:144`）触发保存，持久化链路完整 |
| F13 | ESC 关闭弹窗 | `infoServer.py:102/1692`、`faq/ui.py:150/493` | ✅ **已完成** | 主窗口 `bind('<Escape>')` → `_close_top_window` 销毁所有 Toplevel；添加/编辑弹窗自身也绑定 ESC；FAQ 窗口及其新增/修改条目对话框同样绑定 ESC |
| F15 | RDP 凭据异常残留清理 | `tools/tool.py:cleanup_rdp_credentials / cleanup_temp_rdp_files` | ✅ **已完成** | 启动时扫描清理孤儿 TERMSRV 凭据（开关 `rdp_cred_cleanup`，默认开启）+ 清理超过 1 小时的残留 `mstsc_*.rdp`；连接前清理（B62）保留为第二道防线（详见「七（续）」S6） |
| F16 | FAQ 知识库功能 | `infoServer.py:2152 show_faq` / `faq/` 包 | ✅ **已完成** | 主界面 FAQ 按钮绑定 `show_faq`（`infoServer.py:348/353`，图片缺失时降级文字按钮）；`faq/` 包按 da / server / ui / main / sample_data 分层，独立库 `faq.db`；树形分类导航 + 关键词检索 + Markdown 渲染（缺 tkhtmlview 时降级纯文本）+ text/sql/doc 三种内容预览 |
| F17 | 运维智脑（AI 聊天） | `opsbrain/` 包 / `infoServer.py:show_ops_brain` | ✅ **已完成**（2026-08-30） | 主界面 Ping 按钮下方新增「运维智脑」按钮（`infoServer.py` 新增 `opsbrain_btn_container` + `show_ops_brain`）；新建 `opsbrain/` 包分层实现（da 数据层 / service 功能层 / ui 界面层 / mdrender Markdown 渲染 / token 长度控制）；支持多模型配置（模型列表增删改、排序、密钥落库加密+界面遮蔽）、会话持久化（独立 `aichat.db`）、Markdown 渲染与代码块复制/另存、思考过程折叠、输入长度加权截断、流式/非流式双通道与停止生成（详见下方「九、运维智脑（F17）实现说明」） |
| F19 | 运维智脑对话窗口滚动 | `opsbrain/ui.py` | ✅ **已完成**（2026-08-31） | 原对话窗口无滚动条且鼠标滚轮在消息区域失效，历史消息无法回看。4.0.20260831 在消息区右侧新增 `ttk.Scrollbar`（与 Canvas `yscrollcommand`/`yview` 双向绑定），并把 `<MouseWheel>` 同时绑定到 `msg_canvas`、`msg_inner` 以及每个 AI 回复 `tk.Text` 文本框（`add='+'` 转发），使滚轮在空白区和消息上均可正常翻页。注入 15 轮对话（30 条气泡，内容高度 2640px 超出视口）验证滚动条出现且可正常上下滚动。改动仅涉及 `opsbrain/ui.py` |
| F20 | 运维智脑多轮上下文记忆 | `opsbrain/service.py` | ✅ **已完成**（2026-08-31） | 经核查，**多轮上下文记忆功能已正确实现**：`ChatService.send()` 每次请求通过 `chat_dao.list_messages(session_id)` 读取完整会话历史，作为 `api_messages`（system + 全部历史 + 当前输入）发送给模型；`truncate_context` 仅在超出 token 预算时裁剪，且始终保留 system 提示与最近消息，多轮交互连贯性不受影响。非流式与流式（SSE）两条路径均携带历史，无需改动 |

### 已关闭（评估后确定无需开发）

| # | 功能 | 结论 | 关闭理由 |
|---|------|------|----------|
| F9 | 批量添加主机 | ⛔ **无需开发** | 经评估不纳入开发计划：批量录入已有等价且更安全的替代路径——服务器右键「导入服务器」支持 JSON 批量导入（`import_server`，`infoServer.py:1750`），可一次性导入任意数量主机，且支持"导出 JSON → 编辑 → 导入"的批量编辑流程。再单独做一套批量录入 UI 属于重复建设，且需重复实现现有的主机名/地址查重、端口校验、密码加密等逻辑，维护成本高。另：原清单备注的「README 声称支持」已不成立——当前 README 仅描述 Ping 批量检测与 JSON 导入导出，并未承诺批量录入 UI，无文档与实现不一致问题。如后续确有高频逐条录入需求，再评估在添加主机弹窗内增加"连续添加"模式。 |
| F14 | 分组双击查看主机 | ⛔ **无需开发** | 经评估不纳入开发计划：分组查看主机的交互已由**单击**承担——`group_tree` 绑定 `<<TreeviewSelect>>` → `on_group_selection_change`（`infoServer.py:378`）在单击时即刷新右侧服务器列表，比双击更符合直觉且少一次操作；原 `groupTree_click` 死代码已在 Q10 中删除。双击与单击指向同一行为，实现双击只会增加"双击时先触发一次单击"的事件冲突与冗余代码，无实际收益。 |

---

## 三（续）、3.0.20260827 对话框完善与界面美化（F16 收尾）

### 1. FAQ 新增/修改条目对话框修复与完善
- **布局 bug 修复**：原对话框用 `pack` 布局，内容区 `text_frame(side=TOP, expand=True)` 先 pack 且 `expand=True` 会一次性耗尽窗口全部空间，导致后 pack 的按钮区 `btn_frame(side=BOTTOM)` 仅分到 1px 高度（请求 33px），"保存/取消"按钮被压缩不可见。改为 **grid 布局**：内容区行 `grid_rowconfigure(5, weight=1)` 拉伸占满剩余空间，按钮行固定第 6 行 `sticky='ew'` 恒定高度，按钮始终可见（已通过真实 map 窗口测试：`btn_frame y=477 h=33`，`BUTTON_VISIBLE: True`）。
- **居中显示**：对话框尺寸 `560x520`，根据父窗口 `winfo_rootx/y/width/height` 计算中心偏移并 `geometry('+x+y')` 居中（原为默认左上角）。
- **保存/取消明确化**：保存成功后状态栏反馈"已保存修改/已新增条目：xxx"；绑定 `<Escape>` 到对话框关闭（放弃更改），绑定已验证注册生效。

### 2. 主窗口"保存设置"按钮美化（视觉突出 + 四态反馈）
- 配色：绿系主色 `#4CAF50`，悬停 `#43A047`、按下 `#388E3C` 明暗渐变；禁用浅绿 `#A5D6A7` + 灰字。
- 字体：`('Microsoft YaHei', 10, 'bold')` 加粗；内边距 `padx=20, pady=7`；左侧磁盘图标 `💾`；`cursor='hand2'` 手型光标。
- 四态反馈：`<Enter>/<Leave>/<ButtonPress-1>/<ButtonRelease-1>` 实时切换背景；禁用态下悬停/点击不改变颜色；新增 `set_rdp_save_enabled(bool)` 方法供外部切换禁用状态。
- 风格一致：保持 `relief='flat'`，未改变布局结构；与窗口其他 flat 按钮统一。

### 3. 版本号更新
- `version.txt`：`filevers`/`prodvers` 改为 `(3, 0, 2026, 827)`，`FileVersion`/`ProductVersion` 改为 `3.0.20260827`（程序窗口标题从此文件读取）
- `README.md` / `ISSUES.md`：版本号、发布文件名、版本历史表、GitHub Tag 同步为 `3.0.20260827`

### 4. 4.0.20260830 版本号更新（本轮）
- `version.txt`：`filevers`/`prodvers` 改为 `(4, 0, 2026, 830)`，`FileVersion`/`ProductVersion` 改为 `4.0.20260830`（程序窗口标题从此文件读取）
- `更新说明.txt`：新增「★ 4.0.20260830 更新」块（运维智脑 AI 聊天、密码加密存储、导出/日志明文修复、update_server 注入加固、RDP 凭据残留清理、RDP 连接黑框修复、运维智脑按钮美化对齐、连接参数窗口加宽一倍、移除显示密钥复选框），并在「不兼容改动」补充密码加密存储说明
- `README.md` / `ISSUES.md`：版本号、发布文件名、版本历史表、GitHub Tag 同步为 `4.0.20260830`；目录结构补充 `opsbrain/`、`tools/secret.py`
- 关联条目：RDP 连接黑框闪烁修复见 **B67**（子进程附加 `CREATE_NO_WINDOW` + `SW_HIDE`），密码加密见 **S1**、SQL 注入加固见 **S3**、RDP 凭据残留清理见 **S6**、运维智脑实现见 **F17**

### 5. 4.0.20260831 版本号更新（本轮）
- `version.txt`：`filevers`/`prodvers` 改为 `(4, 0, 2026, 831)`，`FileVersion`/`ProductVersion` 改为 `4.0.20260831`（程序窗口标题从此文件读取）
- `installer.iss`：`AppVersion` 与 `OutputBaseFilename` 同步为 `4.0.20260831`
- `build_release.ps1`：`$Version` 同步为 `4.0.20260831`
- `更新说明.txt`：新增「★ 4.0.20260831 更新」块（运维智脑对话窗口新增滚动条 + 修复滚轮翻页失效、上下文记忆核查确认已生效），顶部版本/日期更新
- `README.md` / `ISSUES.md`：版本号、发布文件名、版本历史表、GitHub Tag 同步为 `4.0.20260831`；运维智脑章节补充「多轮上下文记忆」「对话窗口可滚动」说明；功能清单新增 **F19**（对话窗口滚动修复）、**F20**（上下文记忆确认正常）
- 关联条目：运维智脑对话窗口滚动修复见 **F19**，多轮上下文记忆确认见 **F20**（均仅涉及 `opsbrain/ui.py` 与既有 `service.py`，无功能回归）

### 6. 4.1.20260830 版本号更新（本轮 hotfix）
- `version.txt`：`filevers`/`prodvers` 改为 `(4, 1, 2026, 830)`，`FileVersion`/`ProductVersion` 改为 `4.1.20260830`（程序窗口标题从此文件读取）
- `installer.iss`：`AppVersion` 与 `OutputBaseFilename` 同步为 `4.1.20260830`
- `build_release.ps1`：`$Version` 同步为 `4.1.20260830`
- `更新说明.txt`：新增「★ 4.1.20260830 更新」块（RDP 远程桌面窗口隐藏回归修复、远程桌面高级选项保存报错回归修复），顶部版本/日期更新
- `README.md` / `ISSUES.md`：版本号、发布文件名、版本历史表、GitHub Tag 同步为 `4.1.20260830`；功能清单新增 **B68**（mstsc 误用 SW_HIDE）、**B69**（set_setting 变量名笔误）
- 关联条目：RDP 窗口隐藏回归修复见 **B68**（`tools/tool.py` 移除 mstsc 的隐藏参数），高级选项保存报错修复见 **B69**（`Object/gui_DA.py:set_setting` 参数名 `stored`→`value`）

### 7. 4.2.20260830 版本号更新（本轮 hotfix）
- `version.txt`：`filevers`/`prodvers` 改为 `(4, 2, 2026, 830)`，`FileVersion`/`ProductVersion` 改为 `4.2.20260830`（程序窗口标题从此文件读取）
- `installer.iss`：`AppVersion` 与 `OutputBaseFilename` 同步为 `4.2.20260830`
- `build_release.ps1`：`$Version` 同步为 `4.2.20260830`
- `更新说明.txt`：新增「★ 4.2.20260830 更新」块（导出分组/服务器 `name 'sqlite3' is not defined` 回归修复），顶部版本/日期更新
- `README.md` / `ISSUES.md`：版本号、发布文件名、版本历史表、GitHub Tag 同步为 `4.2.20260830`；功能清单新增 **B70**（sqlite3 缺失导入）
- 关联条目：导出功能 `NameError` 修复见 **B70**（`Object/infoServer.py` 顶部补充 `import sqlite3`）；此前 hotfix 见 **B68**/**B69**（4.1.20260830）

### 8. 4.3.20260830 版本号更新（本轮 hotfix）
- `version.txt`：`filevers`/`prodvers` 改为 `(4, 3, 2026, 830)`，`FileVersion`/`ProductVersion` 改为 `4.3.20260830`（程序窗口标题从此文件读取）
- `installer.iss`：`AppVersion` 与 `OutputBaseFilename` 同步为 `4.3.20260830`
- `build_release.ps1`：`$Version` 同步为 `4.3.20260830`
- `更新说明.txt`：新增「★ 4.3.20260830 更新」块（导入服务器 `init_servers_data` 方法名笔误导致 `AttributeError` 修复），顶部版本/日期更新
- `README.md` / `ISSUES.md`：版本号、发布文件名、版本历史表、GitHub Tag 同步为 `4.3.20260830`；功能清单新增 **B71**（导入服务器刷新调用 `init_server_data`）
- 关联条目：导入服务器 `AttributeError` 修复见 **B71**（`Object/infoServer.py:import_server` 调用 `init_server_data()` 而非 `init_servers_data()`）

### 9. 4.4.20260830 版本号更新（本轮 hotfix，全量自查修复）
- `version.txt`：`filevers`/`prodvers` 改为 `(4, 4, 2026, 830)`，`FileVersion`/`ProductVersion` 改为 `4.4.20260830`（程序窗口标题从此文件读取）
- `installer.iss`：`AppVersion` 与 `OutputBaseFilename` 同步为 `4.4.20260830`
- `build_release.ps1`：`$Version` 同步为 `4.4.20260830`
- `更新说明.txt`：新增「★ 4.4.20260830 更新」块（VNC/Radmin 连接窗口被 SW_HIDE 隐藏修复、服务器导入二次加密损坏修复），顶部版本/日期更新
- `README.md` / `ISSUES.md`：版本号、发布文件名、版本历史表、GitHub Tag 同步为 `4.4.20260830`；功能清单确认 **B72**（VNC/Radmin 隐藏参数）、**B73**（导入二次加密）已修复
- 关联条目：VNC/Radmin 窗口隐藏回归修复见 **B72**（`tools/tool.py` 移除 vncviewer/radmin 的隐藏参数）；导入二次加密数据损坏修复见 **B73**（`Object/infoServer.py:export_server` 保留库中密文）

### 10. 4.5.20260830 版本号更新（本轮 hotfix）
- `version.txt`：`filevers`/`prodvers` 改为 `(4, 5, 2026, 830)`，`FileVersion`/`ProductVersion` 改为 `4.5.20260830`（程序窗口标题从此文件读取）
- `installer.iss`：`AppVersion` 与 `OutputBaseFilename` 同步为 `4.5.20260830`
- `build_release.ps1`：`$Version` 同步为 `4.5.20260830`
- `更新说明.txt`：新增「★ 4.5.20260830 更新」块（安装到 Program Files 启动 PermissionError、分组导出缺 id、导出密码改为明文便于跨机器迁移）
- `README.md` / `ISSUES.md`：版本号、发布文件名、版本历史表、GitHub Tag 同步为 `4.5.20260830`；功能清单新增 **B74**（日志目录回退 LOCALAPPDATA）、**B75**（分组导出 id）、**B76**（导出明文密码）
- 关联条目：Program Files 启动崩溃修复见 **B74**（`tools/logs.py` 默认回退 `%LOCALAPPDATA%`）；分组导出 id 修复见 **B75**（`export_group` 保留 id）；导出明文密码见 **B76**（`export_server` 解密明文、导入重新加密）

### 11. 4.6.20260830 版本号更新（本轮 hotfix）
- `version.txt`：`filevers`/`prodvers` 改为 `(4, 6, 2026, 830)`，`FileVersion`/`ProductVersion` 改为 `4.6.20260830`（程序窗口标题从此文件读取）
- `installer.iss`：`AppVersion` 与 `OutputBaseFilename` 同步为 `4.6.20260830`
- `build_release.ps1`：`$Version` 同步为 `4.6.20260830`
- `更新说明.txt`：新增「★ 4.6.20260830 更新」块（导入分组/服务器 id 漂移修复：先 truncate 并重置自增序列，再按导出 id 恢复）
- `README.md` / `ISSUES.md`：版本号、发布文件名、版本历史表、GitHub Tag 同步为 `4.6.20260830`；功能清单新增 **B77**（导入 id 漂移）
- 关联条目：导入 id 漂移修复见 **B77**（`gui_DA.py` 新增 `import_group_replace`/`import_server_replace`，`infoServer.py` 改用之）

---

## 四、本次新增功能（2.2.20260825）

### 1. RDP 连接重构 —— 临时 .rdp 配置文件 + 凭据管理器
- 连接流程：清理旧凭据（TERMSRV/ip）→ cmdkey 写入用户名/密码 → 按高级选项生成临时 .rdp（tempfile.mkstemp 唯一文件名，**不含密码**）→ mstsc 执行 → 会话关闭后 finally 自动删除凭据与临时文件
- 高级选项（音频位置/剪贴板/驱动器映射/全屏/分辨率）从 settings 表读取并写入 .rdp，随连接自动生效
- 列表形式传参，密码含特殊字符安全；后台线程执行界面不卡死

### 2. 远程桌面高级选项（持久化）
- 远程音频位置（本地/远程 → audiomode 0/1）、启用剪贴板（redirectclipboard）、映射本地驱动器（drivestoredirect `*`）、全屏模式（screen mode id 2）、分辨率（desktopwidth/height，预设+自定义）
- 修改即时保存到 settings 表（rdp_audio/rdp_clipboard/rdp_drive/rdp_fullscreen/rdp_resolution），重启自动恢复

### 3. Ping 批量检测
- 右侧功能区"Ping检测"按钮一键遍历服务器树全部主机，逐台 ping（Windows `-n 1 -w 1000`）
- 进度窗口实时显示"当前/总数"与检测主机；状态列更新绿色 ✓ / 红色 ✗
- 后台线程 + queue + after(100) 轮询刷新 UI；按钮检测中置灰防重复

### 4. 服务器树密码列脱敏（B63）
- 密码列默认 `*********`；选中行右键"显示密码"查看当前行明文

### 5. 主界面下方左右布局功能区
- 服务器树下方新增左右容器：左侧服务器说明（沿用既有组件），右侧功能区
- 右侧上下结构：上方 Ping+FAQ 按钮左右排列（左右外边距 25px、间距 10px、上边距 20px），下方高级选项区占满剩余高度（B64，无滚动）
- FAQ 知识库按钮（img/btn-faqzsk.png，191x45）占位，功能待实现（F16）

### 6. 服务器树列宽与界面细节
- 图标列（第一列）宽度缩小，IP地址列宽度增加
- 顶部按钮区（top/top_frame/top_R）与"主机名或域名搜索"、"服务器说明"标签固定 #F0F0F0，不随界面背景设置变化

---

### 2.1.20260825 版功能记录（历史）
- RDP 凭据管理器方式（cmdkey 写入/自动清除）、编辑主机三项修复+输入校验、鼠标中键释放焦点、连接确认弹框补全、分组展开状态全层级持久化、界面设置实时生效、分组树图标更换（详见更新说明.txt 历史记录）

---

## 五、代码兼容性问题（Python 3.10.11 升级相关）

| # | 位置 | 问题 | 建议 | 状态 | 修复措施 |
|---|------|------|------|------|----------|
| C1 | `tool.py:27` | `t.setDaemon(True)` 在 Python 3.10 已弃用，3.12 将移除 | 改为 `t.daemon = True` | ✅ 已解决 | 已在 B22 中改为 `t.daemon = True` |
| C2 | `tool.py:63` | `import re` 在方法内部，Python 3.10 虽支持但不符合 PEP 8 | 移到模块顶部 | ✅ 已解决 | `re` 已移至模块顶部导入（第 9 行）；方法内的 `from tools.logs import logs` 作为延迟导入刻意保留（B23），并添加注释说明其为规避 `tool.py` 与 `logs.py` 循环依赖的必要手段，非 PEP 8 违规 |
| C3 | `infoServer.py:179, 185, 188, 191, 194` | `pack_propagate(1)/(0)` 以整数作为布尔值 | 改为 `pack_propagate(True/False)` | ✅ 已解决 | 全部改为语义明确的 `True`/`False`（`infoServer.py` 共 6 处） |
| C4 | `infoServer.py:1192, 1361, 1382, 1444, 1652` | `resizable(0, 0)` 以整数作为布尔值 | 改为 `resizable(False, False)` | ✅ 已解决 | 全部 5 处改为 `resizable(False, False)` |
| C5 | `gui_DA.py:26` | `port int` 应为 `port INTEGER` | SQL 语法虽兼容但不规范 | ✅ 已解决 | `servers` 表 `port` 列类型由 `int` 改为标准 SQL `INTEGER`，保证跨数据库引擎类型解析正确 |
| C6 | `infoServer.py:5` | `from Object.gui_DA import *` 通配符导入 | 改为显式导入 | ✅ 已解决 | 改为 `from Object.gui_DA import DataAccess`（经核查仅 `DataAccess` 被使用），消除命名空间污染并符合 PEP 8 |
| C7 | 全局 | 相对路径 `./img/xxx.png` 依赖工作目录 | 用 `os.path.dirname(__file__)` 构造绝对路径 | ✅ 已解决 | `infoServer.py` 已统一使用基于 `__file__` 的 `_img_dir` 绝对路径；`gui_DA.py` 已使用基于 `__file__` 的 `db_path`（数据目录改 `%LOCALAPPDATA%\ServerRemoteInfoManager`），exe 与源码运行均无资源缺失 |
| C8 | `version.txt` / `README.md` | 版本号不一致 | 同步更新 version.txt | ✅ 已解决 | 经核查 `version.txt` 已为 `2.2.20260825`，`README.md` 中的版本号、发布文件名、版本历史均已同步为 `2.2.20260825`，无冲突；`gui_DA.py` 中 `ssh_tool_type` 默认值保留为跨平台安全的 `xterm`（仅作读取失败回退，不影响兼容性） |

---

## 六、代码质量问题

| # | 类别 | 问题描述 | 状态 | 修复说明 |
|---|------|----------|------|----------|
| Q1 | 命名 | `too` 类名应为 `Tool`（类名应大写） | ✅ 已解决 | `tools/tool.py` 中类 `too` 重命名为 `Tool`；同步更新引用方 `tools/logs.py`（延迟导入 `from tools.tool import Tool`）、`Object/infoServer.py`（`from tools.tool import Tool` 及 `self.too = Tool(...)` 实例化）。实例变量名 `self.too` 保留不变，避免大范围改动带来的回归风险 |
| Q2 | 命名 | `infoServer` 类名应为 `InfoServer`（类名应大写） | ✅ 已解决 | `Object/infoServer.py` 中类 `infoServer` 重命名为 `InfoServer`；同步更新入口 `app.py`（`from Object.infoServer import InfoServer` 与 `InfoServer(root)` 实例化） |
| Q3 | 命名 | `edit_da`、`add_server`（内部函数）命名风格不统一 | ✅ 已解决 | `Object/infoServer.py` 中两个内部嵌套函数统一为语义清晰的 `snake_case`：`add_server`（嵌套于 `add_server_window`）重命名为 `add_server_entry`，`edit_da`（嵌套于 `edit_server`）重命名为 `edit_server_entry`，避免与 `self.db.add_server` 等公开方法混淆，并同步更新对应按钮 `command=` 绑定 |
| Q4 | 重复代码 | `edit_da` 中 6 个 `elif` 分支结构几乎相同 | ✅ 已解决（2.1 版重构） | 见 B 系列记录：统一为字段映射表 + 单一更新/刷新流程；此外本次对 `gui_DA.py` 的连接管理模式也做了统一抽象（见 Q5/Q7） |
| Q5 | 重复代码 | `gui_DA.py` 每个方法都重复 `sqlite3.connect` → `cursor` → `execute` → `close` 模式 | ✅ 已解决 | `Object/gui_DA.py` 新增 `_connect()` 上下文管理器方法（`@contextmanager`，`from contextlib import contextmanager`），统一所有方法的连接打开/关闭逻辑，消除了约 20 处重复的 `connect/cursor/close` 样板代码 |
| Q6 | 异常处理 | 多处 `except Exception as e` 过于宽泛，吞掉所有异常 | ✅ 已解决 | `Object/gui_DA.py` 中数据访问层的宽泛 `except Exception` 已全部收窄为 `except sqlite3.Error`（及 `except sqlite3.IntegrityError`），仅捕获数据库相关异常，避免掩盖编程错误（如 `TypeError`/`NameError`）；`infoServer.py` 中 UI 层的 `force_refresh_ui` 等少数 `except Exception` 为向用户弹窗报错所需，属合理用法，已保留并注明 |
| Q7 | 资源管理 | `gui_DA.py` 未使用 `with` 语句管理数据库连接，异常时连接不关闭 | ✅ 已解决 | 借助 Q5 的 `_connect()` 上下文管理器，所有数据访问方法均通过 `with self._connect() as (conn, cursor):` 使用连接，无论正常结束还是异常，`finally` 块保证连接关闭，杜绝连接泄漏 |
| Q8 | 调试代码 | `infoServer.py` 和 `gui_DA.py` 中大量 `print()` 未清理 | ✅ 已解决（B27/B28） | 调试 `print` 已替换为 `logs` 日志记录 |
| Q9 | 注释 | `pack_propagate` 注释与代码行为相反 | ✅ 已解决（B20） | 注释已在兼容性修复中更正为 `True`/`False` 语义 |
| Q10 | 死代码 | `infoServer.py` 中 `groupTree_click` 整个方法被注释 | ✅ 已解决 | 已删除 `Object/infoServer.py` 中被注释掉的 `groupTree_click` 死代码块（约 17 行），并清理了第 372 行指向该方法的失效注释绑定 |
| Q11 | 死代码 | `Object/testInfoserver.py` 是早期原型，未接入主程序 | ✅ 已解决 | 已归档至 `_archive/testInfoserver.py`，并从 `Object/` 目录移除；`.gitignore` 已补充 `Object/testInfoserver.py` 规则，防止重新污染工作树 |
| Q12 | 死代码 | `Object/gui_DA -20240905.py` 是旧版备份，应使用 git 管理 | ✅ 已解决 | 已归档至 `_archive/gui_DA-20240905.py`（文件名空格规范化），并从 `Object/` 目录移除；`.gitignore` 已补充 `_archive/` 与 `gui_DA -*.py` 规则 |
| Q13 | 类型安全 | `server_tree.item(...)['values'][1]` 取值后未做类型转换 | ✅ 已解决（B54） | 树中取值统一 `str()` 转换 |

---

## 七、安全风险

| # | 风险 | 说明 | 状态 |
|---|------|------|------|
| S1 | 密码明文存储 | `servers.password` 明文存入 sqlite | ✅ **已解决**：新增 `tools/secret.py`，Windows 下用系统 DPAPI（绑定当前用户账户、密钥不落盘）加密，非 Windows / DPAPI 不可用时回退 `cryptography` Fernet（PBKDF2-HMAC-SHA256 派生，随机盐随密文存储），均不可用才降级明文并告警；`settings.default_password` 同样加密；首次启动自动迁移历史明文；导出 JSON 解密为明文前增加风险二次确认；添加主机日志密码脱敏 |
| S2 | ~~RDP 文件含明文密码~~ | ~~`tool.py:86` 将密码明文写入 `temp.rdp`~~ | ✅ **保持已解决**（2.2 版）：RDP 重新生成临时 .rdp 文件，但文件中**不含密码**（仅连接地址、用户名与高级选项），密码仅经凭据管理器传递 |
| S3 | SQL 注入 | `gui_DA.py` 表名/列名通过 f-string 拼接 | ✅ **已解决**：SQL 标识符无法参数化，改为常量白名单校验——`ALLOWED_TABLES`（`exists` 表名）、`SERVER_COLUMNS`（`update_server` 列名），非法标识符直接拒绝执行并写错误日志；其余 SQL 全部使用 `?` 占位符传参 |
| S4 | ~~日志泄露敏感信息~~ | ~~`infoServer.py` 日志中记录用户名和密码~~ | ✅ **已解决**：日志中密码已脱敏（S1/S2/S4） |
| S5 | ~~临时文件竞态~~ | ~~`tool.py:80` `temp.rdp` 写在固定路径，多实例并发时互相覆盖~~ | ✅ **保持已解决**（2.2 版）：临时 .rdp 改用 `tempfile.mkstemp` 生成唯一文件名，多实例并发互不干扰，会话关闭后自动删除 |
| S6 | RDP 凭据残留 | 程序被强杀时 `finally` 不执行，`TERMSRV/ip` 凭据可能残留在系统凭据管理器 | ✅ **已解决**：`Tool.cleanup_rdp_credentials()` 启动时扫描全部 TERMSRV 凭据，删除数据库中已不存在主机的孤儿凭据（可由 settings 表 `rdp_cred_cleanup = 0` 关闭）；新增 `Tool.cleanup_temp_rdp_files()` 一并清理残留的临时 `mstsc_*.rdp`（仅清理超过 1 小时的，避免影响进行中的连接）；保留 B62 的连接前清理作为第二道防线 |

---

## 七（续）、本轮安全风险处理记录

至此第七节"安全风险"已全部闭环（S1/S2/S3/S4/S5/S6 均为已解决）。本轮针对 S1、S3、S6 的处理如下：

### S1 密码加密存储（P0）

| 项目 | 处理内容 |
|------|----------|
| 新增模块 | `tools/secret.py` —— 统一封装加密/解密/脱敏，存储格式 `enc:v1:<backend>:<base64>` |
| 后端优先级 | ① **Windows DPAPI**（`ctypes` 调用 `crypt32.dll` 的 `CryptProtectData`/`CryptUnprotectData`）：零第三方依赖，密钥由系统按当前用户账户管理且从不落盘，数据库被拷到其它机器或由其它用户登录时无法解密；② **Fernet**（`cryptography`）：`PBKDF2-HMAC(SHA256)` 20 万轮从「机器特征种子 + 随机盐」派生主密钥，随机盐随密文一起存储，无需密钥文件；③ 两者都不可用时**降级明文**并写错误日志，保证功能不中断 |
| 影响范围 | `servers.password`（新增/编辑/读取）、`settings.default_password`（默认密码） |
| 兼容迁移 | 无 `enc:v1:` 前缀的值一律视为历史明文，读取时原样返回；首次启动由 `DataAccess.migrate_plaintext_secrets()` 批量加密，用 `settings.secret_encryption_migrated` 标记保证幂等 |
| 关联修复 | `gui_DA.search_servers` 搜索结果原样把密码明文插入树（绕过 B63 脱敏），已改为 `********`；`infoServer.add_server_window` 日志明文记录密码，已改用 `secret.mask()` 脱敏（S4 遗留） |
| 导出风险 | `export_server` 从库里读出的是密文，导出前解密为明文以便备份迁移，但**写入文件前增加风险二次确认弹窗**（提示含明文密码、妥善保管、及时删除）；`import_server` 导入时明文自动加密、密文不被二次加密 |
| 使用限制 | 加密与当前 Windows 用户绑定：换机器或换用户拷贝 `data.db` 会导致密码无法解密（解密失败返回空串并写日志）。**跨机器迁移请走"导出服务器 JSON → 导入"** |

### S3 SQL 注入加固

- `exists()` 的表名、`update_server()` 的列名无法用 `?` 参数化，改为常量白名单校验：`ALLOWED_TABLES = ('servers', 'groups')`、`SERVER_COLUMNS = ('conn_type','name','host','port','username','password','parent_id','server_info')`，非法标识符拒绝执行并写错误日志。
- 其余全部 SQL 均已使用 `?` 占位符传参，无字符串拼接值。

### S6 RDP 凭据残留

- `Tool.cleanup_rdp_credentials()` 增加启动扫描清理：读取 `cmdkey /list` 的全部 `TERMSRV/*` 凭据，删除数据库中已不存在主机的孤儿凭据；新增开关 settings 表 `rdp_cred_cleanup`（默认 `1` 开启，置 `0` 可关闭，避免误删用户手动保存的其它 RDP 凭据）。
- 新增 `Tool.cleanup_temp_rdp_files()`：清理系统临时目录中残留的 `mstsc_*.rdp`，仅删除超过 1 小时的文件，避免影响进行中的连接。
- 两者均在 `InfoServer.__init__` 启动时调用；B62 的"连接前清理"保留为第二道防线。

### 依赖与打包

- `requirements.txt`：
  - `cryptography==46.0.3` 登记为**可选回退依赖**（Windows 下走 DPAPI 时无需安装）；文件头部注释同步说明依赖分层（运行时必需 / FAQ / 可选回退 / 开发打包）。
  - 修复缺失项：补入运行时必需的 `Pillow==12.1.0`（GUI 图标与 Font Awesome 渲染，`infoServer.py` 直接 `import PIL`）——此前 README「源码运行」与「打包前置依赖」均已声明 Pillow，但依赖清单中缺失，按 `pip install -r requirements.txt` 全新装机会因无 Pillow 直接启动失败。
- `build.spec`：`hiddenimports` 增加 `tools.secret`；并加注说明 `cryptography` 仅作回退后端，若确定只面向 Windows 可将其加入 `excludes` 以精简发行包体积（代价是失去 Fernet 回退）。
- `README.md` 同步：修正「密码以明文存储」的过期 FAQ（现为 DPAPI/Fernet 加密存储），补充跨机器迁移只能走 JSON 导出导入的限制；配置项表补充 `rdp_cred_cleanup`、`secret_encryption_migrated`。

---

## 八、优先修复建议

### P0（立即修复，影响基本功能）
> 暂无 —— S1（密码明文存储）已修复，第七节"安全风险"全部闭环

### P1（近期修复，影响体验）
> 暂无 —— F15/S6（RDP 凭据残留扫描清理）已修复

### P2（中期优化）
> 暂无 —— F9（批量添加主机，JSON 导入已覆盖）、F14（分组双击查看主机，单击交互已覆盖）经评估确定无需开发，已移入第三节「已关闭」小节

> 注：F4（重命名分组）、F8（编辑主机类型）、F12（窗口位置记忆）已在 2.2 版实现（2026-08-30 代码复核确认）；Q5/Q7（数据库连接上下文管理器）、C7（绝对路径）、F11（密码加密存储）、F15/S6（RDP 凭据残留）均已解决，移出优先修复列表。

---

## 九、运维智脑（F17）实现说明

### 9.1 需求与方案
新增独立的 AI 聊天模块，主界面「Ping 检测」按钮下方提供入口，打开多线程聊天窗口；支持多模型自定义配置、会话持久化、Markdown 渲染与代码块操作、思考过程折叠、输入长度自动截取。

经与用户确认的技术选型：
- **HTTP 客户端**：`requests`（流式 SSE 解析简单可靠），已登记 `requirements.txt` 与 `build.spec`
- **存储**：模型配置放主库 `data.db`（新建 `ai_models` 表），聊天记录放独立库 `aichat.db`（与 `faq.db` 一致的用户数据目录隔离策略）
- **Markdown 渲染**：自研轻量分块渲染（`opsbrain/mdrender.py`），代码块内嵌「复制 / 另存为」按钮，不依赖 tkhtmlview
- **长度控制**：字符加权估算（CJK 1.5 字符/token，其余 4 字符/token，零新增依赖）

### 9.2 分层结构
| 文件 | 职责 |
|------|------|
| `opsbrain/__init__.py` | 惰性导出 `open_ops_brain` |
| `opsbrain/main.py` | 入口层：解析用户数据目录得到 `aichat.db` 路径，单例打开/复用窗口，异常兜底日志 |
| `opsbrain/da.py` | DA 层：`ModelDAO`（主库 `ai_models` 建表与 CRUD/排序/启用）、`ChatDAO`（独立库会话表/消息表建表与 CRUD/级联删除） |
| `opsbrain/service.py` | 功能层：`ModelService`（校验、密钥加解密与遮蔽）、`ChatService`（上下文组装、发送、落库）、`AIClient`（requests 流式/非流式、SSE 解析、错误分类） |
| `opsbrain/token.py` | 长度控制：`estimate_tokens` / `input_budget` / `truncate_context` / `truncate_single` |
| `opsbrain/mdrender.py` | Markdown 轻量解析与分块渲染（标题/引用/列表/代码块/行内码/粗体/斜体），代码块工具栏 |
| `opsbrain/ui.py` | UI 层：`OpsBrainWindow`（会话列表、消息滚动区、输入区、模型单选框动态生成） |

### 9.3 数据库表
主库 `data.db`（新增）：
```
ai_models(id, name UNIQUE, api_url, api_key(加密), model_name,
          temperature REAL, max_tokens INTEGER, supports_stream INTEGER,
          description TEXT, sort_order INTEGER, enabled INTEGER,
          created_at TEXT, updated_at TEXT)
```
独立库 `aichat.db`（新建）：
```
chat_sessions(id, title, model_id, model_name, created_at, updated_at)
chat_messages(id, session_id, role, content, thinking, created_at)
```

### 9.4 关键实现点
- **密钥三段式**：落库 `secret.encrypt`（DPAPI/Fernet）；读取 `secret.decrypt`；界面展示 `mask_key`（保留前 4 后 4，中间 `****`），表单 Entry 默认 `show='*'` 并提供显示切换
- **思考折叠**：`<think>…</think>` 标签或 `reasoning_content` 字段归一化后折叠展示，默认折叠、可手动展开
- **流式双通道**：`supports_stream=1` 走 SSE 增量渲染 + 可中途停止（取消标志 + 关闭响应流）；`=0` 走一次性返回
- **输入长度控制**：提交时按所选模型 `max_tokens` 加权估算，超 `max_tokens×(1-储备比例)` 时优先丢弃最早历史轮次，单条仍超则尾部硬截断并提示
- **多线程**：后台线程执行请求 + 主线程 `after()` 回填（复用 `ping_all_servers` 范式），窗口关闭不阻塞退出

### 9.5 设置窗口改造（需求 6）
「系统设置-连接参数」Tab 重构为 AI 模型配置：左侧模型列表（新增/删除/上移/下移），右侧参数表单（含密钥遮蔽预览）。同时移除了原有的「默认用户名 / 默认密码 / 默认 SSH 端口 / 默认 VNC 端口」四项，包括 `save_settings` 保存逻辑、`restore_defaults` 默认值、`gui_DA.ENCRYPTED_SETTING_KEYS`（`default_password`）白名单、README 文档引用，已通过 code-explorer 全仓排查确保无悬挂读写残留。

### 9.6 验证情况
- DA 层：临时库脚本验证 `ai_models` 与 `chat_sessions/chat_messages` 的 CRUD 与级联删除
- 功能层：桩对象模拟流式/非流式/401 鉴权失败与输入截断断言通过
- UI 层：隔离数据目录实例化主窗口 + 打开聊天窗口，验证按钮、模型单选框、Markdown 渲染、新建会话均正常
- 主程序：启动冒烟验证「运维智脑」按钮与改造后的设置窗口无报错

### 9.7 外观与设置窗口微调（2026-08-30）
- 新增 `img/btn-ywzn.png`（191x45 紫色圆角胶囊按钮，含白色「运维智脑」文字与脑形图标），与「Ping 检测」按钮同尺寸、同 `padx=(25,10)`、同 `width=191/height=45` 对齐，视觉风格统一
- 「系统设置」窗口宽度由 400 扩大至 800（高度保持 650），「连接参数」Tab 内的模型列表框（250→300）、参数表单区（x=280/宽370 → x=330/宽440）与输入框（22→40，描述 38→56）同步加宽，提供更宽敞的编辑区域

### 9.8 移除「显示密钥」复选框（2026-08-30 收尾）
- 「连接参数」模型参数表单中不再提供「显示密钥」复选框与明文切换逻辑（`toggle_key_show` 移除），密钥输入框始终以 `show='*'` 掩码显示，界面更简洁、避免明文暴露
- 保留「当前密钥：****」遮蔽预览（`lbl_key_mask`），便于编辑时确认已配置密钥而不泄露全文

---

*本文档随项目迭代持续更新。*
