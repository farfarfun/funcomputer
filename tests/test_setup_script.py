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


def test_status_reports_every_service():
    result = run_setup("status")

    assert result.returncode == 0
    assert result.stdout.splitlines() == [
        "code-server 未运行",
        "natapp 未运行",
    ]


def test_status_can_filter_service():
    result = run_setup("status", "natapp")

    assert result.returncode == 0
    assert result.stdout.strip() == "natapp 未运行"


def test_invalid_arguments_show_usage():
    result = run_setup("start", "unknown")

    assert result.returncode == 1
    assert "用法:" in result.stderr
    assert run_setup("start", "code-server", "dev").returncode == 1


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


def test_start_reports_and_replaces_stale_pid_file(clean_run_dir, tmp_path):
    pid_file = clean_run_dir / "code-server.pid"
    clean_run_dir.mkdir()
    pid_file.write_text("999999\n")
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    fake_server = fake_bin / "code-server"
    fake_server.write_text("#!/bin/sh\nexec sleep 300\n")
    fake_server.chmod(0o755)
    env = dict(os.environ)
    env["PATH"] = f"{fake_bin}{os.pathsep}{env['PATH']}"
    env["CODE_SERVER_PASSWORD"] = "test-password"

    result = run_setup("start", "code-server", env=env)

    try:
        assert result.returncode == 0, result.stderr
        assert "检测到陈旧 PID 文件" in result.stderr
    finally:
        run_setup("stop", "code-server")


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

    started = run_setup("start", "code-server", env=env)
    assert started.returncode == 0, started.stderr

    pid_file = clean_run_dir / "code-server.pid"
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

    assert run_setup("status", "code-server").stdout.strip() == (
        f"code-server 运行中 (pid {pid})"
    )

    stopped = run_setup("stop", "code-server")
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
