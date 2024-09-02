# dit_test_case
### Запуск unit тестов

```shell
pytest -vv
```

### Сборка проекта
```shell
cp .env.example .env
```
### Установка зависимостей
```shell
python -m venv venv
```

```shell
source venv/bin/activate
```

```shell
pip install -r requirements.txt
```

```shell
python manage.py migrate
```
###
#### наполнение базы комнатами
```shell
python manage.py loaddata rooms.json
```

#### Сваггер доступен на
```shell
http://localhost:8000/swagger/
```
