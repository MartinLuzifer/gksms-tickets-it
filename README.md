# gksms-tickets-it

# Настройка:

1. Зайти в каталог `./config` и переименовать файлы `*.py.example` в `*.py`  
2. Заполнить поля конфигурационных файлов корректными данными

# Запуск

1. Установить необходимые компененты

       sudo apt update 
       sudo apt install -y git docker.io docker-compose

2. Скачать репозиторий на машину:

       sudo git clone https://github.com/MartinLuzifer/gksms-tickets-it.git

3. Запустить контейнер `mongodb`, используя файл `mongodb.yml` 

       sudo docker-compose -f mongodb.yml up -d

4. Дать права на исполнение для bash-скрипта

       chmod +x ./bot.sh

5. Запустить бота через bash-скрипт `bot.sh`. Будет создан образ и запущен контейнер

       sudo ./bot.sh start

6. Остановить бота. Будет остановлен и удален контейнер и удалится образ

       sudo ./bot.sh stop