def test_import():
    import funcomputer  # noqa: F401


def test_command_errors_redact_credentials(monkeypatch):
    from funcomputer import run

    monkeypatch.setenv("NATAPP_AUTH_TOKEN", "secret-token")
    assert "secret-token" not in run._safe_command("natapp secret-token")
    assert "[REDACTED]" in run._safe_command("natapp secret-token")
