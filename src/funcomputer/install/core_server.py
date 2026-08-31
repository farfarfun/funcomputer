import os
from typing import Optional

from funcomputer.run import run_cmd

config_dir = "/root/configs/"


def install_drive() -> None:
    """挂载 Google Drive（仅可在 Colab 运行时环境中调用）。"""
    from google.colab import drive

    drive.mount("/content/gdrive/")


def install_code_server() -> None:
    """安装 code-server，并装一批常用 VSCode 插件。"""
    run_cmd("curl -fsSL https://code-server.dev/install.sh | sh")

    # run_cmd("code-server --config /root/configs/code/code-server.yaml --install-extension ")
    run_cmd(
        "code-server --config /root/configs/code/code-server.yaml --install-extension tushortz.python-extended-snippets"
    )
    run_cmd(
        "code-server --config /root/configs/code/code-server.yaml --install-extension ms-python.python"
    )
    run_cmd(
        "code-server --config /root/configs/code/code-server.yaml --install-extension rogalmic.bash-debug"
    )
    run_cmd(
        "code-server --config /root/configs/code/code-server.yaml --install-extension eamodio.gitlens"
    )
    run_cmd(
        "code-server --config /root/configs/code/code-server.yaml --install-extension formulahendry.code-runner"
    )
    run_cmd(
        "code-server --config /root/configs/code/code-server.yaml --install-extension spywhere.guides"
    )
    run_cmd(
        "code-server --config /root/configs/code/code-server.yaml --install-extension vscode-icons-team.vscode-icons"
    )
    run_cmd(
        "code-server --config /root/configs/code/code-server.yaml --install-extension yzhang.markdown-all-in-one"
    )
    run_cmd(
        "code-server --config /root/configs/code/code-server.yaml --install-extension akamud.vscode-theme-onedark"
    )
    run_cmd(
        "code-server --config /root/configs/code/code-server.yaml --install-extension coenraads.bracket-pair-colorizer"
    )
    run_cmd(
        "code-server --config /root/configs/code/code-server.yaml --install-extension ms-python.anaconda-extension-pack"
    )
    run_cmd(
        "code-server --config /root/configs/code/code-server.yaml --install-extension christian-kohler.path-intellisense"
    )


def install_natapp() -> None:
    """下载 natapp 内网穿透客户端并赋予可执行权限。"""
    run_cmd(
        "wget http://download.natapp.cn/assets/downloads/clients/2_3_9/natapp_linux_amd64/natapp -O natapp"
    )
    run_cmd("chmod a+x natapp")


def start_code_server(user_data_dir: Optional[str] = "/root/workspace") -> None:
    """后台启动 code-server。

    Args:
        user_data_dir: code-server 的用户数据目录，传 None 则不指定。

    Raises:
        ValueError: 未通过 `CODE_SERVER_PASSWORD` 环境变量提供密码。
    """
    password = os.environ.get("CODE_SERVER_PASSWORD")
    if not password:
        raise ValueError(
            "code-server password not provided -- set the CODE_SERVER_PASSWORD "
            "environment variable (refusing to start with --auth none, which "
            "exposes an unauthenticated remote-code-execution endpoint)"
        )
    os.environ["PASSWORD"] = password

    run_cmd("mkdir -vp /root/logs/code-server/")
    cmd = " nohup code-server"
    if user_data_dir is not None:
        cmd += " --user-data-dir " + user_data_dir
    cmd += " --auth password"
    cmd += " --config {}code/code-server.yaml".format(config_dir)
    cmd += " >>/root/logs/code-server/code-server.log 2>&1 &"
    run_cmd(cmd)


def start_natapp(authtoken: Optional[str] = None) -> None:
    """后台启动 natapp 内网穿透。

    Args:
        authtoken: natapp 的 authtoken，不传则读取 `NATAPP_AUTH_TOKEN` 环境变量。

    Raises:
        ValueError: 既未传入 authtoken 也未设置对应环境变量。
    """
    authtoken = authtoken or os.environ.get("NATAPP_AUTH_TOKEN")
    if not authtoken:
        raise ValueError(
            "natapp authtoken not provided -- pass authtoken= explicitly or "
            "set the NATAPP_AUTH_TOKEN environment variable"
        )
    run_cmd("mkdir -vp /root/logs/natapp/")
    run_cmd(
        "nohup ./natapp -authtoken={authtoken}  >>/root/logs/natapp/natapp.log 2>&1 &".format(
            authtoken=authtoken
        )
    )
