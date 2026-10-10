from funcomputer.run import run_cmd


def init() -> None:
    """创建 `/root/workspace` 并克隆 fun 系列仓库进去。"""
    run_cmd("mkdir -vp /root/workspace")
    run_cmd(
        [
            "cd /root/workspace",
            "git clone git@github.com:farfarfun/funtool.git",
            "git clone git@github.com:farfarfun/funkeras.git",
            "git clone git@github.com:farfarfun/fundrive.git",
            "git clone git@github.com:farfarfun/funcomputer.git",
        ]
    )
