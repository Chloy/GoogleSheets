### Тестовое задание для компании Каналсервис
---
Файл GoogleSheets https://docs.google.com/spreadsheets/d/1ZZGVwnOgCkglTk5WHS6yXQkLNjsolbMmXilCbWsrGuo/edit#gid=0

Данные для подключения к БД стандартные:
- User: postgres
- Password:
- Database: postgres
- Table: purchases


#### Инструкция по запуску
1. Нужно запустить команду ```docker-compose up --build -d``` (в зависимости от вашей версии docker вам может не подойти данная команда, тогда попробуйте эту ```docker compose up --build -d```) из директории с файлом docker-compose.yml
2. Чтобы проверить БД нужно выполнить команды:
- ```docker exec -it psql /bin/bash``` вы попадете в контейнер с БД
- ```psql -U postgres``` подключение к БД
- ```\c postgres``` подключение к базе postgres
- ```select * from purchases;``` будут выведены все записи из таблицы.
Чтобы выйти двады введите ```exit```

Скрипт работает постоянно и каждые 15 секунд обновляет данные в БД в соответствии с таблицей.