from unittest.mock import AsyncMock

from mcp.client.session import ClientSession

from mcp_wiki.wiki.proto.types.pages import WikiGrid, WikiPage
from tests.mcp.conftest import get_tool_result_content


class TestPageReadTools:
    async def test_page_get_by_slug(
        self,
        client_session: ClientSession,
        mock_wiki_protocol: AsyncMock,
    ) -> None:
        mock_wiki_protocol.page_get_by_slug.return_value = WikiPage.model_construct(
            id=10,
            slug="users/test/page",
            title="Page title",
        )

        result = await client_session.call_tool(
            "page_get",
            {"slug": "users/test/page"},
        )

        assert get_tool_result_content(result)["slug"] == "users/test/page"
        mock_wiki_protocol.page_get_by_slug.assert_awaited_once()

    async def test_page_get_descendants(
        self,
        client_session: ClientSession,
        mock_wiki_protocol: AsyncMock,
    ) -> None:
        mock_wiki_protocol.page_get_descendants.return_value = {
            "results": [{"id": 10, "slug": "users/test/page"}],
            "next_cursor": None,
            "prev_cursor": None,
        }

        result = await client_session.call_tool(
            "page_get_descendants",
            {"slug": "users/test/page", "include_self": True},
        )

        assert (
            get_tool_result_content(result)["results"][0]["slug"] == "users/test/page"
        )
        mock_wiki_protocol.page_get_descendants.assert_awaited_once()

    async def test_page_get_with_fields(
        self,
        client_session: ClientSession,
        mock_wiki_protocol: AsyncMock,
    ) -> None:
        mock_wiki_protocol.page_get.return_value = WikiPage.model_construct(
            id=10,
            slug="users/test/page",
            content="Page content",
        )

        result = await client_session.call_tool(
            "page_get",
            {"page_id": 10, "fields": ["content", "breadcrumbs"]},
        )

        assert get_tool_result_content(result)["content"] == "Page content"
        mock_wiki_protocol.page_get.assert_awaited_once()
        assert mock_wiki_protocol.page_get.await_args.args == (10,)
        assert mock_wiki_protocol.page_get.await_args.kwargs["fields"] == [
            "content",
            "breadcrumbs",
        ]
        assert "auth" in mock_wiki_protocol.page_get.await_args.kwargs

    async def test_page_get_resources(
        self,
        client_session: ClientSession,
        mock_wiki_protocol: AsyncMock,
    ) -> None:
        mock_wiki_protocol.page_get_resources.return_value = {
            "results": [{"type": "attachment", "item": {"name": "file.zip"}}],
            "next_cursor": None,
            "prev_cursor": None,
        }
        mock_wiki_protocol.page_get_by_slug.return_value = WikiPage.model_construct(
            id=10
        )

        result = await client_session.call_tool(
            "page_get_resources",
            {"slug": "users/test/page", "resource_types": ["attachment"]},
        )

        assert get_tool_result_content(result)["results"][0]["type"] == "attachment"
        mock_wiki_protocol.page_get_by_slug.assert_awaited_once()
        mock_wiki_protocol.page_get_resources.assert_awaited_once()

    async def test_page_get_resources_with_attachment_filter(
        self,
        client_session: ClientSession,
        mock_wiki_protocol: AsyncMock,
    ) -> None:
        mock_wiki_protocol.page_get_resources.return_value = {
            "results": [{"type": "attachment", "item": {"name": "file.zip"}}],
            "next_cursor": None,
            "prev_cursor": None,
        }

        result = await client_session.call_tool(
            "page_get_resources",
            {"page_id": 10, "resource_types": ["attachment"]},
        )

        assert get_tool_result_content(result)["results"][0]["type"] == "attachment"
        mock_wiki_protocol.page_get_resources.assert_awaited_once()
        assert mock_wiki_protocol.page_get_resources.await_args.args == (10,)
        assert mock_wiki_protocol.page_get_resources.await_args.kwargs[
            "resource_types"
        ] == ["attachment"]
        assert mock_wiki_protocol.page_get_resources.await_args.kwargs["q"] is None
        assert (
            mock_wiki_protocol.page_get_resources.await_args.kwargs["page_size"] == 50
        )
        assert mock_wiki_protocol.page_get_resources.await_args.kwargs["cursor"] is None
        assert (
            mock_wiki_protocol.page_get_resources.await_args.kwargs["order_by"] is None
        )
        assert (
            mock_wiki_protocol.page_get_resources.await_args.kwargs["order_direction"]
            is None
        )
        assert "auth" in mock_wiki_protocol.page_get_resources.await_args.kwargs

    async def test_page_get_grids(
        self,
        client_session: ClientSession,
        mock_wiki_protocol: AsyncMock,
    ) -> None:
        mock_wiki_protocol.page_get_grids.return_value = {
            "results": [{"id": "grid-1", "title": "Roadmap"}],
            "next_cursor": None,
            "prev_cursor": None,
        }
        mock_wiki_protocol.page_get_by_slug.return_value = WikiPage.model_construct(
            id=10
        )

        result = await client_session.call_tool(
            "page_get_grids",
            {"slug": "users/test/page", "order_by": "title", "order_direction": "asc"},
        )

        assert get_tool_result_content(result)["results"][0]["id"] == "grid-1"
        mock_wiki_protocol.page_get_by_slug.assert_awaited_once()
        mock_wiki_protocol.page_get_grids.assert_awaited_once()
        assert mock_wiki_protocol.page_get_grids.await_args.args == (10,)
        assert (
            mock_wiki_protocol.page_get_grids.await_args.kwargs["order_by"] == "title"
        )
        assert (
            mock_wiki_protocol.page_get_grids.await_args.kwargs["order_direction"]
            == "asc"
        )
        assert mock_wiki_protocol.page_get_grids.await_args.kwargs["page_size"] == 50
        assert "auth" in mock_wiki_protocol.page_get_grids.await_args.kwargs

    async def test_grid_get(
        self,
        client_session: ClientSession,
        mock_wiki_protocol: AsyncMock,
    ) -> None:
        mock_wiki_protocol.grid_get.return_value = WikiGrid.model_construct(
            id="grid-1",
            title="Roadmap",
            revision="7",
            rows=[{"id": "row-1", "row": ["In progress", 3]}],
        )

        result = await client_session.call_tool(
            "grid_get",
            {
                "grid_id": "grid-1",
                "fields": ["attributes", "user_permissions"],
                "filter": "[status] = done",
                "only_cols": "status,eta",
                "only_rows": "row-1,row-2",
                "revision": "7",
                "sort": "eta",
            },
        )

        assert get_tool_result_content(result)["id"] == "grid-1"
        mock_wiki_protocol.grid_get.assert_awaited_once()
        assert mock_wiki_protocol.grid_get.await_args.args == ("grid-1",)
        assert mock_wiki_protocol.grid_get.await_args.kwargs["fields"] == [
            "attributes",
            "user_permissions",
        ]
        assert (
            mock_wiki_protocol.grid_get.await_args.kwargs["filter"] == "[status] = done"
        )
        assert (
            mock_wiki_protocol.grid_get.await_args.kwargs["only_cols"] == "status,eta"
        )
        assert (
            mock_wiki_protocol.grid_get.await_args.kwargs["only_rows"] == "row-1,row-2"
        )
        assert mock_wiki_protocol.grid_get.await_args.kwargs["revision"] == "7"
        assert mock_wiki_protocol.grid_get.await_args.kwargs["sort"] == "eta"
        assert "auth" in mock_wiki_protocol.grid_get.await_args.kwargs

    async def test_grid_get_rejects_empty_grid_id(
        self,
        client_session: ClientSession,
    ) -> None:
        result = await client_session.call_tool("grid_get", {"grid_id": "   "})

        assert result.isError is True
        assert result.content
        assert "grid_id must not be empty" in result.content[0].text
