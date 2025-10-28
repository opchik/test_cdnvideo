from pydantic import BaseModel, Field
from typing import List


class CityCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Название города")

class CityResponse(BaseModel):
    id: int
    name: str
    latitude: float
    longitude: float

    class Config:
        from_attributes = True

class Coordinates(BaseModel):
    latitude: float = Field(..., ge=-90, le=90, description="Широта от -90 до 90")
    longitude: float = Field(..., ge=-180, le=180, description="Долгота от -180 до 180")

class NearestCitiesResponse(BaseModel):
    coordinates: Coordinates
    nearest_cities: List[CityResponse]

class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    database: str

class StatsResponse(BaseModel):
    total_cities: int