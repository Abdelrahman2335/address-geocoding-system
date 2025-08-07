"""
Models for the geocoding system
Contains data classes similar to Flutter models
"""
from dataclasses import dataclass
from typing import Optional, List, Dict, Any


@dataclass
class Address:
    """Address model - like a Dart class with fields"""
    original: str
    cleaned: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    
    @property
    def is_geocoded(self) -> bool:
        """Check if address has coordinates"""
        return self.latitude is not None and self.longitude is not None
    
    @property
    def coordinates(self) -> Optional[str]:
        """Get coordinates as string (lat,lng)"""
        if self.is_geocoded:
            return f"{self.latitude},{self.longitude}"
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary - like toJson() in Flutter"""
        return {
            'original': self.original,
            'cleaned': self.cleaned,
            'latitude': self.latitude,
            'longitude': self.longitude
        }


@dataclass
class ProcessingStats:
    """Statistics model for tracking progress"""
    total_addresses: int = 0
    processed_addresses: int = 0
    successful_geocodes: int = 0
    failed_geocodes: int = 0
    current_batch: int = 0
    total_batches: int = 0
    
    @property
    def progress_percentage(self) -> float:
        """Get progress as percentage"""
        if self.total_addresses == 0:
            return 0.0
        return (self.processed_addresses / self.total_addresses) * 100
    
    @property
    def success_rate(self) -> float:
        """Get success rate as percentage"""
        if self.processed_addresses == 0:
            return 0.0
        return (self.successful_geocodes / self.processed_addresses) * 100


@dataclass
class GeocodingConfig:
    """Configuration model - like app config in Flutter"""
    batch_size: int = 1000
    cache_file: str = "geocoding_cache.pkl"
    max_workers: int = 5
    delay_between_requests: float = 1.5
    user_agent: str = "large_scale_geocoder_v2"
    input_file: str = "geocoded_addresses.csv"
    output_file: str = "geocoded_addresses_updated.csv"
    json_output: str = "address_coordinates_map.json"
    python_output: str = "address_coordinates_map.py"
