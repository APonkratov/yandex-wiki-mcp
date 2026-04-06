# Yet Another Yandex Wiki MCP Server

`mcp-name: io.github.APonkratov/ya-yandex-wiki-mcp`

Yet another MCP server for the Yandex Wiki API, focused on Wiki pages, comments, resources, attachments, and recovery workflows.

## Supported tools

- `page_get`: get a page by `page_id` or `slug`
- `page_get_descendants`: get a page subtree
- `page_get_comments`: get page comments
- `page_get_resources`: get page resources, including attachments and grids
- `page_get_attachments`: get page attachments
- `page_create`: create a page
- `page_update`: update page title and/or full content
- `page_append_content`: append content to top, bottom, or anchor
- `page_add_comment`: add a page comment or reply
- `page_delete`: delete a page and receive recovery token
- `page_recover`: recover a page by recovery token
- `page_upload_attachment`: upload a local file in chunks and attach it to a page

## Why these tools

The toolset is based on the public Yandex Wiki API areas that are most useful in an MCP workflow:

- page read/write operations
- subtree traversal for documentation sections
- comments for review and collaboration flows
- resources and attachments for document management
- recovery tokens for safe automation
- upload sessions for large local files

These areas are documented in the official Yandex Wiki API references and examples:

- API overview: `https://yandex.ru/support/wiki/en/api-ref/about`
- API examples: `https://yandex.ru/support/wiki/ru/api-ref/examples`
- Page resources: `https://yandex.ru/support/wiki/ru/api-ref/pagesresources/pagesresources__resources`

## Authentication

Set one of these:

- `WIKI_TOKEN`
- `WIKI_IAM_TOKEN`

And exactly one organization header source:

- `WIKI_ORG_ID`
- `WIKI_CLOUD_ORG_ID`

Optional:

- `TRANSPORT=stdio|sse|streamable-http`
- `WIKI_API_BASE_URL=https://api.wiki.yandex.net`

## Run locally

```bash
uv sync --dev
uv run ya-yandex-wiki-mcp
```

## Tests

```bash
uv run pytest
```
