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

## Docker deployment

Docker-образ требует те же базовые переменные окружения, что и локальный запуск:

- один из `WIKI_TOKEN` или `WIKI_IAM_TOKEN`
- ровно один из `WIKI_ORG_ID` или `WIKI_CLOUD_ORG_ID`
- `TRANSPORT=streamable-http` для HTTP deployment

Опционально:

- `HOST=0.0.0.0`
- `PORT=8000`
- `WIKI_API_BASE_URL=https://api.wiki.yandex.net`
- `WIKI_READ_ONLY=true|false`

## Использование готового образа (рекомендуется)

```bash
# Используя файл окружения
docker run --env-file .env -p 8000:8000 ghcr.io/aponkratov/ya-yandex-wiki-mcp:latest

# С встроенными переменными окружения
docker run -e WIKI_TOKEN=ваш_токен \
           -e WIKI_ORG_ID=ваш_org_id \
           -e TRANSPORT=streamable-http \
           -p 8000:8000 \
           ghcr.io/aponkratov/ya-yandex-wiki-mcp:latest
```

MCP endpoint будет доступен по адресу `http://localhost:8000/mcp`.

## Сборка образа локально

```bash
docker build -t ya-yandex-wiki-mcp .
```

## Docker Compose

**Используя готовый образ:**

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

**Сборка локально:**

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

Если позже понадобится Redis-backed OAuth storage, текущий [`compose.yaml`](compose.yaml) можно использовать как основу для Redis сервиса.

## Разработка

Перед коммитом и перед созданием или обновлением merge request нужно прогонять полный локальный набор проверок из [CONTRIBUTING.md](CONTRIBUTING.md).

## Тесты

```bash
uv run pytest
```
