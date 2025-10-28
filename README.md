# City API

HTTP API для управления информацией о городах и поиска ближайших городов. Приложение автоматически получает координаты городов из OpenStreetMap.

## Возможности

- ✅ Добавление/удаление городов в хранилище
- ✅ Получение информации о городах
- ✅ Поиск 2 ближайших городов по координатам
- ✅ Автоматическое получение координатов из OpenStreetMap
- ✅ Полностью асинхронная архитектура
- ✅ Документация API (Swagger/ReDoc)
- ✅ Health checks и мониторинг


## Технологии

- **Python 3.11** + **FastAPI** + **SQLAlchemy 2.0**
- **PostgreSQL 15** + **asyncpg**
- **Docker** + **Docker Compose**
- **Alembic** (миграции базы данных)
- **Geopy** (географические расчеты)
- **AIOHTTP** (асинхронные HTTP запросы)


## Быстрый запуск и настройка

### 1. Клонирование репозитория

```bash
git clone git@github.com:opchik/test_cdnvideo.git
cd test_cdnvideo
```

### 2. Создание файла переменных окружения в корне 
### и добавление данных данных для примера
### Здесь необходимо ввести ваши данные 
В примере указаны тестовые данные (за исключением ссылок сервиса geocoding)
```bash
cat > .env << 'EOF'
HOST=0.0.0.0
PORT=8000
RELOAD=true

POSTGRES_DB=city_db
POSTGRES_USER=postgres
POSTGRES_HOST=localhost
POSTGRES_PASSWORD=postgres
POSTGRES_PORT=5432

GEOCODING_BASE_URL=https://nominatim.openstreetmap.org/search
GEOCODING_USER_AGENT=CityAPI/1.0
EOF

echo "✅ Файл .env успешно создан в корне проекта"
```

### 3. Сборка и запуск контейнеров
```bash
sudo docker-compose up -d --build
```

### 4. Проверка статуса (если нужно)
```bash
sudo docker-compose ps
```

### 5. Создание и применение миграций
``` bash
sudo docker-compose exec city-api alembic revision --autogenerate -m "Initial tables"
sudo docker-compose exec city-api alembic upgrade head
```

### 6. Проверка логов
``` bash
# Логи сервиса
sudo docker-compose logs -f city-api
# Логи базы данных
sudo docker-compose logs -f postgres
# Логи всего сервиса
sudo docker-compose logs -f
```


После запуска проекта на локальной машине - можно проверить функциональность api по этой ссылке (документация FastAPI):

http://localhost:8000/docs


## API Endpoints
Метод	Endpoint	    Описание
---------------------------------
POST	/cities	        Добавить город
GET	    /cities	        Получить все города
GET	    /cities/{id}	Получить город по ID
DELETE	/cities/{id}	Удалить город
POST	/cities/nearest	Найти ближайшие города
GET	    /health	        Проверка здоровья
GET	    /stats	        Статистика хранилища