# 🌍 Address Geocoding System

A Python application that converts physical addresses into GPS coordinates (latitude, longitude) with support for processing large datasets efficiently.

## 📋 Table of Contents
- [Overview](#overview)
- [Project Structure](#project-structure)
- [Libraries and Dependencies](#libraries-and-dependencies)
- [Core Functions](#core-functions)
- [Code Architecture](#code-architecture)
- [Usage](#usage)
- [Configuration](#configuration)
- [Output Formats](#output-formats)

## 🎯 Overview

This project takes a CSV file containing addresses and converts them into precise GPS coordinates using the OpenStreetMap geocoding service. It's designed to handle everything from a few addresses to millions of addresses efficiently using batch processing and caching.

### Key Features:
- **Batch Processing**: Handles large datasets in configurable chunks
- **Smart Caching**: Avoids re-processing duplicate addresses
- **Progress Tracking**: Real-time progress monitoring with progress bars
- **Resume Capability**: Can stop and restart from where it left off
- **Multiple Output Formats**: CSV, JSON, and Python dictionary
- **Error Handling**: Comprehensive error management and logging

## 📁 Project Structure

```
📁 address-geocoding-system/
├── 📄 main.py              # Main application entry point
├── 📄 models.py            # Data models and structures
├── 📄 services.py          # Service layer (File, Cache, Geocoding)
├── 📄 viewmodel.py         # Business logic layer
├── 📄 config.py            # Configuration management
├── 📄 utils.py             # Utility functions and helpers
├── 📄 main_legacy.py       # Original single-file version
└── 📄 README.md            # Documentation
```

## 📚 Libraries and Dependencies

### Core Libraries:
- **pandas**: Data manipulation and CSV handling
- **geopy**: Geocoding services and API integration
- **tqdm**: Progress bars and monitoring
- **pickle**: Data serialization for caching
- **json**: JSON file operations
- **dataclasses**: Python data structures
- **typing**: Type hints and annotations
- **datetime**: Timestamp and logging
- **time**: Timing and delays
- **os**: File system operations

### Installation:
```bash
pip install pandas geopy tqdm
```

## 🔧 Core Functions

### Main Application (`main.py`)
```python
def main():
    """Main function entry point with MVVM architecture"""
```
- Initializes the application
- Loads configuration
- Manages the geocoding workflow
- Handles errors and logging

### Data Models (`models.py`)

#### Address Class
```python
@dataclass
class Address:
    original: str           # Original address text
    cleaned: str           # Cleaned address text
    latitude: Optional[float]  # GPS latitude
    longitude: Optional[float] # GPS longitude
```

**Key Methods:**
- `is_geocoded`: Checks if address has coordinates
- `coordinates`: Returns "lat,lng" string format
- `to_dict()`: Converts to dictionary

#### ProcessingStats Class
```python
@dataclass
class ProcessingStats:
    total_addresses: int
    processed_addresses: int
    successful_geocodes: int
    failed_geocodes: int
```

**Key Methods:**
- `progress_percentage`: Calculates completion percentage
- `success_rate`: Calculates geocoding success rate

#### GeocodingConfig Class
```python
@dataclass
class GeocodingConfig:
    batch_size: int = 1000
    cache_file: str = "geocoding_cache.pkl"
    delay_between_requests: float = 1.5
```

### Services Layer (`services.py`)

#### FileService Class
```python
class FileService:
    def load_csv(file_path: str) -> pd.DataFrame
    def save_csv(data: pd.DataFrame, file_path: str)
    def save_json(data: dict, file_path: str)
    def save_python_dict(data: dict, file_path: str)
```

#### CacheService Class
```python
class CacheService:
    def load_cache() -> dict
    def save_cache(cache: dict)
    def get(key: str) -> any
    def set(key: str, value: any)
```

#### GeocodingService Class
```python
class GeocodingService:
    def clean_address(address: str) -> str
    def geocode_address(address: str) -> tuple
    def process_batch(addresses: List[Address]) -> List[Address]
```

### Business Logic (`viewmodel.py`)

#### GeocodingViewModel Class
```python
class GeocodingViewModel:
    def load_addresses() -> bool
    def process_all_addresses() -> bool
    def print_final_summary()
    def export_results()
```

### Configuration (`config.py`)

#### AppConfig Class
```python
@dataclass
class AppConfig:
    api: APIConfig
    database: DatabaseConfig
    processing: ProcessingConfig
    files: FileConfig
```

**Key Methods:**
- `create_default()`: Creates default configuration
- `load_from_file()`: Loads config from JSON
- `save_to_file()`: Saves config to JSON

### Utilities (`utils.py`)

#### Logger Class
```python
class Logger:
    @staticmethod
    def info(message: str)
    @staticmethod
    def error(message: str)
    @staticmethod
    def warning(message: str)
```

#### Timer Class
```python
class Timer:
    def start()
    def stop() -> float
    def elapsed() -> float
```

#### Console Class
```python
class Console:
    @staticmethod
    def print_header(title: str, width: int)
    @staticmethod
    def print_section(title: str)
```

#### Formatter Class
```python
class Formatter:
    @staticmethod
    def format_duration(seconds: float) -> str
    @staticmethod
    def format_number(number: int) -> str
```

## 🏗️ Code Architecture

### MVVM Pattern Implementation:

1. **Model Layer** (`models.py`):
   - Pure data structures
   - Business entities (Address, Stats, Config)
   - No business logic, only data representation

2. **View Layer** (`main.py`):
   - User interface (console output)
   - User input handling
   - Display formatting

3. **ViewModel Layer** (`viewmodel.py`):
   - Business logic and workflows
   - Coordinates between Model and View
   - State management

4. **Service Layer** (`services.py`):
   - External API calls (geocoding)
   - File operations
   - Caching mechanisms

## 🚀 Usage

### Basic Usage:
```bash
python main.py
```

### Input File Format:
Create a CSV file named `geocoded_addresses.csv`:
```csv
Shipping Address
"123 Main St, New York, NY"
"456 Park Ave, Los Angeles, CA"
```

### Process Flow:
1. **Load Configuration**: Reads settings from `config.json` or uses defaults
2. **Initialize Services**: Sets up file operations, caching, and geocoding
3. **Load Addresses**: Reads addresses from CSV file
4. **Clean Addresses**: Removes unwanted prefixes and normalizes text
5. **Batch Processing**: Processes addresses in configurable batches
6. **Geocode**: Converts addresses to coordinates using OpenStreetMap API
7. **Cache Results**: Stores results to avoid re-processing
8. **Export**: Saves results in multiple formats

## ⚙️ Configuration

### Default Configuration:
```python
APIConfig:
    user_agent: "large_scale_geocoder_mvvm"
    delay_between_requests: 1.5
    max_retries: 3

ProcessingConfig:
    batch_size: 1000
    max_workers: 5
    save_progress_every: 100

FileConfig:
    input_file: "geocoded_addresses.csv"
    output_file: "geocoded_addresses_updated.csv"
    json_output: "address_coordinates_map.json"
```

### Custom Configuration:
```python
config = AppConfig.create_default()
config.processing.batch_size = 2000
config.api.delay_between_requests = 1.0
config.save_to_file("custom_config.json")
```

## 📤 Output Formats

### 1. CSV Format (`geocoded_addresses_updated.csv`)
```csv
Shipping Address,Cleaned_Address,Latitude,Longitude
"New York, NY",New York,40.7128,-74.0060
```

### 2. JSON Format (`address_coordinates_map.json`)
```json
{
  "New York, NY": "40.7128,-74.0060",
  "Los Angeles, CA": "34.0522,-118.2437"
}
```

### 3. Python Dictionary (`address_coordinates_map.py`)
```python
address_coordinates = {
  "New York, NY": "40.7128,-74.0060",
  "Los Angeles, CA": "34.0522,-118.2437"
}
```

## 🛠️ Error Handling

The application includes comprehensive error handling:

- **File Errors**: Missing input files, permission issues
- **API Errors**: Rate limiting, network timeouts
- **Data Errors**: Invalid addresses, encoding issues
- **System Errors**: Memory issues, interruptions

All errors are logged with timestamps and detailed messages for debugging.

## 📊 Performance Features

- **Batch Processing**: Configurable batch sizes for memory efficiency
- **Smart Caching**: Avoids duplicate API calls
- **Progress Tracking**: Real-time progress with estimated completion times
- **Resume Capability**: Automatic progress saving and resumption
- **Rate Limiting**: Respects API limits to avoid blocking
