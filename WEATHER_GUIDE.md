# Weather Widget User Guide

## Quick Start

### Setting Up Your City

1. **Launch the app**: Run `python app.py`
2. **Look at the top-right**: You'll see "Weather" in the header bar
3. **Click on "Weather"**: A dialog will appear
4. **Enter your city**: Type your city name (e.g., "Paris", "New York", "Tokyo")
5. **Press Enter**: The weather will load automatically

### What You'll See

After setup, the header shows:
- **Weather icon**: ☀️ (sunny), ☁️ (cloudy), 💧 (rainy), etc.
- **Current temperature**: In Celsius (°C)

Example: `☀️ 15°C` or `💧 10°C`

### Viewing Detailed Forecast

1. **Click the weather display** (the temperature/icon)
2. A **forecast dialog** opens showing:
   - Next 12 hours of weather
   - Time, icon, temperature, and description for each hour
   - Easy to see when rain is coming!

Example forecast:
```
14:00  ☀️ 16°C  Clear sky
15:00  ☁️ 15°C  Partly cloudy
16:00  💧 14°C  Light rain
17:00  💧 13°C  Rain
```

3. **Press Enter or Escape** to close the forecast

### Weather Icons Explained

- ☀️ **Clear/Sunny** - Clear skies
- ☁️ **Cloudy** - Overcast or partly cloudy
- 💧 **Rain** - Light rain or drizzle
- 🌧️ **Showers** - Rain showers
- ❄️ **Snow** - Snow or snow grains
- 🌨️ **Snow Showers** - Snow showers
- ⛈️ **Thunderstorm** - Storms with lightning
- 🌫️ **Fog** - Foggy conditions

### Auto-Updates

- Weather refreshes **automatically every 30 minutes**
- No need to manually refresh
- Always shows current conditions

### Changing Your City

To change to a different city:
1. Close the app
2. Delete `~/.config/terminallysimple/config.json` (or edit it)
3. Restart the app
4. Click "Weather" and enter new city

### Troubleshooting

**"Weather N/A" or dimmed?**
- Check your internet connection
- The API might be temporarily unavailable
- Try clicking to reconfigure

**City not found?**
- Try a larger nearby city
- Include country name: "Springfield, USA"
- Use official city names

**No forecast showing?**
- Weather data might be temporarily unavailable
- Try again in a few minutes
- Check app logs at `~/.config/terminallysimple/app.log`

### Technical Details

- **Free service**: Uses Open-Meteo API (no API key needed)
- **Global**: Works for any city worldwide
- **Accurate**: Data from meteorological services
- **Privacy**: No tracking, no accounts, no data collection
- **Offline**: Shows last cached data if internet unavailable

## Examples of Cities That Work

- London
- New York
- Tokyo
- Paris
- Berlin
- Sydney
- Mumbai
- São Paulo
- Moscow
- Cairo
- Buenos Aires
- Vancouver
- ...and thousands more!

Enjoy your weather widget! 🌤️
