"""vault CLI — 命令行入口，纯本地，零网络依赖。"""

import argparse
import os
import subprocess
import sys

from . import __version__
from .store import (
    init_master_key,
    get_secret,
    set_secret,
    delete_secret,
    list_secrets,
    list_platforms,
    parse_ref,
)
from .alias import (
    set_alias,
    get_alias,
    resolve_ref,
    list_aliases,
    delete_alias,
)
from .wizard import wizard
from .import_env import import_env_file


def cmd_get(args: argparse.Namespace) -> None:
    """读取密钥并打印明文（供人使用）。"""
    ref = resolve_ref(args.ref)
    try:
        plaintext = get_secret(ref)
        if plaintext is None:
            print(f"未找到：{ref}", file=sys.stderr)
            sys.exit(1)
        print(plaintext, end="")
    except ValueError as e:
        print(f"错误：{e}", file=sys.stderr)
        sys.exit(1)


def cmd_list(args: argparse.Namespace) -> None:
    """列出密钥，支持按平台过滤。"""
    secrets = list_secrets()
    if not secrets:
        print("（空）")
        return

    # 按平台过滤
    if args.platform:
        secrets = [s for s in secrets if s["platform"] == args.platform]
        if not secrets:
            print(f"平台 {args.platform} 下没有密钥")
            return

    for s in secrets:
        account = f" ({s['account']})" if s.get("account") else ""
        print(f"  secret://{s['platform']}/{s['name']}{account}  [{s.get('kind', '?')}]")


def cmd_platforms(args: argparse.Namespace) -> None:
    """列出所有平台及其密钥数量。"""
    platforms = list_platforms()
    if not platforms:
        print("（空）")
        return
    print("平台  密钥数")
    print("-" * 30)
    for platform, secrets in sorted(platforms.items()):
        kinds = ", ".join(set(s["kind"] for s in secrets))
        print(f"  {platform:<15} {len(secrets)}  [{kinds}]")


def cmd_set(args: argparse.Namespace) -> None:
    """写入/更新密钥。"""
    try:
        set_secret(args.ref, args.value, kind=args.kind, account=args.account)
        platform, name = parse_ref(args.ref)
        print(f"✓ secret://{platform}/{name} 已保存")
    except ValueError as e:
        print(f"错误：{e}", file=sys.stderr)
        sys.exit(1)


def cmd_delete(args: argparse.Namespace) -> None:
    """删除密钥。"""
    try:
        if delete_secret(args.ref):
            platform, name = parse_ref(args.ref)
            print(f"✓ secret://{platform}/{name} 已删除")
        else:
            print(f"未找到：{args.ref}", file=sys.stderr)
            sys.exit(1)
    except ValueError as e:
        print(f"错误：{e}", file=sys.stderr)
        sys.exit(1)


def cmd_run(args: argparse.Namespace) -> None:
    """非交互式：注入环境变量到子进程，AI 无法读取明文。

    vault run --env TOKEN=github_token -- python app.py
    vault run --env TOKEN=secret://github/pat -- python app.py
    """
    env = os.environ.copy()

    for env_spec in args.env:
        if "=" not in env_spec:
            print(f"格式错误：{env_spec}，应为 NAME=secret://... 或 NAME=别名", file=sys.stderr)
            sys.exit(1)
        var_name, ref_or_alias = env_spec.split("=", 1)
        ref = resolve_ref(ref_or_alias)
        try:
            value = get_secret(ref)
            if value is None:
                print(f"未找到：{ref}", file=sys.stderr)
                sys.exit(1)
            env[var_name] = value
        except ValueError as e:
            print(f"错误：{e}", file=sys.stderr)
            sys.exit(1)

    # 过滤掉 -- 分隔符
    command = [c for c in args.command if c != "--"]
    if not command:
        print("错误：未指定命令", file=sys.stderr)
        sys.exit(1)

    result = subprocess.run(command, env=env)
    sys.exit(result.returncode)


def cmd_alias(args: argparse.Namespace) -> None:
    """管理别名。"""
    if args.alias_action == "set":
        set_alias(args.name, args.ref)
        print(f"✓ {args.name} → {args.ref}")
    elif args.alias_action == "get":
        ref = get_alias(args.name)
        if ref:
            print(ref)
        else:
            print(f"未找到别名：{args.name}", file=sys.stderr)
            sys.exit(1)
    elif args.alias_action == "list":
        aliases = list_aliases()
        if not aliases:
            print("（空）")
            return
        for name, ref in aliases.items():
            print(f"  {name} → {ref}")
    elif args.alias_action == "delete":
        if delete_alias(args.name):
            print(f"✓ 已删除别名：{args.name}")
        else:
            print(f"未找到别名：{args.name}", file=sys.stderr)
            sys.exit(1)


