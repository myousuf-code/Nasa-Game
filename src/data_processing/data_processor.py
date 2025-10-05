"""
Module for processing and converting NASA data for use in the farming simulation game.

This module transforms raw NASA data into formats usable by the game engine.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

from . import nasa_data

class GameDataProcessor:
    """
    Class for processing NASA data into game-usable formats.
    """
    
    def __init__(self, data_cache_dir=None):
        """
        Initialize the data processor.
        
        Args:
            data_cache_dir (str): Directory to cache processed data
        """
        self.data_cache_dir = data_cache_dir
        
    def get_daily_weather(self, lat, lon, date):
        """
        Get weather data for a specific day, formatted for game use.
        
        Args:
            lat (float): Latitude
            lon (float): Longitude
            date (str): Date in YYYY-MM-DD format
            
        Returns:
            dict: Dictionary with weather data for the game
        """
        # Convert date to required format - use historical year for NASA data
        date_obj = datetime.strptime(date, "%Y-%m-%d")
        
        # NASA POWER only has historical data, so use the same day/month from a recent historical year
        historical_year = 2023  # Use 2023 data as recent historical reference
        historical_date_obj = date_obj.replace(year=historical_year)
        
        start_date = historical_date_obj.strftime("%Y%m%d")
        end_date = historical_date_obj.strftime("%Y%m%d")
        
        print(f"Requesting NASA data for historical date: {start_date} (game date: {date})")
        
        # Get climate data from NASA POWER API
        climate_data = nasa_data.get_climate_data(
            lat, lon, start_date, end_date, 
            parameters=["T2M", "T2M_MAX", "T2M_MIN", "PRECTOTCORR", "RH2M", "WS2M"]
        )
        
        if not climate_data or "properties" not in climate_data:
            # Return placeholder data if API call fails
            return {
                "temperature": 20.0,
                "temperature_max": 25.0,
                "temperature_min": 15.0,
                "precipitation": 0.0,
                "humidity": 65.0,
                "wind_speed": 3.0,
                "is_placeholder": True
            }
        
        # Extract the data for the specific date
        try:
            daily_data = climate_data["properties"]["parameter"]
            # Use the historical date key that matches what we requested from NASA
            date_key = historical_date_obj.strftime("%Y%m%d")
            
            # Create a game-ready weather dictionary
            weather = {
                "temperature": daily_data["T2M"][date_key],
                "temperature_max": daily_data["T2M_MAX"][date_key],
                "temperature_min": daily_data["T2M_MIN"][date_key],
                "precipitation": daily_data["PRECTOTCORR"][date_key],
                "humidity": daily_data["RH2M"][date_key],
                "wind_speed": daily_data["WS2M"][date_key],
                "is_placeholder": False
            }
            
            return weather
            
        except (KeyError, TypeError) as e:
            print(f"Error processing climate data: {e}")
            # Return placeholder data
            return {
                "temperature": 20.0,
                "temperature_max": 25.0,
                "temperature_min": 15.0,
                "precipitation": 0.0,
                "humidity": 65.0,
                "wind_speed": 3.0,
                "is_placeholder": True
            }
    
    def get_soil_info(self, lat, lon):
        """
        Get soil information for a specific location, formatted for game use.
        
        Args:
            lat (float): Latitude
            lon (float): Longitude
            
        Returns:
            dict: Dictionary with soil data for the game
        """
        soil_data = nasa_data.get_soil_data(lat, lon)
        
        # Process soil data for game use
        game_soil = {
            "type": soil_data["soil_type"],
            "quality": self._calculate_soil_quality(soil_data),
            "nutrients": {
                "nitrogen": soil_data["nitrogen"],
                "phosphorus": soil_data["phosphorus"],
                "potassium": soil_data["potassium"]
            },
            "ph": soil_data["ph"],
            "water_retention": self._calculate_water_retention(soil_data)
        }
        
        return game_soil
        
    def _calculate_soil_quality(self, soil_data):
        """Calculate overall soil quality on a scale of 0-100."""
        # Simplified model - in a real game this would be more complex
        quality = 50  # Base value
        
        # Adjust for organic matter (ideal range is around 3-5%)
        om = soil_data["organic_matter"]
        if om < 2:
            quality -= 10
        elif om > 2 and om < 5:
            quality += 15
        else:
            quality += 5
            
        # Adjust for pH (ideal range is around 6-7)
        ph = soil_data["ph"]
        if ph < 5.5 or ph > 7.5:
            quality -= 15
        elif ph >= 6 and ph <= 7:
            quality += 15
        
        # Ensure quality is within 0-100 range
        return max(0, min(100, quality))
        
    def _calculate_water_retention(self, soil_data):
        """Calculate soil water retention on a scale of 0-1."""
        # Simple model based on soil type
        soil_type = soil_data["soil_type"].lower()
        
        if soil_type == "sandy":
            return 0.3
        elif soil_type == "loamy":
            return 0.6
        elif soil_type == "clay":
            return 0.8
        else:
            return 0.5
            
    def create_seasonal_forecast(self, lat, lon, start_date, days=90):
        """
        Create a seasonal weather forecast for game planning.
        
        Args:
            lat (float): Latitude
            lon (float): Longitude
            start_date (str): Start date in YYYY-MM-DD format
            days (int): Number of days to forecast
            
        Returns:
            pd.DataFrame: DataFrame with daily forecast data
        """
        # Convert start date to datetime object
        start = datetime.strptime(start_date, "%Y-%m-%d")
        
        # Generate date range
        date_range = [start + timedelta(days=i) for i in range(days)]
        dates = [d.strftime("%Y-%m-%d") for d in date_range]
        
        # For a real application, we would use actual seasonal forecast data
        # Here, we'll generate simulated data
        
        # Temperature oscillates around a baseline with random variations
        base_temp = 20  # Base temperature in Celsius
        amplitude = 8  # Annual temperature variation amplitude
        
        # Calculate day of year and simulate seasonal variation
        doy_values = [(start + timedelta(days=i)).timetuple().tm_yday for i in range(days)]
        seasonal_factor = [amplitude * np.sin(2 * np.pi * (doy - 80) / 365) for doy in doy_values]
        
        # Generate temperatures with seasonal trend and random variations
        temps = [base_temp + sf + np.random.normal(0, 2) for sf in seasonal_factor]
        temp_min = [t - np.random.uniform(3, 8) for t in temps]
        temp_max = [t + np.random.uniform(3, 8) for t in temps]
        
        # Generate precipitation (more likely in certain seasons)
        precip_prob = [0.3 + 0.2 * np.sin(2 * np.pi * (doy - 100) / 365) for doy in doy_values]
        precipitation = [np.random.exponential(5) if np.random.random() < p else 0 for p in precip_prob]
        
        # Create DataFrame
        forecast = pd.DataFrame({
            'date': dates,
            'temperature': temps,
            'temperature_min': temp_min,
            'temperature_max': temp_max,
            'precipitation': precipitation
        })
        
        return forecast
        
    def plot_forecast(self, forecast, output_file=None):
        """
        Plot a seasonal forecast for visualization.
        
        Args:
            forecast (pd.DataFrame): Forecast DataFrame
            output_file (str): Path to save the plot image
            
        Returns:
            matplotlib.figure.Figure: The created figure
        """
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)
        
        # Convert date strings to datetime objects
        dates = [datetime.strptime(d, "%Y-%m-%d") for d in forecast['date']]
        
        # Plot temperature
        ax1.plot(dates, forecast['temperature'], label='Avg Temp', color='orange')
        ax1.fill_between(dates, forecast['temperature_min'], forecast['temperature_max'], 
                        alpha=0.2, color='orange')
        ax1.set_ylabel('Temperature (°C)')
        ax1.set_title('Seasonal Forecast')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Plot precipitation
        ax2.bar(dates, forecast['precipitation'], width=1, label='Precipitation', 
               color='blue', alpha=0.7)
        ax2.set_xlabel('Date')
        ax2.set_ylabel('Precipitation (mm)')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # Format the x-axis to show dates nicely
        fig.autofmt_xdate()
        
        plt.tight_layout()
        
        # Save if output file is specified
        if output_file:
            plt.savefig(output_file, dpi=100)
        
        return fig