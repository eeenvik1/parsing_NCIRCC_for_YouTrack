# Description
Скрипты для парсинга сайта OpenCVE и работы в YouTrack
```
main.py - основной скрипт, который заводит задачи в Панель мониторинга YouTrack
remove_repetitions.py - скрипт, который удаляет повторяющиеся задачи
```

## Install
Для установки запустить 
```pip3 install -r requirements.txt```

## Usage
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
URL = '<URL>'
EMAIL_HOST = '<EMAIL_HOST>'
EMAIL_PORT = '<EMAIL_PORT>'
EMAIL_HOST_PASSWORD = '<EMAIL_HOST_PASSWORD>'
EMAIL_HOST_USER = '<EMAIL_HOST_USER>'
MSG_TO = '<MSG_TO>'
```
Запуск скрипта
```
python3 main.py
```
Для автоматической работы скрипта следует использовать `cron`
Например запуск скрипта каждый час:
```
0 * * * * cd parsing_pdf && python3 parsing_pdf/main.py 
``` 

## Example
Пример работы скрипта main.py
![alt text](https://github.com/eeenvik1/parsing_NCIRCC_for_YouTrack/blob/main/example_youtrack(NCICC).png?raw=true)
