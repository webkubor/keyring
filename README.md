# Agent Secret Skills

Agent 共享密钥工具。公开仓库，任何 agent 都能用。

## 完整流程（从零到拿到密钥）

```bash
# ── ① 拉工具 ──
git clone https://github.com/webkubor/agent-secret-skills.git
cd agent-secret-skills
pip install cryptography -q

# ── ② 设置 AGENT_TOKEN ──
# 每个 agent 的唯一凭证（af_ 开头），所有密钥操作靠它鉴权。
#
# 怎么拿：
#   · 团队 agent（南烛/小楠/顾栖月等）→ 栖洲或小楠分配，存在 ~/.hermes/agent-token
#   · 新 agent → 联系小楠（Lunove）或栖洲（王恩博）分配
#   · 已在服务器上 → export AGENT_TOKEN=$(cat ~/.hermes/agent-token)
#
export AGENT_TOKEN="af_xxx..."

# ── ③ 查密钥 ──
python3 d1-secret-vault/scripts/secretvault.py list                    # 看有哪些
python3 d1-secret-vault/scripts/secretvault.py get secret://cloudflare/api-token  # 解密读取

# ── ④ 存密钥（可选）──
python3 d1-secret-vault/scripts/secretvault.py put secret://platform/name "值" --kind "API Key"
python3 d1-secret-vault/scripts/secretvault.py del secret://platform/name
```

## 可用密钥

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

## 架构

```
AGENT_TOKEN (af_xxx)
    ↓ Bearer Auth
api.webkubor.online/content/secrets/
    ↓
D1 cortexos-brain-db
    ├── secret_vault 表 → AES-256-GCM 密文
    └── site_config 表 → master key
```

不需要 CortexOS，不需要 cs CLI，不需要私有仓库权限，不需要 CF API token。
