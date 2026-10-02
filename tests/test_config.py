import pytest

from funcomputer.config import core
from funcomputer.install import config


@pytest.mark.parametrize("module", [core, config])
def test_config_ssh_requires_agent(module, monkeypatch):
    monkeypatch.delenv("SSH_AUTH_SOCK", raising=False)

    with pytest.raises(RuntimeError, match="SSH_AUTH_SOCK"):
        module.config_ssh()


@pytest.mark.parametrize("module", [core, config])
def test_config_ssh_accepts_agent(module, monkeypatch):
    monkeypatch.setenv("SSH_AUTH_SOCK", "/tmp/agent.sock")

    module.config_ssh()


def test_config_init_installs_expected_uv_tools(monkeypatch):
    calls = []
    monkeypatch.setattr(config, "run_cmd", calls.append)

    config.config_init()

    assert calls == [
        "uv tool install twine",
        "uv tool install pyecharts",
        "uv tool install ruff",
    ]


def test_config_all_runs_steps_in_order(monkeypatch):
    calls = []
    for name in ("config_init", "config_ssh", "config_git", "config_workspace"):
        monkeypatch.setattr(config, name, lambda name=name: calls.append(name))

    config.config_all()

    assert calls == ["config_init", "config_ssh", "config_git", "config_workspace"]


def test_config_git_sets_name_and_email(monkeypatch):
    calls = []
    monkeypatch.setattr(config, "run_cmd", calls.append)

    config.config_git()

    assert calls == [
        'git config --global user.email "1007530194@qq.com"',
        'git config --global user.name "niuliangtao"',
    ]


def test_config_workspace_uses_one_ordered_clone_batch(monkeypatch):
    calls = []
    monkeypatch.setattr(config, "run_cmd", calls.append)

    config.config_workspace()

    assert calls[:3] == [
        "mkdir -vp /root/workspace",
        "mkdir -vp /root/workspace/.vscode",
        "cp -rf '/content/gdrive/My Drive/core/configs/core/settings.json' '/root/workspace/.vscode/'",
    ]
    assert calls[3][0] == "cd /root/workspace"
    assert len(calls[3]) == 5
