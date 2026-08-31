from farlog import getLogger

from funcomputer.run import run_cmd

logger = getLogger("funcomputer.install.config")


def config_all() -> None:
    """依次执行 init/ssh/git/workspace 全部配置步骤，并整体拷贝个人 configs 目录。"""
    config_init()
    config_ssh()
    config_git()
    config_workspace()
    run_cmd("cp -rf '/content/gdrive/My Drive/core/configs/' '/root/'")
    logger.info("config all done")


def config_init() -> None:
    """升级 pip，并安装 twine、pyecharts、pylint 等常用工具。"""
    run_cmd("pip3 install -U pip")
    run_cmd("pip3 install -U twine")
    run_cmd("pip3 install -U pyecharts pylint")


def config_ssh() -> None:
    """从 Google Drive 恢复 ssh 私钥/公钥和 `.pypirc` 到 `/root/`。"""
    # run_cmd("cp -r '/root/.ssh' '/content/gdrive/My Drive/core/configs/ssh'")
    run_cmd("cp -rf '/content/gdrive/My Drive/core/configs/ssh/id_rsa' '/root/.ssh/'")
    run_cmd("cp -rf '/content/gdrive/My Drive/core/configs/ssh/id_rsa.pub' '/root/.ssh/'")
    run_cmd("cp -rf '/content/gdrive/My Drive/core/configs/root/.pypirc' '/root/.pypirc'")
    logger.info("config ssh done")


def config_git() -> None:
    """恢复 ssh key 并写入全局 git 用户名/邮箱。"""
    run_cmd("cp -rf '/content/gdrive/My Drive/core/configs/ssh/id_rsa' '/root/.ssh/'")
    run_cmd("cp -rf '/content/gdrive/My Drive/core/configs/ssh/id_rsa.pub' '/root/.ssh/'")

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
