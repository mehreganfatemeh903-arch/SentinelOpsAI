import os

import pytest

from app.services.adapters import EnvironmentToolAdapter
from app.services.credentials import CredentialError


def test_environment_adapter_does_not_expose_secret(monkeypatch):
    secret = "SUPER_SECRET_VALUE_123"

    monkeypatch.setenv("SENTINELOPS_EXTERNAL_TOOL_SECRET", secret)

    adapter = EnvironmentToolAdapter("SENTINELOPS_EXTERNAL_TOOL_SECRET")

    from app.services.adapters import AdapterRequest

    request = AdapterRequest(
        agent_id="agent-test",
        tool_id="tool-test",
        action="read",
        resource="external-resource",
        context={},
    )

    result = adapter.execute(request)

    assert result.status == "authorized"
    assert secret not in result.message
    assert secret not in str(result.data)


def test_environment_adapter_requires_server_credential(monkeypatch):
    monkeypatch.delenv("SENTINELOPS_EXTERNAL_TOOL_SECRET", raising=False)

    adapter = EnvironmentToolAdapter("SENTINELOPS_EXTERNAL_TOOL_SECRET")

    from app.services.adapters import AdapterRequest

    request = AdapterRequest(
        agent_id="agent-test",
        tool_id="tool-test",
        action="read",
        resource="external-resource",
        context={},
    )

    with pytest.raises(CredentialError):
        adapter.execute(request)
