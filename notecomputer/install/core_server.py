from .base import run_cmd

config_dir = '~/configs/'


def install_drive():
    from google.colab import drive
    drive.mount('/content/gdrive/')


def install_code_server():
    run_cmd("curl -fsSL https://code-server.dev/install.sh | sh")
    run_cmd("mkdir -vp ~/logs/code-server/")

    run_cmd(
        "nohup code-server --auth none --config {}code/code-server.yaml >>~/logs/code-server/code-server.log 2>&1 &".format(
            config_dir))


def install_natapp():
    run_cmd("wget http://download.natapp.cn/assets/downloads/clients/2_3_9/natapp_linux_amd64/natapp -O natapp")
    run_cmd("chmod a+x natapp")

    run_cmd("mkdir -vp ~/logs/natapp/")
    run_cmd("nohup ./natapp -authtoken=65a40f94924dc275  >>~/logs/natapp/natapp.log 2>&1 &")
