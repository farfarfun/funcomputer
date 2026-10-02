import os

from farlog import getLogger

from funcomputer.run import run_cmd

logger = getLogger("funcomputer.install.config")


def config_all() -> None:
    """依次执行工具、git、workspace 配置步骤。"""
    config_init()
    config_ssh()
    config_git()
    config_workspace()
    logger.info("config all done")


def config_init() -> None:
    """使用 uv 安装常用命令行工具。"""
    run_cmd("uv tool install twine")
    run_cmd("uv tool install pyecharts")
    run_cmd("uv tool install ruff")


def config_ssh() -> None:
    """使用环境中已配置的 SSH agent，不复制私钥或 PyPI 凭据文件。"""
    if not os.environ.get("SSH_AUTH_SOCK"):
        raise RuntimeError("未配置 SSH agent，请先设置 SSH_AUTH_SOCK")
    logger.info("config ssh done")


def config_git() -> None:
    """写入全局 git 用户名和邮箱。"""
    run_cmd('git config --global user.email "1007530194@qq.com"')
    run_cmd('git config --global user.name "niuliangtao"')
    logger.info("config git done")


def config_workspace() -> None:
    """创建 `/root/workspace`，恢复 VSCode 配置，并克隆 fun 系列仓库。"""
    run_cmd("mkdir -vp /root/workspace")
    run_cmd("mkdir -vp /root/workspace/.vscode")
    run_cmd(
        "cp -rf '/content/gdrive/My Drive/core/configs/core/settings.json' '/root/workspace/.vscode/'"
    )

    run_cmd(
        [
            "cd /root/workspace",
            "git clone git@github.com:farfarfun/funtool.git",
            "git clone git@github.com:farfarfun/funkeras.git",
            "git clone git@github.com:farfarfun/fundrive.git",
            "git clone git@github.com:farfarfun/funcomputer.git",
        ]
    )
    logger.info("config workspace done")
