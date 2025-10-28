from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.sql.expression import cast
from sqlalchemy import Float
from geopy.distance import geodesic

from .models_db import DBCity
from .models_api import CityResponse
from .database import get_db

class CityStorage:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def add_city(self, city_data: CityResponse) -> CityResponse:
        """Добавление города в базу данных"""
        db_city = DBCity(
            name=city_data.name,
            latitude=city_data.latitude,
            longitude=city_data.longitude
        )
        
        self.db.add(db_city)
        await self.db.commit()
        await self.db.refresh(db_city)
        
        return CityResponse(
            id=db_city.id,
            name=db_city.name,
            latitude=db_city.latitude,
            longitude=db_city.longitude
        )
    
    async def get_city(self, city_id: int) -> Optional[CityResponse]:
        """Получение города по ID"""
        result = await self.db.execute(
            select(DBCity).where(DBCity.id == city_id)
        )
        db_city = result.scalar_one_or_none()
        
        if db_city:
            return CityResponse(
                id=db_city.id,
                name=db_city.name,
                latitude=db_city.latitude,
                longitude=db_city.longitude
            )
        return None
    
    async def get_all_cities(self) -> List[CityResponse]:
        """Получение всех городов"""
        result = await self.db.execute(select(DBCity))
        db_cities = result.scalars().all()
        
        return [
            CityResponse(
                id=city.id,
                name=city.name,
                latitude=city.latitude,
                longitude=city.longitude
            )
            for city in db_cities
        ]
    
    async def delete_city(self, city_id: int) -> bool:
        """Удаление города по ID"""
        result = await self.db.execute(
            select(DBCity).where(DBCity.id == city_id)
        )
        db_city = result.scalar_one_or_none()
        
        if db_city:
            await self.db.delete(db_city)
            await self.db.commit()
            return True
        return False
    
    async def find_nearest_cities(self, latitude: float, longitude: float, limit: int = 2) -> List[CityResponse]:
        """Поиск ближайших городов с использованием геоспецифических расчетов"""
        # Получаем все города из базы
        result = await self.db.execute(select(DBCity))
        all_cities = result.scalars().all()
        
        if not all_cities:
            return []
        
        # Вычисляем расстояния и сортируем
        target_coords = (latitude, longitude)
        cities_with_distance = []
        
        for city in all_cities:
            city_coords = (city.latitude, city.longitude)
            distance = geodesic(target_coords, city_coords).kilometers
            cities_with_distance.append((distance, city))
        
        # Сортируем по расстоянию и берем ближайшие
        cities_with_distance.sort(key=lambda x: x[0])
        nearest_cities = cities_with_distance[:limit]
        
        return [
            CityResponse(
                id=city.id,
                name=city.name,
                latitude=city.latitude,
                longitude=city.longitude
            )
            for distance, city in nearest_cities
        ]
    
    async def get_stats(self) -> dict:
        """Получение статистики хранилища"""
        result = await self.db.execute(select(func.count(DBCity.id)))
        total_cities = result.scalar()
        
        return {
            "total_cities": total_cities
        }

    async def city_exists(self, name: str) -> bool:
        """Проверка существования города с таким именем"""
        result = await self.db.execute(
            select(DBCity).where(func.lower(DBCity.name) == func.lower(name))
        )
        return result.scalar_one_or_none() is not None