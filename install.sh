#!/bin/bash
set -e

KEYRING_DIR="$HOME/.keyring"
KEYRING_BIN="/usr/local/bin/keyring"

echo "🔐 Keyring — 安装中..."

# 检查 Python
if ! command -v python3 &>/dev/null; then
    echo "❌ 需要 Python 3.10+"
    echo "   macOS: brew install python"
    echo "   Linux: sudo apt install python3"
    exit 1
fi

# 检查 Python 版本
PY_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
PY_MAJOR=$(echo "$PY_VERSION" | cut -d. -f1)
PY_MINOR=$(echo "$PY_VERSION" | cut -d. -f2)
if [ "$PY_MAJOR" -lt 3 ] || ([ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -lt 10 ]); then
    echo "❌ 需要 Python 3.10+，当前 $PY_VERSION"
    exit 1
fi

# 安装 cryptography（如果需要）
if ! python3 -c "import cryptography" 2>/dev/null; then
    echo "📦 安装 cryptography..."
    pip3 install cryptography
fi

# 安装 keyring 模块
echo "📦 安装 keyring..."
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
KEYRING_MODULE="$SCRIPT_DIR/keyring"

if [ ! -d "$KEYRING_MODULE" ]; then
    echo "❌ 找不到 keyring 模块：$KEYRING_MODULE"
    exit 1
fi

# 复制 keyring 模块到 ~/.keyring/module
mkdir -p "$KEYRING_DIR/module"
rm -rf "$KEYRING_DIR/module/keyring"
cp -r "$KEYRING_MODULE" "$KEYRING_DIR/module/"

# 创建 keyring 命令
cat > "$KEYRING_BIN" << 'KEYRING_EOF'
#!/usr/bin/env python3
import sys
import os

KEYRING_DIR = os.path.join(os.path.expanduser("~"), ".keyring", "module")
sys.path.insert(0, KEYRING_DIR)

from keyring.cli import main
if __name__ == "__main__":
    main()
KEYRING_EOF

chmod +x "$KEYRING_BIN"

echo ""
echo "✅ 安装完成！"
echo ""
echo "开始使用："
echo "  keyring wizard                    # 交互式向导（推荐）"
echo "  keyring import --file .env        # 从 .env 导入"
echo "  keyring set secret://... \"值\"     # 手动添加"
echo ""
echo "查询："
echo "  keyring list                      # 列出所有密钥/密码"
echo "  keyring platforms                 # 查看有哪些平台"
