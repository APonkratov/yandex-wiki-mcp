# Wiki Grids Support Plan

## Branch

- Working branch: `feature/wiki-grids-support-plan`

## Current Status

Implemented in this branch:

- Phase 1 read path:
  - `page_get_grids`
  - `grid_get`
- Phase 2 / adjacent write path:
  - `grid_create`
  - `grid_update`
  - `grid_delete`
  - `grid_copy`
  - `grid_add_rows`
  - `grid_delete_rows`
  - `grid_update_cells`
- Phase 3 partial structural editing:
  - `grid_add_columns`
  - `grid_delete_columns`
  - `grid_move_rows`
  - `grid_move_columns`

Implemented behavior:

- all new write tools remain behind the existing `wiki_read_only` gate, which disables all non-read MCP tools;
- grid cell values stay typed and are not stringified;
- `revision` is required where the confirmed API contract requires optimistic locking;
- MCP layer validates destructive and structural operations before calling the client;
- client and MCP tests are green for the implemented surface.

Latest verification:

- `uv run pytest -q`
- result: `102 passed`
- live userspace probe:
  - all currently implemented grid methods were exercised against real temporary pages
  - `grid_update.title` works
  - `grid_update.default_sort` is confirmed as a list of single-entry mappings such as `[{"status": "asc"}]`

## Goal

Add first-class support for Yandex Wiki dynamic tables ("grids") to this MCP server in a way that:

- matches the current Python architecture;
- preserves safe read-only mode behavior;
- supports incremental delivery;
- keeps tool schemas explicit and testable;
- avoids lossy type conversion for grid cell values.

## Confirmed API Capability

Based on the official Yandex Wiki API documentation, grids support more than read operations.

Available endpoint groups:

- create grid;
- get grid;
- update grid;
- delete grid;
- add rows;
- delete rows;
- add columns;
- delete columns;
- update cells;
- move rows;
- move columns;
- copy grid.

Reference index:

- https://yandex.ru/support/wiki/ru/api-ref/grids/
- https://yandex.ru/support/wiki/ru/api-ref/grids/grids__create_grid

## Recommended Delivery Strategy

Implement support in 3 phases instead of shipping all write operations at once.

### Phase 1: Read Path

Ship the minimum useful read functionality first.

Tools:

- `page_get_grids`
- `grid_get`

Why first:

- lowest risk;
- aligns with existing `page_get_resources`;
- useful immediately for discovery and analysis;
- validates the response models before write support is added.

### Phase 2: Core Write Path

Add high-value write operations needed for normal automation workflows.

Tools:

- `grid_create`
- `grid_update`
- `grid_delete`
- `grid_copy`
- `grid_add_rows`
- `grid_update_cells`

Current status:

- implemented:
  - `grid_create`
  - `grid_update`
  - `grid_delete`
  - `grid_copy`
  - `grid_add_rows`
  - `grid_delete_rows`
  - `grid_update_cells`
- not yet implemented:
  - none

Why this set:

- enough to create and maintain grids programmatically;
- covers the most common data-entry and synchronization flows;
- keeps the first write release smaller than full structure management.

### Phase 3: Full Structural Editing

Add the remaining structural operations.

Tools:

- `grid_delete_rows`
- `grid_add_columns`
- `grid_delete_columns`
- `grid_move_rows`
- `grid_move_columns`

Current status:

- implemented:
  - `grid_delete_rows`
  - `grid_add_columns`
  - `grid_delete_columns`
  - `grid_move_rows`
  - `grid_move_columns`
- not yet implemented:
  - none

Why later:

- more complex input schemas;
- stronger validation requirements;
- higher chance of destructive mistakes from LLM-generated calls.

## Proposed Tool Surface

Tool names should follow the current project naming style and stay consistent with existing page tools.

### Read Tools

- `page_get_grids`
  - input:
    - `page_id` or `slug`
    - `page_size`
    - `cursor`
    - `order_by`
    - `order_direction`
  - output:
    - list of grid summaries
    - `next_cursor`
    - `prev_cursor`

- `grid_get`
  - input:
    - `grid_id`
    - `fields`
    - `filter`
    - `only_cols`
    - `only_rows`
    - `revision`
    - `sort`
  - output:
    - full grid payload

### Write Tools

- `grid_create`
  - input:
    - `page_id` or `slug`
    - `title`
    - optional `structure`
    - optional initial `rows`
    - optional `rich_text_format`
  - output:
    - created grid object

