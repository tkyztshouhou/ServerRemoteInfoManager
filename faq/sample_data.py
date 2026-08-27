# faq/sample_data.py
# 首次启动预置示例数据，便于演示与冒烟测试。

from faq.da import FaqDataAccess


_SAMPLES = [
    ('常见问题', [
        ('如何添加服务器？',
         '## 添加服务器\n\n1. 点击左侧「添加」按钮新建分组\n2. 在分组下点击「添加主机」\n3. 填写 `IP`、`端口`、`用户名`、`密码` 后保存\n\n> 支持 SSH / RDP / VNC 等多种连接方式', 'text'),
        ('连接超时怎么办？',
         '## 连接超时排查\n\n- 确认目标主机网络可达（可先使用 **Ping 检测**）\n- 检查防火墙是否放通对应端口\n- 确认用户名/密码正确', 'text'),
    ]),
    ('SQL 参考', [
        ('查询服务器列表',
         "SELECT id, name, host, port, username\nFROM servers\nWHERE type = 'ssh'\nORDER BY name;", 'sql'),
        ('按分组统计主机数',
         "SELECT g.name AS group_name, COUNT(s.id) AS cnt\nFROM groups g\nLEFT JOIN servers s ON s.parent_id = g.id\nGROUP BY g.name;", 'sql'),
    ]),
    ('文档模板', [
        ('部署检查清单',
         '# 部署检查清单\n\n## 前置条件\n- [ ] 操作系统版本符合要求\n- [ ] 端口已放通\n\n## 步骤\n1. 上传安装包\n2. 执行安装脚本\n3. 验证服务状态', 'doc'),
    ]),
]


def ensure_sample_data(db_path: str) -> None:
    """若数据库为空，则写入示例分类与条目。"""
    da = FaqDataAccess(db_path)
    da.create_database()
    existing = da.get_categories()
    if existing:
        return  # 已有数据，不重复写入
    for cat_name, articles in _SAMPLES:
        cid = da.add_category(cat_name)
        for title, content, ctype in articles:
            da.add_article(cid, title, content, ctype)
