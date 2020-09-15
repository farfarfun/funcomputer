from notecomputer.run import run_cmd

def init():
    run_cmd("mkdir -vp /root/workspace")
    
    run_cmd("git clone git@github.com:notechats/notetool.git")
    run_cmd("git clone git@github.com:notechats/notekeras.git")
    run_cmd("git clone git@github.com:notechats/notedrive.git")
    run_cmd("git clone git@github.com:notechats/notecomputer.git")


