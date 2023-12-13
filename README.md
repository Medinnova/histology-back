#Запуск проекта

##Как запустить проект локально

###Сначала устанавливаем зависимости:
`pip install -r requirements.txt`

Затем в '/gist_backend/gist_backend' создаем файл '.env'
Там должны быть следующие переменные:
```
EMAIL_HOST_USER=info@xn----7sbkbx3cfeek7g.xn--p1ai
EMAIL_HOST_PASSWORD=<тут вставить пароль от почты>
Debug=True
ACCESS_TOKEN_LIFETIME=5
REFRESH_TOKEN_LIFETIME=30
MAX_SECTIONS=20
```
###Можно запускать проект в папке /gist_backend:
`python manage.py runserver`

##Как запустить проект на сервере

###Подключаемся по ssh к серверу(можно и через любое другое ПО):
`ssh root@185.154.192.54`

Пароль можно узнать [тут](https://timeweb.cloud/my/servers/1533067).

###Gunicorn сервер уже запущен. Каждый раз когда делается git pull сервер можно перезагрузить следующим образом:
`sudo systemctl gunicorn restart`

На сервере также можно менять '.env' файл в '/gista-back/gist_backend/gist_backend/'
