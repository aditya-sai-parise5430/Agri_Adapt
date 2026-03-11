from deep_translator import GoogleTranslator

# Crop name translations per language (used inside advisory templates)
CROP_NAMES = {
    "English": {"Wheat": "Wheat", "Rice": "Rice", "Cotton": "Cotton", "Soybean": "Soybean", "Maize": "Maize"},
    "Hindi":   {"Wheat": "गेहूँ", "Rice": "चावल", "Cotton": "कपास", "Soybean": "सोयाबीन", "Maize": "मक्का"},
    "Telugu (తెలుగు)": {"Wheat": "గోధుమ", "Rice": "వరి", "Cotton": "పత్తి", "Soybean": "సోయాబీన్", "Maize": "మొక్కజొన్న"},
    "Tamil (தமிழ்)":   {"Wheat": "கோதுமை", "Rice": "அரிசி", "Cotton": "பருத்தி", "Soybean": "சோயாபீன்", "Maize": "மக்காச்சோளம்"},
    "Kannada (ಕನ್ನಡ)": {"Wheat": "ಗೋಧಿ", "Rice": "ಅಕ್ಕಿ", "Cotton": "ಹತ್ತಿ", "Soybean": "ಸೋಯಾಬೀನ್", "Maize": "ಮೆಕ್ಕೆ ಜೋಳ"},
    "Malayalam (മലയാളം)": {"Wheat": "ഗോതമ്പ്", "Rice": "അരി", "Cotton": "പരുത്തി", "Soybean": "സോയാബീൻ", "Maize": "ചോളം"},
}

TEMPLATES = {
    "English": {
        "high":     "High drought risk expected. Consider drought-resistant {crop} varieties and secure early irrigation resources.",
        "moderate": "Moderate weather risk observed. Monitor soil moisture levels closely for your {crop} fields.",
        "favorable": "Favorable climate conditions expected for {crop} cultivation.",
        "price":    "Market price for {crop} is predicted to be around ₹{price} per quintal next week.",
    },
    "Hindi": {
        "high":     "उच्च सूखे का खतरा है। सूखा-प्रतिरोधी {crop} किस्मों पर विचार करें और सिंचाई संसाधन पहले ही सुरक्षित करें।",
        "moderate": "मध्यम मौसम जोखिम देखा गया है। अपने {crop} खेतों की मिट्टी की नमी पर नजर रखें।",
        "favorable": "{crop} की खेती के लिए अनुकूल जलवायु परिस्थितियां अपेक्षित हैं।",
        "price":    "अगले सप्ताह {crop} का बाजार मूल्य लगभग ₹{price} प्रति क्विंटल रहने का अनुमान है।",
    },
    "Telugu (తెలుగు)": {
        "high":     "తీవ్రమైన కరువు ముప్పు ఉంది. కరువును తట్టుకునే {crop} రకాలను పరిశీలించండి.",
        "moderate": "మితమైన వాతావరణ ముప్పు గమనించబడింది. మీ {crop} పొలాలకు నేల తేమను పర్యవేక్షించండి.",
        "favorable": "{crop} సాగుకు అనుకూలమైన వాతావరణ పరిస్థితులు ఆశించబడుతున్నాయి.",
        "price":    "వచ్చే వారం {crop} మార్కెట్ ధర సుమారు ₹{price} గా అంచనా వేయబడింది.",
    },
    "Tamil (தமிழ்)": {
        "high":     "கடும் வறட்சி அபாயம் உள்ளது. வறட்சியைத் தாங்கும் {crop} வகைகளைக் கவனியுங்கள்.",
        "moderate": "மிதமான வானிலை அபாயம் உள்ளது. உங்கள் {crop} களுக்கான மண் ஈரப்பதத்தை கண்காணிக்கவும்.",
        "favorable": "{crop} விவசாயத்திற்கு சாதகமான வானிலை எதிர்பார்க்கப்படுகிறது.",
        "price":    "அடுத்த வாரம் {crop} சந்தை விலை சுமார் ₹{price} என்று கணிக்கப்பட்டுள்ளது.",
    },
    "Kannada (ಕನ್ನಡ)": {
        "high":     "ಹೆಚ್ಚಿನ ಬರಗಾಲದ ಅಪಾಯವಿದೆ. ಬರ ನಿರೋಧಕ {crop} ತಳಿಗಳನ್ನು ಪರಿಗಣಿಸಿ.",
        "moderate": "ಮಧ್ಯಮ ಹವಾಮಾನ ಅಪಾಯವಿದೆ. ನಿಮ್ಮ {crop} ಬೆಳೆಗಳ ಮಣ್ಣಿನ ತೇವಾಂಶವನ್ನು ಗಮನಿಸಿ.",
        "favorable": "{crop} ಬೆಳೆಗೆ ಅನುಕೂಲಕರ ಹವಾಮಾನವನ್ನು ನಿರೀಕ್ಷಿಸಲಾಗಿದೆ.",
        "price":    "ಮುಂದಿನ ವಾರ {crop} ಮಾರುಕಟ್ಟೆ ಬೆಲೆ ಸುಮಾರು ₹{price} ಆಗುವ ನಿರೀಕ್ಷೆಯಿದೆ.",
    },
    "Malayalam (മലയാളം)": {
        "high":     "കടുത്ത വരൾച്ചാ അപകടസാധ്യതയുണ്ട്. വരൾച്ചയെ പ്രതിരോധിക്കുന്ന {crop} ഇനങ്ങൾ പരിഗണിക്കുക.",
        "moderate": "മിതമായ കാലാവസ്ഥാ അപകടസാധ്യതയുണ്ട്. നിങ്ങളുടെ {crop} കൃഷിയുടെ മണ്ണിലെ ഈർപ്പം നിരീക്ഷിക്കുക.",
        "favorable": "{crop} കൃഷിക്ക് അനുകൂലമായ കാലാവസ്ഥ പ്രതീക്ഷിക്കുന്നു.",
        "price":    "അടുത്ത ആഴ്ച {crop} വിപണി വില ഏകദേശം ₹{price} ആകുമെന്ന് പ്രതീക്ഷിക്കുന്നു.",
    },
}

