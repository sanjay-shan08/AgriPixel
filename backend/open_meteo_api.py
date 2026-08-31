import requests
import datetime
import numpy as np

# Statistics from training dataset for standard scaling (must match the model's training distribution)
# These are the means from the 10-year NASA POWER dataset
MEAN = np.array([3.288984665936473, 26.858233296823656, 72.88647645125958, 2.305576122672508])
STD = np.array([6.782428717059142, 2.825773451072823, 12.156484483205176, 0.905205913370738])

def get_real_features(lat: float, lon: float, lookback: int = 14) -> list:
    """
    Fetches the last `lookback` days of weather data from Open-Meteo for the given location,
    inclusive of TODAY (zero lag), and returns a scaled 2D list of features.
    """
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "past_days": lookback - 1, # e.g. 13 days past + 1 day current = 14 days
        "forecast_days": 1,
        "daily": "temperature_2m_mean,precipitation_sum,wind_speed_10m_max",
        "hourly": "relative_humidity_2m",
        "timezone": "auto"
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        daily = data.get("daily", {})
        hourly = data.get("hourly", {})
        
        features_list = []
        
        # Open-Meteo returns lists of data parallel to the 'time' array
        for i in range(len(daily.get("time", []))):
            rain = daily.get("precipitation_sum", [])[i]
            temp = daily.get("temperature_2m_mean", [])[i]
            wind = daily.get("wind_speed_10m_max", [])[i]
            
            # Wind speed is in km/h from Open-Meteo, convert to m/s to match NASA's training data
            if wind is not None:
                wind = wind * (1000 / 3600)
                
            # Calculate daily mean humidity from hourly data
            # Each day has 24 hours. The i-th day corresponds to hours [i*24 : i*24 + 24]
            daily_humidity_hours = hourly.get("relative_humidity_2m", [])[i*24 : i*24 + 24]
            # filter out Nones
            valid_humidity = [h for h in daily_humidity_hours if h is not None]
            if valid_humidity:
                hum = sum(valid_humidity) / len(valid_humidity)
            else:
                hum = None
                
            # Handle potential nulls
            if rain is None: rain = MEAN[0]
            if temp is None: temp = MEAN[1]
            if hum is None: hum = MEAN[2]
            if wind is None: wind = MEAN[3]
            
            raw_features = np.array([rain, temp, hum, wind])
            scaled_features = (raw_features - MEAN) / STD
            features_list.append(scaled_features.tolist())
            
        # Ensure exactly `lookback` length
        if len(features_list) > lookback:
            features_list = features_list[-lookback:]
        elif len(features_list) < lookback:
            padding = [[0.0, 0.0, 0.0, 0.0]] * (lookback - len(features_list))
            features_list = padding + features_list
            
        return features_list
        
    except Exception as e:
        print(f"[Open-Meteo API ERROR] Failed to fetch live data: {e}")
        raise RuntimeError("Failed to fetch zero-lag data from Open-Meteo API.") from e
