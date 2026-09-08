import os

from app.services.credentials import CredentialRef, EnvironmentCredentialProvider


def test_credential_is_resolved_from_server_environment(monkeypatch):
    monkeypatch.setenv("SENTINEL_TEST_SECRET", "secret-value")

    provider = EnvironmentCredentialProvider()

    value = provider.get(
        CredentialRef("SENTINEL_TEST_SECRET")
    )

    assert value == "secret-value"


def test_missing_credential_is_rejected():
    from app.services.credentials import CredentialError

    provider = EnvironmentCredentialProvider()

    try:
        provider.get(
            CredentialRef("SENTINEL_MISSING_SECRET")
        )
        assert False, "Missing credential should raise CredentialError"
    except CredentialError:
        pass
