import re
from pathlib import Path
from tempfile import TemporaryDirectory

from aioresponses import aioresponses

from mcp_wiki.wiki.custom.client import WikiClient
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