- `grid_update`
  - input:
    - `grid_id`
    - required `revision`
    - optional `title`
    - optional `default_sort` as `[{column_slug: "asc"|"desc"}]`
  - output:
    - update response, typically containing new `revision`

- `grid_delete`
  - input:
    - `grid_id`
  - output:
    - deletion result or empty success body

- `grid_copy`
  - input:
    - `grid_id`
    - required target `page_id` or `slug`
    - optional `title`
  - output:
    - copied grid object

- `grid_add_rows`
  - input:
    - `grid_id`
    - required `revision`
    - `rows`
    - optional `position`
    - optional `after_row_id`
  - output:
    - new `revision`
    - created rows

- `grid_delete_rows`
  - input:
    - `grid_id`
    - required `revision`
    - `row_ids`
  - output:
    - new `revision`

- `grid_add_columns`
  - input:
    - `grid_id`
    - required `revision`
    - `columns`
    - optional `position`
    - optional `after_column_id`
  - output:
    - new `revision`
    - created columns

- `grid_delete_columns`
  - input:
    - `grid_id`
    - required `revision`
    - `column_ids`
  - output:
    - new `revision`

- `grid_update_cells`
  - input:
    - `grid_id`
    - required `revision`
    - cell patch payload
  - output:
    - new `revision`
    - updated rows or cells depending on upstream API

- `grid_move_rows`
  - input:
    - `grid_id`
    - required `revision`
    - `row_ids`
    - optional `position`
    - optional `after_row_id`
  - output:
    - new `revision`

- `grid_move_columns`
  - input:
    - `grid_id`
    - required `revision`
    - `column_ids`
    - optional `position`
    - optional `after_column_id`
  - output:
    - new `revision`

## Model Design

### Principle

Do not copy the Go implementation's lossy behavior of converting all cell values to strings.

In this project, grid cells should remain typed as `Any` because:

- Python and Pydantic can preserve native JSON types naturally;
- numbers, booleans, arrays, objects, and null must survive round trips;
- write operations need typed payloads, not stringified approximations.

### New Models in `mcp_wiki/wiki/proto/types/pages.py`

Read models:

- `GridFieldEnum`
- `GridSortDirectionEnum`
- `GridColumnTypeEnum`
- `GridColumnPinEnum`
- `GridColorEnum`
- `GridTextFormatEnum`
- `WikiGridPageRef`
- `WikiGridColumn`
- `WikiGridSort`
- `WikiGridStructure`
- `WikiGridRow`
- `WikiGridSummary`
- `WikiGrid`
- `GridsResponse`

Write request/response models:

- `GridCreateRequest`
- `GridUpdateRequest`
- `GridCopyRequest`
- `GridAddRowsRequest`
- `GridDeleteRowsRequest`
- `GridAddColumnsRequest`
- `GridDeleteColumnsRequest`
- `GridUpdateCellsRequest`
- `GridMoveRowsRequest`
- `GridMoveColumnsRequest`
- `GridMutationResponse`

Implementation note:

- keep `extra="allow"` for forward compatibility with upstream API changes;
- use explicit field aliases where Yandex API names differ from Python style;
- preserve row and cell payloads as structured JSON.

## Protocol Changes

Extend `mcp_wiki/wiki/proto/pages.py` with new protocol methods:

- `page_get_grids(...) -> GridsResponse`
- `grid_get(...) -> WikiGrid`
- `grid_create(...) -> WikiGrid`
- `grid_update(...) -> GridUpdateResponse`
- `grid_delete(...) -> dict[str, Any]`
- `grid_copy(...) -> WikiGrid`
- `grid_add_rows(...) -> GridMutationResponse`
- `grid_delete_rows(...) -> GridMutationResponse`
- `grid_add_columns(...) -> GridMutationResponse`
- `grid_delete_columns(...) -> GridMutationResponse`
- `grid_update_cells(...) -> GridMutationResponse`
- `grid_move_rows(...) -> GridMutationResponse`
- `grid_move_columns(...) -> GridMutationResponse`

## Client Changes

Extend `mcp_wiki/wiki/custom/client.py`.

### New read methods

- `page_get_grids`
  - `GET /v1/pages/{page_id}/grids`

- `grid_get`
  - `GET /v1/grids/{grid_id}`

### New write methods

- `grid_create`
  - `POST /v1/grids`

- `grid_update`
  - likely `POST /v1/grids/{grid_id}` or the exact upstream update endpoint

