from mcp.client.session import ClientSession
from mcp.types import TextResourceContents
from pydantic import AnyUrl


class TestConfigurationResource:
    async def test_read_returns_configuration(
        self,
        client_session: ClientSession,
    ) -> None:
        result = await client_session.read_resource(AnyUrl("wiki-mcp://configuration"))

        assert len(result.contents) > 0
        content = result.contents[0]
        assert isinstance(content, TextResourceContents)
        assert content.text is not None

    async def test_contains_expected_fields(
        self,
        client_session: ClientSession,
    ) -> None:
        result = await client_session.read_resource(AnyUrl("wiki-mcp://configuration"))

        content = result.contents[0]
        assert isinstance(content, TextResourceContents)
        assert "api_base_url" in content.text
        assert "read_only" in content.text
