def generate_advisory(predicted_price: float, risk_probability: float, crop_type: str, language: str = "English") -> str:
    """
    Generates a farmer-friendly advisory using NLP-like template generation based on predictions.
    Supports multiple South Indian languages natively without relying on external APIs.
    """
    
    templates = {
        "English": {
            "high": "High drought risk expected. Consider drought-resistant {crop} varieties and secure early irrigation resources.",
            "moderate": "Moderate weather risk observed. Monitor soil moisture levels closely for your {crop} fields.",
            "favorable": "Favorable climate conditions expected for observing and managing {crop}.",
            "price": "Market price for {crop} is predicted to be around ₹{price} next week."
        },
        "Telugu (తెలుగు)": {
            "high": "తీవ్రమైన కరువు ముప్పు ఉంది. కరువును తట్టుకునే {crop} రకాలను పరిశీలించండి.",
            "moderate": "మితమైన వాతావరణ ముప్పు గమనించబడింది. మీ {crop} పొలాలకు నేల తేమను పర్యవేక్షించండి.",
            "favorable": "{crop} సాగుకు అనుకూలమైన వాతావరణ పరిస్థితులు ఆశించబడుతున్నాయి.",
            "price": "వచ్చే వారం {crop} మార్కెట్ ధర సుమారు ₹{price} గా అంచనా వేయబడింది."
        },
        "Tamil (தமிழ்)": {
            "high": "கடும் வறட்சி அபாயம் உள்ளது. வறட்சியைத் தாங்கும் {crop} வகைகளைக் கவனியுங்கள்.",
            "moderate": "மிதமான வானிலை அபாயம் உள்ளது. உங்கள் {crop} களுக்கான மண் ஈரப்பதத்தை கண்காணிக்கவும்.",
            "favorable": "{crop} விவசாயத்திற்கு சாதகமான வானிலை எதிர்பார்க்கப்படுகிறது.",
            "price": "அடுத்த வாரம் {crop} சந்தை விலை சுமார் ₹{price} என்று கணிக்கப்பட்டுள்ளது."
        },
        "Kannada (ಕನ್ನಡ)": {
            "high": "ಹೆಚ್ಚಿನ ಬರಗಾಲದ ಅಪಾಯವಿದೆ. ಬರ ನಿರೋಧಕ {crop} ತಳಿಗಳನ್ನು ಪರಿಗಣಿಸಿ.",
            "moderate": "ಮಧ್ಯಮ ಹವಾಮಾನ ಅಪಾಯವಿದೆ. ನಿಮ್ಮ {crop} ಬೆಳೆಗಳ ಮಣ್ಣಿನ ತೇವಾಂಶವನ್ನು ಗಮನಿಸಿ.",
            "favorable": "{crop} ಬೆಳೆಗೆ ಅನುಕೂಲಕರ ಹವಾಮಾನವನ್ನು ನಿರೀಕ್ಷಿಸಲಾಗಿದೆ.",
            "price": "ಮುಂದಿನ ವಾರ {crop} ಮಾರುಕಟ್ಟೆ ಬೆಲೆ ಸುಮಾರು ₹{price} ಆಗುವ ನಿರೀಕ್ಷೆಯಿದೆ."
        },
        "Malayalam (മലയാളം)": {
            "high": "കടുത്ത വരൾച്ചാ അപകടസാധ്യതയുണ്ട്. വരൾച്ചയെ പ്രതിരോധിക്കുന്ന {crop} ഇനങ്ങൾ പരിഗണിക്കുക.",
            "moderate": "മിതമായ കാലാവസ്ഥാ അപകടസാധ്യതയുണ്ട്. നിങ്ങളുടെ {crop} കൃഷിയുടെ മണ്ണിലെ ഈർപ്പം നിരീക്ഷിക്കുക.",
            "favorable": "{crop} കൃഷിക്ക് അനുകൂലമായ കാലാവസ്ഥ പ്രതീക്ഷിക്കുന്നു.",
            "price": "അടുത്ത ആഴ്ച {crop} വിപണി വില ഏകദേശം ₹{price} ആകുമെന്ന് പ്രതീക്ഷിക്കുന്നു."
        }
    }
    
    # 0. Safety fallback
    lang_dict = templates.get(language, templates["English"])
    
    advisory_parts = []
    
    # 1. Risk Advisory Layer
    if risk_probability >= 0.7:
        advisory_parts.append(lang_dict["high"].format(crop=crop_type))
    elif risk_probability >= 0.3:
        advisory_parts.append(lang_dict["moderate"].format(crop=crop_type))
    else:
        advisory_parts.append(lang_dict["favorable"].format(crop=crop_type))
        
    # 2. Market/Price Forecast Layer
    advisory_parts.append(lang_dict["price"].format(crop=crop_type, price=f"{predicted_price:.2f}"))
    
    return " ".join(advisory_parts)

if __name__ == "__main__":
    print(generate_advisory(predicted_price=1250.00, risk_probability=0.88, crop_type="Rice", language="Tamil (தமிழ்)"))
