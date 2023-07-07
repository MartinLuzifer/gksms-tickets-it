# gksms-tickets-it

# Настройка:

1. Переименовать каталог `config_example` в `config`  
2. В файле `config/tgb_token.py` указать токен вашего бота
3. В файле `config/itop_cred.py` указать логин и пароль от сервера itop
4. В файле `config/mongodb.py` указать логин и пароль от субд
   - Указать такой же пароль в файле `docker-compose.yml`)
   ```yaml
   ...    
   environment:
     MONGO_INITDB_ROOT_USERNAME: root
     MONGO_INITDB_ROOT_PASSWORD: gfWUIR
   ...
   ```

   
# Запуск

1. Установить необходимые компоненты

       sudo apt update 
       sudo apt install -y git docker.io docker-compose

2. Скачать репозиторий на машину:

       sudo git clone https://github.com/MartinLuzifer/gksms-tickets-it.git

3. Запустить бота и mongodb

       sudo docker-compose up -d
