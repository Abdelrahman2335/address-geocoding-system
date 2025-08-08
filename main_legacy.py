import pandas as pd
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from tqdm import tqdm
import time
import json
import os
import pickle
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# --- Configuration for Large Scale Processing ---
BATCH_SIZE = 1000  # Process in batches to save progress
CACHE_FILE = "geocoding_cache.pkl"  # Cache to avoid re-geocoding
MAX_WORKERS = 5  # Number of concurrent threads (be respectful to the API)
DELAY_BETWEEN_REQUESTS = 1.5  # Seconds between requests (increased for stability)

# --- Initialize Geocoder ---
geolocator = Nominatim(user_agent="large_scale_egypt_geocoder_v2")
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=DELAY_BETWEEN_REQUESTS)

# --- Cache Management ---
def load_cache():
    """Load existing geocoding cache to avoid re-processing"""
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'rb') as f:
                return pickle.load(f)
        except:
            return {}
    return {}

def save_cache(cache):
    """Save geocoding cache"""
    with open(CACHE_FILE, 'wb') as f:
        pickle.dump(cache, f)

# --- Clean Addresses ---
def clean_address(address):
    if isinstance(address, str):
        # Remove common prefixes and simplify address
        address = address.replace("Jumia- Pargo- Pickup station -", "")
        address = address.replace("Point 192 -", "")
        address = address.split(",")[0].strip()  # Take first part before comma
    return address

# --- Enhanced Geocoding Function ---
def get_lat_long_cached(address, cache):
    """Get coordinates with caching support"""
    if address in cache:
        return cache[address]
    
    try:
        location = geocode(address)
        if location:
            result = (location.latitude, location.longitude)
            cache[address] = result
            return result
    except Exception as e:
        print(f"Error geocoding {address}: {e}")
        # Cache failed attempts to avoid retrying
        cache[address] = (None, None)
    
    return (None, None)

# --- Batch Processing Function ---
def process_batch(batch_df, cache, batch_num, total_batches):
    """Process a batch of addresses"""
    print(f"\nProcessing batch {batch_num}/{total_batches} ({len(batch_df)} addresses)")
    
    results = []
    for idx, row in tqdm(batch_df.iterrows(), total=len(batch_df), desc=f"Batch {batch_num}"):
        cleaned_address = row['Cleaned_Address']
        lat, lon = get_lat_long_cached(cleaned_address, cache)
        results.append({'index': idx, 'lat': lat, 'lon': lon})
        
        # Save cache every 100 addresses
        if len(results) % 100 == 0:
            save_cache(cache)
    
    return results

# --- Load Data ---
print("Loading data...")
try:
    df = pd.read_csv("geocoded_addresses.csv", encoding='utf-8')
except UnicodeDecodeError:
    df = pd.read_csv("geocoded_addresses.csv", encoding='latin1')

print(f"Loaded {len(df)} addresses")

# --- Load Cache ---
print("Loading cache...")
cache = load_cache()
print(f"Cache contains {len(cache)} previously geocoded addresses")

# --- Process Addresses ---
print("Cleaning addresses...")
df["Cleaned_Address"] = df["Shipping Address"].apply(clean_address)

# Initialize result columns
df["Latitude"] = None
df["Longitude"] = None

# --- Batch Processing for Large Scale ---
print(f"\nStarting batch processing for {len(df)} addresses...")
print(f"Batch size: {BATCH_SIZE}")

# Calculate number of batches
total_batches = (len(df) + BATCH_SIZE - 1) // BATCH_SIZE

