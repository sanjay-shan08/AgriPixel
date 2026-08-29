# Advisory Rule Engine and Localization

TRANSLATIONS = {
    "en": {
        "extreme_rain": "🚨 CRITICAL: Extreme rainfall expected in the next 3 days. Postpone all sowing and spraying activities immediately. Ensure proper field drainage to prevent waterlogging.",
        "heavy_rain": "⚠️ Warning: Heavy rainfall predicted. Delay fertilizer and pesticide applications as they will wash away. Good time for rain-fed crops.",
        "moderate_rain": "ℹ️ Moderate rain expected. Favorable conditions for sowing. No need for additional irrigation.",
        "clear_weather": "☀️ Clear weather over the next 3 days. Ideal conditions for harvesting, spraying pesticides, and applying fertilizers. Ensure standard irrigation schedule is maintained.",
        "greeting": "Hello Farmer! Here is your AgriPixel weather advisory for the next 3 days:"
    },
    "ta": {
        "extreme_rain": "🚨 எச்சரிக்கை: அடுத்த 3 நாட்களில் மிகக் கடுமையான மழை எதிர்பார்க்கப்படுகிறது. விதைப்பு மற்றும் மருந்து தெளிப்பதைத் தவிர்க்கவும். வயலில் தண்ணீர் தேங்காமல் பார்த்துக் கொள்ளவும்.",
        "heavy_rain": "⚠️ எச்சரிக்கை: பலத்த மழை எதிர்பார்க்கப்படுகிறது. உரம் மற்றும் பூச்சிக்கொல்லி தெளிப்பதைத் தள்ளிப்போடவும்.",
        "moderate_rain": "ℹ️ மிதமான மழை எதிர்பார்க்கப்படுகிறது. விதைப்புக்கு உகந்த நேரம். கூடுதல் நீர்ப்பாசனம் தேவையில்லை.",
        "clear_weather": "☀️ அடுத்த 3 நாட்களுக்கு தெளிவான வானிலை. அறுவடை மற்றும் உரம் இட இதுவே சரியான நேரம். வழக்கமான நீர்ப்பாசனத்தைத் தொடரவும்.",
        "greeting": "வணக்கம் விவசாயி! அடுத்த 3 நாட்களுக்கான அக்ரிபிக்சல் வானிலை ஆலோசனை:"
    }
}

def generate_advisory(predicted_rain_mm: list, extreme_prob: list, language: str = "ta") -> str:
    """
    Generates a localized advisory based on the 3-day forecast.
    """
    # Simple rule engine
    avg_rain = sum(predicted_rain_mm) / len(predicted_rain_mm)
    max_extreme_prob = max(extreme_prob)
    
    lang_dict = TRANSLATIONS.get(language, TRANSLATIONS["en"])
    
    if max_extreme_prob > 0.8 or avg_rain > 50:
        advice = lang_dict["extreme_rain"]
    elif avg_rain > 20:
        advice = lang_dict["heavy_rain"]
    elif avg_rain > 5:
        advice = lang_dict["moderate_rain"]
    else:
        advice = lang_dict["clear_weather"]
        
    return f"{lang_dict['greeting']}\n\n{advice}"
