import os

config_dir = os.path.abspath(os.path.dirname(__file__)) + '/configs/'

def run_cmd(cmd):
    print(cmd)
    #return os.system(cmd)

def install_code_server():
    run_cmd("curl -fsSL https://code-server.dev/install.sh | sh")
    run_cmd("!code-server --auth none --config {}code-server.yaml >>/content/code-server-2.log 2>&1 &".format(config_dir))
    
