"""
Main application entry point - like main.dart in Flutter
Clean and simple, delegates to ViewModel
"""
from models import GeocodingConfig
from viewmodel import GeocodingViewModel


def main():
    """
    Main function - clean and simple like Flutter's main()
    All business logic is handled by the ViewModel
    """
    print("🌍 Large-Scale Address Geocoding System")
    print("=" * 50)
    
    # Create configuration (like loading app config in Flutter)
    config = GeocodingConfig(
        batch_size=1000,
        delay_between_requests=1.5,
        user_agent="large_scale_geocoder_mvvm_v1"
    )
    
    # Initialize ViewModel (like creating a Cubit/Bloc in Flutter)
    viewmodel = GeocodingViewModel(config)
    
    # Load and process data
    if not viewmodel.load_addresses():
        print("❌ Failed to load addresses. Exiting.")
        return
    
    # Process all addresses
    success = viewmodel.process_all_addresses()
    
    if success:
        # Print final summary
        viewmodel.print_final_summary()
    else:
        print("❌ Processing failed. Check logs for details.")


if __name__ == "__main__":
    main()
