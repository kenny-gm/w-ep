"""
AI Client - OpenAI 兼容接口调用

支持 OpenAI / MiniMax / OpenAI-Compatible providers。
API Key 只从环境变量或数据库加密存储读取，禁止日志打印 Key。
非密钥配置优先读 SystemSetting，没有则读 settings。
"""

from __future__ import annotations

import json
import re
from typing import Any, Dict, Optional

import requests
from sqlalchemy.orm import Session

from app.config import settings
from app.models.models import SystemSetting
from app.services.secret_crypto import decrypt_secret, encrypt_secret, SecretCryptoError


def get_system_setting(db: Session, key: str, default: str = "") -> str:
    """读取 SystemSetting，优先数据库，没有则用 default"""
    row = db.query(SystemSetting).filter(SystemSetting.key == key).first()
    return row.value if row else default


class AIClientDisabled(Exception):
    """AI 未启用或未配置"""


class AIClientError(Exception):
    """AI 调用错误"""


class AIClient:
    def __init__(self, db: Session):
        self._db = db

    def is_enabled(self) -> bool:
        val = get_system_setting(self._db, "ai.enabled", str(settings.AI_ENABLED)).lower()
        return val in ("true", "1", "yes", "on")

    def get_api_key_info(self) -> dict:
        """
        返回 API Key 配置状态（不含明文）。
        source: database / env / none / decrypt_error
        """
        encrypted = get_system_setting(self._db, "ai.api_key_encrypted", "")
        if encrypted:
            try:
                decrypt_secret(encrypted)
                return {"api_key_configured": True, "api_key_source": "database"}
            except SecretCryptoError:
                return {"api_key_configured": True, "api_key_source": "decrypt_error"}
        if settings.AI_API_KEY:
            return {"api_key_configured": True, "api_key_source": "env"}
        return {"api_key_configured": False, "api_key_source": "none"}

    def get_effective_api_key(self) -> str | None:
        """返回可用的解密后 API Key，不存在返回 None"""
        encrypted = get_system_setting(self._db, "ai.api_key_encrypted", "")
        if encrypted:
            try:
                return decrypt_secret(encrypted)
            except SecretCryptoError:
                raise AIClientError("AI API Key 解密失败，请重新保存 API Key")
        if settings.AI_API_KEY:
            return settings.AI_API_KEY
        return None

    def get_effective_config(self) -> dict:
        """返回配置，不含 API Key 明文"""
        key_info = self.get_api_key_info()
        return {
            "enabled": self.is_enabled(),
            "provider": get_system_setting(self._db, "ai.provider", settings.AI_PROVIDER),
            "base_url": get_system_setting(self._db, "ai.base_url", settings.AI_BASE_URL),
            "model": get_system_setting(self._db, "ai.model", settings.AI_MODEL),
            "api_key_configured": key_info["api_key_configured"],
            "api_key_source": key_info["api_key_source"],
            "timeout": int(get_system_setting(self._db, "ai.timeout", str(settings.AI_TIMEOUT))),
            "max_tokens": int(get_system_setting(self._db, "ai.max_tokens", str(settings.AI_MAX_TOKENS))),
        }

    def _build_chat_url(self, base_url: str, provider: str) -> str:
        """构造 chat completions URL，不重复拼接"""
        base = (base_url or "").rstrip("/")
        if "/chat/completions" in base:
            return base
        path = settings.AI_CHAT_COMPLETIONS_PATH.lstrip("/")
        return f"{base}/{path}"

    def _build_headers(self) -> dict:
        key = self.get_effective_api_key()
        return {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        }

    def _openai_compatible_request(
        self,
        url: str,
        model: str,
        system_prompt: str,
        user_prompt: str,
        temperature: float,
        max_tokens: int,
        timeout: int,
    ) -> str:
        """通用 OpenAI 兼容请求，返回文本内容"""
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        resp = requests.post(
            url,
            headers=self._build_headers(),
            json=payload,
            timeout=timeout,
        )
        if resp.status_code != 200:
            raise AIClientError(f"AI API 错误 [{resp.status_code}]: {resp.text[:300]}")
        data = resp.json()
        return data["choices"][0]["message"]["content"]

    def chat_text(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """返回纯文本"""
        key = self.get_effective_api_key()
        if not key:
            raise AIClientDisabled("AI_API_KEY 未配置")
        if not self.is_enabled():
            raise AIClientDisabled("AI 未启用")

        eff = self.get_effective_config()
        url = self._build_chat_url(eff["base_url"], eff["provider"])
        temperature = temperature if temperature is not None else 0.2
        max_tokens = max_tokens or eff.get("max_tokens", 1200)

        return self._openai_compatible_request(
            url,
            eff["model"],
            system_prompt,
            user_prompt,
            temperature,
            max_tokens,
            eff["timeout"],
        )

    def chat_json(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> dict:
        """解析 JSON 输出（支持 ```json fenced block 和纯 JSON）"""
        text = self.chat_text(system_prompt, user_prompt, temperature, max_tokens)
        text = re.sub(r"^```json\s*", "", text.strip())
        text = re.sub(r"^```\s*", "", text.strip())
        text = re.sub(r"\s*```$", "", text.strip())
        try:
            return json.loads(text)
        except json.JSONDecodeError as exc:
            raise AIClientError(f"AI 返回不是合法 JSON: {exc}\n原始: {text[:200]}")

    def test_connection(self) -> dict:
        """返回连接测试结果"""
        if not self.is_enabled():
            return {"success": False, "error": "AI 未启用"}
        try:
            key = self.get_effective_api_key()
        except AIClientError as e:
            return {"success": False, "error": str(e)}
        if not key:
            return {"success": False, "error": "AI_API_KEY 未配置"}
        try:
            eff = self.get_effective_config()
            url = self._build_chat_url(eff["base_url"], eff["provider"])
            content = self._openai_compatible_request(
                url,
                eff["model"],
                "You are a helpful assistant.",
                '{"ok": true}',
                0.1,
                20,
                eff["timeout"],
            )
            return {"success": True, "model": eff["model"], "content": content[:100]}
        except requests.exceptions.Timeout:
            return {"success": False, "error": "请求超时"}
        except AIClientError as e:
            return {"success": False, "error": str(e)[:200]}
        except Exception as e:
            return {"success": False, "error": str(e)[:200]}