from app.core.api_keys import generate_api_key, hash_api_key
from app.api.api_keys import authenticate_agent_key
from app.db.session import SessionLocal
from app.models import Agent, AgentApiKey


def test_generate_api_key_and_hash():
    raw_key, digest = generate_api_key()

    assert raw_key.startswith("sntl_")
    assert len(raw_key) > 20
    assert digest == hash_api_key(raw_key)
    assert digest != raw_key


def test_authenticate_agent_key_returns_agent_and_updates_last_used():
    db = SessionLocal()
    try:
        agent = db.query(Agent).filter(Agent.active.is_(True)).first()
        assert agent is not None

        raw_key, digest = generate_api_key()

        key = AgentApiKey(
            agent_id=agent.id,
            key_hash=digest,
            name="test-key",
        )
        db.add(key)
        db.commit()
        db.refresh(key)

        assert key.last_used_at is None

        authenticated = authenticate_agent_key(raw_key, db)

        assert authenticated is not None
        assert authenticated.id == agent.id

        db.refresh(key)
        assert key.last_used_at is not None
    finally:
        db.query(AgentApiKey).filter(AgentApiKey.name == "test-key").delete(
            synchronize_session=False
        )
        db.commit()
        db.close()


def test_authenticate_invalid_key_returns_none():
    db = SessionLocal()
    try:
        assert authenticate_agent_key("sntl_invalid_key", db) is None
    finally:
        db.close()


def test_authenticate_revoked_key_returns_none():
    db = SessionLocal()
    try:
        agent = db.query(Agent).filter(Agent.active.is_(True)).first()
        assert agent is not None

        raw_key, digest = generate_api_key()

        key = AgentApiKey(
            agent_id=agent.id,
            key_hash=digest,
            name="test-revoked-key",
            active=False,
        )
        db.add(key)
        db.commit()

        assert authenticate_agent_key(raw_key, db) is None
    finally:
        db.query(AgentApiKey).filter(
            AgentApiKey.name == "test-revoked-key"
        ).delete(synchronize_session=False)
        db.commit()
        db.close()