LANG_TO_ISO = {
    "Hindi": "hi",
    "Telugu (తెలుగు)": "te",
    "Tamil (தமிழ்)": "ta",
    "Kannada (ಕನ್ನಡ)": "kn",
    "Malayalam (മലയാളം)": "ml",
}


def generate_advisory(predicted_price: float, risk_probability: float, crop_type: str, language: str = "English") -> str:
    """
    Generates a fully localized farmer advisory.
    Uses pre-translated templates with native-script crop names.
    Falls back to GoogleTranslator for any template miss.
    """
    # Resolve template dict (fall back to English if key not found)
    lang_dict = TEMPLATES.get(language, TEMPLATES["English"])

    # Get native crop name for this language
    crop_map = CROP_NAMES.get(language, CROP_NAMES["English"])
    native_crop = crop_map.get(crop_type, crop_type)  # fallback: keep English if crop unknown

    advisory_parts = []

    # 1. Risk tier
    if risk_probability >= 0.7:
        advisory_parts.append(lang_dict["high"].format(crop=native_crop))
    elif risk_probability >= 0.3:
        advisory_parts.append(lang_dict["moderate"].format(crop=native_crop))
    else:
        advisory_parts.append(lang_dict["favorable"].format(crop=native_crop))

    # 2. Market price
    advisory_parts.append(lang_dict["price"].format(crop=native_crop, price=f"{predicted_price:.2f}"))

    result = " ".join(advisory_parts)

    # 3. Fallback: if a language key existed but content is somehow English, translate via Google
    if language not in TEMPLATES and language in LANG_TO_ISO:
        try:
            result = GoogleTranslator(source='en', target=LANG_TO_ISO[language]).translate(result)
        except Exception:
            pass

    return result


if __name__ == "__main__":
    for lang in TEMPLATES:
        print(f"[{lang}]: {generate_advisory(2155.80, 0.85, 'Rice', lang)}")