def cmd_init(args: argparse.Namespace) -> None:
    """初始化 master key。"""
    master_key = init_master_key()
    print(f"✓ Master key 已生成：~/.keyring/master.key")
    print(f"\n开始使用：")
    print(f"  keyring wizard              # 交互式向导")
    print(f"  keyring import --file .env  # 从 .env 导入")
    print(f"  keyring set secret://...    # 手动添加")


def cmd_wizard(args: argparse.Namespace) -> None:
    """交互式设置向导。"""
    wizard()


def cmd_import(args: argparse.Namespace) -> None:
    """从 .env 文件导入。"""
    if args.dry_run:
        print("预览模式（不会实际导入）：")
        print()
    imported = import_env_file(
        filepath=args.file,
        prefix=args.prefix,
        dry_run=args.dry_run,
        auto_alias=not args.no_alias,
    )
    if args.dry_run:
        print()
        print(f"共 {len(imported)} 个密钥将被导入。")
        print("去掉 --dry-run 执行实际导入。")
    else:
        print(f"\n✓ 已导入 {len(imported)} 个密钥")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="keyring",
        description="轻量级加密密钥管理 — AES-256-GCM，纯本地存储",
    )
    parser.add_argument("-V", "--version", action="version", version=f"vault {__version__}")
    sub = parser.add_subparsers(dest="command", help="子命令")

    # get — 支持别名
    p_get = sub.add_parser("get", help="读取密钥（打印明文）")
    p_get.add_argument("ref", help="secret://platform/name 或别名")
    p_get.set_defaults(func=cmd_get)

    # list
    p_list = sub.add_parser("list", help="列出密钥（支持按平台过滤）")
    p_list.add_argument("--platform", "-p", help="只显示指定平台的密钥")
    p_list.set_defaults(func=cmd_list)

    # platforms
    p_platforms = sub.add_parser("platforms", help="列出所有平台及密钥数量")
    p_platforms.set_defaults(func=cmd_platforms)

    # set
    p_set = sub.add_parser("set", help="写入/更新密钥")
    p_set.add_argument("ref", help="secret://platform/name")
    p_set.add_argument("value", help="密钥值")
    p_set.add_argument("--kind", default="API Key", help="密钥类型")
    p_set.add_argument("--account", default="", help="关联账号")
    p_set.set_defaults(func=cmd_set)

    # delete
    p_del = sub.add_parser("delete", help="删除密钥")
    p_del.add_argument("ref", help="secret://platform/name")
    p_del.set_defaults(func=cmd_delete)

    # run — 支持别名
    p_run = sub.add_parser("run", help="注入环境变量到子进程（不打印明文）")
    p_run.add_argument("--env", action="append", default=[], metavar="NAME=别名或secret://...",
                        help="注入环境变量，可多次使用")
    p_run.add_argument("command", nargs=argparse.REMAINDER, help="要执行的命令")
    p_run.set_defaults(func=cmd_run)

    # alias — 管理别名
    p_alias = sub.add_parser("alias", help="管理别名")
    p_alias_sub = p_alias.add_subparsers(dest="alias_action", help="别名操作")

    p_alias_set = p_alias_sub.add_parser("set", help="设置别名")
    p_alias_set.add_argument("name", help="别名名称（如 github_token）")
    p_alias_set.add_argument("ref", help="secret:// 引用")

    p_alias_get = p_alias_sub.add_parser("get", help="查看别名")
    p_alias_get.add_argument("name", help="别名名称")

    p_alias_list = p_alias_sub.add_parser("list", help="列出所有别名")

    p_alias_del = p_alias_sub.add_parser("delete", help="删除别名")
    p_alias_del.add_argument("name", help="别名名称")

    p_alias.set_defaults(func=cmd_alias)

    # init
    p_init = sub.add_parser("init", help="初始化 master key")
    p_init.set_defaults(func=cmd_init)

    # wizard
    p_wizard = sub.add_parser("wizard", help="交互式设置向导")
    p_wizard.set_defaults(func=cmd_wizard)

    # import
    p_import = sub.add_parser("import", help="从 .env 文件导入密钥")
    p_import.add_argument("--file", "-f", default=".env", help=".env 文件路径（默认 .env）")
    p_import.add_argument("--prefix", "-p", default="", help="只导入以此开头的环境变量")
    p_import.add_argument("--dry-run", "-n", action="store_true", help="预览模式，不实际导入")
    p_import.add_argument("--no-alias", action="store_true", help="不自动创建别名")
    p_import.set_defaults(func=cmd_import)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)
    args.func(args)
