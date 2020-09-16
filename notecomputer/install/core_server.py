from notecomputer.run import run_cmd

config_dir = '/root/configs/'


def install_drive():
    from google.colab import drive
    drive.mount('/content/gdrive/')


def install_code_server():
    run_cmd("curl -fsSL https://code-server.dev/install.sh | sh")
    
    #run_cmd("code-server --config /root/configs/code/code-server.yaml --install-extension ")
    run_cmd("code-server --config /root/configs/code/code-server.yaml --install-extension tushortz.python-extended-snippets")
    run_cmd("code-server --config /root/configs/code/code-server.yaml --install-extension ms-python.python")
    run_cmd("code-server --config /root/configs/code/code-server.yaml --install-extension rogalmic.bash-debug")
    run_cmd("code-server --config /root/configs/code/code-server.yaml --install-extension eamodio.gitlens")
    run_cmd("code-server --config /root/configs/code/code-server.yaml --install-extension formulahendry.code-runner")
    run_cmd("code-server --config /root/configs/code/code-server.yaml --install-extension spywhere.guides")
    
    
    
def install_natapp():
    run_cmd("wget http://download.natapp.cn/assets/downloads/clients/2_3_9/natapp_linux_amd64/natapp -O natapp")
    run_cmd("chmod a+x natapp")
    

def start_code_server(user_data_dir="/root/workspace"):
    run_cmd("mkdir -vp /root/logs/code-server/")
    cmd = " nohup code-server"
    if user_data_dir is not None:
        cmd += " --user-data-dir "+user_data_dir
    cmd += " --auth none"
    cmd += " --config {}code/code-server.yaml".format(config_dir)
    cmd += " >>/root/logs/code-server/code-server.log 2>&1 &"
    run_cmd(cmd)


def start_natapp(authtoken='65a40f94924dc275'):
    run_cmd("mkdir -vp /root/logs/natapp/")
    run_cmd("nohup ./natapp -authtoken={authtoken}  >>/root/logs/natapp/natapp.log 2>&1 &".format(authtoken=authtoken))
