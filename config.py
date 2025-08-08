"""
Configuration manager - handles app settings
Centralized configuration management for the application
"""
import os
from dataclasses import dataclass, asdict
import json


@dataclass
class DatabaseConfig:
    """Database/Cache configuration"""
    cache_file: str = "geocoding_cache.pkl"
    enable_caching: bool = True
    cache_expiry_days: int = 30


@dataclass
class APIConfig:
    """API configuration settings"""
    user_agent: str = "large_scale_geocoder_mvvm"
    delay_between_requests: float = 1.5
    max_retries: int = 3
    timeout_seconds: int = 30


@dataclass
class ProcessingConfig:
    """Processing configuration"""
    batch_size: int = 1000
    max_workers: int = 5
    save_progress_every: int = 100
    auto_resume: bool = True


@dataclass
class FileConfig:
    """File paths configuration"""
    input_file: str = "geocoded_addresses.csv"
    output_file: str = "geocoded_addresses_updated.csv"
    json_output: str = "address_coordinates_map.json"
    python_output: str = "address_coordinates_map.py"
    log_file: str = "geocoding.log"


@dataclass
class AppConfig:
    """Main application configuration settings"""
    api: APIConfig
    database: DatabaseConfig
    processing: ProcessingConfig
    files: FileConfig
    
    @classmethod
    def create_default(cls) -> 'AppConfig':
        """Create default configuration"""
        return cls(
            api=APIConfig(),
            database=DatabaseConfig(),
            processing=ProcessingConfig(),
            files=FileConfig()
        )
    
    @classmethod
    def load_from_file(cls, file_path: str = "config.json") -> 'AppConfig':
        """Load configuration from JSON file"""
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                return cls.from_dict(data)
            except Exception as e:
                print(f"Warning: Could not load config from {file_path}: {e}")
        
        # Return default config if file doesn't exist or can't be loaded
        return cls.create_default()
    
    @classmethod
    def from_dict(cls, data: dict) -> 'AppConfig':
        """Create config from dictionary"""
        return cls(
            api=APIConfig(**data.get('api', {})),
            database=DatabaseConfig(**data.get('database', {})),
            processing=ProcessingConfig(**data.get('processing', {})),
            files=FileConfig(**data.get('files', {}))
        )
    
    def save_to_file(self, file_path: str = "config.json") -> None:
        """Save configuration to JSON file"""
        try:
            with open(file_path, 'w') as f:
                json.dump(asdict(self), f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save config to {file_path}: {e}")
    
    def to_geocoding_config(self):
        """Convert to the legacy GeocodingConfig for backward compatibility"""
        from models import GeocodingConfig
        return GeocodingConfig(
            batch_size=self.processing.batch_size,
            cache_file=self.database.cache_file,
            max_workers=self.processing.max_workers,
            delay_between_requests=self.api.delay_between_requests,
            user_agent=self.api.user_agent,
            input_file=self.files.input_file,
            output_file=self.files.output_file,
            json_output=self.files.json_output,
            python_output=self.files.python_output
        )
