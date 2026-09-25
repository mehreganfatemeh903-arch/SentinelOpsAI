from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlparse
import ipaddress
import socket
import httpx

from app.services.credentials import CredentialError, CredentialRef, credential_provider


@dataclass(frozen=True)
class AdapterRequest:
    agent_id: str
    tool_id: str
    action: str
    resource: str
    context: dict[str, Any]


@dataclass(frozen=True)
class AdapterResult:
    status: str
    action: str
    resource: str
    message: str
    data: dict[str, Any]


class ToolAdapter(ABC):
    """Server-side contract for executing an authorized tool."""

    name: str

    @abstractmethod
    def execute(self, request: AdapterRequest) -> AdapterResult:
        raise NotImplementedError


class SimulatedToolAdapter(ToolAdapter):
    """Safe compatibility adapter."""

    name = "simulated"

    def execute(self, request: AdapterRequest) -> AdapterResult:
        return AdapterResult(
            status="simulated",
            action=request.action,
            resource=request.resource,
            message="Tool execution passed through SentinelOps Gateway",
            data={
                "agent_id": request.agent_id,
                "tool_id": request.tool_id,
            },
        )


class EnvironmentToolAdapter(ToolAdapter):
    """
    Server-side adapter boundary.

    The credential is resolved exclusively on the SentinelOps server.
    The raw secret is never returned in AdapterResult.
    """

    name = "environment"

    def __init__(self, credential_name: str):
        self.credential_ref = CredentialRef(credential_name)

    def execute(self, request: AdapterRequest) -> AdapterResult:
        credential_provider.get(self.credential_ref)

        return AdapterResult(
            status="authorized",
            action=request.action,
            resource=request.resource,
            message="Server-side credential resolved for authorized tool",
            data={
                "agent_id": request.agent_id,
                "tool_id": request.tool_id,
                "credential": "server-side",
            },
        )


class HttpToolAdapter(ToolAdapter):
    """Executes an approved external HTTPS webhook without exposing secrets."""

    name = "http"

    def __init__(self, endpoint: str, credential_name: str | None = None):
        parsed = urlparse(endpoint)

        if parsed.scheme != "https" or not parsed.hostname:
            raise ValueError("HTTP adapter requires a valid HTTPS endpoint")

        addresses = {
            item[4][0]
            for item in socket.getaddrinfo(
                parsed.hostname,
                parsed.port or 443,
                type=socket.SOCK_STREAM,
            )
        }

        for address in addresses:
            ip = ipaddress.ip_address(address)
            if ip.is_private or ip.is_loopback or ip.is_link_local:
                raise ValueError("Private or local tool endpoints are not allowed")

        self.endpoint = endpoint
        self.credential_ref = (
            CredentialRef(credential_name)
            if credential_name
            else None
        )

    def execute(self, request: AdapterRequest) -> AdapterResult:
        headers = {"Content-Type": "application/json"}

        if self.credential_ref:
            secret = credential_provider.get(self.credential_ref)
            headers["Authorization"] = f"Bearer {secret}"

        payload = {
            "action": request.action,
            "resource": request.resource,
            "agent_id": request.agent_id,
            "tool_id": request.tool_id,
            "context": request.context,
        }

        try:
            response = httpx.post(
                self.endpoint,
                json=payload,
                headers=headers,
                timeout=10.0,
                follow_redirects=False,
            )
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise RuntimeError("External tool request failed") from exc

        return AdapterResult(
            status="executed",
            action=request.action,
            resource=request.resource,
            message="External tool executed through SentinelOps Gateway",
            data={"status_code": response.status_code},
        )


class AdapterRegistry:

    """Maps registered adapter names to server-side adapter instances."""

    def __init__(self) -> None:
        self._adapters: dict[str, ToolAdapter] = {}

    def register(self, adapter: ToolAdapter) -> None:
        self._adapters[adapter.name] = adapter

    def get(
        self,
        name: str,
        credential_ref: str | None = None,
        endpoint: str | None = None,
    ) -> ToolAdapter:
        if name == "http":
            if not endpoint:
                raise ValueError("HTTP adapter requires endpoint")
            return HttpToolAdapter(endpoint, credential_ref)

        if name == "environment":
            if not credential_ref:
                raise CredentialError(
                    "Environment adapter requires credential_ref"
                )
            return EnvironmentToolAdapter(credential_ref)

        try:
            return self._adapters[name]
        except KeyError as exc:
            raise ValueError(
                f"Unknown tool adapter: {name}"
            ) from exc


registry = AdapterRegistry()
registry.register(SimulatedToolAdapter())
