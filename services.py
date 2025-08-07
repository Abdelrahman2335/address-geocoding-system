"""
Services layer - handles external API calls and data operations
Similar to repository pattern in Flutter
"""
import pandas as pd
import json
import pickle
import os
from typing import List, Optional, Dict, Any, Tuple
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from models import Address, GeocodingConfig


class FileService:
    """Handles file operations - like file_service.dart in Flutter"""
    
    @staticmethod
    def load_csv(file_path: str) -> pd.DataFrame:
        """Load CSV file with encoding fallback"""
        try:
            return pd.read_csv(file_path, encoding='utf-8')
        except UnicodeDecodeError:
            return pd.read_csv(file_path, encoding='latin1')
    
    @staticmethod
    def save_csv(df: pd.DataFrame, file_path: str) -> None:
        """Save DataFrame to CSV"""
        df.to_csv(file_path, index=False, encoding='utf-8-sig')
    
    @staticmethod
    def save_json(data: Dict[str, Any], file_path: str) -> None:
        """Save data as JSON"""
        with open(file_path, "w", encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    @staticmethod
    def save_python_dict(data: Dict[str, Any], file_path: str, description: str = "") -> None:
        """Save data as Python dictionary file"""
        with open(file_path, "w", encoding='utf-8') as f:
            f.write("# Address to Coordinates Mapping\n")
            if description:
                f.write(f"# {description}\n")
            f.write("address_coordinates = ")
            f.write(json.dumps(data, indent=2, ensure_ascii=False))


class CacheService:
    """Handles caching operations - like cache_service.dart in Flutter"""
    
    def __init__(self, cache_file: str):
        self.cache_file = cache_file
        self._cache: Dict[str, Tuple[Optional[float], Optional[float]]] = {}
    
    def load_cache(self) -> Dict[str, Tuple[Optional[float], Optional[float]]]:
        """Load cache from file"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'rb') as f:
                    self._cache = pickle.load(f)
            except Exception as e:
                print(f"Warning: Could not load cache: {e}")
                self._cache = {}
        else:
            self._cache = {}
        return self._cache
    
    def save_cache(self) -> None:
        """Save cache to file"""
        try:
            with open(self.cache_file, 'wb') as f:
                pickle.dump(self._cache, f)
        except Exception as e:
            print(f"Warning: Could not save cache: {e}")
    
    def get(self, key: str) -> Optional[Tuple[Optional[float], Optional[float]]]:
        """Get cached result"""
        return self._cache.get(key)
    
    def set(self, key: str, value: Tuple[Optional[float], Optional[float]]) -> None:
        """Set cached result"""
        self._cache[key] = value
    
    def size(self) -> int:
        """Get cache size"""
        return len(self._cache)


class GeocodingService:
    """Handles geocoding API calls - like geocoding_service.dart in Flutter"""
    
    def __init__(self, config: GeocodingConfig, cache_service: CacheService):
        self.config = config
        self.cache_service = cache_service
        self.geolocator = Nominatim(user_agent=config.user_agent)
        self.geocode = RateLimiter(
            self.geolocator.geocode, 
            min_delay_seconds=config.delay_between_requests
        )
    
    def clean_address(self, address: str) -> str:
        """Clean address text - remove unwanted prefixes"""
        if not isinstance(address, str):
            return ""
        
        # Remove common prefixes and simplify address
        cleaned = address.replace("Jumia- Pargo- Pickup station -", "")
        cleaned = cleaned.replace("Point 192 -", "")
        cleaned = cleaned.split(",")[0].strip()
        return cleaned
    
    def geocode_address(self, address: str) -> Tuple[Optional[float], Optional[float]]:
        """
        Geocode a single address with caching
        Returns (latitude, longitude) or (None, None) if failed
        """
        # Check cache first
        cached_result = self.cache_service.get(address)
        if cached_result is not None:
            return cached_result
        
        try:
            location = self.geocode(address)
            if location:
                result = (location.latitude, location.longitude)
                self.cache_service.set(address, result)
                return result
        except Exception as e:
            print(f"Error geocoding {address}: {e}")
        
        # Cache failed attempts to avoid retrying
        failed_result = (None, None)
        self.cache_service.set(address, failed_result)
        return failed_result
