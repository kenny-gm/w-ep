"""
AI Client - OpenAI 兼容接口调用

API Key 只从环境变量读取，禁止日志打印 Key。
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


class AIClientDisabled(Exception):
    """AI 未启用或未配置"""


class AIClientError(Exception):
    """AI 调用错误"""


def _setting(db: Session, key: str, default: str = "") -> str:
    row = db.query(SystemSetting).filter(SystemSetting.key == key).first()
    return row.value if row else default


class AIClient:
    def __init__(self, db: Session):
        self._db = db

    def is_enabled(self) -> bool:
        val = _setting(self._db, "ai.enabled", str(settings.AI_ENABLED)).lower()
        return val in ("true", "1", "yes", "on")

    def get_effective_config(self) -> dict:
        """返回配置，不含 API Key 明文"""
        return {
            "enabled": self.is_enabled(),
            "provider": _setting(self._db, "ai.provider", settings.AI_PROVIDER),
            "base_url": _setting(self._db, "ai.base_url", settings.AI_BASE_URL),
            "model": _setting(self._db, "ai.model", settings.AI_MODEL),
            "api_key_configured": bool(settings.AI_API_KEY),
            "timeout": int(_setting(self._db, "ai.timeout", str(settings.AI_TIMEOUT))),
            "max_tokens": int(_setting(self._db, "ai.max_tokens", str(settings.AI_MAX_TOKENS))),
        }

    def _build_headers(self) -> dict:
        return {
            "Authorization": f"Bearer {settings.AI_API_KEY}",
            "Content-Type": "application/json",
        }

    def _chat_payload(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: Optional[float],
        max_tokens: Optional[int],
    ) -> dict:
        eff = self.get_effective_config()
        return {
            "model": eff["model"],
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temperature if temperature is not None else 0.2,
            "max_tokens": max_tokens or eff.get("max_tokens", 1200),
        }

    def chat_text(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """返回纯文本"""
        if not settings.AI_API_KEY:
            raise AIClientDisabled("AI_API_KEY 未配置")
        if not self.is_enabled():
            raise AIClientDisabled("AI 未启用")

        eff = self.get_effective_config()
        payload = self._chat_payload(system_prompt, user_prompt, temperature, max_tokens)

        resp = requests.post(
            f"{eff['base_url'].rstrip('/v1')}/v1/chat/completions",
            headers=self._build_headers(),
            json=payload,
            timeout=eff["timeout"],
        )
        if resp.status_code != 200:
            raise AIClientError(f"AI API 错误 [{resp.status_code}]: {resp.text[:300]}")

        data = resp.json()
        return data["choices"][0]["message"]["content"]

    def chat_json(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> dict:
        """解析 JSON 输出（支持 ```json fenced block）"""
        text = self.chat_text(system_prompt, user_prompt, temperature, max_tokens)
        # 去掉 ```json ... ``` 或 ``` ... ``` 包装
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
        if not settings.AI_API_KEY:
            return {"success": False, "error": "AI_API_KEY 未配置"}
        try:
            eff = self.get_effective_config()
            payload = self._chat_payload(
                "You are a helpful assistant.",
                "Reply with exactly: {\"ok\": true}",
                0.1,
                20,
            )
            resp = requests.post(
                f"{eff['base_url'].rstrip('/v1')}/v1/chat/completions",
                headers=self._build_headers(),
                json=payload,
                timeout=eff["timeout"],
            )
            if resp.status_code != 200:
                return {"success": False, "error": f"API 错误 [{resp.status_code}]: {resp.text[:200]}"}
            data = resp.json()
            model = data.get("model", "?")
            return {"success": True, "model": model}
        except requests.exceptions.Timeout:
            return {"success": False, "error": "请求超时"}
        except Exception as e:
            return {"success": False, "error": str(e)[:200]}
