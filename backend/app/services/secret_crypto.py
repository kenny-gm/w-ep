"""
加解密工具 - 使用 Fernet 对称加密
不用于简单 XOR/base64 伪加密。
"""
from __future__ import annotations

import base64
import hashlib

from cryptography.fernet import Fernet, InvalidToken

from app.config import settings


class SecretCryptoError(Exception):
    pass


def _fernet() -> Fernet:
    """从 SECRET_KEY 派生 Fernet 密钥"""
    raw = settings.SECRET_KEY.encode("utf-8")
    key = base64.urlsafe_b64encode(hashlib.sha256(raw).digest())
    return Fernet(key)


def encrypt_secret(value: str) -> str:
    """加密字符串，返回 base64 文本"""
    if not value:
        return ""
    return _fernet().encrypt(value.encode("utf-8")).decode("utf-8")


def decrypt_secret(value: str) -> str:
    """解密字符串，失败抛 SecretCryptoError"""
    if not value:
        return ""
    try:
        return _fernet().decrypt(value.encode("utf-8")).decode("utf-8")
    except InvalidToken as exc:
        raise SecretCryptoError("密钥解密失败，请检查 SECRET_KEY 是否变化") from exc