import pytest
from mcp.client.session import ClientSession

READ_ONLY_TOOL_NAMES = [
    "page_get",
    "page_get_descendants",
    "page_get_comments",
    "page_get_resources",
    "page_get_attachments",
]

WRITE_TOOL_NAMES = [
    "page_create",
    "page_update",
    "page_append_content",
    "page_add_comment",
    "page_delete",
    "page_recover",
    "page_upload_attachment",
]

EXPECTED_TOOL_NAMES = READ_ONLY_TOOL_NAMES + WRITE_TOOL_NAMES


class TestToolRegistration:
    @pytest.mark.parametrize("tool_name", EXPECTED_TOOL_NAMES)
    async def test_tool_is_registered(
        self,
        client_session: ClientSession,
        tool_name: str,
    ) -> None:
        result = await client_session.list_tools()
        tool_names = [tool.name for tool in result.tools]
        assert tool_name in tool_names


class TestReadOnlyModeToolRegistration:
    @pytest.mark.parametrize("tool_name", READ_ONLY_TOOL_NAMES)
    async def test_read_only_tools_are_registered(
        self,
        client_session_read_only: ClientSession,
        tool_name: str,
    ) -> None:
        result = await client_session_read_only.list_tools()
        tool_names = [tool.name for tool in result.tools]
        assert tool_name in tool_names

    @pytest.mark.parametrize("tool_name", WRITE_TOOL_NAMES)
    async def test_write_tools_are_not_registered(
        self,
        client_session_read_only: ClientSession,
        tool_name: str,
    ) -> None:
        result = await client_session_read_only.list_tools()
        tool_names = [tool.name for tool in result.tools]
        assert tool_name not in tool_names


class TestResourceRegistration:
    async def test_configuration_resource_is_registered(
        self,
        client_session: ClientSession,
    ) -> None:
        result = await client_session.list_resources()
        resource_uris = [str(resource.uri) for resource in result.resources]
        assert "wiki-mcp://configuration" in resource_uris


class TestServerConfiguration:
    async def test_server_has_correct_name(
        self,
        client_session: ClientSession,
    ) -> None:
        result = await client_session.initialize()
        assert result.serverInfo.name == "Yandex Wiki MCP Server"

    async def test_server_has_instructions(
        self,
        client_session: ClientSession,
    ) -> None:
        result = await client_session.initialize()
        assert result.instructions
