#!/usr/bin/env python3
"""d1-secret-vault — 对 `cs secrets` 的薄转发层（thin shim）。

密钥库的唯一实现是 cs（CortexOS，Go）。本脚本不再自带 AES/HTTP/token 逻辑，
只把调用转发给 `cs secrets`，避免「不同 agent 框架各维护一套脚本/密钥逻辑」。

前置：cs 在 PATH 中（CortexOS）。agent token 由 cs 统一解析
（AGENT_TOKEN env > ~/CortexOS/.fleet-creds.json > ~/.hermes/agent-token）。

用法：
  secretvault.py get  secret://platform/name
  secretvault.py list
  secretvault.py put  secret://platform/name "值" [--kind 类型] [--account 账号]
  （等价于直接用 cs secrets get / list / set —— 推荐直接用 cs）
"""
import shutil
import subprocess
import sys


def _need_cs() -> None:
    if shutil.which("cs") is None:
        sys.exit("错误：未找到 cs（CortexOS）。密钥库已统一收口到 cs，请先安装 cs。")


def _parse_ref(ref: str):
    if not ref.startswith("secret://"):
        sys.exit("引用格式错误，应为 secret://platform/name")
    parts = ref[len("secret://"):].split("/", 1)
    if len(parts) != 2:
        sys.exit(f"引用格式错误：{ref}")
    return parts[0], parts[1]


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    _need_cs()
    cmd = sys.argv[1]
    args = sys.argv[2:]

    if cmd == "get":
        if not args:
            sys.exit("用法：secretvault.py get secret://platform/name")
        sys.exit(subprocess.call(["cs", "secrets", "get", args[0]]))

    if cmd == "list":
        sys.exit(subprocess.call(["cs", "secrets", "list", *args]))

    if cmd == "put":
        if len(args) < 2:
            sys.exit('用法：secretvault.py put secret://platform/name "值" [--kind ..] [--account ..]')
        platform, name = _parse_ref(args[0])
        value = args[1]
        passthrough = args[2:]  # --kind / --account 直接透传给 cs secrets set
        sys.exit(subprocess.call([
            "cs", "secrets", "set",
            "--platform", platform, "--name", name, "--value", value,
            *passthrough,
        ]))

    if cmd == "del":
        sys.exit("cs secrets 暂无 del 子命令；如需删除请在 D1 secret_vault 表手动处理或扩展 cs。")

    sys.exit(f"未知子命令：{cmd}\n{__doc__}")


if __name__ == "__main__":
    main()
