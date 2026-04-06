# Changelog

All notable changes to this project are documented in this file.

## [0.1.0] - 2026-04-06

### Added
- Initial release of `ya-yandex-wiki-mcp`
- FastMCP server for Yandex Wiki API with `stdio`, `sse`, and `streamable-http` transports
- Wiki HTTP client with support for:
  - page read by `page_id` or `slug`
  - subtree traversal via descendants endpoint
  - comments, resources, and attachments retrieval
  - page create, update, append, delete, and recover flows
  - multipart file upload and attachment linking
- MCP tools:
  - `page_get`
  - `page_get_descendants`
  - `page_get_comments`
  - `page_get_resources`
  - `page_get_attachments`
  - `page_create`
  - `page_update`
  - `page_append_content`
  - `page_add_comment`
  - `page_delete`
  - `page_recover`
  - `page_upload_attachment`
- Configuration resource `wiki-mcp://configuration`
- Project packaging files for PyPI/MCP registry/OCI metadata
- Basic repository documentation in English and Russian
- Test suite for:
  - MCP server registration
  - configuration resource
  - read/write MCP tools
  - core Wiki client requests

### Changed
- Adopted a modular MCP layout with separate settings, Wiki client, protocol models, MCP tools, and tests

### Verified
- `uv run ruff format .`
- `uv run ruff check . --fix`
- `uv run pytest`
