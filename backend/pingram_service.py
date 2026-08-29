import os
import requests
from dotenv import load_dotenv

load_dotenv()

PINGRAM_API_KEY = os.getenv("PINGRAM_API_KEY", "")
PINGRAM_API_URL = "https://api.pingram.app/v1/messages" # Dummy endpoint for Pingram

def send_whatsapp_advisory(phone_number: str, message: str, forecast_id: int) -> bool:
    """
    Sends the advisory message to the farmer via Pingram WhatsApp API.
    """
    if not PINGRAM_API_KEY or PINGRAM_API_KEY == "your_pingram_api_key_here":
        raise ValueError("PINGRAM_API_KEY is not set. Refusing to use mock data in production.")
        
    headers = {
        "Authorization": f"Bearer {PINGRAM_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "to": phone_number,
        "message": message,
        "channel": "whatsapp",
        "metadata": {
            "forecast_id": forecast_id
        }
    }
    
    try:
        response = requests.post(PINGRAM_API_URL, json=payload, headers=headers)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        print(f"[PINGRAM ERROR] Failed to send message: {e}")
        return False
