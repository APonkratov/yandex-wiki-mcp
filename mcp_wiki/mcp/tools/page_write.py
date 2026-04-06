from typing import Annotated, Any, Literal

from mcp.server import FastMCP
from mcp.server.fastmcp import Context
from pydantic import Field
from starlette.requests import Request

from mcp_wiki.mcp.context import AppContext
from mcp_wiki.mcp.params import PageID, PageSlug, RecoveryToken
from mcp_wiki.mcp.tools.page_read import _resolve_page_id
from mcp_wiki.mcp.utils import get_yandex_auth


def register_page_write_tools(mcp: FastMCP[Any]) -> None:
    @mcp.tool(
        title="Create Wiki Page",
        description="Create a Yandex Wiki page.",
    )
    async def page_create(
        ctx: Context[Any, AppContext, Request],
        slug: PageSlug,
        title: Annotated[str, Field(description="Wiki page title.")],
        content: Annotated[str, Field(description="Full page content.")],
        page_type: Annotated[
            str,
            Field(
                description=(
                    "Wiki page type. Prefer 'wysiwyg' unless a different editor type is required."
                )
            ),
        ] = "wysiwyg",
    ) -> Any:
        return await ctx.request_context.lifespan_context.wiki.page_create(
            slug=slug,
            title=title,
            content=content,
            page_type=page_type,
            auth=get_yandex_auth(ctx),
        )

    @mcp.tool(
        title="Update Wiki Page",
        description="Update an existing Yandex Wiki page. Content replacement is full-page when content is provided.",
    )
    async def page_update(
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
        title: Annotated[str | None, Field(description="New page title.")] = None,
        content: Annotated[
            str | None,
            Field(description="New full page content. Replaces the existing body."),
        ] = None,
        allow_merge: Annotated[
            bool,
            Field(
                description="Whether to allow Yandex Wiki three-way merge on concurrent edits."
            ),
        ] = False,
        is_silent: Annotated[
            bool,
            Field(
                description="Whether to suppress notifications when supported by the API."
            ),
        ] = False,
    ) -> Any:
        resolved_page_id = await _resolve_page_id(ctx, page_id=page_id, slug=slug)
        return await ctx.request_context.lifespan_context.wiki.page_update(
            resolved_page_id,
            title=title,
            content=content,
            allow_merge=allow_merge,
            is_silent=is_silent,
            auth=get_yandex_auth(ctx),
        )

    @mcp.tool(
        title="Append Wiki Content",
        description="Append content to the top, bottom, or anchor of a Yandex Wiki page.",
    )
    async def page_append_content(
        ctx: Context[Any, AppContext, Request],
        content: Annotated[str, Field(description="Content block to append.")],
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
        location: Annotated[
            Literal["top", "bottom"],
            Field(
                description="Target location in the page body when anchor is not provided."
            ),
        ] = "bottom",
        anchor: Annotated[
            str | None,
            Field(
                description="Anchor name like '#release-notes'. Overrides location when provided."
            ),
        ] = None,
    ) -> Any:
        resolved_page_id = await _resolve_page_id(ctx, page_id=page_id, slug=slug)
        return await ctx.request_context.lifespan_context.wiki.page_append_content(
            resolved_page_id,
            content=content,
            location=location,
            anchor=anchor,
            auth=get_yandex_auth(ctx),
        )

    @mcp.tool(
        title="Add Page Comment",
        description="Add a comment to a Yandex Wiki page.",
    )
    async def page_add_comment(
        ctx: Context[Any, AppContext, Request],
        body: Annotated[str, Field(description="Comment body.")],
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
        parent_id: Annotated[
            int | None,
            Field(description="Optional parent comment ID for a reply."),
        ] = None,
        thread_id: Annotated[
            int | None,
            Field(
                description="Optional thread ID when replying in an existing thread."
            ),
        ] = None,
    ) -> Any:
        resolved_page_id = await _resolve_page_id(ctx, page_id=page_id, slug=slug)
        return await ctx.request_context.lifespan_context.wiki.page_add_comment(
            resolved_page_id,
            body=body,
            parent_id=parent_id,
            thread_id=thread_id,
            auth=get_yandex_auth(ctx),
        )

    @mcp.tool(
        title="Delete Wiki Page",
        description="Delete a Yandex Wiki page and return a recovery token.",
    )
    async def page_delete(
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
    ) -> Any:
        resolved_page_id = await _resolve_page_id(ctx, page_id=page_id, slug=slug)
        return await ctx.request_context.lifespan_context.wiki.page_delete(
            resolved_page_id,
            auth=get_yandex_auth(ctx),
        )

    @mcp.tool(
        title="Recover Wiki Page",
        description="Recover a deleted Yandex Wiki page using a recovery token.",
    )
    async def page_recover(
        ctx: Context[Any, AppContext, Request],
        recovery_token: RecoveryToken,
    ) -> Any:
        return await ctx.request_context.lifespan_context.wiki.page_recover(
            recovery_token,
            auth=get_yandex_auth(ctx),
        )

    @mcp.tool(
        title="Upload Page Attachment",
        description="Upload a local file to Yandex Wiki and attach it to a page.",
    )
    async def page_upload_attachment(
        ctx: Context[Any, AppContext, Request],
        file_path: Annotated[
            str,
            Field(
                description="Local filesystem path to the file that should be uploaded."
            ),
        ],
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
        append_markup: Annotated[
            bool,
            Field(
                description="Whether to append Wiki file macro markup to the page after uploading the attachment."
            ),
        ] = False,
        append_location: Annotated[
            Literal["top", "bottom"],
            Field(
                description="Where to append the generated file macro when append_markup is true."
            ),
        ] = "bottom",
    ) -> Any:
        resolved_page_id = await _resolve_page_id(ctx, page_id=page_id, slug=slug)
        return await ctx.request_context.lifespan_context.wiki.page_upload_attachment(
            resolved_page_id,
            file_path=file_path,
            append_markup=append_markup,
            append_location=append_location,
            auth=get_yandex_auth(ctx),
        )
