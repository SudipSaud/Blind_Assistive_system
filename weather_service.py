"""
Weather Service Module - OpenWeatherMap API Integration
"""

import os
import requests
import logging

logger = logging.getLogger(__name__)


class WeatherService:
    """Independent weather service using OpenWeatherMap API"""
    
    def __init__(self):
        self.api_key = os.getenv("OPENWEATHER_API_KEY", "demo_key")
        self.is_initialized = False
        logger.info(f"WeatherService __init__: API key loaded = {bool(self.api_key and self.api_key != 'demo_key')}")
        if self.api_key and self.api_key != "demo_key":
            logger.info(f"API key length: {len(self.api_key)} characters")
        
    def initialize(self) -> bool:
        """Initialize weather service"""
        try:
            logger.info("Initializing Weather Service...")
            if self.api_key == "demo_key" or not self.api_key:
                logger.warning("No OpenWeatherMap API key found. Using demo weather data.")
                logger.warning("Please ensure .env file exists with OPENWEATHER_API_KEY set.")
            else:
                logger.info(f"OpenWeatherMap API key found ({len(self.api_key)} chars). Real weather data will be used.")
            self.is_initialized = True
            return True
        except Exception as e:
            logger.error(f"Error initializing weather service: {e}")
            return False
    
    def set_api_key(self, api_key: str):
        """Set OpenWeatherMap API key"""
        self.api_key = api_key
        logger.info("OpenWeatherMap API key updated")
    
    def get_weather(self, city: str) -> str:
        """Get real weather information for a city"""
        try:
            if self.api_key == "demo_key" or not self.api_key:
                # Simulate weather data for demo
                logger.warning("Using demo weather data - no API key configured")
                return f"The weather in {city} is sunny with 22°C and 65% humidity. This is demo data. To get real weather, please provide your OpenWeatherMap API key."
            
            # Clean city name - remove punctuation and extra spaces
            city_clean = city.strip().rstrip('.,!?').strip()
            logger.info(f"Cleaned city name: '{city}' -> '{city_clean}'")
            
            # Real API call to OpenWeatherMap
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city_clean}&appid={self.api_key}&units=metric"
            logger.info(f"Making weather API call to OpenWeatherMap for city: {city_clean}")
            logger.debug(f"API URL: {url.replace(self.api_key, 'API_KEY_HIDDEN')}")
            
            response = requests.get(url, timeout=10)
            logger.info(f"Weather API response status code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                temp = data['main']['temp']
                condition = data['weather'][0]['description']
                humidity = data['main']['humidity']
                wind_speed = data['wind']['speed']
                feels_like = data['main']['feels_like']
                
                logger.info(f"Weather data retrieved successfully for {city_clean}: {condition}, {temp}°C")
                return f"The weather in {city_clean} is {condition} with temperature {temp}°C, feels like {feels_like}°C, humidity {humidity}%, and wind speed {wind_speed} meters per second."
            elif response.status_code == 401:
                logger.error(f"Weather API authentication failed - invalid API key")
                return f"Weather service error: Invalid API key. Please check your OpenWeatherMap API key configuration."
            elif response.status_code == 404:
                logger.error(f"City not found: {city_clean}")
                return f"City '{city_clean}' not found. Please check the city name and try again."
            else:
                logger.error(f"Weather API error: Status {response.status_code}, Response: {response.text}")
                return f"Weather data not available for {city_clean}. API returned status code {response.status_code}."
                
        except Exception as e:
            logger.error(f"Error getting weather: {e}", exc_info=True)
            return f"Weather service error: {str(e)}"
    
    def release(self):
        """Release resources"""
        self.is_initialized = False
        logger.info("Weather Service resources released")

