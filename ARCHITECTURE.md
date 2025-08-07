# 🏗️ MVVM Architecture Guide

## Project Structure (Flutter-Style)

```
📁 Python Projects/
├── 📄 main_mvvm.py          # Main entry point (like main.dart)
├── 📄 models.py             # Data models (like models/ folder)
├── 📄 services.py           # Services layer (like services/ folder)
├── 📄 viewmodel.py          # Business logic (like viewmodels/ folder)
├── 📄 config.py             # Configuration (like config.dart)
├── 📄 utils.py              # Utilities (like utils.dart)
├── 📄 main.py               # Legacy single-file version
└── 📄 README.md             # Documentation
```

## Architecture Comparison: Flutter vs Python

### Flutter MVVM Structure
```dart
lib/
├── main.dart
├── models/
│   ├── address.dart
│   └── geocoding_config.dart
├── services/
│   ├── file_service.dart
│   ├── cache_service.dart
│   └── geocoding_service.dart
├── viewmodels/
│   └── geocoding_viewmodel.dart
├── config/
│   └── app_config.dart
└── utils/
    └── helpers.dart
```

### Python MVVM Structure (This Project)
```python
project/
├── main_mvvm.py         # main.dart equivalent
├── models.py            # models/ folder equivalent
├── services.py          # services/ folder equivalent
├── viewmodel.py         # viewmodels/ folder equivalent
├── config.py            # config/ folder equivalent
└── utils.py             # utils/ folder equivalent
```

## Key Benefits of This Architecture

### 1. **Separation of Concerns**
- **Models**: Pure data structures (like Dart classes)
- **Services**: External API calls and data operations
- **ViewModel**: Business logic and state management
- **Utils**: Helper functions and utilities
- **Config**: App configuration and settings

### 2. **Testability**
Each layer can be tested independently:
```python
# Test models
def test_address_model():
    address = Address("Cairo, Egypt", "Cairo")
    assert address.cleaned == "Cairo"

# Test services
def test_geocoding_service():
    service = GeocodingService(config, cache)
    result = service.clean_address("Jumia- Cairo, Egypt")
    assert result == "Cairo, Egypt"

# Test viewmodel
def test_viewmodel():
    vm = GeocodingViewModel(config)
    assert vm.load_addresses() == True
```

### 3. **Maintainability**
- Easy to find and modify specific functionality
- Clear dependencies between layers
- Single responsibility principle

### 4. **Scalability**
- Easy to add new services (e.g., GoogleMapsService)
- Easy to add new output formats
- Easy to add new data sources

## Usage Examples

### Running the Clean Version
```bash
# Use the new MVVM version
python main_mvvm.py

# Or the simple clean version
python main_clean.py

# Legacy version (single file)
python main.py
```

### Customizing Configuration
```python
# Create custom config
config = AppConfig.create_default()
config.processing.batch_size = 2000
config.api.delay_between_requests = 1.0
config.save_to_file("my_config.json")
```

### Using Individual Components
```python
# Use services independently
file_service = FileService()
data = file_service.load_csv("addresses.csv")

# Use models independently
address = Address("Cairo, Egypt", "Cairo")
print(address.coordinates)  # None initially

# Use cache service
cache = CacheService("cache.pkl")
cache.load_cache()
cached_result = cache.get("Cairo")
```

## Comparison: Old vs New

| Aspect | Old (Single File) | New (MVVM) |
|--------|------------------|------------|
| **Lines of Code** | 213 lines in 1 file | ~200 lines across 6 files |
| **Readability** | Hard to navigate | Easy to find specific code |
| **Testing** | Difficult | Each component testable |
| **Maintenance** | Monolithic | Modular |
| **Debugging** | Single large file | Isolated components |
| **Reusability** | None | Services/models reusable |
| **Collaboration** | Merge conflicts | Multiple developers can work |

## Flutter Developer Notes

If you're familiar with Flutter development, here's how the concepts map:

### State Management
```python
# Python ViewModel (like Cubit/Bloc)
class GeocodingViewModel:
    def __init__(self):
        self.stats = ProcessingStats()  # Like state in Cubit
    
    def process_addresses(self):
        # Like a method in Cubit that emits new states
        self.stats.processed_addresses += 1
```

### Dependency Injection
```python
# Python (manual DI)
cache_service = CacheService(config.cache_file)
geocoding_service = GeocodingService(config, cache_service)
viewmodel = GeocodingViewModel(config)

# Flutter equivalent with get_it
final cacheService = GetIt.instance<CacheService>();
final geocodingService = GetIt.instance<GeocodingService>();
```

### Models with Methods
```python
# Python dataclass with methods
@dataclass
class Address:
    original: str
    cleaned: str
    
    @property
    def is_geocoded(self) -> bool:
        return self.latitude is not None

# Flutter equivalent
class Address {
  final String original;
  final String cleaned;
  
  bool get isGeocoded => latitude != null;
}
```

This architecture makes the Python code feel much more like Flutter development! 🚀
