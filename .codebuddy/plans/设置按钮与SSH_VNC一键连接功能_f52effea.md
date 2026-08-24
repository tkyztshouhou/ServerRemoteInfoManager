---
name: 设置按钮与SSH/VNC一键连接功能
overview: 在远程桌面按钮右侧添加设置按钮，创建设置对话框配置工具路径、连接参数和界面样式，持久化到SQLite，并实现SSH/VNC一键连接功能。
design:
  architecture:
    framework: html
  styleKeywords:
    - Windows原生
    - 简洁
    - 功能优先
  fontSystem:
    fontFamily: Microsoft YaHei
    heading:
      size: 11px
      weight: 400
    subheading:
      size: 10px
      weight: 400
    body:
      size: 10px
      weight: 400
  colorSystem:
    primary:
      - "#F0F0F0"
      - "#FFFFFF"
    background:
      - "#F0F0F0"
      - "#FFFFFF"
    text:
      - "#000000"
    functional:
      - "#000000"
      - "#FFFFFF"
      - "#404040"
todos:
  - id: add-settings-table
    content: 在 gui_DA.py 的 create_database 中新增 settings 表建表语句
    status: completed
  - id: add-settings-methods
    content: 在 gui_DA.py 中新增 get_setting 和 set_setting 方法
    status: completed
    dependencies:
      - add-settings-table
  - id: add-ssh-vnc-tool
    content: 在 tool.py 中新增 run_ssh 和 run_vnc 方法，调用外部工具并传入参数
    status: completed
    dependencies:
      - add-settings-methods
  - id: add-settings-button
    content: 在 infoServer.py 的 create_widgets 中，mstsc 按钮右侧新增设置按钮（sz.png）
    status: completed
    dependencies:
      - add-settings-methods
  - id: create-settings-dialog
    content: 在 infoServer.py 中新增 open_settings 方法，创建设置对话框（三个 Tab：连接工具/连接参数/界面设置），含保存/取消按钮，调用 set_setting 持久化
    status: completed
    dependencies:
      - add-settings-methods
  - id: implement-ssh-vnc-connect
    content: 在 infoServer.py 的 connect_server 方法中补全 SSH 和 VNC 分支，读取配置的工具路径和参数，调用 tool.py 中的 run_ssh/run_vnc
    status: completed
    dependencies:
      - add-settings-methods
      - add-ssh-vnc-tool
  - id: load-settings-on-startup
    content: 在 infoServer.py 的 __init__ 中，初始化完成后调用加载设置方法，应用字体和背景颜色到主窗口及控件
    status: completed
    dependencies:
      - add-settings-methods
---

## 需求概述

在远程桌面（mstsc）按钮右侧添加一个设置按钮（使用 `img/sz.png`），点击后打开设置对话框，配置内容分为三大类：

1. **连接工具路径配置**：SSH 工具（plink/ssh）安装路径、VNC 工具（TightVNC/RealVNC/UltraVNC/vncviewer）安装路径
2. **连接参数配置**：默认用户名、默认密码、默认端口（SSH/VNC）
3. **界面配置**：字体、背景颜色

所有配置持久化存储到 SQLite 数据库（新建 `settings` 表，key-value 结构）。

同时实现 SSH 和 VNC 的一键连接功能：双击或右键连接时，根据配置自动调用对应工具并传入主机地址、端口、用户名、密码，无需手动输入。

## 核心功能

- 工具栏新增设置按钮（mstsc 按钮右侧，sz.png 图标）
- 设置对话框（Toplevel），含三个 Tab：连接工具 / 连接参数 / 界面设置
- settings 表建表与读写方法（gui_DA.py）
- tool.py 新增 `run_ssh` 和 `run_vnc` 方法
- connect_server 方法补全 SSH/VNC 分支
- 程序启动时加载设置并应用界面样式

## 技术栈

- 语言：Python 3.10.11
- GUI 框架：tkinter + ttk（项目现有）
- 数据库：SQLite（项目现有 data.db）
- 进程调用：subprocess.Popen（SSH/VNC 工具调用）
- 无新增第三方依赖

## 技术架构

### 系统架构

- 保持现有三层结构：UI 层（infoServer.py）/ DA 层（gui_DA.py）/ 工具层（tool.py）
- 设置数据通过新建 `settings` 表（key-value 结构）持久化
- SSH/VNC 连接通过 subprocess.Popen 调用外部工具，与原 RDP 的 subprocess.call 模式一致

### 模块划分

- **gui_DA.py**：新增 `settings` 表建表逻辑 + `get_setting` / `set_setting` 方法
- **tool.py**：新增 `run_ssh` / `run_vnc` 方法
- **infoServer.py**：新增设置按钮、设置对话框、SSH/VNC 连接分支、启动时加载设置

### 数据流

设置保存：对话框输入 → set_setting(key, value) → SQLite settings 表
设置读取：程序启动 → get_setting(key) → 应用字体/背景色
SSH 连接：connect_server → 读取 plink 路径 + 主机参数 → subprocess.Popen(['plink', ...])
VNC 连接：connect_server → 读取 vncviewer 路径 + 主机参数 → subprocess.Popen(['vncviewer', ...])

## 数据库设计

新增表 `settings`：

```sql
CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT
)
```

预设 key 及默认值：

| key | 默认值 |
| --- | --- |
| ssh_tool_path | plink |
| vnc_tool_path | vncviewer |
| default_username | (空) |
| default_password | (空) |
| default_ssh_port | 22 |
| default_vnc_port | 5900 |
| ui_font | Microsoft YaHei |
| ui_font_size | 10 |
| ui_bg_color | #F0F0F0 |


## 目录结构

```
Object/
  gui_DA.py          [MODIFY] 新增 settings 表 + get_setting/set_setting
  infoServer.py      [MODIFY] 新增设置按钮、设置对话框、SSH/VNC 连接分支
tools/
  tool.py            [MODIFY] 新增 run_ssh、run_vnc 方法
```

## 设计说明

设置对话框采用 tkinter Toplevel + ttk.Notebook 多标签页结构，风格与现有界面保持一致（#F0F0F0 背景、微软雅黑字体）。

### 对话框布局（宽 420，高 480）

- **Tab 1 - 连接工具**：SSH 工具路径（Entry + 浏览按钮）、VNC 工具路径（Entry + 浏览按钮）
- **Tab 2 - 连接参数**：默认用户名、默认密码（Entry）、默认 SSH 端口、默认 VNC 端口（Entry）
- **Tab 3 - 界面设置**：字体选择（Combobox）、字体大小（Combobox）、背景颜色（Entry + 颜色预览 Label）
- 底部：保存按钮 + 取消按钮

### 工具路径浏览

使用 tk.filedialog.askopenfilename 让用户选择可执行文件，与现有项目风格一致。

## Agent Extensions

### SubAgent

- **code-explorer**
- Purpose: 探索现有代码结构，确认修改点和调用链
- Expected outcome: 精确定位 infoServer.py、gui_DA.py、tool.py 的修改位置