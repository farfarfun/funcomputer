from notecomputer.core import run_cmd


def config_all():
    config_ssh()
    run_cmd("cp -rf '/content/gdrive/My Drive/core/configs/' '/root/'")


def config_ssh():
    # run_cmd("cp -r '/root/.ssh' '/content/gdrive/My Drive/core/configs/ssh'")
    run_cmd("cp -rf '/content/gdrive/My Drive/core/configs/ssh/id_rsa' '/root/.ssh/'")
    run_cmd("cp -rf '/content/gdrive/My Drive/core/configs/ssh/id_rsa.pub' '/root/.ssh/'")
    run_cmd("cp -rf '/content/gdrive/My Drive/core/configs/root/.pypirc' '/root/.pypirc'")
