# Agent Secret Skills

Agent 共享密钥工具。公开仓库，任何 agent 都能用。

## d1-secret-vault

从 Cloudflare D1 加密密钥库解密读取密钥。AES-256-GCM，纯 Python。

### 完整流程

```
① 拉工具（公开，谁都能拉）
   git clone https://github.com/webkubor/agent-secret-skills.git

② 配环境变量（CF token 只需给一次）
   export CF_API_TOKEN="cfat_xxx"       # Cloudflare API Token
   export CF_ACCOUNT_ID="916ebb1b9f240bf4c8826021dd161692"
   pip install cryptography -q

③ 查密钥
   python3 d1-secret-vault/scripts/secretvault.py list
   python3 d1-secret-vault/scripts/secretvault.py get secret://gitlab/personal-pat
```

### 可用密钥

| 引用 | 用途 |
|------|------|
| `secret://feishu/nanzhu-token` | 南烛 |
| `secret://feishu/xiaonan-token` | 小楠 |
| `secret://feishu/guqiuyue-token` | 顾栖月 |
| `secret://feishu/xiaowei-token` | 小薇 |
| `secret://gitlab/personal-pat` | GitLab PAT |
| `secret://gitlab-modelgo/personal-pat` | GitLab ModelGo |
| `secret://gitlab-paylinker/personal-pat` | GitLab Paylinker |
| `secret://github/personal-pat` | GitHub PAT |
| `secret://cloudflare/api-token` | Cloudflare |
| `secret://zhipu/api-key` | 智谱 GLM |
| `secret://deepseek/api-key` | DeepSeek |
| `secret://volcengine/ark-api-key` | 火山方舟 |

### 架构

```
任何 agent（任何框架，任何机器）
  │
  ├── git clone 本仓库（公开）
  ├── CF_API_TOKEN（从 agents 表或线下获取）
  ├── pip install cryptography
  │
  ▼
  D1 cortexos-brain-db
    ├── secret_vault 表 → 密文（AES-256-GCM）
    └── site_config 表 → master key（解密钥匙）
```

不需要 CortexOS，不需要 cs CLI，不需要私有仓库权限。
