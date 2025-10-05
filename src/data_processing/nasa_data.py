"""
Module for fetching NASA satellite and climate data.

This module provides functions to download and process NASA Earth science data
for use in agricultural simulations.
"""

import os
import requests
from datetime import datetime
import pandas as pd
import numpy as np
import time
import json

# NASA API endpoint and key (get a free key from https://api.nasa.gov/)
NASA_API_ENDPOINT = "https://api.nasa.gov"
NASA_API_KEY = "DEMO_KEY"  # Replace with your API key for higher rate limits

# NASA POWER data endpoint (for climate data)
POWER_API_ENDPOINT = "https://power.larc.nasa.gov/api/temporal/daily/point"

# Simple cache for API responses to avoid repeated calls
_api_cache = {}
_last_api_call = 0
_min_call_interval = 1.0  # Minimum 1 second between API calls

def set_api_key(api_key):
    """Set the NASA API key for data access."""
    global NASA_API_KEY
    NASA_API_KEY = api_key

def get_climate_data(lat, lon, start_date, end_date, parameters=None):
    """
    Fetch climate data for a specific location and time period.
    
    Args:
        lat (float): Latitude
        lon (float): Longitude
        start_date (str): Start date in format YYYYMMDD
        end_date (str): End date in format YYYYMMDD
        parameters (list): List of parameters to fetch. Defaults to temperature and precipitation.
        
    Returns:
        dict: Dictionary containing the requested climate data
    """
    if parameters is None:
        parameters = ["T2M", "PRECTOTCORR"]  # Temperature and precipitation
    
    # Create cache key for this request
    cache_key = f"{lat}_{lon}_{start_date}_{end_date}_{','.join(parameters)}"
    
    # Check if we have cached data
    if cache_key in _api_cache:
        print(f"Using cached NASA data for {start_date}")
        return _api_cache[cache_key]
    
    # Rate limiting - ensure minimum interval between API calls
    global _last_api_call
    time_since_last_call = time.time() - _last_api_call
    if time_since_last_call < _min_call_interval:
        time.sleep(_min_call_interval - time_since_last_call)
        
    # Build parameters according to NASA POWER API specification
    params = {
        "parameters": ",".join(parameters),
        "community": "RE",  # Renewable Energy community (more stable than AG)
        "longitude": str(lon),  # Ensure string format
        "latitude": str(lat),   # Ensure string format  
        "start": str(start_date),  # Format: YYYYMMDD
        "end": str(end_date),      # Format: YYYYMMDD
        "format": "JSON"
    }
    
    # Add timeout and retry logic
    max_retries = 2
    for attempt in range(max_retries + 1):
        try:
            response = requests.get(POWER_API_ENDPOINT, params=params, timeout=15)
            _last_api_call = time.time()
            
            # Print the actual URL being requested for debugging (only on first attempt)
            if attempt == 0:
                print(f"Requesting: {response.url}")
            
            if response.status_code == 200:
                data = response.json()
                # Cache successful response
                _api_cache[cache_key] = data
                return data
            else:
                if attempt == 0:  # Only print errors on first attempt
                    print(f"Error fetching climate data: {response.status_code}")
                    if response.status_code != 500:  # Don't print server errors repeatedly
                        print(f"Response: {response.text[:200]}")
                
                # If it's a 500 error and we have retries left, try again
                if response.status_code == 500 and attempt < max_retries:
                    print(f"Retrying in {2 ** attempt} seconds... (attempt {attempt + 2}/{max_retries + 1})")
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                    
                return None
                
        except requests.exceptions.RequestException as e:
            if attempt == 0:
                print(f"Request failed: {e}")
            
            # Retry on network errors
            if attempt < max_retries:
                print(f"Retrying in {2 ** attempt} seconds... (attempt {attempt + 2}/{max_retries + 1})")
                time.sleep(2 ** attempt)
                continue
                
            return None
    
    return None

def download_satellite_imagery(lat, lon, date, cloud_score=True, save_path=None):
    """
    Download NASA satellite imagery for a specific location and date.
    
    Args:
        lat (float): Latitude
        lon (float): Longitude
        date (str): Date in YYYY-MM-DD format
        cloud_score (bool): Whether to include cloud score data
        save_path (str): Path to save the image. If None, image is not saved.
        
    Returns:
        dict: Dictionary containing image data and metadata
    """
    endpoint = f"{NASA_API_ENDPOINT}/planetary/earth/imagery"
    
    params = {
        "lon": lon,
        "lat": lat,
        "date": date,
        "cloud_score": str(cloud_score).lower(),
        "api_key": NASA_API_KEY
    }
    
    response = requests.get(endpoint, params=params)
    
    if response.status_code == 200:
        data = response.json()
        
        # Download the actual image if requested
        if save_path and "url" in data:
            img_response = requests.get(data["url"])
            if img_response.status_code == 200:
                os.makedirs(os.path.dirname(save_path), exist_ok=True)
                with open(save_path, "wb") as f:
                    f.write(img_response.content)
                print(f"Image saved to {save_path}")
            else:
                print(f"Error downloading image: {img_response.status_code}")
        
        return data
    else:
        print(f"Error fetching satellite data: {response.status_code}")
        print(response.text)
        return None

def get_soil_data(lat, lon):
    """
    Placeholder function for fetching soil data.
    In a real application, this would connect to soil databases or models.
    
    Args:
        lat (float): Latitude
        lon (float): Longitude
        
    Returns:
        dict: Dictionary containing soil data
    """
    # This is a placeholder. In a real application, you would connect to 
    # actual soil databases or models.
    return {
        "soil_type": "loamy",
        "ph": 6.5,
        "organic_matter": 3.2,
        "nitrogen": 0.15,
        "phosphorus": 0.05,
        "potassium": 0.2
    }

def get_vegetation_index(lat, lon, date):
    """
    Get vegetation indices (like NDVI) for a specific location and date.
    
    Args:
        lat (float): Latitude
        lon (float): Longitude
        date (str): Date in YYYY-MM-DD format
        
    Returns:
        float: NDVI value (between -1 and 1)
    """
    # This is a simplified placeholder. In a real application, you would
    # process actual satellite data to calculate NDVI.
    # For demonstration, we'll return a random value within a realistic range.
    return np.random.uniform(0.2, 0.8)