from unittest.mock import AsyncMock

from mcp.client.session import ClientSession

from mcp_wiki.wiki.proto.types.pages import WikiPage
from tests.mcp.conftest import get_tool_result_content


class TestPageWriteTools:
    async def test_page_create(
        self,
        client_session: ClientSession,
        mock_wiki_protocol: AsyncMock,
    ) -> None:
        mock_wiki_protocol.page_create.return_value = {
            "id": 10,
            "slug": "users/test/page",
            "title": "Created page",
        }

        result = await client_session.call_tool(
            "page_create",
            {
                "slug": "users/test/page",
                "title": "Created page",
                "content": "content",
            },
        )

        assert get_tool_result_content(result)["title"] == "Created page"
        mock_wiki_protocol.page_create.assert_awaited_once()

    async def test_page_update_by_slug(
        self,
        client_session: ClientSession,
        mock_wiki_protocol: AsyncMock,
    ) -> None:
        mock_wiki_protocol.page_get_by_slug.return_value = WikiPage.model_construct(
            id=10
        )
        mock_wiki_protocol.page_update.return_value = {
            "id": 10,
            "title": "Updated",
        }

        result = await client_session.call_tool(
            "page_update",
            {"slug": "users/test/page", "content": "new content"},
        )

        assert get_tool_result_content(result)["title"] == "Updated"
        mock_wiki_protocol.page_get_by_slug.assert_awaited_once()
        mock_wiki_protocol.page_update.assert_awaited_once()

    async def test_page_upload_attachment(
        self,
        client_session: ClientSession,
        mock_wiki_protocol: AsyncMock,
    ) -> None:
        mock_wiki_protocol.page_upload_attachment.return_value = {
            "page_id": 10,
            "attachments": [{"id": 1, "name": "file.zip"}],
            "appended_markup": False,
            "appended_content": None,
        }

        result = await client_session.call_tool(
            "page_upload_attachment",
            {"page_id": 10, "file_path": "C:\\temp\\file.zip"},
        )

        assert get_tool_result_content(result)["attachments"][0]["name"] == "file.zip"
        mock_wiki_protocol.page_upload_attachment.assert_awaited_once()
