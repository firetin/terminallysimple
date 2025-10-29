"""
Weather service using Open-Meteo API
No API key required - completely free and open-source
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

import httpx

logger = logging.getLogger(__name__)

# Open-Meteo API endpoints
GEOCODING_API = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_API = "https://api.open-meteo.com/v1/forecast"

# Weather cache settings
CACHE_DURATION_MINUTES = 30


class WeatherCache:
    """Simple in-memory cache for weather data."""
    
    def __init__(self):
        self.data: Optional[Dict] = None
        self.timestamp: Optional[datetime] = None
    
    def is_valid(self) -> bool:
        """Check if cached data is still valid."""
        if self.data is None or self.timestamp is None:
            return False
        age = datetime.now() - self.timestamp
        return age < timedelta(minutes=CACHE_DURATION_MINUTES)
    
    def set(self, data: Dict) -> None:
        """Store data in cache."""
        self.data = data
        self.timestamp = datetime.now()
    
    def get(self) -> Optional[Dict]:
        """Get cached data if valid."""
        return self.data if self.is_valid() else None


# Global weather cache
_weather_cache = WeatherCache()


def get_weather_icon(weather_code: int) -> str:
    """
    Convert WMO weather code to icon.
    
    WMO Weather interpretation codes (WW):
    0: Clear sky
    1, 2, 3: Mainly clear, partly cloudy, and overcast
    45, 48: Fog
    51, 53, 55: Drizzle
    61, 63, 65: Rain
    71, 73, 75: Snow
    77: Snow grains
    80, 81, 82: Rain showers
    85, 86: Snow showers
    95: Thunderstorm
    96, 99: Thunderstorm with hail
    """
    if weather_code == 0 or weather_code == 1:
        return "☀️"  # Clear/Mainly clear
    elif weather_code in (2, 3):
        return "☁️"  # Partly cloudy/Overcast
    elif weather_code in (45, 48):
        return "🌫️"  # Fog
    elif weather_code in range(51, 68):  # Drizzle and rain (51-67)
        return "💧"  # Rain
    elif weather_code in range(71, 78):  # Snow (71-77)
        return "❄️"  # Snow
    elif weather_code in (80, 81, 82):
        return "🌧️"  # Rain showers
    elif weather_code in (85, 86):
        return "🌨️"  # Snow showers
    elif weather_code >= 95:
        return "⛈️"  # Thunderstorm
    else:
        return "🌤️"  # Default/Unknown


def get_weather_description(weather_code: int) -> str:
    """Get human-readable weather description."""
    descriptions = {
        0: "Clear sky",
        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",
        45: "Foggy",
        48: "Foggy",
        51: "Light drizzle",
        53: "Drizzle",
        55: "Heavy drizzle",
        61: "Light rain",
        63: "Rain",
        65: "Heavy rain",
        71: "Light snow",
        73: "Snow",
        75: "Heavy snow",
        77: "Snow grains",
        80: "Light showers",
        81: "Showers",
        82: "Heavy showers",
        85: "Light snow showers",
        86: "Snow showers",
        95: "Thunderstorm",
        96: "Thunderstorm with hail",
        99: "Thunderstorm with hail",
    }
    return descriptions.get(weather_code, "Unknown")


async def geocode_city(city_name: str) -> Optional[Tuple[str, float, float]]:
    """
    Convert city name to coordinates using Open-Meteo Geocoding API.
    
    Args:
        city_name: Name of the city to geocode
        
    Returns:
        Tuple of (full_city_name, latitude, longitude) or None if not found
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                GEOCODING_API,
                params={"name": city_name, "count": 1, "language": "en", "format": "json"}
            )
            response.raise_for_status()
            data = response.json()
            
            if not data.get("results"):
                logger.warning(f"City not found: {city_name}")
                return None
            
            result = data["results"][0]
            full_name = result.get("name", city_name)
            country = result.get("country", "")
            if country:
                full_name = f"{full_name}, {country}"
            
            latitude = result["latitude"]
            longitude = result["longitude"]
            
            logger.info(f"Geocoded {city_name} -> {full_name} ({latitude}, {longitude})")
            return (full_name, latitude, longitude)
            
    except httpx.TimeoutException:
        logger.error(f"Timeout geocoding city: {city_name}")
        return None
    except httpx.HTTPError as e:
        logger.error(f"HTTP error geocoding city: {e}")
        return None
    except (KeyError, ValueError) as e:
        logger.error(f"Error parsing geocoding response: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error geocoding city: {e}")
        return None


