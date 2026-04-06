from typing import Any, Protocol

from mcp_wiki.wiki.proto.common import YandexAuth
from mcp_wiki.wiki.proto.types.pages import (
    AttachmentListResponse,
    AttachmentResultsResponse,
    CommentsResponse,
    DeletePageResponse,
    DescendantsResponse,
    PageComment,
    RecoverPageResponse,
    ResourcesResponse,
    UploadAttachmentResult,
    UploadSessionResponse,
    WikiPage,
)


class WikiProtocol(Protocol):
    async def prepare(self) -> None: ...
    async def close(self) -> None: ...

    async def page_get_by_slug(
        self,
        slug: str,
        *,
        fields: list[str] | None = None,
        auth: YandexAuth | None = None,
    ) -> WikiPage: ...

    async def page_get(
        self,
        page_id: int,
        *,
        fields: list[str] | None = None,
        auth: YandexAuth | None = None,
    ) -> WikiPage: ...

    async def page_get_descendants(
        self,
        slug: str,
        *,
        include_self: bool = False,
        page_size: int = 100,
        cursor: str | None = None,
        auth: YandexAuth | None = None,
    ) -> DescendantsResponse: ...

    async def page_get_comments(
        self,
        page_id: int,
        *,
        page_size: int = 100,
        cursor: str | None = None,
        auth: YandexAuth | None = None,
    ) -> CommentsResponse: ...

    async def page_get_resources(
        self,
        page_id: int,
        *,
        resource_types: list[str] | None = None,
        q: str | None = None,
        page_size: int = 50,
        cursor: str | None = None,
        order_by: str | None = None,
        order_direction: str | None = None,
        auth: YandexAuth | None = None,
    ) -> ResourcesResponse: ...

    async def page_get_attachments(
        self,
        page_id: int,
        *,
        page_size: int = 100,
        cursor: str | None = None,
        auth: YandexAuth | None = None,
    ) -> AttachmentListResponse: ...

    async def page_create(
        self,
        *,
        slug: str,
        title: str,
        content: str,
        page_type: str = "wysiwyg",
        auth: YandexAuth | None = None,
    ) -> WikiPage: ...

    async def page_update(
        self,
        page_id: int,
        *,
        title: str | None = None,
        content: str | None = None,
        allow_merge: bool = False,
        is_silent: bool = False,
        auth: YandexAuth | None = None,
    ) -> WikiPage: ...

    async def page_append_content(
        self,
        page_id: int,
        *,
        content: str,
        location: str = "bottom",
        anchor: str | None = None,
        auth: YandexAuth | None = None,
    ) -> dict[str, Any]: ...

    async def page_add_comment(
        self,
        page_id: int,
        *,
        body: str,
        parent_id: int | None = None,
        thread_id: int | None = None,
        auth: YandexAuth | None = None,
    ) -> PageComment: ...

    async def page_delete(
        self,
        page_id: int,
        *,
        auth: YandexAuth | None = None,
    ) -> DeletePageResponse: ...

    async def page_recover(
        self,
        recovery_token: str,
        *,
        auth: YandexAuth | None = None,
    ) -> RecoverPageResponse: ...

    async def upload_session_create(
        self,
        *,
        file_name: str,
        file_size: int,
        auth: YandexAuth | None = None,
    ) -> UploadSessionResponse: ...

    async def page_attach_upload_sessions(
        self,
        page_id: int,
        *,
        session_ids: list[str],
        auth: YandexAuth | None = None,
    ) -> AttachmentResultsResponse: ...

    async def page_upload_attachment(
        self,
        page_id: int,
        *,
        file_path: str,
        append_markup: bool = False,
        append_location: str = "bottom",
        auth: YandexAuth | None = None,
    ) -> UploadAttachmentResult: ...
