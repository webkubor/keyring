---
name: d1-secret-vault
description: "D1 加密密钥库 — 统一走 cs secrets（CortexOS），唯一实现，不重复造轮子"
version: 3.0.0
---

# D1 Secret Vault

从 D1 `cortexos-brain-db` 加密密钥库读写密钥。**唯一实现是 cs（CortexOS，Go）**，
所有 agent 框架统一调 `cs secrets`，不再各自维护 python/AES/HTTP 脚本。

## 前置条件

- `cs`（CortexOS）在 PATH 中
- agent token 由 cs 自动解析，按优先级：
  `AGENT_TOKEN` env > `~/CortexOS/.fleet-creds.json` > `~/.hermes/agent-token`
- 不需要 CF_API_TOKEN（cs 内部 CF token 也是从本密钥库取的）

## 用法（推荐直接用 cs）

```bash
# 解密读取
cs secrets get secret://jenkins/modelgo

# 列出元信息（不出明文）
cs secrets list

# 写入/更新（自动加密）
cs secrets set --platform jenkins --name modelgo --value "<token>" --kind "API Key" --account wangenbo

# 注入子进程环境变量，不打印明文
cs secrets run --env TOKEN=secret://jenkins/modelgo -- some-command
```

`scripts/secretvault.py` 仅是对 `cs secrets` 的薄转发层（兼容老调用），内部不含任何
密钥逻辑：`secretvault.py get|list|put` → 转发 `cs secrets get|list|set`。

## 常用密钥

| 引用 | 用途 |
|------|------|
| `secret://jenkins/modelgo` | Jenkins 部署（账号 wangenbo） |
| `secret://cloudflare/api-token` | Cloudflare API Token |
| `secret://gitlab-modelgo/personal-pat` | GitLab ModelGo |
| `secret://github/personal-pat` | GitHub |
| `secret://zhipu/api-key` / `secret://deepseek/api-key` / `secret://volcengine/ark-api-key` | 各 LLM |
| `secret://feishu/{nanzhu,xiaonan,guqiuyue,xiaowei}-token` | 各 agent 飞书 token |

## 技术细节

- 加密 AES-256-GCM（客户端加解密，API 只存密文），master key 由 API 下发
- 密文表：D1 `secret_vault`；库：`cortexos-brain-db`
- API：`https://api.webkubor.online/content/secrets`，Bearer agent token
- agent 身份鉴权：D1 `agents.token_sha256` 运行时查表（加人 `cs agent register` / 踢人 `cs agent revoke` 即时生效）