- `grid_delete`
  - grid delete endpoint from upstream docs

- `grid_copy`
  - copy endpoint from upstream docs

- `grid_add_rows`
  - `POST /v1/grids/{grid_id}/rows`

- `grid_delete_rows`
  - delete-rows endpoint from upstream docs

- `grid_add_columns`
  - add-columns endpoint from upstream docs

- `grid_delete_columns`
  - delete-columns endpoint from upstream docs

- `grid_update_cells`
  - update-cells endpoint from upstream docs

- `grid_move_rows`
  - move-rows endpoint from upstream docs

- `grid_move_columns`
  - move-columns endpoint from upstream docs

### Client implementation rules

- reuse `_build_headers`;
- reuse `_read_json` for mutation endpoints that may return partial bodies;
- always pass `revision` for mutating operations that require optimistic locking;
- resolve `slug` to `page_id` in MCP layer, not client layer;
- return typed Pydantic models whenever response shape is stable.

## MCP Layer Changes

### `mcp_wiki/mcp/params.py`

Add typed params and enums for grid tools:

- `GridID`
- `GridFields`
- `GridPageSize`
- `GridOrderBy`
- `GridOrderDirection`
- `GridColumnIDs`
- `GridRowIDs`

Potentially add helper models for:

- column schemas;
- row payloads;
- cell patch payloads.

### `mcp_wiki/mcp/tools/page_read.py`

Add:

- `page_get_grids`
- `grid_get`

Behavior:

- `page_get_grids` should accept `page_id` or `slug`;
- `grid_get` should accept `grid_id` only;
- both tools should be marked `readOnlyHint=True`.

### `mcp_wiki/mcp/tools/page_write.py`

Add all mutating grid tools and register them only when `wiki_read_only` is false.

Behavior:

- all grid write tools must disappear in read-only mode, same as existing page write tools;
- for page-targeted operations, resolve `slug` to `page_id` through existing helper flow;
- require `revision` where upstream API expects concurrency control.

## Safety Rules

Because grid mutations are significantly more destructive than page comments or append operations, add explicit guardrails.

### Mandatory validation

- forbid empty `rows`, `columns`, `row_ids`, `column_ids` when arrays are required;
- validate `page_size` bounds;
- validate mutual exclusivity such as `position` vs `after_*` where needed;
- validate enum-like values in MCP layer before client call;
- require `revision` for every mutation endpoint that supports optimistic locking.

### Recommended tool descriptions

Each mutating tool description should say:

- it changes structured data;
- caller should fetch latest grid first;
- caller must pass current `revision`;
- wrong revision may cause conflict or failure.

### Read-only mode

The current `wiki_read_only` switch should remain the single feature gate for all new write tools.

## Data Modeling Decisions

### Row representation

Prefer a schema that preserves the upstream row payload shape.

Recommended structure:

- `id`
- `row` as ordered list of cell values when upstream uses positional rows;
- optional `cells` only if the API also provides keyed data in some endpoints;
- `pinned`
- `color`

Important:

- the Go project simplified rows into `map[column_slug] -> string`;
- that is not a good fit for this project because future write support depends on preserving the actual API structure.

### Column representation

Support all documented column fields from the start:

- `id`
- `slug`
- `title`
- `type`
- `required`
- `width`
- `width_units`
- `pinned`
- `color`
- `multiple`
- `format`
- `ticket_field`
- `select_options`
- `mark_rows`
- `description`

## Test Plan

### Unit tests for client

Add request/response coverage in `tests/wiki/custom/test_client.py` for:

- `page_get_grids`
- `grid_get`
- `grid_create`
- `grid_update`
- `grid_delete`
- `grid_copy`
- `grid_add_rows`
- `grid_delete_rows`
- `grid_add_columns`
- `grid_delete_columns`
- `grid_update_cells`
- `grid_move_rows`
- `grid_move_columns`

Assertions:

- URL path;
- query params;
- request JSON payload;
- auth headers;
- typed response parsing;
- revision propagation.

### MCP tool tests

Add coverage in:

- `tests/mcp/tools/test_page_read_tools.py`
- `tests/mcp/tools/test_page_write_tools.py`

Assertions:

- proper tool registration;
- `slug` to `page_id` resolution;
- `wiki_read_only` hides mutating grid tools;
- validated parameters reach the protocol client correctly;
- required fields fail early with clear errors.

### Server registration tests

Extend `tests/mcp/server/test_server_creation.py` to verify:

