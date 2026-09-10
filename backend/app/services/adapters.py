from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

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
    ) -> ToolAdapter:
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
