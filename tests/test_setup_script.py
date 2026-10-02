import contextlib
import os
import shutil
import signal
import subprocess
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[1]
SETUP = ROOT / "scripts" / "setup.sh"
RUN_DIR = ROOT / ".run"


def run_setup(*args, env=None):
    return subprocess.run(
        [str(SETUP), *args],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )


def test_status_reports_every_service_and_environment():
    result = run_setup("status")

    assert result.returncode == 0
    assert result.stdout.splitlines() == [
        "code-server[dev] 未运行",
        "code-server[prod] 未运行",
        "natapp[dev] 未运行",
        "natapp[prod] 未运行",
    ]


def test_status_can_filter_service():
    result = run_setup("status", "natapp")

    assert result.returncode == 0
    assert result.stdout.splitlines() == [
        "natapp[dev] 未运行",
        "natapp[prod] 未运行",
    ]


def test_invalid_arguments_show_usage():
    result = run_setup("start", "unknown", "dev")

    assert result.returncode == 1
    assert "用法:" in result.stderr


def _pid_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except (OSError, ProcessLookupError):
        return False
    return True


@pytest.fixture
def clean_run_dir():
    """每个生命周期测试前后都清空 `.run/`，避免污染 status 相关测试。"""
    shutil.rmtree(RUN_DIR, ignore_errors=True)
    yield RUN_DIR
    shutil.rmtree(RUN_DIR, ignore_errors=True)


def test_start_prod_refuses_to_run_repo_source(clean_run_dir):
    """prod 校验失败后必须真正中止，不能继续把源码跑起来。

    回归用例：`nohup bash -c` 起的是新 shell，不继承脚本顶部的 `set -e`，
    早先只写 `check_prod_installed` 导致校验失败也照样执行 python3。
    """
    result = run_setup("start", "code-server", "prod")

    assert result.returncode == 0, result.stderr
    log = clean_run_dir / "code-server-prod.log"
    for _ in range(50):
        if log.is_file() and log.read_text():
            break
        time.sleep(0.1)

    content = log.read_text()
    assert "prod 模式禁止直接跑源码" in content
    # 校验生效的标志：日志里只有校验错误，没有 start_code_server 真正执行留下的痕迹。
    assert "start_code_server" not in content
    assert "Traceback" not in content
    assert run_setup("status", "code-server", "prod").stdout.strip() == (
        "code-server[prod] 未运行"
    )


def test_stop_kills_the_whole_service_process_tree(tmp_path, clean_run_dir):
    """stop 必须把包装层、python 解释器和底下真正的服务一起带走。

    回归用例：早先 `kill $pid` 只杀 nohup 的 bash 包装层，python 与它启动的
    code-server 会被 reparent 成孤儿继续运行，而脚本已经打印了「已停止」。
    """
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    fake_server = fake_bin / "code-server"
    fake_server.write_text("#!/bin/sh\nexec sleep 300\n")
    fake_server.chmod(0o755)

    env = dict(os.environ)
    env["PATH"] = f"{fake_bin}{os.pathsep}{env['PATH']}"
    env["CODE_SERVER_PASSWORD"] = "test-password"

    started = run_setup("start", "code-server", "dev", env=env)
    assert started.returncode == 0, started.stderr

    pid_file = clean_run_dir / "code-server-dev.pid"
    pid = int(pid_file.read_text().strip())

    # 等整条 bash -> python3 -> sh -> code-server 链路起来
    descendants: list[int] = []
    for _ in range(50):
        descendants = _process_group_members(pid)
        if len(descendants) >= 3:
            break
        time.sleep(0.1)
    assert len(descendants) >= 3, f"服务进程树没起来: {descendants}"
    # setsid 的效果：整棵树和 pid 同一个进程组，pid 自己是组长
    assert all(_pgid_of(member) == pid for member in descendants)

    assert run_setup("status", "code-server", "dev").stdout.strip() == (
        f"code-server[dev] 运行中 (pid {pid})"
    )

    stopped = run_setup("stop", "code-server", "dev")
    assert stopped.returncode == 0, stopped.stderr
    assert "已停止" in stopped.stdout

    for _ in range(50):
        if not any(_pid_alive(member) for member in descendants):
            break
        time.sleep(0.1)

    survivors = [member for member in descendants if _pid_alive(member)]
    for member in survivors:  # 断言失败也别把残留进程留给后续测试
        with contextlib.suppress(OSError):
            os.kill(member, signal.SIGKILL)
    assert not survivors, f"stop 之后仍有残留进程: {survivors}"
    assert not pid_file.exists()


def _process_group_members(pgid: int) -> list[int]:
    result = subprocess.run(
        ["ps", "-o", "pid=", "-g", str(pgid)],
        check=False,
        capture_output=True,
        text=True,
    )
    return [int(line) for line in result.stdout.split()]


def _pgid_of(pid: int) -> int | None:
    try:
        return os.getpgid(pid)
    except OSError:
        return None
