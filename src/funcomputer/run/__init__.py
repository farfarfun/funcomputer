from funshell import run_shell, run_shell_list


def run_cmd(cmd: str | list[str]) -> None:
    """执行 shell 命令。

    Args:
        cmd: 单条命令字符串，或多条命令组成的列表（列表按顺序用 `&&` 连接执行，
            前一条失败则后面的不再执行）。

    Raises:
        RuntimeError: 命令以非 0 状态退出。
    """
    if isinstance(cmd, list):
        code = run_shell_list(cmd)
    else:
        code = run_shell(cmd)
    if code != "0":
        raise RuntimeError(f"command failed (exit {code}): {cmd}")
