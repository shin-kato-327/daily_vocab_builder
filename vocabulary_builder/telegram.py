"""Telegram sender based on the stock_screening outbound-only client."""

from __future__ import annotations

import os

import requests

API_BASE = "https://api.telegram.org"


class TelegramConfigError(RuntimeError):
    pass


def load_env_file(path: str = ".env") -> None:
    if not os.path.exists(path):
        return
    with open(path, "r", encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip())


def _config() -> tuple[str, str]:
    load_env_file()
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not token:
        raise TelegramConfigError("TELEGRAM_BOT_TOKEN not set in environment or .env")
    if not chat_id:
        raise TelegramConfigError("TELEGRAM_CHAT_ID not set in environment or .env")
    return token, chat_id


def send(message: str, timeout_s: float = 15.0) -> None:
    token, chat_id = _config()
    url = f"{API_BASE}/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "disable_web_page_preview": True,
    }
    resp = requests.post(url, json=payload, timeout=timeout_s)
    if resp.status_code >= 300 or not resp.json().get("ok", False):
        raise RuntimeError(f"telegram send failed: {resp.status_code} {resp.text[:300]}")
