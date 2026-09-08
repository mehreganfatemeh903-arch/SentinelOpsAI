from __future__ import annotations

import os
from dataclasses import dataclass


class CredentialError(RuntimeError):
    """Raised when a required server-side credential is unavailable."""


@dataclass(frozen=True)
class CredentialRef:
    name: str


class EnvironmentCredentialProvider:
    """
    Resolves credentials from the server environment only.

    Agents and ActionRequest objects never carry raw credentials.
    """

    def get(self, ref: CredentialRef) -> str:
        value = os.getenv(ref.name)

        if not value:
            raise CredentialError(
                f"Server credential '{ref.name}' is not configured"
            )

        return value


credential_provider = EnvironmentCredentialProvider()
