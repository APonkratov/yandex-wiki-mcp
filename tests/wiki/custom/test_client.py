import re
from pathlib import Path
from tempfile import TemporaryDirectory

from aioresponses import aioresponses

from mcp_wiki.wiki.custom.client import WikiClient
from mcp_wiki.wiki.custom.errors import WikiApiError
from tests.aioresponses_utils import RequestCapture


class TestWikiClient:
    async def test_build_headers_with_token_and_org(
        self,
        wiki_client: WikiClient,
    ) -> None:
        headers = await wiki_client._build_headers()
        assert headers["Authorization"] == "OAuth test-token"
        assert headers["X-Org-Id"] == "test-org"

    async def test_page_get_by_slug(
        self,
        wiki_client: WikiClient,
    ) -> None:
        capture = RequestCapture(
            payload={"id": 10, "slug": "users/test/page", "title": "Page title"}
        )
        with aioresponses() as mocked:
            mocked.get(
                re.compile(r"https://api\.wiki\.yandex\.net/v1/pages.*"),
                callback=capture.callback,
            )
            page = await wiki_client.page_get_by_slug("users/test/page")

        assert page.id == 10
        capture.assert_called_once()
        capture.last_request.assert_headers(
            {
                "Authorization": "OAuth test-token",
                "X-Org-Id": "test-org",
            }
        )
        capture.last_request.assert_params({"slug": "users/test/page"})

    async def test_page_upload_attachment(
        self,
        wiki_client: WikiClient,
    ) -> None:
        with TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "example.txt"
            file_path.write_text("hello wiki", encoding="utf-8")

            upload_capture = RequestCapture(payload={"session_id": "session-1"})
            upload_part_capture = RequestCapture()
            finish_capture = RequestCapture()
            attach_capture = RequestCapture(
                payload={
                    "results": [
                        {
                            "id": 1,
                            "name": "example.txt",
                            "download_url": "https://wiki.yandex.net/file/example.txt",
                        }
                    ]
                }
            )

            with aioresponses() as mocked:
                mocked.post(
                    "https://api.wiki.yandex.net/v1/upload_sessions",
                    callback=upload_capture.callback,
                )
                mocked.put(
                    re.compile(
                        r"https://api\.wiki\.yandex\.net/v1/upload_sessions/session-1/upload_part.*"
                    ),
                    callback=upload_part_capture.callback,
                )
                mocked.post(
                    "https://api.wiki.yandex.net/v1/upload_sessions/session-1/finish",
                    callback=finish_capture.callback,
                )
                mocked.post(
                    "https://api.wiki.yandex.net/v1/pages/10/attachments",
                    callback=attach_capture.callback,
                )

                result = await wiki_client.page_upload_attachment(
                    10,
                    file_path=str(file_path),
                )

        assert result.page_id == 10
        assert result.attachments[0].name == "example.txt"
        upload_capture.assert_called_once()
        upload_part_capture.assert_called_once()
        finish_capture.assert_called_once()
        attach_capture.assert_called_once()

    async def test_page_append_content_with_anchor(
        self,
        wiki_client: WikiClient,
    ) -> None:
        capture = RequestCapture(payload={"id": 10, "slug": "users/test/page"})

        with aioresponses() as mocked:
            mocked.post(
                "https://api.wiki.yandex.net/v1/pages/10/append-content",
                callback=capture.callback,
            )
            await wiki_client.page_append_content(
                10,
                content="Anchored block",
                anchor="#release-notes",
            )

        capture.assert_called_once()
        capture.last_request.assert_json_body(
            {
                "content": "Anchored block",
                "anchor": {"name": "#release-notes"},
            }
        )

    async def test_page_append_content_anchor_not_found_raises_wiki_api_error(
        self,
        wiki_client: WikiClient,
    ) -> None:
        append_capture = RequestCapture(
            status=400,
            body=(
                '{"error_code":"ANCHOR_NOT_FOUND","debug_message":"Anchor not found","message":null}'
            ),
        )
        get_capture = RequestCapture(
            payload={
                "id": 10,
                "slug": "users/test/page",
                "content": "# Root\n\nNo explicit anchors here.\n\nBody",
            }
        )

        with aioresponses() as mocked:
            mocked.post(
                "https://api.wiki.yandex.net/v1/pages/10/append-content",
                callback=append_capture.callback,
            )
            mocked.get(
                re.compile(r"https://api\.wiki\.yandex\.net/v1/pages/10.*"),
                callback=get_capture.callback,
            )
            try:
                await wiki_client.page_append_content(
                    10,
                    content="Anchored block",
                    anchor="#release-notes",
                )
            except WikiApiError as exc:
                assert exc.status == 400
                assert exc.error_code == "ANCHOR_NOT_FOUND"
                assert exc.debug_message == "Anchor not found"
            else:  # pragma: no cover
                raise AssertionError("Expected WikiApiError to be raised")
        append_capture.assert_called_once()
        get_capture.assert_called_once()

    async def test_page_append_content_falls_back_to_source_anchor_replace(
        self,
        wiki_client: WikiClient,
    ) -> None:
        append_capture = RequestCapture(
            status=400,
            body=(
                '{"error_code":"ANCHOR_NOT_FOUND","debug_message":"Anchor not found","message":null}'
            ),
        )
        get_capture = RequestCapture(
            payload={
                "id": 10,
                "slug": "users/test/page",
                "content": "# Root\n\n## Section {#release-notes}\n\nBody",
            }
        )
        update_capture = RequestCapture(
            payload={"id": 10, "slug": "users/test/page", "title": "Updated"}
        )

        with aioresponses() as mocked:
            mocked.post(
                "https://api.wiki.yandex.net/v1/pages/10/append-content",
                callback=append_capture.callback,
            )
            mocked.get(
                re.compile(r"https://api\.wiki\.yandex\.net/v1/pages/10.*"),
                callback=get_capture.callback,
            )
            mocked.post(
                re.compile(r"https://api\.wiki\.yandex\.net/v1/pages/10.*"),
                callback=update_capture.callback,
            )
            result = await wiki_client.page_append_content(
                10,
                content="\n\nAppended under anchor.",
                anchor="#release-notes",
            )

        assert result["id"] == 10
        append_capture.assert_called_once()
        get_capture.assert_called_once()
        update_capture.assert_called_once()
        update_capture.last_request.assert_json_field(
            "content",
            "# Root\n\n## Section {#release-notes}\n\nAppended under anchor.\n\nBody",
        )
        update_capture.last_request.assert_param("allow_merge", "true")