- read tools are always present;
- write tools are absent in read-only mode;
- write tools are present otherwise.

## Documentation Changes

Update:

- `README.md`
- `README_ru.md`
- `CHANGELOG.md`

Document:

- new read tools;
- new write tools;
- read-only gating;
- revision requirement for mutations;
- examples for read and write scenarios.

## Suggested Implementation Order

1. Add read-side grid models.
2. Add protocol signatures for read operations.
3. Implement `page_get_grids` and `grid_get` in client.
4. Add read MCP tools and tests.
5. Add write-side request/response models.
6. Implement `grid_create`, `grid_update`, `grid_delete`, `grid_copy`.
7. Implement row operations.
8. Implement column operations.
9. Implement move operations.
10. Implement `grid_update_cells`.
11. Tighten validation and improve docs.

## Scope Recommendation

Recommended target for the first implementation PR:

- full Phase 1;
- `grid_create`;
- `grid_update`;
- `grid_add_rows`;
- `grid_update_cells`.

Reason:

- enough to support serious grid automation;
- smaller than full structural CRUD;
- easier to validate against real API behavior.

## Open Questions Before Implementation

- exact update/delete/copy endpoint paths and body shapes for all grid mutations should be verified against official docs before coding each method;
- whether `grid_update` supports partial updates or expects full structure payload;
- whether row payloads are always positional arrays or sometimes keyed objects;
- whether copy endpoint can target another page by slug directly or only by page id;
- whether some grid mutation responses return full grid objects versus revision-only bodies.

## Remaining Work

### High Priority

- no remaining grid operations in code

### Documentation

- update `README.md`
- update `README_ru.md`
- update `CHANGELOG.md`

### API Gaps Blocking Safe Implementation

- `grid_copy`:
  - confirmed by real API probe
  - request:
    - endpoint: `POST /v1/grids/{idx}/clone`
    - body:
      - `target`: string slug of an existing target page
      - optional `title`
  - response:
    - async operation metadata with `operation`, `dry_run`, `status_url`
  - caveat:
    - `status_url` from the API was not reliable in the probe and returned `404`, while the clone itself still completed
- `grid_delete_rows`:
  - confirmed by real API probe
  - request:
    - endpoint: `DELETE /v1/grids/{idx}/rows`
    - body:
      - `revision`
      - `row_ids`
  - response:
    - `{"revision": "..."}`
- `grid_delete_columns`, `grid_move_rows`, `grid_move_columns`:
  - confirmed by real API probes
  - `grid_delete_columns`:
    - endpoint: `DELETE /v1/grids/{idx}/columns`
    - body:
      - `revision`
      - `column_slugs`
    - response:
      - `{"revision": "..."}`
  - `grid_move_rows`:
    - endpoint: `POST /v1/grids/{idx}/rows/move`
    - body:
      - `revision`
      - `row_id`
      - exactly one of:
        - `position`
        - `after_row_id`
    - response:
      - `{"revision": "..."}`
  - `grid_move_columns`:
    - endpoint: `POST /v1/grids/{idx}/columns/move`
    - body:
      - `revision`
      - `column_slug`
      - `position`
    - response:
      - `{"revision": "..."}`

### Real API Notes

- `grid_add_columns`:
  - real API requires `required` on every new column
  - MCP validation was tightened accordingly
- `grid_update`:
  - real API supports partial updates
  - title-only updates succeed
  - response may be revision-only, for example `{"revision": "2"}`
  - `default_sort` is accepted only as a list of single-entry mappings, for example:
    - `[{"status": "asc"}]`
    - `[{"status": "asc"}, {"priority": "desc"}]`
  - shapes like `[{"slug": "status", "direction": "asc"}]` are rejected by the API
- `grid_copy`:
  - the copy itself was confirmed by real API
  - returned `status_url` was not reliable in the probe and may return `404` even when the copy completed
  - for now the tool returns the raw operation metadata and does not try to poll it

### Recommended Next Step

Grid operation support in code is complete for the currently planned surface.

Recommended next steps:

1. update `README.md`
2. update `README_ru.md`
3. update `CHANGELOG.md`
4. optionally add a dedicated helper around operation polling for `grid_copy` if the operations API behavior can be made reliable

## Definition of Done

Grid support is done when:

- read-only tools expose list/get operations for grids;
- write tools are implemented behind the existing read-only gate;
- cell values remain typed;
- optimistic locking via `revision` is enforced;
- tests cover both client and MCP layers;
- README and changelog describe the new capability.
