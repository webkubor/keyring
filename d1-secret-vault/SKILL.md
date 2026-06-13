---
name: d1-secret-vault
description: "D1 加密密钥库 — 通过 api.webkubor.online 解密读写密钥，仅需 AGENT_TOKEN"
version: 2.0.0
---

# D1 Secret Vault

从 D1 `cortexos-brain-db` 加密密钥库解密读取密钥。纯 Python，零框架依赖。

## 前置条件

- 环境变量 `AGENT_TOKEN`（af_ 开头的 agent token）
- Python 3 + `cryptography`（`pip install cryptography`）

## 用法

```bash
SCRIPT=d1-secret-vault/scripts/secretvault.py

# 列出所有密钥元信息（不出明文）
python3 $SCRIPT list

# 解密读取密钥明文
python3 $SCRIPT get secret://platform/name

# 存储/更新密钥（自动加密）
python3 $SCRIPT put secret://platform/name "值" --kind "API Key" --account "账号描述"

# 删除密钥
python3 $SCRIPT del secret://platform/name
```

## 常用密钥

| 引用 | 用途 |
|------|------|
| `secret://feishu/nanzhu-token` | 南烛 |
| `secret://feishu/xiaonan-token` | 小楠 |
| `secret://feishu/guqiuyue-token` | 顾栖月 |
| `secret://feishu/xiaowei-token` | 小薇 |
| `secret://gitlab/personal-pat` | GitLab |
| `secret://gitlab-modelgo/personal-pat` | GitLab ModelGo |
| `secret://gitlab-paylinker/personal-pat` | GitLab Paylinker |
| `secret://github/personal-pat` | GitHub |
| `secret://cloudflare/api-token` | Cloudflare |
| `secret://zhipu/api-key` | 智谱 GLM |
| `secret://deepseek/api-key` | DeepSeek |
| `secret://volcengine/ark-api-key` | 火山方舟 |

## 技术细节

- 加密：AES-256-GCM（客户端加解密，API 只存密文）
- Master key：API 自动获取
- 密文表：D1 `secret_vault`
- D1 数据库：`cortexos-brain-db`（a43038ff-8fe7-4aaa-b661-23238458456a）
- API 端点：`https://api.webkubor.online/content/secrets`
- 认证：Bearer token（AGENT_TOKEN）
