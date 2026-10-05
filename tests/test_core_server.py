import sys
import types

import pytest

from funcomputer.install import core_server


def test_install_drive_mounts_expected_path(monkeypatch):
    calls = []
    google = types.ModuleType("google")
    colab = types.ModuleType("google.colab")
    colab.drive = types.SimpleNamespace(mount=calls.append)
    monkeypatch.setitem(sys.modules, "google", google)
    monkeypatch.setitem(sys.modules, "google.colab", colab)

    core_server.install_drive()

    assert calls == ["/content/gdrive/"]


def test_install_code_server_installs_server_and_extensions(monkeypatch):
    calls = []
    downloads = []
    monkeypatch.setattr(core_server, "run_cmd", calls.append)
    monkeypatch.setattr(
        core_server,
        "download",
        lambda url, path, overwrite: downloads.append((url, path, overwrite)) or True,
    )

    core_server.install_code_server()

    assert downloads[0][0] == "https://code-server.dev/install.sh"
    assert downloads[0][2] is True
    assert calls[0].startswith("sh ")
    assert len(calls) == 13
    assert all("--install-extension" in command for command in calls[1:])


def test_install_natapp_downloads_and_marks_executable(monkeypatch):
    calls = []
    downloads = []
    monkeypatch.setattr(core_server, "run_cmd", calls.append)
    monkeypatch.setattr(
        core_server,
        "download",
        lambda url, path, overwrite: downloads.append((url, path, overwrite)) or True,
    )

    core_server.install_natapp()

    assert downloads == [
        (
            "https://download.natapp.cn/assets/downloads/clients/2_3_9/natapp_linux_amd64/natapp",
            "natapp",
            True,
        )
    ]
    assert calls == ["chmod a+x natapp"]


@pytest.mark.parametrize("installer", ["code-server", "natapp"])
def test_install_raises_when_download_fails(monkeypatch, installer):
    monkeypatch.setattr(core_server, "download", lambda *args, **kwargs: False)

    with pytest.raises(RuntimeError, match="下载"):
        getattr(core_server, f"install_{installer.replace('-', '_')}")()


def test_start_code_server_requires_password(monkeypatch):
    monkeypatch.delenv("CODE_SERVER_PASSWORD", raising=False)

    with pytest.raises(ValueError, match="CODE_SERVER_PASSWORD"):
        core_server.start_code_server()


@pytest.mark.parametrize(
    ("user_data_dir", "expected"),
    [
        ("/tmp/data", "code-server --user-data-dir /tmp/data --auth password"),
        (None, "code-server --auth password"),
    ],
)
def test_start_code_server_builds_command(user_data_dir, expected, monkeypatch):
    calls = []
    monkeypatch.setenv("CODE_SERVER_PASSWORD", "password")
    # 这里必须用 setenv 占位：被测函数会自己覆写这个变量，只有 monkeypatch 事先
    # 接管过该键，teardown 才会把它清掉。否则凭据样本会泄漏到整个测试会话的环境里。
    monkeypatch.setenv("PASSWORD", "placeholder")
    monkeypatch.setattr(core_server, "run_cmd", calls.append)

    core_server.start_code_server(user_data_dir)

    assert core_server.os.environ["PASSWORD"] == "password"
    assert calls == [f"{expected} --config /root/configs/code/code-server.yaml"]


def test_start_natapp_requires_token(monkeypatch):
    monkeypatch.delenv("NATAPP_AUTH_TOKEN", raising=False)

    with pytest.raises(ValueError, match="NATAPP_AUTH_TOKEN"):
        core_server.start_natapp()


def test_start_natapp_keeps_token_out_of_command(monkeypatch):
    calls = []
    # 同上：先占位，避免 "secret-token" 留在后续测试的进程环境里。
    monkeypatch.setenv("NATAPP_AUTH_TOKEN", "placeholder")
    monkeypatch.setattr(core_server, "run_cmd", calls.append)

    core_server.start_natapp("secret-token")

    assert core_server.os.environ["NATAPP_AUTH_TOKEN"] == "secret-token"
    assert calls == ['env NATAPP_AUTH_TOKEN="$NATAPP_AUTH_TOKEN" ./natapp']
    assert "secret-token" not in calls[0]
