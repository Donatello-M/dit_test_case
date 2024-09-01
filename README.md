# dit_test_case
### Запуск unit тестов

```shell
pytest -vv
```

### Сборка проекта
```shell
cp .env.example .env
```

```shell
python manage.py migrate
```
###
####наполнение базы комнатами
```shell
python manage.py loaddata rooms.json
```

####Сваггер доступен на
```shell
http://localhost:8000/swagger/
```