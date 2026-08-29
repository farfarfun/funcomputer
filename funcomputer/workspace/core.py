from funcomputer.run import run_cmd

def init():
    run_cmd("mkdir -vp /root/workspace")
    
    run_cmd("git clone git@github.com:farfarfun/funtool.git")
    run_cmd("git clone git@github.com:farfarfun/funkeras.git")
    run_cmd("git clone git@github.com:farfarfun/fundrive.git")
    run_cmd("git clone git@github.com:farfarfun/funcomputer.git")


