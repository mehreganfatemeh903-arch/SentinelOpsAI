import httpx
import pytest

from app.services.adapters import AdapterRequest, HttpToolAdapter


def test_http_adapter_rejects_non_https():
    with pytest.raises(ValueError):
        HttpToolAdapter("http://example.com/tool")


def test_http_adapter_rejects_private_endpoint(monkeypatch):
    monkeypatch.setattr(
        "socket.getaddrinfo",
        lambda *args, **kwargs: [
            (2, 1, 6, "", ("127.0.0.1", 443))
        ],
    )

    with pytest.raises(ValueError):
        HttpToolAdapter("https://example.com/tool")


def test_http_adapter_sends_secret_server_side(monkeypatch):
    captured = {}

    def fake_post(url, **kwargs):
        captured["url"] = url
        captured["headers"] = kwargs["headers"]
        captured["json"] = kwargs["json"]
        return httpx.Response(200, request=httpx.Request("POST", url))

    monkeypatch.setattr(httpx, "post", fake_post)
    monkeypatch.setenv("TEST_EXTERNAL_SECRET", "super-secret")

    adapter = HttpToolAdapter(
        "https://example.com/tool",
        "TEST_EXTERNAL_SECRET",
    )

    result = adapter.execute(
        AdapterRequest(
            agent_id="agent-1",
            tool_id="tool-1",
            action="run",
            resource="/test",
            context={"safe": True},
        )
    )

    assert captured["headers"]["Authorization"] == "Bearer super-secret"
    assert captured["json"]["action"] == "run"
    assert result.data == {"status_code": 200}
    assert "super-secret" not in str(result)
