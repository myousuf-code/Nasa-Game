"""
Example script demonstrating the use of NASA data in the farming simulation game.
"""

import os
import sys
from datetime import datetime

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from data_processing import nasa_data, data_processor

def main():
    """
    Run a demonstration of NASA data access and processing.
    """
    print("NASA Farm Navigator - Data Demo")
    print("===============================")
    
    # Example location (Central Valley, California)
    lat = 36.7783
    lon = -119.4179
    
    # Get today's date
    today = datetime.now().strftime("%Y-%m-%d")
    print(f"Fetching data for location: ({lat}, {lon}) on {today}\n")
    
    # Create a data processor
    processor = data_processor.GameDataProcessor()
    
    # Get and display weather
    print("Daily Weather:")
    weather = processor.get_daily_weather(lat, lon, today)
    for key, value in weather.items():
        if key != 'is_placeholder':
            print(f"  {key}: {value}")
    
    if weather.get('is_placeholder', False):
        print("  (Note: Using placeholder data)")
    
    print("\nSoil Information:")
    soil = processor.get_soil_info(lat, lon)
    print(f"  Type: {soil['type']}")
    print(f"  Quality: {soil['quality']}/100")
    print(f"  pH: {soil['ph']}")
    print(f"  Water Retention: {soil['water_retention']}")
    print("  Nutrients:")
    for nutrient, value in soil['nutrients'].items():
        print(f"    {nutrient}: {value}")
    
    # Get vegetation index
    ndvi = nasa_data.get_vegetation_index(lat, lon, today)
    print(f"\nVegetation Index (NDVI): {ndvi:.2f}")
    
    print("\nGenerating 90-day seasonal forecast...")
    forecast = processor.create_seasonal_forecast(lat, lon, today, days=90)
    
    # Save the forecast plot to the data directory
    os.makedirs(os.path.join('..', '..', 'data'), exist_ok=True)
    output_file = os.path.join('..', '..', 'data', 'forecast.png')
    processor.plot_forecast(forecast, output_file)
    
    print(f"Forecast saved to {os.path.abspath(output_file)}")
    
    print("\nDemo completed successfully!")

if __name__ == "__main__":
    main()