from backend.app.schemas.tool import ToolCreate

def test_tool_create_supports_adapter_and_credential_ref():
    tool = ToolCreate(
        name="test-tool",
        description="test",
        sensitivity=50,
        adapter_name="environment",
        credential_ref="MY_SECRET",
    )

    assert tool.adapter_name == "environment"
    assert tool.credential_ref == "MY_SECRET"


def test_tool_create_defaults_to_simulated_adapter():
    tool = ToolCreate(name="test-tool")

    assert tool.adapter_name == "simulated"
    assert tool.credential_ref is None

