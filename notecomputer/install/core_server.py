from notecomputer.run import run_cmd

config_dir = '/root/configs/'


def install_drive():
    from google.colab import drive
    drive.mount('/content/gdrive/')


def install_code_server():
    run_cmd("curl -fsSL https://code-server.dev/install.sh | sh")
    
    
def install_natapp():
    run_cmd("wget http://download.natapp.cn/assets/downloads/clients/2_3_9/natapp_linux_amd64/natapp -O natapp")
    run_cmd("chmod a+x natapp")
    
    
def start_code_server():
    run_cmd("mkdir -vp /root/logs/code-server/")
    run_cmd(
        "nohup code-server --auth none --config {}code/code-server.yaml >>/root/logs/code-server/code-server.log 2>&1 &".format(
            config_dir))


def start_natapp(authtoken='65a40f94924dc275'):
    run_cmd("mkdir -vp /root/logs/natapp/")
    run_cmd("nohup ./natapp -authtoken={authtoken}  >>/root/logs/natapp/natapp.log 2>&1 &".format(authtoken=authtoken))
