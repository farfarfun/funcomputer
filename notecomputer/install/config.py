from .base import run_cmd


def config_all():
    config_ssh()
    run_cmd("cp -rf '/content/gdrive/My Drive/core/configs/' '~/'")


def config_ssh():
    # run_cmd("cp -r '/root/.ssh' '/content/gdrive/My Drive/core/configs/ssh'")
    run_cmd("cp -rf '/content/gdrive/My Drive/core/configs/ssh/id_rsa' '~/.ssh/'")
    run_cmd("cp -rf '/content/gdrive/My Drive/core/configs/ssh/id_rsa.pub' '~/.ssh/'")
