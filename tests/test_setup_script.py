import subprocess
from pathlib import Path

ROOT = Path(__file__).parents[1]
SETUP = ROOT / "scripts" / "setup.sh"


def run_setup(*args):
    return subprocess.run(
        [str(SETUP), *args],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
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
