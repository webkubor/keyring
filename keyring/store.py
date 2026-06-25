"""本地密钥存储 — 加密存 ~/.keyring/secrets.json，零网络依赖。"""

import base64
import json
import os
from pathlib import Path
from typing import Optional

from .crypto import encrypt, decrypt

SECRETS_DIR = Path.home() / ".keyring"
SECRETS_FILE = SECRETS_DIR / "secrets.json"
MASTER_KEY_FILE = SECRETS_DIR / "master.key"


def _load_secrets() -> dict:
    if not SECRETS_FILE.exists():
        return {}
    try:
        with open(SECRETS_FILE) as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def _save_secrets(data: dict) -> None:
    SECRETS_DIR.mkdir(parents=True, exist_ok=True)
    with open(SECRETS_FILE, "w") as f:
        json.dump(data, f, indent=2)


def get_master_key() -> str:
    """获取 master key，优先环境变量，其次本地文件。"""
    key = os.environ.get("KEYRING_MASTER_KEY", "")
    if key:
        return key
    if MASTER_KEY_FILE.exists():
        return MASTER_KEY_FILE.read_text().strip()
    raise SystemExit("未初始化。运行 keyring init 生成 master key。")


def init_master_key() -> str:
    """生成 master key 并保存到本地。"""
    if MASTER_KEY_FILE.exists():
        return MASTER_KEY_FILE.read_text().strip()
    key = base64.b64encode(os.urandom(32)).decode("ascii")
    SECRETS_DIR.mkdir(parents=True, exist_ok=True)
    MASTER_KEY_FILE.write_text(key)
    MASTER_KEY_FILE.chmod(0o600)
    return key


def parse_ref(ref: str) -> tuple[str, str]:
    """解析 secret://platform/name 引用。"""
    if not ref.startswith("secret://"):
        raise ValueError(f"格式错误，应为 secret://platform/name: {ref}")
    parts = ref[len("secret://"):].split("/", 1)
    if len(parts) != 2:
        raise ValueError(f"格式错误：{ref}")
    return parts[0], parts[1]


def get_secret(ref: str) -> Optional[str]:
    """读取并解密本地密钥。"""
    platform, name = parse_ref(ref)
    secrets = _load_secrets()
    key = f"{platform}/{name}"
    if key not in secrets:
        return None
    return decrypt(secrets[key]["ciphertext"], get_master_key())


def set_secret(ref: str, value: str, kind: str = "API Key", account: str = "") -> None:
    """加密并保存密钥。"""
    platform, name = parse_ref(ref)
    ciphertext = encrypt(value, get_master_key())
    secrets = _load_secrets()
    secrets[f"{platform}/{name}"] = {
        "ciphertext": ciphertext,
        "kind": kind,
        "account": account,
    }
    _save_secrets(secrets)


def delete_secret(ref: str) -> bool:
    """删除密钥。"""
    platform, name = parse_ref(ref)
    secrets = _load_secrets()
    key = f"{platform}/{name}"
    if key in secrets:
        del secrets[key]
        _save_secrets(secrets)
        return True
    return False


def list_secrets() -> list[dict]:
    """列出所有密钥元信息（不含明文）。"""
    secrets = _load_secrets()
    result = []
    for key, val in secrets.items():
        platform, name = key.split("/", 1)
        result.append({
            "platform": platform,
            "name": name,
            "kind": val.get("kind", ""),
            "account": val.get("account", ""),
        })
    return result


def list_platforms() -> dict[str, list[dict]]:
    """按平台分组列出密钥。"""
    secrets = _load_secrets()
    platforms = {}
    for key, val in secrets.items():
        platform, name = key.split("/", 1)
        if platform not in platforms:
            platforms[platform] = []
        platforms[platform].append({
            "name": name,
            "kind": val.get("kind", ""),
            "account": val.get("account", ""),
        })
    return platforms
