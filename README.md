
#  Foodgram - продуктовый помощник
![Yamdb_workflow](https://github.com/belkalev/yamdb_final/actions/workflows/yamdb_workflow.yml/badge.svg)

### Описание

На этом сервисе пользователи могут: 
- публиковать рецепты,
- подписываться на публикации других пользователей,
- добавлять понравившиеся рецепты в список «Избранное», 
- перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

### Стек технологий:

-   Python
-   Django
-   Django Rest Framework
-   PosgreSQL
-   Docker


## Запуск проекта

### Запуск проекта локально
 
 1. Клонировать репозиторий и перейти в него

` git@github.com:belkalev/foodgram-project-react.git`

2. Создать и активировать виртуальное окружение

`python3 -m venv venv`

`source venv/bin/activate `

3. Обновить pip и установить зависимости

` python3 -m pip install --upgrade pip `

` pip install -r requirements.txt`

4.  Перейти в папку **backend** 

`сd backend`

5.  Выполнить миграции и создать суперпользователя

`python manage.py makemigrations`

`python manage.py migrate`

`python manage.py createsuperuser`

6. Запустить сервер

`python3 manage.py runserver`

7. Для запуска fronted 
- необходимо выполнить загрузку терминала 
- перейти в папку где хранится проект и найти папку **infra**

8. Собрать контейнер

`docker-compose up --build`

### Запуск проекта на удаленном сервере
1. Выполните вход на свой удаленный сервер
    
2. Установите docker на сервер:

    `sudo apt install docker.io `

4. Установите docker-compose на сервер:
```
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

5. Локально отредактируйте файл infra/nginx.conf и в строке server_name впишите свой IP

6. Скопируйте файлы docker-compose.yml и nginx.conf из директории infra на сервер:

`scp docker-compose.yml <username>@<host>:/home/<username>/docker-compose.yml`
`scp nginx.conf <username>@<host>:/home/<username>/nginx.conf`

7. Cоздайте .env файл и впишите:
    ```
    DB_ENGINE=<django.db.backends.postgresql>
    DB_NAME=<имя базы данных postgres>
    DB_USER=<пользователь бд>
    DB_PASSWORD=<пароль>
    DB_HOST=<db>
    DB_PORT=<5432>
    SECRET_KEY=<секретный ключ проекта django>
    ```
    
8. Для работы с Workflow добавьте в Secrets GitHub переменные окружения для работы:
    ```
    DB_ENGINE=<django.db.backends.postgresql>
    DB_NAME=<имя базы данных postgres>
    DB_USER=<пользователь бд>
    DB_PASSWORD=<пароль>
    DB_HOST=<db>
    DB_PORT=<5432>
    
    DOCKER_PASSWORD=<пароль от DockerHub>
    DOCKER_USERNAME=<имя пользователя>
    
    SECRET_KEY=<секретный ключ проекта django>
    
    USER=<username для подключения к серверу>
    HOST=<IP сервера>
    PASSPHRASE=<пароль для сервера, если он установлен>
    SSH_KEY=<ваш SSH ключ (для получения команда: cat ~/.ssh/id_rsa)>
    
    TELEGRAM_TO=<ID чата, в который придет сообщение>
    TELEGRAM_TOKEN=<токен вашего бота>
    ```
    
9.  Workflow состоит из трёх шагов:
    
    -   Проверка кода на соответствие PEP8
    -   Сборка и публикация образа бекенда на DockerHub.
    -   Автоматический деплой на удаленный сервер.
    -   Отправка уведомления в телеграм-чат.
 
10. На сервере соберите docker-compose:
 
`sudo docker-compose up -d --build`

11. После успешной сборки на сервере выполните команды (только после первого деплоя):
    
  -   Соберите статические файлы:
  
    `sudo docker-compose exec backend python manage.py collectstatic --noinput`
    
   - Примените миграции:
    
    `sudo docker-compose exec backend python manage.py migrate --noinput`
    
   -   Загрузите ингридиенты в базу данных (необязательно):  
        _Если файл не указывать, по умолчанию выберется ingredients.json_
        
    `sudo docker-compose exec backend python manage.py load_ingredients <Название файла из директории data>`
    
   -   Создать суперпользователя Django:
 
    `sudo docker-compose exec backend python manage.py createsuperuser`
    
   -   Проект будет доступен по вашему IP


Проект доступен по адресе http://158.160.4.123/recipes/

Проект выполнен студентом курса Python-разработчик плюс Малявко  
                 Татьяной
