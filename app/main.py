from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession
import logging
from typing import List

from .models_api import CityCreate, CityResponse, Coordinates, NearestCitiesResponse, HealthResponse
from .storage import CityStorage
from .geocoding_service import geocoding_service
from .config import settings
from .database import get_db, init_db, check_db_health

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.APP_NAME} v{settings.VERSION}")
    logger.info(f"Server running on {settings.HOST}:{settings.PORT}")
    
    await init_db()
    logger.info("Database initialized")
    
    yield
    
    await geocoding_service.close()
    logger.info(f"{settings.APP_NAME} stopped")


app = FastAPI(
    title=settings.APP_NAME,
    description="API для управления информацией о городах и поиска ближайших городов",
    version=settings.VERSION,
    lifespan=lifespan
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post(
    "/cities", 
    response_model=CityResponse, 
    status_code=status.HTTP_201_CREATED,
    summary="Добавить город",
    description="Добавляет город в хранилище. Координаты автоматически получаются из внешнего API"
)
async def add_city(
    city_data: CityCreate,
    db: AsyncSession = Depends(get_db)
):
    storage = CityStorage(db)
    
    if await storage.city_exists(city_data.name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Город '{city_data.name}' уже существует в базе"
        )
    
    coordinates = await geocoding_service.get_coordinates(city_data.name)
    
    if not coordinates:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Не удалось найти координаты для города '{city_data.name}'"
        )
    
    latitude, longitude = coordinates
    
    city = CityResponse(
        id=0,
        name=city_data.name,
        latitude=latitude,
        longitude=longitude
    )
    
    added_city = await storage.add_city(city)
    logger.info(f"City added: {added_city.name} (ID: {added_city.id})")
    return added_city


@app.get(
    "/cities", 
    response_model=List[CityResponse],
    summary="Получить все города",
    description="Возвращает список всех городов в хранилище"
)
async def get_all_cities(db: AsyncSession = Depends(get_db)):
    storage = CityStorage(db)
    cities = await storage.get_all_cities()
    return cities


@app.get(
    "/cities/{city_id}", 
    response_model=CityResponse,
    summary="Получить город по ID",
    description="Возвращает информацию о конкретном городе по его ID"
)
async def get_city(city_id: int, db: AsyncSession = Depends(get_db)):
    storage = CityStorage(db)
    city = await storage.get_city(city_id)
    if not city:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Город с ID {city_id} не найден"
        )
    return city

@app.delete(
    "/cities/{city_id}",
    status_code=status.HTTP_200_OK,
    summary="Удалить город",
    description="Удаляет город из хранилища по его ID"
)
async def delete_city(city_id: int, db: AsyncSession = Depends(get_db)):
    storage = CityStorage(db)
    deleted = await storage.delete_city(city_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Город с ID {city_id} не найден"
        )
    
    logger.info(f"City deleted: ID {city_id}")
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": f"Город с ID {city_id} успешно удален"}
    )


@app.post(
    "/cities/nearest",
    response_model=NearestCitiesResponse,
    summary="Найти ближайшие города",
    description="Возвращает 2 ближайших города к заданным координатам"
)
async def find_nearest_cities(
    coords: Coordinates,
    db: AsyncSession = Depends(get_db)
):
    storage = CityStorage(db)
    nearest_cities = await storage.find_nearest_cities(
        coords.latitude, 
        coords.longitude
    )
    
    if len(nearest_cities) < 2:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="В хранилище недостаточно городов для поиска ближайших"
        )
    
    return NearestCitiesResponse(
        coordinates=coords,
        nearest_cities=nearest_cities
    )


@app.get(
    "/health", 
    response_model=HealthResponse,
    summary="Проверка здоровья сервиса",
    description="Возвращает статус работы сервиса"
)
async def health_check():
    db_health = await check_db_health()
    status_text = "healthy" if db_health else "unhealthy"
    
    return HealthResponse(
        status=status_text, 
        service=settings.APP_NAME,
        version=settings.VERSION,
        database="connected" if db_health else "disconnected"
    )


@app.get(
    "/stats",
    summary="Статистика хранилища",
    description="Возвращает статистику по хранилищу городов"
)
async def get_stats(db: AsyncSession = Depends(get_db)):
    storage = CityStorage(db)
    stats = await storage.get_stats()
    return stats



# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(
#         "app.main:app",
#         host=settings.HOST,
#         port=settings.PORT,
#         reload=settings.RELOAD
#     )