# Yet Another Yandex Wiki MCP Server

Yet another MCP сервер для публичного API Yandex Wiki. Структура проекта повторяет подход `yandex-tracker-mcp`: отдельные `settings`, HTTP-клиент, MCP resources/tools, optional OAuth provider и тесты. Текущий набор инструментов включает полноценную поддержку динамических таблиц Yandex Wiki.

## Реализованные инструменты

- `page_get_grids`
- `grid_get`
- `page_get`
- `page_get_descendants`
- `page_get_comments`
- `page_get_resources`
- `page_get_attachments`
- `grid_create`
- `grid_update`
- `grid_delete`
- `grid_copy`
- `grid_add_rows`
- `grid_delete_rows`
- `grid_update_cells`
- `grid_add_columns`
- `grid_delete_columns`
- `grid_move_rows`
- `grid_move_columns`
- `page_create`
- `page_update`
- `page_append_content`
- `page_add_comment`
- `page_delete`
- `page_recover`
- `page_upload_attachment`

## Почему именно этот набор

Я ориентировался на публичную документацию Yandex Wiki API и выбрал операции, которые действительно полезны в MCP-сценариях:

- чтение и изменение страниц
- чтение и изменение динамических таблиц
- обход поддерева документации
- работа с комментариями
- работа с ресурсами и вложениями
- безопасное удаление и восстановление
- multipart upload локальных файлов с прикреплением к странице

## Особенности grids

- При `WIKI_READ_ONLY=true` скрываются все non-read tools, а не только grid-операции.
- Там, где API требует optimistic locking, mutation tools принимают `revision`.
- `grid_copy` возвращает metadata асинхронной операции, а не готовую копию таблицы.
- Для `grid_add_columns` каждая колонка должна содержать поле `required`, потому что это требует реальный API Yandex Wiki.
- `grid_update.default_sort` проверен на реальном API и должен передаваться как список одноэлементных словарей, например `[{"status": "asc"}, {"priority": "desc"}]`.

Официальные материалы:

- обзор API: `https://yandex.ru/support/wiki/en/api-ref/about`
- примеры API: `https://yandex.ru/support/wiki/ru/api-ref/examples`
- ресурсы страниц: `https://yandex.ru/support/wiki/ru/api-ref/pagesresources/pagesresources__resources`
- индекс API по таблицам: `https://yandex.ru/support/wiki/ru/api-ref/grids/`

## Переменные окружения

Нужен один из токенов:

- `WIKI_TOKEN`
- `WIKI_IAM_TOKEN`

И ровно один идентификатор организации:

- `WIKI_ORG_ID`
- `WIKI_CLOUD_ORG_ID`

Опционально:

- `TRANSPORT=stdio|sse|streamable-http`
- `WIKI_API_BASE_URL=https://api.wiki.yandex.net`
- `WIKI_READ_ONLY=true|false`

## Локальный запуск

```bash
uv sync --dev
uv run ya-yandex-wiki-mcp
```

## Тесты

```bash
uv run pytest
```
