import pytest

from app.core.config import Settings


def test_production_rejects_default_jwt_secret():
    with pytest.raises(ValueError):
        Settings(
            environment="production",
            jwt_secret="change-me-in-production-use-32-plus-random-chars",
        )
