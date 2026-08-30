# 敏感数据加密存储
# \tools\secret.py

"""服务器密码等敏感字段的加密存储（ISSUES.md 安全风险 S1）

后端优先级：
  1. Windows DPAPI（CryptProtectData / CryptUnprotectData，ctypes 调用 crypt32.dll）
     - 无第三方依赖；密钥由系统按当前 Windows 用户账户管理且从不落盘；
     - 数据库文件被拷贝到其它机器、或被其它 Windows 用户登录时无法解密。
  2. cryptography.fernet.Fernet（非 Windows 或 DPAPI 不可用时的跨平台回退）
     - 主密钥由 PBKDF2-HMAC(SHA256) 从「机器特征种子 + 随机盐」派生；
     - 随机盐与密文一起存储，无需额外的密钥文件或数据库字段。
  3. 明文（两者都不可用时降级，写入警告日志，保证功能不中断）

存储格式：enc:v1:<backend>:<base64(blob)>
不带该前缀的值一律视为历史明文数据，解密时原样返回，实现平滑迁移。
"""

import base64
import ctypes
import hashlib
import platform
import sys
import uuid

PREFIX = 'enc:v1:'

_BACKEND = None      # 'dpapi' | 'fernet' | 'plain'
_WARNED = set()


# ------------------------------------------------------------------ 日志告警
def _warn(tag, message):
    """写错误日志（延迟导入 logs，避免与 tool.py 形成循环依赖）"""
    if tag in _WARNED:
        return
    _WARNED.add(tag)
    try:
        from tools.logs import logs
        logs().write_log_error('[secret] ' + message)
    except Exception:
        pass


# -------------------------------------------------------------- Windows DPAPI
class _DATA_BLOB(ctypes.Structure):
    """对应 Win32 DATA_BLOB 结构体"""
    _fields_ = [('cbData', ctypes.c_uint32),
                ('pbData', ctypes.POINTER(ctypes.c_char))]


def _dpapi_crypt(protect, data):
    """调用 CryptProtectData / CryptUnprotectData

    protect=True 加密，False 解密。失败时抛出 OSError（含 Windows 错误码）。
    """
    crypt32 = ctypes.WinDLL('crypt32.dll', use_last_error=True)
    kernel32 = ctypes.WinDLL('kernel32.dll', use_last_error=True)

    crypt32.CryptProtectData.restype = ctypes.c_bool
    crypt32.CryptProtectData.argtypes = [
        ctypes.POINTER(_DATA_BLOB), ctypes.c_wchar_p, ctypes.POINTER(_DATA_BLOB),
        ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint32, ctypes.POINTER(_DATA_BLOB)]
    crypt32.CryptUnprotectData.restype = ctypes.c_bool
    crypt32.CryptUnprotectData.argtypes = crypt32.CryptProtectData.argtypes
    kernel32.LocalFree.restype = ctypes.c_void_p
    kernel32.LocalFree.argtypes = [ctypes.c_void_p]

    buf = ctypes.create_string_buffer(data, max(len(data), 1))
    blob_in = _DATA_BLOB()
    blob_in.cbData = len(data)
    blob_in.pbData = ctypes.cast(buf, ctypes.POINTER(ctypes.c_char))

    blob_out = _DATA_BLOB()
    fn = crypt32.CryptProtectData if protect else crypt32.CryptUnprotectData
    if not fn(ctypes.byref(blob_in), None, None, None, None, 0, ctypes.byref(blob_out)):
        raise ctypes.WinError(ctypes.get_last_error())
    try:
        return ctypes.string_at(blob_out.pbData, blob_out.cbData)
    finally:
        if blob_out.pbData:
            kernel32.LocalFree(blob_out.pbData)


# ----------------------------------------------------------------- Fernet 回退
def _machine_seed():
    """机器/用户特征种子（不保密，仅用于让密钥无法在其它机器上复现）"""
    seed = platform.node() + '|' + str(uuid.getnode())
    if sys.platform == 'win32':
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                r'SOFTWARE\Microsoft\Cryptography') as key:
                seed += '|' + str(winreg.QueryValueEx(key, 'MachineGuid')[0])
        except Exception:
            pass
    return seed.encode('utf-8')


_FERNET_KEY_CACHE = {}


def _fernet_key(salt):
    """PBKDF2-HMAC(SHA256) 派生 32 字节密钥，按 salt 缓存避免重复计算"""
    cached = _FERNET_KEY_CACHE.get(salt)
    if cached is not None:
        return cached
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32,
                     salt=salt, iterations=200000)
    key = base64.urlsafe_b64encode(kdf.derive(_machine_seed()))
    _FERNET_KEY_CACHE[salt] = key
    return key


