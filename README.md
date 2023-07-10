# gksms-tickets-it



   
# Установка:

1. Установить необходимые компоненты

       sudo apt update 
       sudo apt install -y git docker.io docker-compose

2. Скачать репозиторий на машину:

       sudo git clone https://github.com/MartinLuzifer/gksms-tickets-it.git

# Настройка:

1. Переименовать каталог `config_example` в `config`  
2. В файле `config/tgb_token.py` указать токен вашего бота
3. В файле `config/itop_cred.py` указать логин и пароль от сервера itop
4. В файле `config/mongodb.py` указать логин и пароль от СУБД

   - Указать такой же пароль в файле `docker-compose.yml`)
   ```yaml
   ...    
   environment:
     MONGO_INITDB_ROOT_USERNAME: root
     MONGO_INITDB_ROOT_PASSWORD: gfWUIR
   ...
   ```

# Запуск:

1. Запустить бота и mongodb

       sudo docker-compose up -d

2. Проверить работоспособность

# Альтернативный способ запуска


1. Использовать bash-скрипт для запуска

       ./bot.sh start

2. Использовать bash-скрипт для остановки (будет удален контейнер и образ контейнера)

       ./bot.sh stop