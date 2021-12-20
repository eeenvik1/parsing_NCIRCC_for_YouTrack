# parsing_NCIRCC_for_YouTrack
Скрипт позволяет заводить задачи в Панель мониторинга YouTrack на основе парсинга сайта safe-surf.ru

## Использование
Перед началом работы необходимо создать файл `.env` и добавить в него необходимые ссылки и креды.

Создать `.env` файл

```sh
touch .env
```

Добавить креды и ссылки в `.env`

```
PATH = '<PATH>'
YOU_TRACK_TOKEN='<YOUR_TOKEN>'
YOU_TRACK_PROJECT_ID = '<YOU_TRACK_PROJECT_ID>'
YOU_TRACK_BASE_URL = '<YOU_TRACK_BASE_URL>'
URL_GET_PRODUCTS = '<URL_GET_PRODUCTS>'
URL_GET_VERSIONS = '<URL_GET_VERSIONS>'
URL = "<URL>'
```
 

Для автоматической работы скрипта следует использовать `cron`
