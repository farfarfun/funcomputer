from funcomputer.workspace import core


def test_init_creates_workspace_and_clones_repositories(monkeypatch):
    calls = []
    monkeypatch.setattr(core, "run_cmd", calls.append)

    core.init()

    assert calls[0] == "mkdir -vp /root/workspace"
    assert calls[1] == [
        "cd /root/workspace",
        "git clone git@github.com:farfarfun/funtool.git",
        "git clone git@github.com:farfarfun/funkeras.git",
        "git clone git@github.com:farfarfun/fundrive.git",
        "git clone git@github.com:farfarfun/funcomputer.git",
    ]
