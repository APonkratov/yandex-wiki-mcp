import json
from pathlib import Path
from typing import Any, Literal

from aiohttp import ClientSession, ClientTimeout

from mcp_wiki.mcp.utils import normalize_slug
from mcp_wiki.wiki.custom.errors import PageNotFound
from mcp_wiki.wiki.proto.common import YandexAuth
from mcp_wiki.wiki.proto.pages import WikiProtocol
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

UploadLocation = Literal["top", "bottom"]


class WikiClient(WikiProtocol):
    CHUNK_SIZE = 5 * 1024 * 1024

    def __init__(
        self,
        *,
        token: str | None,
        iam_token: str | None = None,
        auth_scheme: Literal["OAuth", "Bearer"] = "OAuth",
        org_id: str | None = None,
        cloud_org_id: str | None = None,
        base_url: str = "https://api.wiki.yandex.net",
        timeout: float = 30,
    ):
        self._token = token
        self._iam_token = iam_token
        self._auth_scheme = auth_scheme
        self._org_id = org_id
        self._cloud_org_id = cloud_org_id
        self._session = ClientSession(
            base_url=base_url,
            timeout=ClientTimeout(total=timeout),
        )

    async def prepare(self) -> None:
        return None

    async def close(self) -> None:
        await self._session.close()

    async def _build_headers(self, auth: YandexAuth | None = None) -> dict[str, str]:
        if auth and auth.token:
            auth_header = f"{self._auth_scheme} {auth.token}"
        elif self._token:
            auth_header = f"{self._auth_scheme} {self._token}"
        elif self._iam_token:
            auth_header = f"Bearer {self._iam_token}"
        else:
            raise ValueError(
                "No authentication method provided. Configure wiki_token, wiki_iam_token, or OAuth."
            )

        org_id = auth.org_id if auth and auth.org_id else self._org_id
        cloud_org_id = (
            auth.cloud_org_id if auth and auth.cloud_org_id else self._cloud_org_id
        )

        if org_id and cloud_org_id:
            raise ValueError("Only one of org_id or cloud_org_id should be provided.")
        if not org_id and not cloud_org_id:
            raise ValueError("Either org_id or cloud_org_id must be provided.")

        headers = {"Authorization": auth_header}
        if org_id:
            headers["X-Org-Id"] = org_id
        if cloud_org_id:
            headers["X-Cloud-Org-Id"] = cloud_org_id
        return headers

    async def _read_json(self, response: Any) -> Any:
        response.raise_for_status()
        payload = await response.read()
        if not payload:
            return {}
        return json.loads(payload)

    async def page_get_by_slug(
        self,
        slug: str,
        *,
        fields: list[str] | None = None,
        auth: YandexAuth | None = None,
    ) -> WikiPage:
        params: dict[str, str] = {"slug": normalize_slug(slug)}
        if fields:
            params["fields"] = ",".join(fields)

        async with self._session.get(
            "v1/pages",
            headers=await self._build_headers(auth),
            params=params,
        ) as response:
            if response.status == 404:
                raise PageNotFound(slug)
            response.raise_for_status()
            return WikiPage.model_validate_json(await response.read())

    async def page_get(
        self,
        page_id: int,
        *,
        fields: list[str] | None = None,
        auth: YandexAuth | None = None,
    ) -> WikiPage:
        params: dict[str, str] = {}
        if fields:
            params["fields"] = ",".join(fields)

        async with self._session.get(
            f"v1/pages/{page_id}",
            headers=await self._build_headers(auth),
            params=params if params else None,
        ) as response:
            if response.status == 404:
                raise PageNotFound(page_id)
            response.raise_for_status()
            return WikiPage.model_validate_json(await response.read())

    async def page_get_descendants(
        self,
        slug: str,
        *,
        include_self: bool = False,
        page_size: int = 100,
        cursor: str | None = None,
        auth: YandexAuth | None = None,
    ) -> DescendantsResponse:
        params: dict[str, Any] = {
            "slug": normalize_slug(slug),
            "include_self": str(include_self).lower(),
            "page_size": page_size,
        }
        if cursor:
            params["cursor"] = cursor

        async with self._session.get(
            "v1/pages/descendants",
            headers=await self._build_headers(auth),
            params=params,
        ) as response:
            response.raise_for_status()
            return DescendantsResponse.model_validate_json(await response.read())

    async def page_get_comments(
        self,
        page_id: int,
        *,
        page_size: int = 100,
        cursor: str | None = None,
        auth: YandexAuth | None = None,
    ) -> CommentsResponse:
        params: dict[str, Any] = {"page_size": page_size}
        if cursor:
            params["cursor"] = cursor

        async with self._session.get(
            f"v1/pages/{page_id}/comments",
            headers=await self._build_headers(auth),
            params=params,
        ) as response:
            if response.status == 404:
                raise PageNotFound(page_id)
            response.raise_for_status()
            return CommentsResponse.model_validate_json(await response.read())

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
    ) -> ResourcesResponse:
        params: dict[str, Any] = {"page_size": page_size}
        if resource_types:
            params["types"] = ",".join(resource_types)
        if q:
            params["q"] = q
        if cursor:
            params["cursor"] = cursor
        if order_by:
            params["order_by"] = order_by
        if order_direction:
            params["order_direction"] = order_direction

        async with self._session.get(
            f"v1/pages/{page_id}/resources",
            headers=await self._build_headers(auth),
            params=params,
        ) as response:
            if response.status == 404:
                raise PageNotFound(page_id)
            response.raise_for_status()
            return ResourcesResponse.model_validate_json(await response.read())

    async def page_get_attachments(
        self,
        page_id: int,
        *,
        page_size: int = 100,
        cursor: str | None = None,
        auth: YandexAuth | None = None,
    ) -> AttachmentListResponse:
        params: dict[str, Any] = {"page_size": page_size}
        if cursor:
            params["cursor"] = cursor

        async with self._session.get(
            f"v1/pages/{page_id}/attachments",
            headers=await self._build_headers(auth),
            params=params,
        ) as response:
            if response.status == 404:
                raise PageNotFound(page_id)
            response.raise_for_status()
            return AttachmentListResponse.model_validate_json(await response.read())

    async def page_create(
        self,
        *,
        slug: str,
        title: str,
        content: str,
        page_type: str = "wysiwyg",
        auth: YandexAuth | None = None,
    ) -> WikiPage:
        body = {
            "slug": normalize_slug(slug),
            "title": title,
            "content": content,
            "page_type": page_type,
        }
        async with self._session.post(
            "v1/pages",
            headers=await self._build_headers(auth),
            json=body,
        ) as response:
            response.raise_for_status()
            return WikiPage.model_validate_json(await response.read())

    async def page_update(
        self,
        page_id: int,
        *,
        title: str | None = None,
        content: str | None = None,
        allow_merge: bool = False,
        is_silent: bool = False,
        auth: YandexAuth | None = None,
    ) -> WikiPage:
        if title is None and content is None:
            raise ValueError("Provide at least one of title or content.")

        body: dict[str, Any] = {}
        if title is not None:
            body["title"] = title
        if content is not None:
            body["content"] = content

        params: dict[str, str] = {}
        if allow_merge:
            params["allow_merge"] = "true"
        if is_silent:
            params["is_silent"] = "true"

        async with self._session.post(
            f"v1/pages/{page_id}",
            headers=await self._build_headers(auth),
            json=body,
            params=params if params else None,
        ) as response:
            if response.status == 404:
                raise PageNotFound(page_id)
            response.raise_for_status()
            return WikiPage.model_validate_json(await response.read())

    async def page_append_content(
        self,
        page_id: int,
        *,
        content: str,
        location: str = "bottom",
        anchor: str | None = None,
        auth: YandexAuth | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {"content": content}
        if anchor:
            body["anchor"] = {"name": anchor}
        else:
            body["body"] = {"location": location}

        async with self._session.post(
            f"v1/pages/{page_id}/append-content",
            headers=await self._build_headers(auth),
            json=body,
        ) as response:
            if response.status == 404:
                raise PageNotFound(page_id)
            return await self._read_json(response)

    async def page_add_comment(
        self,
        page_id: int,
        *,
        body: str,
        parent_id: int | None = None,
        thread_id: int | None = None,
        auth: YandexAuth | None = None,
    ) -> PageComment:
        request_body: dict[str, Any] = {"body": body}
        if parent_id is not None:
            request_body["parent_id"] = parent_id
        if thread_id is not None:
            request_body["thread_id"] = thread_id

        async with self._session.post(
            f"v1/pages/{page_id}/comments",
            headers=await self._build_headers(auth),
            json=request_body,
        ) as response:
            if response.status == 404:
                raise PageNotFound(page_id)
            response.raise_for_status()
            return PageComment.model_validate_json(await response.read())

    async def page_delete(
        self,
        page_id: int,
        *,
        auth: YandexAuth | None = None,
    ) -> DeletePageResponse:
        async with self._session.delete(
            f"v1/pages/{page_id}",
            headers=await self._build_headers(auth),
        ) as response:
            if response.status == 404:
                raise PageNotFound(page_id)
            response.raise_for_status()
            return DeletePageResponse.model_validate_json(await response.read())

    async def page_recover(
        self,
        recovery_token: str,
        *,
        auth: YandexAuth | None = None,
    ) -> RecoverPageResponse:
        async with self._session.post(
            f"v1/recovery_tokens/{recovery_token}/recover",
            headers=await self._build_headers(auth),
        ) as response:
            response.raise_for_status()
            return RecoverPageResponse.model_validate_json(await response.read())

    async def upload_session_create(
        self,
        *,
        file_name: str,
        file_size: int,
        auth: YandexAuth | None = None,
    ) -> UploadSessionResponse:
        async with self._session.post(
            "v1/upload_sessions",
            headers=await self._build_headers(auth),
            json={"file_name": file_name, "file_size": file_size},
        ) as response:
            response.raise_for_status()
            return UploadSessionResponse.model_validate_json(await response.read())

    async def _upload_part(
        self,
        session_id: str,
        *,
        part_number: int,
        data: bytes,
        auth: YandexAuth | None = None,
    ) -> None:
        headers = await self._build_headers(auth)
        headers["Content-Type"] = "application/octet-stream"

        async with self._session.put(
            f"v1/upload_sessions/{session_id}/upload_part",
            headers=headers,
            params={"part_number": part_number},
            data=data,
        ) as response:
            response.raise_for_status()

    async def _finish_upload_session(
        self,
        session_id: str,
        *,
        auth: YandexAuth | None = None,
    ) -> None:
        async with self._session.post(
            f"v1/upload_sessions/{session_id}/finish",
            headers=await self._build_headers(auth),
        ) as response:
            response.raise_for_status()

    async def page_attach_upload_sessions(
        self,
        page_id: int,
        *,
        session_ids: list[str],
        auth: YandexAuth | None = None,
    ) -> AttachmentResultsResponse:
        async with self._session.post(
            f"v1/pages/{page_id}/attachments",
            headers=await self._build_headers(auth),
            json={"upload_sessions": session_ids},
        ) as response:
            if response.status == 404:
                raise PageNotFound(page_id)
            response.raise_for_status()
            return AttachmentResultsResponse.model_validate_json(await response.read())

    async def page_upload_attachment(
        self,
        page_id: int,
        *,
        file_path: str,
        append_markup: bool = False,
        append_location: str = "bottom",
        auth: YandexAuth | None = None,
    ) -> UploadAttachmentResult:
        path = Path(file_path)
        if not path.exists() or not path.is_file():
            raise FileNotFoundError(f"File not found: {file_path}")

        upload_session = await self.upload_session_create(
            file_name=path.name,
            file_size=path.stat().st_size,
            auth=auth,
        )

        with path.open("rb") as handle:
            part_number = 1
            while True:
                chunk = handle.read(self.CHUNK_SIZE)
                if not chunk:
                    break
                await self._upload_part(
                    upload_session.session_id,
                    part_number=part_number,
                    data=chunk,
                    auth=auth,
                )
                part_number += 1

        await self._finish_upload_session(upload_session.session_id, auth=auth)
        attachment_result = await self.page_attach_upload_sessions(
            page_id,
            session_ids=[upload_session.session_id],
            auth=auth,
        )

        appended_content: str | None = None
        if append_markup and attachment_result.results:
            first_attachment = attachment_result.results[0]
            appended_content = f'{{% file src="{first_attachment.download_url}" name="{first_attachment.name}" %}}'
            await self.page_append_content(
                page_id,
                content=appended_content,
                location=append_location,
                auth=auth,
            )

        return UploadAttachmentResult(
            page_id=page_id,
            attachments=attachment_result.results,
            appended_markup=append_markup,
            appended_content=appended_content,
        )
