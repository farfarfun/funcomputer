import os

def run_cmd(cmd):
    if isinstance(cmd,list):
        cmd = ' && '.join(cmd)
    # print(cmd)
    os.system(cmd)

