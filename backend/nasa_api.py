import requests
import datetime
import numpy as np

# Statistics from training dataset for standard scaling
MEAN = np.array([3.288984665936473, 26.858233296823656, 72.88647645125958, 2.305576122672508])
STD = np.array([6.782428717059142, 2.825773451072823, 12.156484483205176, 0.905205913370738])

def get_real_features(lat: float, lon: float, lookback: int = 14) -> list:
    """
    Fetches the last `lookback` days of weather data from NASA POWER for the given location,
    and returns a scaled 2D list of features ready for the ML model.
    """
    # NASA POWER has a ~2 day delay, so we fetch from (today - 16 days) to (today - 2 days)
    today = datetime.datetime.now()
    end_date = today - datetime.timedelta(days=2)
    start_date = end_date - datetime.timedelta(days=lookback - 1)
    
    start_str = start_date.strftime("%Y%m%d")
    end_str = end_date.strftime("%Y%m%d")
    
    url = "https://power.larc.nasa.gov/api/temporal/daily/point"
    params = {
        "parameters": "PRECTOTCORR,T2M,RH2M,WS2M",
        "community": "AG",
        "longitude": lon,
        "latitude": lat,
        "start": start_str,
        "end": end_str,
        "format": "JSON"
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        timeseries = data.get("properties", {}).get("parameter", {})
        
        features_list = []
        # Keys are dates in "YYYYMMDD" format
        dates = sorted(list(timeseries.get("PRECTOTCORR", {}).keys()))
        
        for date in dates:
            rain = timeseries.get("PRECTOTCORR", {}).get(date, 0.0)
            temp = timeseries.get("T2M", {}).get(date, 25.0)
            hum = timeseries.get("RH2M", {}).get(date, 70.0)
            wind = timeseries.get("WS2M", {}).get(date, 2.0)
            
            # Handle NASA missing values
            if rain == -999.0: rain = MEAN[0]
            if temp == -999.0: temp = MEAN[1]
            if hum == -999.0: hum = MEAN[2]
            if wind == -999.0: wind = MEAN[3]
            
            raw_features = np.array([rain, temp, hum, wind])
            scaled_features = (raw_features - MEAN) / STD
            features_list.append(scaled_features.tolist())
            
        # Ensure exactly `lookback` length
        if len(features_list) > lookback:
            features_list = features_list[-lookback:]
        elif len(features_list) < lookback:
            # Pad with average (0s after scaling) if NASA API fails to return enough data
            padding = [[0.0, 0.0, 0.0, 0.0]] * (lookback - len(features_list))
            features_list = padding + features_list
            
        return features_list
        
    except Exception as e:
        print(f"[NASA API ERROR] Failed to fetch live data: {e}")
        raise RuntimeError("Failed to fetch live data from NASA POWER API. No mock data allowed.") from e
