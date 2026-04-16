# Yet Another Yandex Wiki MCP Server

`mcp-name: io.github.APonkratov/ya-yandex-wiki-mcp`

Yet another MCP server for the Yandex Wiki API, focused on Wiki pages, comments, resources, attachments, and recovery workflows.
The current tool surface also includes first-class support for Yandex Wiki dynamic tables ("grids").

## Supported tools

- `page_get_grids`: list grids attached to a page
- `grid_get`: get a grid by `grid_id`
- `page_get`: get a page by `page_id` or `slug`
- `page_get_descendants`: get a page subtree
- `page_get_comments`: get page comments
- `page_get_resources`: get page resources, including attachments and grids
- `page_get_attachments`: get page attachments
- `grid_create`: create a grid on a page
- `grid_update`: update grid title and/or default sort
- `grid_delete`: delete a grid
- `grid_copy`: copy a grid to an existing target page
- `grid_add_rows`: add rows to a grid
- `grid_delete_rows`: delete rows from a grid
- `grid_update_cells`: update individual grid cells
- `grid_add_columns`: add columns to a grid
- `grid_delete_columns`: delete columns from a grid
- `grid_move_rows`: move a row inside a grid
- `grid_move_columns`: move a column inside a grid
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
- grid read/write operations
- subtree traversal for documentation sections
- comments for review and collaboration flows
- resources and attachments for document management
- recovery tokens for safe automation
- upload sessions for large local files

## Grid Notes

- All non-read tools are disabled when `WIKI_READ_ONLY=true`.
- Grid mutation tools use optimistic locking where the Wiki API requires `revision`.
- `grid_copy` returns operation metadata from the Wiki API, not a ready copied grid object.
- `grid_add_columns` requires `required` on every column because the real Wiki API validates it.
- `grid_update.default_sort` is verified against the real API as a list of single-entry mappings, for example `[{"status": "asc"}, {"priority": "desc"}]`.

These areas are documented in the official Yandex Wiki API references and examples:

- API overview: `https://yandex.ru/support/wiki/en/api-ref/about`
- API examples: `https://yandex.ru/support/wiki/ru/api-ref/examples`
- Page resources: `https://yandex.ru/support/wiki/ru/api-ref/pagesresources/pagesresources__resources`
- Grids API index: `https://yandex.ru/support/wiki/ru/api-ref/grids/`

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
- `WIKI_READ_ONLY=true|false`

## Run locally

```bash
uv sync --dev
uv run ya-yandex-wiki-mcp
```

## Docker deployment

The Docker image requires the same core environment variables as the local launch:

- one of `WIKI_TOKEN` or `WIKI_IAM_TOKEN`
- exactly one of `WIKI_ORG_ID` or `WIKI_CLOUD_ORG_ID`
- `TRANSPORT=streamable-http` for HTTP deployment

Optional:

- `HOST=0.0.0.0`
- `PORT=8000`
- `WIKI_API_BASE_URL=https://api.wiki.yandex.net`
- `WIKI_READ_ONLY=true|false`

## Using Pre-built Image (Recommended)

```bash
# Using environment file
docker run --env-file .env -p 8000:8000 ghcr.io/aponkratov/ya-yandex-wiki-mcp:latest

# With inline environment variables
docker run -e WIKI_TOKEN=your_token \
           -e WIKI_ORG_ID=your_org_id \
           -e TRANSPORT=streamable-http \
           -p 8000:8000 \
           ghcr.io/aponkratov/ya-yandex-wiki-mcp:latest
```

The MCP endpoint is available at `http://localhost:8000/mcp`.

## Building the Image Locally

```bash
docker build -t ya-yandex-wiki-mcp .
```

## Docker Compose

**Using pre-built image:**

```yaml
version: '3.8'
services:
  mcp-wiki:
    image: ghcr.io/aponkratov/ya-yandex-wiki-mcp:latest
    ports:
      - "8000:8000"
    environment:
      - WIKI_TOKEN=${WIKI_TOKEN}
      - WIKI_ORG_ID=${WIKI_ORG_ID}
      - TRANSPORT=streamable-http
```

**Building locally:**

```yaml
version: '3.8'
services:
  mcp-wiki:
    build: .
    ports:
      - "8000:8000"
    environment:
      - WIKI_TOKEN=${WIKI_TOKEN}
      - WIKI_ORG_ID=${WIKI_ORG_ID}
      - TRANSPORT=streamable-http
```

If you enable Redis-backed OAuth storage later, the existing [`compose.yaml`](compose.yaml) can be used as the Redis service baseline.

## Contributing

Before creating a commit or opening a merge request, run the full local verification set from [CONTRIBUTING.md](CONTRIBUTING.md).

## Tests

```bash
uv run pytest
```
