"""
Quick test script for weather API functionality
"""

import asyncio
import sys
from utils.weather import geocode_city, fetch_weather, parse_current_weather, parse_hourly_forecast


async def test_weather():
    """Test the weather API functions."""
    print("Testing Open-Meteo Weather API...")
    print("-" * 50)
    
    # Test geocoding
    print("\n1. Testing geocoding...")
    city_name = "London"
    result = await geocode_city(city_name)
    if result:
        full_name, lat, lon = result
        print(f"✓ Found: {full_name}")
        print(f"  Coordinates: {lat}, {lon}")
    else:
        print(f"✗ Failed to geocode {city_name}")
        return
    
    # Test weather fetch
    print("\n2. Testing weather fetch...")
    weather_data = await fetch_weather(lat, lon, use_cache=False)
    if weather_data:
        print(f"✓ Weather data received")
    else:
        print("✗ Failed to fetch weather")
        return
    
    # Test current weather parsing
    print("\n3. Testing current weather parsing...")
    current = parse_current_weather(weather_data)
    if current:
        temp, code, icon = current
        print(f"✓ Current weather: {icon} {temp}°C (code: {code})")
    else:
        print("✗ Failed to parse current weather")
        return
    
    # Test forecast parsing
    print("\n4. Testing hourly forecast...")
    forecast = parse_hourly_forecast(weather_data, hours=6)
    if forecast:
        print(f"✓ Forecast for next {len(forecast)} hours:")
        for hour in forecast[:3]:  # Show first 3
            print(f"  {hour['time']} - {hour['icon']} {hour['temperature']:.0f}°C - {hour['description']}")
        if len(forecast) > 3:
            print(f"  ... and {len(forecast) - 3} more hours")
    else:
        print("✗ Failed to parse forecast")
        return
    
    print("\n" + "-" * 50)
    print("✓ All tests passed!")
    print("\nThe weather widget is ready to use in the app.")
    print("Click on 'Weather' in the header to set up your city.")


if __name__ == "__main__":
    asyncio.run(test_weather())
