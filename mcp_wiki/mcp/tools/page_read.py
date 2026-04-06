from typing import Annotated, Any, Literal

from mcp.server import FastMCP
from mcp.server.fastmcp import Context
from mcp.types import ToolAnnotations
from pydantic import Field
from starlette.requests import Request

from mcp_wiki.mcp.context import AppContext
from mcp_wiki.mcp.params import (
    Cursor,
    PageFields,
    PageID,
    PageSize,
    PageSlug,
    ResourceTypes,
)
from mcp_wiki.mcp.utils import get_yandex_auth, resolve_page_locator


async def _resolve_page_id(
    ctx: Context[Any, AppContext, Request],
    *,
    page_id: int | None,
    slug: str | None,
) -> int:
    page_id, slug = resolve_page_locator(page_id=page_id, slug=slug)
    if page_id is not None:
        return page_id
    if slug is None:
        raise ValueError("Either page_id or slug must be provided.")

    page = await ctx.request_context.lifespan_context.wiki.page_get_by_slug(
        slug,
        auth=get_yandex_auth(ctx),
    )
    return page.id


async def _resolve_page_slug(
    ctx: Context[Any, AppContext, Request],
    *,
    page_id: int | None,
    slug: str | None,
) -> str:
    page_id, slug = resolve_page_locator(page_id=page_id, slug=slug)
    if slug is not None:
        return slug
    if page_id is None:
        raise ValueError("Either page_id or slug must be provided.")

    page = await ctx.request_context.lifespan_context.wiki.page_get(
        page_id,
        auth=get_yandex_auth(ctx),
    )
    if not page.slug:
        raise ValueError(f"Page {page_id} does not have a slug in the API response.")
    return page.slug


def register_page_read_tools(mcp: FastMCP[Any]) -> None:
    @mcp.tool(
        title="Get Wiki Page",
        description="Get a Yandex Wiki page by page_id or slug.",
        annotations=ToolAnnotations(readOnlyHint=True),
    )
    async def page_get(
        ctx: Context[Any, AppContext, Request],
        page_id: Annotated[
            PageID | None,
            Field(description="Wiki page numeric ID. Provide either page_id or slug."),
        ] = None,
        slug: Annotated[
            PageSlug | None,
            Field(
                description="Wiki page slug or full Wiki URL. Provide either page_id or slug."
            ),
        ] = None,
        fields: PageFields = None,
    ) -> Any:
        page_id, slug = resolve_page_locator(page_id=page_id, slug=slug)
        auth = get_yandex_auth(ctx)
        field_names = [field.value for field in fields] if fields else None

        if page_id is not None:
            return await ctx.request_context.lifespan_context.wiki.page_get(
                page_id,
                fields=field_names,
                auth=auth,
            )
        if slug is None:
            raise ValueError("Either page_id or slug must be provided.")

        return await ctx.request_context.lifespan_context.wiki.page_get_by_slug(
            slug,
            fields=field_names,
            auth=auth,
        )

    @mcp.tool(
        title="Get Page Descendants",
        description="Get a subtree of Yandex Wiki pages under a parent page.",
        annotations=ToolAnnotations(readOnlyHint=True),
    )
    async def page_get_descendants(
        ctx: Context[Any, AppContext, Request],
        page_id: Annotated[
            PageID | None,
            Field(description="Wiki page numeric ID. Provide either page_id or slug."),
        ] = None,
        slug: Annotated[
            PageSlug | None,
            Field(
                description="Wiki page slug or full Wiki URL. Provide either page_id or slug."
            ),
        ] = None,
        include_self: Annotated[
            bool,
            Field(
                description="Whether to include the root page itself in the subtree."
            ),
        ] = False,
        page_size: PageSize = 100,
        cursor: Cursor = None,
    ) -> Any:
        resolved_slug = await _resolve_page_slug(ctx, page_id=page_id, slug=slug)
        return await ctx.request_context.lifespan_context.wiki.page_get_descendants(
            resolved_slug,
            include_self=include_self,
            page_size=page_size,
            cursor=cursor,
            auth=get_yandex_auth(ctx),
        )

    @mcp.tool(
        title="Get Page Comments",
        description="Get comments for a Yandex Wiki page.",
        annotations=ToolAnnotations(readOnlyHint=True),
    )
    async def page_get_comments(
        ctx: Context[Any, AppContext, Request],
        page_id: Annotated[
            PageID | None,
            Field(description="Wiki page numeric ID. Provide either page_id or slug."),
        ] = None,
        slug: Annotated[
            PageSlug | None,
            Field(
                description="Wiki page slug or full Wiki URL. Provide either page_id or slug."
            ),
        ] = None,
        page_size: PageSize = 100,
        cursor: Cursor = None,
    ) -> Any:
        resolved_page_id = await _resolve_page_id(ctx, page_id=page_id, slug=slug)
        return await ctx.request_context.lifespan_context.wiki.page_get_comments(
            resolved_page_id,
            page_size=page_size,
            cursor=cursor,
            auth=get_yandex_auth(ctx),
        )

    @mcp.tool(
        title="Get Page Resources",
        description="Get resources linked to a Yandex Wiki page, including attachments and grids.",
        annotations=ToolAnnotations(readOnlyHint=True),
    )
    async def page_get_resources(
        ctx: Context[Any, AppContext, Request],
        page_id: Annotated[
            PageID | None,
            Field(description="Wiki page numeric ID. Provide either page_id or slug."),
        ] = None,
        slug: Annotated[
            PageSlug | None,
            Field(
                description="Wiki page slug or full Wiki URL. Provide either page_id or slug."
            ),
        ] = None,
        resource_types: ResourceTypes = None,
        search: Annotated[
            str | None,
            Field(description="Optional title search query for resources."),
        ] = None,
        page_size: PageSize = 50,
        cursor: Cursor = None,
        order_by: Annotated[
            Literal["name_title", "created_at"] | None,
            Field(description="Optional resource sorting field."),
        ] = None,
        order_direction: Annotated[
            Literal["asc", "desc"] | None,
            Field(description="Optional resource sorting direction."),
        ] = None,
    ) -> Any:
        resolved_page_id = await _resolve_page_id(ctx, page_id=page_id, slug=slug)
        return await ctx.request_context.lifespan_context.wiki.page_get_resources(
            resolved_page_id,
            resource_types=[resource_type.value for resource_type in resource_types]
            if resource_types
            else None,
            q=search,
            page_size=page_size,
            cursor=cursor,
            order_by=order_by,
            order_direction=order_direction,
            auth=get_yandex_auth(ctx),
        )

    @mcp.tool(
        title="Get Page Attachments",
        description="Get attachments for a Yandex Wiki page.",
        annotations=ToolAnnotations(readOnlyHint=True),
    )
    async def page_get_attachments(
        ctx: Context[Any, AppContext, Request],
        page_id: Annotated[
            PageID | None,
            Field(description="Wiki page numeric ID. Provide either page_id or slug."),
        ] = None,
        slug: Annotated[
            PageSlug | None,
            Field(
                description="Wiki page slug or full Wiki URL. Provide either page_id or slug."
            ),
        ] = None,
        page_size: PageSize = 100,
        cursor: Cursor = None,
    ) -> Any:
        resolved_page_id = await _resolve_page_id(ctx, page_id=page_id, slug=slug)
        return await ctx.request_context.lifespan_context.wiki.page_get_attachments(
            resolved_page_id,
            page_size=page_size,
            cursor=cursor,
            auth=get_yandex_auth(ctx),
        )