async def fetch_weather(latitude: float, longitude: float, use_cache: bool = True) -> Optional[Dict]:
    """
    Fetch current weather and hourly forecast from Open-Meteo API.
    
    Args:
        latitude: Latitude coordinate
        longitude: Longitude coordinate
        use_cache: Whether to use cached data if available
        
    Returns:
        Dictionary with weather data or None if error
    """
    # Check cache first
    if use_cache:
        cached = _weather_cache.get()
        if cached:
            logger.debug("Using cached weather data")
            return cached
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                WEATHER_API,
                params={
                    "latitude": latitude,
                    "longitude": longitude,
                    "current": "temperature_2m,weather_code",
                    "hourly": "temperature_2m,weather_code",
                    "timezone": "auto",
                    "forecast_days": 2,  # Get 2 days of forecast data
                }
            )
            response.raise_for_status()
            data = response.json()
            
            # Cache the result
            _weather_cache.set(data)
            
            logger.debug(f"Fetched weather for ({latitude}, {longitude})")
            return data
            
    except httpx.TimeoutException:
        logger.error("Timeout fetching weather data")
        return None
    except httpx.HTTPError as e:
        logger.error(f"HTTP error fetching weather: {e}")
        return None
    except (KeyError, ValueError) as e:
        logger.error(f"Error parsing weather response: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error fetching weather: {e}")
        return None


def parse_current_weather(data: Dict) -> Optional[Tuple[float, int, str]]:
    """
    Parse current weather from API response.
    
    Args:
        data: Weather API response
        
    Returns:
        Tuple of (temperature, weather_code, icon) or None if error
    """
    try:
        current = data["current"]
        temperature = current["temperature_2m"]
        weather_code = current["weather_code"]
        icon = get_weather_icon(weather_code)
        
        return (temperature, weather_code, icon)
    except (KeyError, TypeError) as e:
        logger.error(f"Error parsing current weather: {e}")
        return None


def parse_hourly_forecast(data: Dict, hours: int = 12) -> List[Dict]:
    """
    Parse hourly forecast from API response.
    
    Args:
        data: Weather API response
        hours: Number of hours to include in forecast
        
    Returns:
        List of forecast dictionaries with time, temperature, weather_code, icon
    """
    try:
        hourly = data["hourly"]
        times = hourly["time"]
        temperatures = hourly["temperature_2m"]
        weather_codes = hourly["weather_code"]
        
        forecast = []
        current_time = datetime.now()
        
        for i, time_str in enumerate(times):
            try:
                # Parse the time string (ISO format: "2025-10-29T14:00")
                forecast_time = datetime.fromisoformat(time_str)
                
                # Only include future hours
                if forecast_time > current_time:
                    forecast.append({
                        "time": forecast_time.strftime("%H:%M"),
                        "temperature": temperatures[i],
                        "weather_code": weather_codes[i],
                        "icon": get_weather_icon(weather_codes[i]),
                        "description": get_weather_description(weather_codes[i])
                    })
                    
                    # Stop when we have enough hours
                    if len(forecast) >= hours:
                        break
            except (ValueError, IndexError) as e:
                logger.debug(f"Skipping time entry {i}: {e}")
                continue
        
        return forecast
    except (KeyError, TypeError) as e:
        logger.error(f"Error parsing hourly forecast: {e}")
        return []
