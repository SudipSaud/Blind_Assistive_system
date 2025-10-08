"""
Navigation Service Module - Real Location-Based Navigation with OpenStreetMap
"""

import requests
import logging
from typing import Dict, Optional, List

logger = logging.getLogger(__name__)


class NavigationService:
    """Real location-based navigation service using OpenStreetMap APIs"""
    
    def __init__(self):
        self.is_initialized = False
        self.current_location = None
        self.nominatim_base_url = "https://nominatim.openstreetmap.org"
        self.osrm_base_url = "https://router.project-osrm.org"
        self.user_agent = "BlindAssistiveSystem/1.0"
        
    def initialize(self) -> bool:
        """Initialize navigation service"""
        try:
            logger.info("Initializing Navigation Service...")
            # Try to get current location
            self.get_current_location()
            self.is_initialized = True
            return True
        except Exception as e:
            logger.error(f"Error initializing navigation service: {e}")
            return False
    
    def get_current_location(self):
        """Get current location using IP-based geolocation"""
        try:
            # Try to get location from IP-based geolocation
            response = requests.get('http://ip-api.com/json', timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.current_location = {
                    'city': data.get('city', 'Unknown'),
                    'country': data.get('country', 'Unknown'),
                    'lat': data.get('lat', 0),
                    'lon': data.get('lon', 0),
                    'display_name': f"{data.get('city', 'Unknown')}, {data.get('country', 'Unknown')}"
                }
                logger.info(f"Current location detected: {self.current_location['city']}, {self.current_location['country']}")
            else:
                # Fallback to default location
                self.current_location = {
                    'city': 'Kathmandu',
                    'country': 'Nepal',
                    'lat': 27.7172,
                    'lon': 85.3240,
                    'display_name': 'Kathmandu, Nepal'
                }
                logger.info("Using default location: Kathmandu, Nepal")
                
        except Exception as e:
            logger.error(f"Error getting location: {e}")
            # Fallback to default location
            self.current_location = {
                'city': 'Kathmandu',
                'country': 'Nepal',
                'lat': 27.7172,
                'lon': 85.3240,
                'display_name': 'Kathmandu, Nepal'
            }
    
    def geocode_location(self, place_name: str) -> Optional[Dict]:
        """Convert place name to coordinates using Nominatim"""
        try:
            # Search for the place
            params = {
                'q': place_name,
                'format': 'json',
                'limit': 1
            }
            headers = {
                'User-Agent': self.user_agent
            }
            
            logger.info(f"Geocoding location: {place_name}")
            response = requests.get(
                f"{self.nominatim_base_url}/search",
                params=params,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                results = response.json()
                if results and len(results) > 0:
                    result = results[0]
                    location = {
                        'lat': float(result['lat']),
                        'lon': float(result['lon']),
                        'display_name': result['display_name']
                    }
                    logger.info(f"Geocoded '{place_name}' to: {location['display_name']}")
                    return location
                else:
                    logger.warning(f"No results found for: {place_name}")
                    return None
            else:
                logger.error(f"Geocoding API error: Status {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error geocoding location: {e}")
            return None
    
    def get_route_instructions(self, origin_lat: float, origin_lon: float, 
                              dest_lat: float, dest_lon: float) -> Optional[Dict]:
        """Get turn-by-turn directions using OSRM"""
        try:
            # Build OSRM route request
            url = f"{self.osrm_base_url}/route/v1/foot/{origin_lon},{origin_lat};{dest_lon},{dest_lat}"
            params = {
                'overview': 'full',
                'steps': 'true',
                'geometries': 'geojson'
            }
            
            logger.info(f"Getting route from ({origin_lat}, {origin_lon}) to ({dest_lat}, {dest_lon})")
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('code') == 'Ok' and data.get('routes'):
                    route = data['routes'][0]
                    logger.info(f"Route found: {route['distance']}m, {route['duration']}s")
                    return route
                else:
                    logger.error(f"OSRM API error: {data.get('code', 'Unknown error')}")
                    return None
            else:
                logger.error(f"OSRM API error: Status {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting route: {e}")
            return None
    
    def format_step_instruction(self, step: Dict) -> str:
        """Format a single navigation step into human-readable instruction"""
        try:
            maneuver = step.get('maneuver', {})
            instruction = maneuver.get('instruction', 'Continue')
            distance = step.get('distance', 0)
            
            # Convert distance to human-readable format
            if distance < 50:
                distance_str = f"{int(distance)} meters"
            elif distance < 1000:
                distance_str = f"{int(distance)} meters"
            else:
                distance_str = f"{distance/1000:.1f} kilometers"
            
            return f"{instruction} for {distance_str}"
            
        except Exception as e:
            logger.error(f"Error formatting step: {e}")
            return "Continue on your route"
    
    def get_directions(self, destination: str, origin: str = None) -> str:
        """Get navigation directions based on current location"""
        try:
            if not self.current_location:
                self.get_current_location()
            
            # Use current location as origin if not specified
            if not origin:
                origin_lat = self.current_location['lat']
                origin_lon = self.current_location['lon']
                origin_name = self.current_location['display_name']
            else:
                # Geocode origin
                origin_location = self.geocode_location(origin)
                if not origin_location:
                    return f"Could not find origin location: {origin}"
                origin_lat = origin_location['lat']
                origin_lon = origin_location['lon']
                origin_name = origin_location['display_name']
            
            # Geocode destination
            logger.info(f"Finding directions to: {destination}")
            dest_location = self.geocode_location(destination)
            
            if not dest_location:
                # Fallback to location-aware generic directions
                return self._get_generic_directions(destination)
            
            dest_lat = dest_location['lat']
            dest_lon = dest_location['lon']
            dest_name = dest_location['display_name']
            
            # Get route from OSRM
            route = self.get_route_instructions(origin_lat, origin_lon, dest_lat, dest_lon)
            
            if not route:
                # Fallback to simple distance-based direction
                return f"Navigate from {origin_name} to {dest_name}. Unable to get detailed directions at this time."
            
            # Extract route information
            distance = route['distance']
            duration = route['duration']
            legs = route.get('legs', [])
            
            # Format distance and duration
            if distance < 1000:
                distance_str = f"{int(distance)} meters"
            else:
                distance_str = f"{distance/1000:.1f} kilometers"
            
            duration_min = int(duration / 60)
            if duration_min < 1:
                duration_str = f"{int(duration)} seconds"
            else:
                duration_str = f"{duration_min} minutes"
            
            # Build instructions
            instructions = []
            instructions.append(f"Navigating from {origin_name} to {dest_name}.")
            instructions.append(f"Total distance: {distance_str}, estimated time: {duration_str}.")
            
            # Add turn-by-turn instructions (first 3 steps)
            if legs and len(legs) > 0:
                steps = legs[0].get('steps', [])
                if steps:
                    instructions.append("Here are your first few directions:")
                    for i, step in enumerate(steps[:3], 1):
                        step_instruction = self.format_step_instruction(step)
                        instructions.append(f"Step {i}: {step_instruction}.")
            
            return " ".join(instructions)
                
        except Exception as e:
            logger.error(f"Error getting directions: {e}", exc_info=True)
            return self._get_generic_directions(destination)
    
    def _get_generic_directions(self, destination: str) -> str:
        """Fallback generic directions when API fails"""
        current_city = self.current_location['city'] if self.current_location else 'your current location'
        
        destination_lower = destination.lower()
        
        # Provide generic location-aware directions based on keywords
        if "store" in destination_lower or "shop" in destination_lower or "market" in destination_lower:
            return f"From {current_city}, navigate to the nearest store. This is a generic direction. For precise navigation, please check your internet connection."
        elif "hospital" in destination_lower or "clinic" in destination_lower:
            return f"From {current_city}, navigate to the nearest hospital. This is a generic direction. For precise navigation, please check your internet connection."
        elif "bank" in destination_lower or "atm" in destination_lower:
            return f"From {current_city}, navigate to the nearest bank or ATM. This is a generic direction. For precise navigation, please check your internet connection."
        elif "restaurant" in destination_lower or "food" in destination_lower:
            return f"From {current_city}, navigate to the nearest restaurant. This is a generic direction. For precise navigation, please check your internet connection."
        else:
            return f"Navigate from {current_city} to {destination}. Unable to get precise directions. Please check your internet connection or try a more specific location name."
    
    def release(self):
        """Release resources"""
        self.is_initialized = False
        logger.info("Navigation Service resources released")

