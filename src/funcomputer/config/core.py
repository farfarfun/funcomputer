import os


def config_all() -> None:
    """检查 SSH agent 配置。"""
    config_ssh()


def config_ssh() -> None:
    """使用环境中已配置的 SSH agent，不复制私钥或 PyPI 凭据文件。"""
    if not os.environ.get("SSH_AUTH_SOCK"):
        raise RuntimeError("未配置 SSH agent，请先设置 SSH_AUTH_SOCK")
