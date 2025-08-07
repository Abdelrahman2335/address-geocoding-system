"""
View Model - handles business logic and state management
Similar to ViewModel/Controller in Flutter MVVM
"""
from typing import List, Optional, Dict, Any
import pandas as pd
from tqdm import tqdm
import time

from models import Address, ProcessingStats, GeocodingConfig
from services import FileService, CacheService, GeocodingService


class GeocodingViewModel:
    """
    Main ViewModel for geocoding operations
    Like a Cubit/Bloc or ChangeNotifier in Flutter
    """
    
    def __init__(self, config: GeocodingConfig):
        self.config = config
        self.stats = ProcessingStats()
        self.addresses: List[Address] = []
        
        # Initialize services
        self.cache_service = CacheService(config.cache_file)
        self.geocoding_service = GeocodingService(config, self.cache_service)
        self.file_service = FileService()
        
        # Load cache
        self.cache_service.load_cache()
    
    def load_addresses(self) -> bool:
        """
        Load addresses from CSV file
        Returns True if successful, False otherwise
        """
        try:
            print("Loading data...")
            df = self.file_service.load_csv(self.config.input_file)
            
            # Convert to Address objects
            self.addresses = []
            for _, row in df.iterrows():
                original = row['Shipping Address'].strip('"') if isinstance(row['Shipping Address'], str) else ""
                cleaned = self.geocoding_service.clean_address(original)
                self.addresses.append(Address(original=original, cleaned=cleaned))
            
            self.stats.total_addresses = len(self.addresses)
            self.stats.total_batches = (len(self.addresses) + self.config.batch_size - 1) // self.config.batch_size
            
            print(f"Loaded {len(self.addresses)} addresses")
            print(f"Cache contains {self.cache_service.size()} previously geocoded addresses")
            
            return True
            
        except Exception as e:
            print(f"Error loading addresses: {e}")
            return False
    
    def process_batch(self, batch_addresses: List[Address], batch_num: int) -> None:
        """Process a single batch of addresses"""
        print(f"\nProcessing batch {batch_num}/{self.stats.total_batches} ({len(batch_addresses)} addresses)")
        
        batch_stats = {'processed': 0, 'successful': 0}
        
        for address in tqdm(batch_addresses, desc=f"Batch {batch_num}"):
            lat, lng = self.geocoding_service.geocode_address(address.cleaned)
            address.latitude = lat
            address.longitude = lng
            
            batch_stats['processed'] += 1
            if address.is_geocoded:
                batch_stats['successful'] += 1
            
            # Save cache every 100 addresses
            if batch_stats['processed'] % 100 == 0:
                self.cache_service.save_cache()
        
        # Update overall stats
        self.stats.processed_addresses += batch_stats['processed']
        self.stats.successful_geocodes += batch_stats['successful']
        self.stats.failed_geocodes = self.stats.processed_addresses - self.stats.successful_geocodes
        self.stats.current_batch = batch_num
    
    def process_all_addresses(self) -> bool:
        """
        Process all addresses in batches
        Returns True if successful, False otherwise
        """
        if not self.addresses:
            print("No addresses to process")
            return False
        
        try:
            print(f"\nStarting batch processing for {len(self.addresses)} addresses...")
            print(f"Batch size: {self.config.batch_size:,}")
            
            for batch_num in range(1, self.stats.total_batches + 1):
                start_idx = (batch_num - 1) * self.config.batch_size
                end_idx = min(start_idx + self.config.batch_size, len(self.addresses))
                
                batch_addresses = self.addresses[start_idx:end_idx]
                self.process_batch(batch_addresses, batch_num)
                
                # Save progress after each batch
                self.save_results()
                self.cache_service.save_cache()
                
                print(f"Batch {batch_num} completed. Progress saved.")
                self._print_progress()
                
                # Small delay between batches
                if batch_num < self.stats.total_batches:
                    time.sleep(2)
            
            return True
            
        except Exception as e:
            print(f"Error processing addresses: {e}")
            return False
    
    def save_results(self) -> None:
        """Save results to various output formats"""
        try:
            # Convert addresses back to DataFrame
            data = []
            for address in self.addresses:
                data.append({
                    'Shipping Address': address.original,
                    'Cleaned_Address': address.cleaned,
                    'Latitude': address.latitude,
                    'Longitude': address.longitude
                })
            
            df = pd.DataFrame(data)
            
            # Save CSV
            self.file_service.save_csv(df, self.config.output_file)
            
            # Create coordinate mapping for successfully geocoded addresses
            coordinate_map = {}
            for address in self.addresses:
                if address.is_geocoded:
                    coordinate_map[address.original] = address.coordinates
            
            # Save JSON format
            self.file_service.save_json(coordinate_map, self.config.json_output)
            
            # Save Python dictionary format
            description = f"Generated from {self.stats.total_addresses:,} addresses - Success rate: {self.stats.success_rate:.2f}%"
            self.file_service.save_python_dict(coordinate_map, self.config.python_output, description)
            
        except Exception as e:
            print(f"Error saving results: {e}")
    
    def _print_progress(self) -> None:
        """Print current progress statistics"""
        print(f"Overall progress: {self.stats.processed_addresses}/{self.stats.total_addresses} addresses processed ({self.stats.progress_percentage:.1f}%)")
        print(f"Success rate so far: {self.stats.successful_geocodes}/{self.stats.processed_addresses} ({self.stats.success_rate:.1f}%)")
    
    def print_final_summary(self) -> None:
        """Print final processing summary"""
        print("\n" + "="*80)
        print("GEOCODING PROCESS COMPLETED!")
        print("="*80)
        
        print(f"Results saved to '{self.config.output_file}'")
        print(f"Cache saved with {self.cache_service.size()} entries")
        
        print(f"\nFINAL STATISTICS:")
        print(f"Total addresses processed: {self.stats.total_addresses:,}")
        print(f"Successfully geocoded: {self.stats.successful_geocodes:,} ({self.stats.success_rate:.2f}%)")
        print(f"Failed addresses: {self.stats.failed_geocodes:,}")
        
        # Show sample of failed addresses
        failed_addresses = [addr.cleaned for addr in self.addresses if not addr.is_geocoded]
        if failed_addresses:
            print(f"\nSample failed addresses (showing up to 10):")
            for i, addr in enumerate(failed_addresses[:10], 1):
                print(f"  {i}. {addr}")
            if len(failed_addresses) > 10:
                print(f"  ... and {len(failed_addresses) - 10} more")
        
        # Print output files info
        successful_count = len([addr for addr in self.addresses if addr.is_geocoded])
        print(f"\nAddress maps saved:")
        print(f"  - JSON format: {self.config.json_output} ({successful_count:,} entries)")
        print(f"  - Python format: {self.config.python_output} ({successful_count:,} entries)")
        
        print(f"\nPERFORMANCE INFO:")
        print(f"  - Cache entries: {self.cache_service.size():,}")
        print(f"  - Batch size used: {self.config.batch_size:,}")
        print(f"  - API delay: {self.config.delay_between_requests}s between requests")
        
        print("\n" + "="*80)
        print("Process completed successfully! 🎉")
        print("="*80)
