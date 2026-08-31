from funcomputer.run import run_cmd


def config_all() -> None:
    """从 Google Drive 恢复 ssh 配置，并把个人 configs 目录整体拷贝到 `/root/`。"""
    config_ssh()
    run_cmd("cp -rf '/content/gdrive/My Drive/core/configs/' '/root/'")


def config_ssh() -> None:
    """从 Google Drive 恢复 ssh 私钥/公钥和 `.pypirc` 到 `/root/`。"""
    # run_cmd("cp -r '/root/.ssh' '/content/gdrive/My Drive/core/configs/ssh'")
    run_cmd("cp -rf '/content/gdrive/My Drive/core/configs/ssh/id_rsa' '/root/.ssh/'")
    run_cmd("cp -rf '/content/gdrive/My Drive/core/configs/ssh/id_rsa.pub' '/root/.ssh/'")
    run_cmd("cp -rf '/content/gdrive/My Drive/core/configs/root/.pypirc' '/root/.pypirc'")
