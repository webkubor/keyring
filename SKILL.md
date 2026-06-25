---
name: keyring
version: 1.0.0
description: "本地加密密钥/密码管理 — AES-256-GCM 加密，AI 能注入但看不到明文。触发条件: 需要管理密钥、密码、API Token 时触发。触发词: 密钥、secret、token、API key、password、keyring。"
license: MIT
author: webkubor
category: security
platforms: [linux, macos]
metadata:
  openclaw:
    tags: [security, secrets, passwords, encryption, keyring]
    requires:
      python: [>=3.10, cryptography>=41.0]
---

# Keyring

本地加密密钥/密码库 — 人存一次，AI 用别名注入，永远看不到明文。

## 用户流程（小白也能用）

### 方式一：一键安装

```bash
curl -sSL https://raw.githubusercontent.com/.../install.sh | bash
keyring wizard
```

### 方式二：手动

```bash
pip install -e .
keyring init
```

### 存密钥/密码

```bash
# 存 GitHub token
keyring set secret://github/my-pat "ghp_xxx" --kind "API Key"

# 存密码
keyring set secret://gmail/my-password "123456" --kind "Password" --account "user@gmail.com"

# 存 SSH 密钥
keyring set secret://ssh/my-server "$(cat ~/.ssh/id_rsa)" --kind "SSH Key"
```

### 建别名（方便 AI 使用）

```bash
keyring alias set github_token secret://github/my-pat
keyring alias set gmail_password secret://gmail/my-password
```

### AI 使用（不打印明文）

```bash
# AI 推代码
keyring run --env GITHUB_TOKEN=github_token -- git push

# AI 调 API
keyring run --env DEEPSEEK_API_KEY=deepseek_key -- python app.py
```

## 查询密码

```bash
# 列出所有密钥/密码
keyring list

# 按平台过滤
keyring list --platform gmail
keyring list --platform github

# 查看有哪些平台
keyring platforms
```

## 双模式设计

| 模式 | 命令 | 谁用 | AI 能否读明文 |
|------|------|------|--------------|
| 交互式 | `keyring get github_token` | 人 | 能（但不该） |
| 非交互式 | `keyring run --env X=github_token -- cmd` | AI | **不能** |

## 从 .env 导入

```bash
# 预览会导入什么
keyring import --file .env --dry-run

# 实际导入
keyring import --file .env

# 只导入以 GITHUB_ 开头的
keyring import --file .env --prefix GITHUB_
```

## AI Agent 怎么用

AI 遇到需要 token/密码时：

```
用户: 帮我登录 Gmail 发邮件
AI:   我需要你的 Gmail 密码。请运行：
      keyring set secret://gmail/my-password "你的密码" --kind "Password"
用户: （已设置）
AI:   keyring run --env GMAIL_PASSWORD=gmail_password -- python send_email.py
```

AI 看到的是 `gmail_password` 别名，不是明文值。

## 命令速查

```bash
keyring init                          # 初始化
keyring wizard                        # 交互式向导
keyring set secret://... "值"         # 存密钥/密码
keyring get 别名                      # 读取（打印明文）
keyring delete secret://...           # 删除
keyring list                          # 列出所有
keyring list --platform gmail         # 按平台过滤
keyring platforms                     # 查看有哪些平台
keyring alias set 别名 secret://...   # 建别名
keyring alias list                    # 列出别名
keyring run --env X=别名 -- cmd       # 注入 env（AI 用）
keyring import --file .env            # 从 .env 导入
keyring import --file .env --dry-run  # 预览导入
```

## 文件结构

```
~/.keyring/
├── master.key       # AES-256 密钥（chmod 600）
├── secrets.json     # 加密后的密钥/密码
└── aliases.json     # 别名映射
```
