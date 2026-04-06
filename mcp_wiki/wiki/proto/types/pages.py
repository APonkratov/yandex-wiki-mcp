from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class BaseWikiModel(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)


class PageFieldEnum(StrEnum):
    CONTENT = "content"
    ATTRIBUTES = "attributes"
    BREADCRUMBS = "breadcrumbs"
    REDIRECT = "redirect"


class ResourceTypeEnum(StrEnum):
    ATTACHMENT = "attachment"
    GRID = "grid"


class WikiPage(BaseWikiModel):
    id: int
    slug: str | None = None
    title: str | None = None
    page_type: str | None = None
    content: Any | None = None
    attributes: dict[str, Any] | None = None
    breadcrumbs: list[dict[str, Any]] | None = None
    redirect: dict[str, Any] | None = None
    created_at: str | None = None
    modified_at: str | None = None


class PageComment(BaseWikiModel):
    id: int
    body: str | None = None
    parent_id: int | None = None
    thread_id: int | None = None
    created_at: str | None = None
    updated_at: str | None = None
    user: dict[str, Any] | None = None


class WikiAttachment(BaseWikiModel):
    id: int
    name: str | None = None
    download_url: str | None = None
    size: str | None = None
    description: str | None = None
    mimetype: str | None = None
    created_at: str | None = None
    has_preview: bool | None = None
    check_status: str | None = None
    user: dict[str, Any] | None = None


class WikiResource(BaseWikiModel):
    type: str
    item: dict[str, Any]


class DescendantsResponse(BaseWikiModel):
    results: list[WikiPage] = Field(default_factory=list)
    next_cursor: str | None = None
    prev_cursor: str | None = None


class CommentsResponse(BaseWikiModel):
    results: list[PageComment] = Field(default_factory=list)
    next_cursor: str | None = None
    prev_cursor: str | None = None


class AttachmentListResponse(BaseWikiModel):
    results: list[WikiAttachment] = Field(default_factory=list)
    next_cursor: str | None = None
    prev_cursor: str | None = None


class ResourcesResponse(BaseWikiModel):
    results: list[WikiResource] = Field(default_factory=list)
    next_cursor: str | None = None
    prev_cursor: str | None = None


class DeletePageResponse(BaseWikiModel):
    recovery_token: str | None = None


class RecoverPageResponse(BaseWikiModel):
    id: int


class UploadSessionResponse(BaseWikiModel):
    session_id: str


class AttachmentResultsResponse(BaseWikiModel):
    results: list[WikiAttachment] = Field(default_factory=list)


class UploadAttachmentResult(BaseWikiModel):
    page_id: int
    attachments: list[WikiAttachment] = Field(default_factory=list)
    appended_markup: bool = False
    appended_content: str | None = None
