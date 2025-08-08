"""
Main application with clean MVVM architecture
Uses separation of concerns with modular design
"""
from config import AppConfig
from viewmodel import GeocodingViewModel
from utils import Logger, Timer, Console, Formatter


def main():
    """
    Main function entry point
    Uses MVVM architecture with proper separation of concerns
    """
    timer = Timer()
    timer.start()
    
    # Print welcome header
    Console.print_header("🌍 Large-Scale Address Geocoding System", 80)
    Logger.info("Starting geocoding application...")
    
    try:
        # Load configuration
        Logger.info("Loading configuration...")
        config = AppConfig.load_from_file()
        
        # Create ViewModel for business logic
        Logger.info("Initializing geocoding engine...")
        viewmodel = GeocodingViewModel(config.to_geocoding_config())
        
        # Load addresses from file
        Console.print_section("📂 Loading Data")
        if not viewmodel.load_addresses():
            Logger.error("Failed to load addresses. Exiting.")
            return False
        
        # Process all addresses
        Console.print_section("⚡ Processing Addresses")
        success = viewmodel.process_all_addresses()
        
        if success:
            # Print final summary
            Console.print_section("📊 Final Results")
            viewmodel.print_final_summary()
            
            # Print execution time
            elapsed_time = timer.stop()
            Logger.info(f"Total execution time: {Formatter.format_duration(elapsed_time)}")
            
            return True
        else:
            Logger.error("Processing failed. Check logs for details.")
            return False
            
    except KeyboardInterrupt:
        Logger.warning("Process interrupted by user")
        return False
    except Exception as e:
        Logger.error(f"Unexpected error: {e}")
        return False


if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ Application completed successfully!")
    else:
        print("\n❌ Application failed. Check the logs above.")
    
    input("\nPress Enter to exit...")