for batch_num in range(1, total_batches + 1):
    start_idx = (batch_num - 1) * BATCH_SIZE
    end_idx = min(start_idx + BATCH_SIZE, len(df))
    
    batch_df = df.iloc[start_idx:end_idx].copy()
    
    # Process batch
    results = process_batch(batch_df, cache, batch_num, total_batches)
    
    # Update main dataframe
    for result in results:
        df.at[result['index'], 'Latitude'] = result['lat']
        df.at[result['index'], 'Longitude'] = result['lon']
    
    # Save progress after each batch
    df.to_csv("geocoded_addresses_updated.csv", index=False, encoding='utf-8-sig')
    save_cache(cache)
    
    print(f"Batch {batch_num} completed. Progress saved.")
    
    # Calculate and display progress
    completed = batch_num * BATCH_SIZE if batch_num < total_batches else len(df)
    success_so_far = df["Latitude"].notna().sum()
    print(f"Overall progress: {completed}/{len(df)} addresses processed ({completed/len(df)*100:.1f}%)")
    print(f"Success rate so far: {success_so_far}/{completed} ({success_so_far/completed*100:.1f}%)")
    
    # Small delay between batches
    if batch_num < total_batches:
        time.sleep(2)

# --- Final Save and Statistics ---
print("\n" + "="*80)
print("GEOCODING PROCESS COMPLETED!")
print("="*80)

# Final save
df.to_csv("geocoded_addresses_updated.csv", index=False, encoding='utf-8-sig')
save_cache(cache)
print(f"Results saved to 'geocoded_addresses_updated.csv'")
print(f"Cache saved with {len(cache)} entries")

# --- Show Summary ---
success_count = df["Latitude"].notna().sum()
total_count = len(df)
success_rate = (success_count / total_count) * 100

print(f"\nFINAL STATISTICS:")
print(f"Total addresses processed: {total_count:,}")
print(f"Successfully geocoded: {success_count:,} ({success_rate:.2f}%)")
print(f"Failed addresses: {total_count - success_count:,}")

# Show sample of failed addresses (max 10)
failed_addresses = df[df["Latitude"].isna()]["Cleaned_Address"].tolist()
if failed_addresses:
    print(f"\nSample failed addresses (showing up to 10):")
    for i, addr in enumerate(failed_addresses[:10], 1):
        print(f"  {i}. {addr}")
    if len(failed_addresses) > 10:
        print(f"  ... and {len(failed_addresses) - 10} more")

# --- Create Address to Coordinates Map (only for successful geocoding) ---
def create_address_map(dataframe):
    """Create a dictionary mapping addresses to coordinates"""
    address_map = {}
    
    for index, row in dataframe.iterrows():
        if pd.notna(row['Latitude']) and pd.notna(row['Longitude']):
            # Use original address as key
            address = row['Shipping Address'].strip('"')
            coordinates = f"{row['Latitude']},{row['Longitude']}"
            address_map[address] = coordinates
    
    return address_map

print("\nGenerating address coordinate maps...")
address_coordinates_map = create_address_map(df)

# Save as JSON file
with open("address_coordinates_map.json", "w", encoding='utf-8') as json_file:
    json.dump(address_coordinates_map, json_file, indent=2, ensure_ascii=False)

# Save as Python dictionary format
with open("address_coordinates_map.py", "w", encoding='utf-8') as py_file:
    py_file.write("# Address to Coordinates Mapping\n")
    py_file.write(f"# Generated from {total_count:,} addresses\n")
    py_file.write(f"# Success rate: {success_rate:.2f}%\n")
    py_file.write("address_coordinates = ")
    py_file.write(json.dumps(address_coordinates_map, indent=2, ensure_ascii=False))

print(f"Address maps saved:")
print(f"  - JSON format: address_coordinates_map.json ({len(address_coordinates_map):,} entries)")
print(f"  - Python format: address_coordinates_map.py ({len(address_coordinates_map):,} entries)")

# Performance statistics
print(f"\nPERFORMANCE INFO:")
print(f"  - Cache entries: {len(cache):,}")
print(f"  - Batch size used: {BATCH_SIZE:,}")
print(f"  - API delay: {DELAY_BETWEEN_REQUESTS}s between requests")

print("\n" + "="*80)
print("Process completed successfully! 🎉")
print("="*80)