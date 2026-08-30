# opsbrain/__init__.py
# 运维智脑功能包入口。为避免包内子模块相互依赖导致的导入副作用，
# open_ops_brain 采用惰性导入，仅在调用时加载 main 模块。

def open_ops_brain(master=None):
    from opsbrain.main import open_ops_brain as _open
    return _open(master)

__all__ = ['open_ops_brain']