def _fernet_encrypt(data):
    import secrets
    from cryptography.fernet import Fernet
    salt = secrets.token_bytes(16)
    token = Fernet(_fernet_key(salt)).encrypt(data)
    return base64.urlsafe_b64encode(salt) + b'.' + token


def _fernet_decrypt(blob):
    from cryptography.fernet import Fernet
    salt_b64, _, token = blob.partition(b'.')
    return Fernet(_fernet_key(base64.urlsafe_b64decode(salt_b64))).decrypt(token)


# ------------------------------------------------------------------ 后端选择
def _detect_backend():
    """按 DPAPI -> Fernet -> 明文 顺序探测可用后端（结果缓存）"""
    if sys.platform == 'win32':
        try:
            probe = _dpapi_crypt(True, b'ServerRemoteInfoManager')
            if _dpapi_crypt(False, probe) == b'ServerRemoteInfoManager':
                return 'dpapi'
        except Exception as e:
            _warn('dpapi', f'DPAPI 不可用，尝试回退 Fernet：{e}')
    try:
        probe = _fernet_encrypt(b'ServerRemoteInfoManager')
        if _fernet_decrypt(probe) == b'ServerRemoteInfoManager':
            return 'fernet'
    except Exception as e:
        _warn('fernet', f'Fernet 不可用，密码将降级为明文存储：{e}')
    _warn('plain', '无可用加密后端，密码以明文存储，请安装 cryptography 或在 Windows 下运行')
    return 'plain'


def backend_name():
    """当前生效的加密后端名：dpapi / fernet / plain"""
    global _BACKEND
    if _BACKEND is None:
        _BACKEND = _detect_backend()
    return _BACKEND


def is_available():
    """是否存在可用的加密后端（False 表示降级为明文）"""
    return backend_name() != 'plain'


def is_encrypted(value):
    """判断值是否为加密格式"""
    return isinstance(value, str) and value.startswith(PREFIX)


# -------------------------------------------------------------------- 加解密
def encrypt(plain):
    """加密字符串，返回 'enc:v1:<backend>:<base64>' 格式密文

    - 空值/空串原样返回
    - 已是密文格式的值原样返回（避免导出再导入时被二次加密）
    - 加密失败或后端不可用时返回原明文，并写入一次警告日志
    """
    if plain is None:
        return None
    text = str(plain)
    if text == '' or is_encrypted(text):
        return text
    backend = backend_name()
    if backend == 'plain':
        return text
    try:
        raw = text.encode('utf-8')
        if backend == 'dpapi':
            blob = _dpapi_crypt(True, raw)
        else:
            blob = _fernet_encrypt(raw)
        return PREFIX + backend + ':' + base64.b64encode(blob).decode('ascii')
    except Exception as e:
        _warn('encrypt', f'加密失败，已按明文保存：{e}')
        return text


def decrypt(stored):
    """解密 encrypt() 生成的密文；历史明文数据原样返回，保证平滑迁移

    解密失败（如数据库被拷贝到其它机器、或由其它 Windows 用户登录）时
    返回空串并写入警告日志——这是预期的保护行为，而非程序缺陷。
    """
    if stored is None:
        return None
    text = str(stored)
    if text == '' or not is_encrypted(text):
        return text
    backend, _, payload = text[len(PREFIX):].partition(':')
    if backend == 'plain':
        return text
    try:
        blob = base64.b64decode(payload)
        if backend == 'dpapi':
            if sys.platform != 'win32':
                raise OSError('DPAPI 密文只能在 Windows 上解密')
            raw = _dpapi_crypt(False, blob)
        elif backend == 'fernet':
            raw = _fernet_decrypt(blob)
        else:
            raise ValueError('未知的加密后端: ' + backend)
        return raw.decode('utf-8')
    except Exception as e:
        _warn('decrypt', f'解密失败（后端 {backend}）：{e}；'
                         f'数据库可能来自其它机器或其它 Windows 用户，密码已置空')
        return ''


# ------------------------------------------------------------------ 日志脱敏
def mask(value, keep=2):
    """密码脱敏：仅保留前 keep 位，其余以 * 代替（用于日志）"""
    if value is None:
        return ''
    text = str(value)
    if not text:
        return ''
    if len(text) <= keep:
        return '*' * len(text)
    return text[:keep] + '*' * (len(text) - keep)
