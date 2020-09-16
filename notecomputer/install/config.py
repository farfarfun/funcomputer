from notecomputer.run import run_cmd
from notetool.tool.log import log
logger = log(name="config")

def config_all():
    config_init()
    config_ssh()
    config_git()
    config_workspace()
    run_cmd("cp -rf '/content/gdrive/My Drive/core/configs/' '/root/'")
    logger.info("config all done")


def config_init():
    run_cmd("pip3 install -U pip")
    run_cmd("pip3 install -U twine")
    run_cmd("pip3 install -U pyecharts pylint")
    
    

def config_ssh():
    # run_cmd("cp -r '/root/.ssh' '/content/gdrive/My Drive/core/configs/ssh'")
    run_cmd("cp -rf '/content/gdrive/My Drive/core/configs/ssh/id_rsa' '/root/.ssh/'")
    run_cmd("cp -rf '/content/gdrive/My Drive/core/configs/ssh/id_rsa.pub' '/root/.ssh/'")
    run_cmd("cp -rf '/content/gdrive/My Drive/core/configs/root/.pypirc' '/root/.pypirc'")
    logger.info("config ssh done")


def config_git():
    run_cmd("cp -rf '/content/gdrive/My Drive/core/configs/ssh/id_rsa' '/root/.ssh/'")
    run_cmd("cp -rf '/content/gdrive/My Drive/core/configs/ssh/id_rsa.pub' '/root/.ssh/'")

    run_cmd('git config --global user.email "1007530194@qq.com"')
    run_cmd('git config --global user.name "niuliangtao"')
    logger.info("config git done")


def config_workspace():
    run_cmd(["cd /root","mkdir -vp /root/workspace"])

    run_cmd(["cd /root/workspace",
    "git clone git@github.com:notechats/notetool.git",
    "git clone git@github.com:notechats/notekeras.git",
    "git clone git@github.com:notechats/notedrive.git",
    "git clone git@github.com:notechats/notecomputer.git"
    ])
    logger.info("config workspace done")

