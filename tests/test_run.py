import pytest

from funcomputer import run


def test_run_cmd_uses_single_command_runner(monkeypatch):
    calls = []
    monkeypatch.setattr(run, "run_shell", lambda command: calls.append(command) or "0")

    run.run_cmd("echo ok")

    assert calls == ["echo ok"]


def test_run_cmd_uses_list_runner(monkeypatch):
    calls = []
    commands = ["echo one", "echo two"]
    monkeypatch.setattr(run, "run_shell_list", lambda value: calls.append(value) or "0")

    run.run_cmd(commands)

    assert calls == [commands]


def test_run_cmd_raises_and_redacts_credentials(monkeypatch):
    monkeypatch.setenv("NATAPP_AUTH_TOKEN", "secret-token")
    monkeypatch.setattr(run, "run_shell", lambda _command: "1")

    with pytest.raises(RuntimeError) as error:
        run.run_cmd("natapp secret-token")

    assert "secret-token" not in str(error.value)
    assert "[REDACTED]" in str(error.value)


def test_safe_command_redacts_credentials_in_list(monkeypatch):
    monkeypatch.setenv("CODE_SERVER_PASSWORD", "secret-password")

    assert run._safe_command(["first", "echo secret-password"]) == [
        "first",
        "echo [REDACTED]",
    ]
