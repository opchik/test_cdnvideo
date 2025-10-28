import aiohttp
import asyncio
from typing import Optional, Tuple
import logging

from .config import settings

logger = logging.getLogger(__name__)

class GeocodingService:
    def __init__(self):
        self.base_url = settings.GEOCODING_BASE_URL
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def get_session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                headers={'User-Agent': settings.GEOCODING_USER_AGENT}
            )
        return self.session
    
    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def get_coordinates(self, city_name: str) -> Optional[Tuple[float, float]]:
        """Получение координат города по названию"""
        try:
            session = await self.get_session()
            params = {
                'q': city_name,
                'format': 'json',
                'limit': 1,
                'accept-language': 'ru'
            }
            
            async with session.get(self.base_url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    data = await response.json()
                    if data and len(data) > 0:
                        lat = float(data[0]['lat'])
                        lon = float(data[0]['lon'])
                        logger.info(f"Found coordinates for {city_name}: {lat}, {lon}")
                        return lat, lon
                else:
                    logger.error(f"Geocoding API error: {response.status}")
                
                return None
                
        except asyncio.TimeoutError:
            logger.error(f"Timeout getting coordinates for {city_name}")
            return None
        except Exception as e:
            logger.error(f"Error getting coordinates for {city_name}: {e}")
            return None


geocoding_service = GeocodingService()