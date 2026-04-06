# Yet Another Yandex Wiki MCP Server

Yet another MCP сервер для публичного API Yandex Wiki. Структура проекта повторяет подход `yandex-tracker-mcp`: отдельные `settings`, HTTP-клиент, MCP resources/tools, optional OAuth provider и тесты.

## Реализованные инструменты

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

## Почему именно этот набор

Я ориентировался на публичную документацию Yandex Wiki API и выбрал операции, которые действительно полезны в MCP-сценариях:

- чтение и изменение страниц
- обход поддерева документации
- работа с комментариями
- работа с ресурсами и вложениями
- безопасное удаление и восстановление
- multipart upload локальных файлов с прикреплением к странице

Официальные материалы:

- обзор API: `https://yandex.ru/support/wiki/en/api-ref/about`
- примеры API: `https://yandex.ru/support/wiki/ru/api-ref/examples`
- ресурсы страниц: `https://yandex.ru/support/wiki/ru/api-ref/pagesresources/pagesresources__resources`

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

## Локальный запуск

```bash
uv sync --dev
uv run ya-yandex-wiki-mcp
```

## Тесты

```bash
uv run pytest
```
