# 🔐 Keyring — 本地加密密钥/密码管理

> **人存一次，AI 用别名注入，永远看不到明文。**

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)

---

## 🔥 3 句话说明白

1. **存密钥/密码：** `keyring set secret://github/my-pat "ghp_xxx"`
2. **建别名：** `keyring alias set github_token secret://github/my-pat`
3. **AI 用：** `keyring run --env GITHUB_TOKEN=github_token -- git push`

**AI 永远只看到 `github_token`，看不到 `ghp_xxx`。**

---

## ⚡ 小白 30 秒上手

```bash
# 1. 安装
pip install -e .

# 2. 初始化
keyring init

# 3. 存密钥
keyring set secret://github/my-pat "ghp_你的token" --kind "API Key"

# 4. 存密码
keyring set secret://gmail/my-password "你的密码" --kind "Password"

# 5. 建别名
keyring alias set github_token secret://github/my-pat

# 6. AI 用
keyring run --env GITHUB_TOKEN=github_token -- git push
```

---

## 🎯 查询密码

```bash
# 列出所有
keyring list

# 按平台过滤
keyring list --platform gmail

# 查看有哪些平台
keyring platforms
```

---

## 🤖 AI Agent 怎么用

```
用户: 帮我部署到 GitHub
AI:   keyring run --env GITHUB_TOKEN=github_token -- git push

用户: 帮我发邮件
AI:   keyring run --env GMAIL_PASSWORD=gmail_password -- python send_email.py
```

AI 看到的是别名，不是明文。

---

## 📁 文件结构

```
~/.keyring/
├── master.key       # AES-256 密钥（chmod 600）
├── secrets.json     # 加密后的密钥/密码
└── aliases.json     # 别名映射
```

---

## 📋 命令速查

| 命令 | 用途 |
|------|------|
| `keyring init` | 初始化 |
| `keyring wizard` | 交互式向导 |
| `keyring set` | 存密钥/密码 |
| `keyring get` | 读取（打印明文） |
| `keyring delete` | 删除 |
| `keyring list` | 列出所有 |
| `keyring list -p gmail` | 按平台过滤 |
| `keyring platforms` | 查看平台列表 |
| `keyring alias set` | 建别名 |
| `keyring alias list` | 列出别名 |
| `keyring run` | 注入 env（AI 用） |
| `keyring import -f .env` | 从 .env 导入 |

---

Built with 🔐 by [webkubor](https://github.com/webkubor)
