import React, { useState, useRef, useEffect } from 'react';

const PREDICT_API = 'http://127.0.0.1:8000/predict';
const ASK_API = 'http://127.0.0.1:8000/ask';

// ─────────────────────────────────────────────────────────────
// DISTRICT TRANSLATIONS  (value sent to backend stays English)
// ─────────────────────────────────────────────────────────────
const DISTRICTS = {
    'English': ['Pune', 'Nagpur', 'Nashik', 'Aurangabad', 'Kolhapur', 'Andhra Pradesh'],
    'Hindi': ['पुणे', 'नागपुर', 'नासिक', 'औरंगाबाद', 'कोल्हापुर', 'आंध्र प्रदेश'],
    'Telugu (\u0c24\u0c46\u0c32\u0c41\u0c17\u0c41)': ['\u0c2a\u0c41\u0c23\u0c47', '\u0c28\u0c3e\u0c17\u0c4d\u0c2a\u0c42\u0c30\u0c4d', '\u0c28\u0c3e\u0c38\u0c3f\u0c15\u0c4d', '\u0c14\u0c30\u0c02\u0c17\u0c3e\u0c2c\u0c3e\u0c26\u0c4d', '\u0c15\u0c4a\u0c32\u0c4d\u0c39\u0c3e\u0c2a\u0c42\u0c30\u0c4d', '\u0c06\u0c02\u0c27\u0c4d\u0c30\u0c2a\u0c4d\u0c30\u0c26\u0c47\u0c36\u0c4d'],
    'Tamil (\u0ba4\u0bae\u0bbf\u0bb4\u0bcd)': ['\u0baa\u0bc1\u0ba3\u0bc7', '\u0ba8\u0bbe\u0b95\u0bcd\u0baa\u0bc2\u0bb0\u0bcd', '\u0ba8\u0bbe\u0b9a\u0bbf\u0b95\u0bcd', '\u0b94\u0bb0\u0b99\u0bcd\u0b95\u0bbe\u0baa\u0bbe\u0ba4\u0bcd', '\u0b95\u0bca\u0bb2\u0bcd\u0bb9\u0bbe\u0baa\u0bc2\u0bb0\u0bcd', '\u0b86\u0ba8\u0bcd\u0ba4\u0bbf\u0bb0 \u0baa\u0bbf\u0bb0\u0ba4\u0bc7\u0b9a\u0bae\u0bcd'],
    'Kannada (\u0c95\u0ca8\u0ccd\u0ca8\u0ca1)': ['\u0caa\u0cc1\u0ca3\u0cc6', '\u0ca8\u0bbe\u0c97\u0ccd\u0caa\u0cc2\u0cb0\u0ccd', '\u0ca8\u0abe\u0cb8\u0cbf\u0c95\u0ccd', '\u0c94\u0cb0\u0c82\u0c97\u0abe\u0cac\u0abe\u0ca6\u0ccd', '\u0c95\u0cca\u0cb2\u0ccd\u0cb9\u0abe\u0caa\u0cc1\u0cb0', '\u0c86\u0c82\u0ca7\u0ccd\u0cb0 \u0caa\u0ccd\u0cb0\u0ca6\u0cc7\u0cb6'],
    'Malayalam (\u0d2e\u0d32\u0d2f\u0d3e\u0d33\u0d02)': ['\u0d2a\u0d42\u0d28\u0d46', '\u0d28\u0d3e\u0d17\u0d4d\u0d2a\u0d42\u0d7c', '\u0d28\u0d3e\u0d38\u0d3f\u0d15\u0d4d', '\u0d14\u0d30\u0d02\u0d17\u0d2c\u0d3e\u0d26\u0d4d', '\u0d15\u0d4a\u0d7d\u0d39\u0d3e\u0d2a\u0d42\u0d7c', '\u0d06\u0d28\u0d4d\u0d27\u0d4d\u0d30\u0d3e \u0d2a\u0d4d\u0d30\u0d26\u0d47\u0d36\u0d4d'],
};
const DISTRICT_KEYS = ['Pune', 'Nagpur', 'Nashik', 'Aurangabad', 'Kolhapur', 'Andhra Pradesh'];

// ─────────────────────────────────────────────────────────────
// CROP TRANSLATIONS  (value sent to backend stays English)
// ─────────────────────────────────────────────────────────────
const CROPS = {
    'English': ['Wheat', 'Rice', 'Cotton', 'Soybean', 'Maize'],
    'Hindi': ['\u0917\u0947\u0939\u0942\u0901', '\u091a\u093e\u0935\u0932', '\u0915\u092a\u093e\u0938', '\u0938\u094b\u092f\u093e\u092c\u0940\u0928', '\u092e\u0915\u094d\u0915\u093e'],
    'Telugu (\u0c24\u0c46\u0c32\u0c41\u0c17\u0c41)': ['\u0c17\u0c4b\u0c27\u0c41\u0c2e', '\u0c35\u0c30\u0c3f', '\u0c2a\u0c24\u0c4d\u0c24\u0c3f', '\u0c38\u0c4b\u0c2f\u0c3e\u0c2c\u0c40\u0c28\u0c4d', '\u0c2e\u0c4a\u0c15\u0c4d\u0c15\u0c1c\u0c4a\u0c28\u0c4d\u0c28'],
    'Tamil (\u0ba4\u0bae\u0bbf\u0bb4\u0bcd)': ['\u0b95\u0bcb\u0ba4\u0bc1\u0bae\u0bc8', '\u0b85\u0bb0\u0bbf\u0b9a\u0bbf', '\u0baa\u0bb0\u0bc1\u0ba4\u0bcd\u0ba4\u0bbf', '\u0b9a\u0bcb\u0baf\u0bbe\u0baa\u0bc0\u0ba9\u0bcd', '\u0bae\u0b95\u0bcd\u0b95\u0bbe\u0b9a\u0bcd\u0b9a\u0bcb\u0bb3\u0bae\u0bcd'],
    'Kannada (\u0c95\u0ca8\u0ccd\u0ca8\u0ca1)': ['\u0c97\u0ccb\u0ca7\u0cbf', '\u0c85\u0c95\u0ccd\u0c95\u0cbf', '\u0cb9\u0ca4\u0ccd\u0ca4\u0cbf', '\u0cb8\u0ccb\u0caf\u0abe\u0cac\u0cc0\u0ca8\u0ccd', '\u0cae\u0cc6\u0c95\u0ccd\u0c95\u0cc6 \u0c9c\u0ccb\u0cb3'],
    'Malayalam (\u0d2e\u0d32\u0d2f\u0d3e\u0d33\u0d02)': ['\u0d17\u0d4b\u0d24\u0d2e\u0d4d\u0d2a\u0d4d', '\u0d05\u0d30\u0d3f', '\u0d2a\u0d30\u0d41\u0d24\u0d4d\u0d24\u0d3f', '\u0d38\u0d4b\u0d2f\u0d3e\u0d2c\u0d40\u0d7b', '\u0d1a\u0d4b\u0d33\u0d02'],
};
const CROP_KEYS = ['Wheat', 'Rice', 'Cotton', 'Soybean', 'Maize'];

// ─────────────────────────────────────────────────────────────
// FULL UI TRANSLATION TABLE  (all 6 languages)
// ─────────────────────────────────────────────────────────────
const UI = {
    'English': {
        parameters: '⚙️ Parameters',
        preferredLanguage: 'Preferred Language',
        district: 'District',
        cropType: 'Crop Type',
        rainfall: 'Rainfall (mm)',
        temperature: 'Temperature (°C)',
        humidity: 'Humidity (%)',
        generateForecast: 'Generate Forecast',
        priceForecast: 'Price Forecast',
        perQuintal: 'per quintal',
        droughtRisk: 'Drought Risk',
        highAlert: '⚠️ HIGH ALERT',
        stable: '✅ STABLE',
        expertAdvisory: 'Expert Advisory',
        chatPlaceholder: 'Ask about subsidies, crop rotation, prices…',
        welcome: '👋 Welcome to AgriAdapt+! Ask me about crop prices, drought risk, subsidies, or farming techniques.',
        loading: 'Analysing…',
    },
    'Hindi': {
        parameters: '⚙️ मापदंड',
        preferredLanguage: 'पसंदीदा भाषा',
        district: 'जिला',
        cropType: 'फसल का प्रकार',
        rainfall: 'वर्षा (मिमी)',
        temperature: 'तापमान (°C)',
        humidity: 'आर्द्रता (%)',
        generateForecast: 'पूर्वानुमान करें',
        priceForecast: 'मूल्य पूर्वानुमान',
        perQuintal: 'प्रति क्विंटल',
        droughtRisk: 'सूखे का जोखिम',
        highAlert: '⚠️ उच्च चेतावनी',
        stable: '✅ स्थिर',
        expertAdvisory: 'विशेषज्ञ परामर्श',
        chatPlaceholder: 'सब्सिडी, फसल चक्र, कीमतों के बारे में पूछें…',
        welcome: '👋 AgriAdapt+ में आपका स्वागत है! फसल मूल्य, सूखा जोखिम, सब्सिडी या कृषि तकनीकों के बारे में पूछें।',
        loading: 'विश्लेषण हो रहा है…',
    },
    'Telugu (తెలుగు)': {
        parameters: '⚙️ పారామీటర్లు',
        preferredLanguage: 'ఇష్టమైన భాష',
        district: 'జిల్లా',
        cropType: 'పంట రకం',
        rainfall: 'వర్షపాతం (మిమీ)',
        temperature: 'ఉష్ణోగ్రత (°C)',
        humidity: 'తేమ (%)',
        generateForecast: 'సూచన రూపొందించు',
        priceForecast: 'ధర సూచన',
        perQuintal: 'క్వింటాలుకు',
        droughtRisk: 'కరువు ప్రమాదం',
        highAlert: '⚠️ అధిక హెచ్చరిక',
        stable: '✅ స్థిరంగా ఉంది',
        expertAdvisory: 'నిపుణుల సలహా',
        chatPlaceholder: 'సబ్సిడీలు, పంట మార్పిడి, ధరల గురించి అడగండి…',
        welcome: '👋 AgriAdapt+ కి స్వాగతం! పంట ధరలు, కరువు ప్రమాదం, సబ్సిడీలు లేదా వ్యవసాయ పద్ధతుల గురించి అడగండి.',
        loading: 'విశ్లేషిస్తోంది…',
    },
    'Tamil (தமிழ்)': {
        parameters: '⚙️ அளவுருக்கள்',
        preferredLanguage: 'விருப்பமான மொழி',
        district: 'மாவட்டம்',
        cropType: 'பயிர் வகை',
        rainfall: 'மழைப்பொழிவு (மி.மீ)',
        temperature: 'வெப்பநிலை (°C)',
        humidity: 'ஈரப்பதம் (%)',
        generateForecast: 'முன்னறிவிப்பை உருவாக்கு',
        priceForecast: 'விலை முன்னறிவிப்பு',
        perQuintal: 'குவிண்டாலுக்கு',
        droughtRisk: 'வறட்சி அபாயம்',
        highAlert: '⚠️ அதிக எச்சரிக்கை',
        stable: '✅ நிலையான நிலை',
        expertAdvisory: 'நிபுணர் ஆலோசனை',
        chatPlaceholder: 'மானியங்கள், பயிர் சுழற்சி, விலைகள் பற்றி கேளுங்கள்…',
        welcome: '👋 AgriAdapt+ இல் வரவேற்கிறோம்! பயிர் விலைகள், வறட்சி அபாயம், மானியங்கள் அல்லது விவசாய நுட்பங்களைப் பற்றி கேளுங்கள்.',
        loading: 'பகுப்பாய்வு செய்கிறது…',
    },
    'Kannada (ಕನ್ನಡ)': {
        parameters: '⚙️ ನಿಯತಾಂಕಗಳು',
        preferredLanguage: 'ಆದ್ಯತೆಯ ಭಾಷೆ',
        district: 'ಜಿಲ್ಲೆ',
        cropType: 'ಬೆಳೆ ವಿಧ',
        rainfall: 'ಮಳೆ (ಮಿಮೀ)',
        temperature: 'ತಾಪಮಾನ (°C)',
        humidity: 'ಆರ್ದ್ರತೆ (%)',
        generateForecast: 'ಮುನ್ಸೂಚನೆ ರಚಿಸಿ',
        priceForecast: 'ಬೆಲೆ ಮುನ್ಸೂಚನೆ',
        perQuintal: 'ಕ್ವಿಂಟಾಲಿಗೆ',
        droughtRisk: 'ಬರ ಅಪಾಯ',
        highAlert: '⚠️ ಹೆಚ್ಚಿನ ಎಚ್ಚರಿಕೆ',
        stable: '✅ ಸ್ಥಿರ',
        expertAdvisory: 'ತಜ್ಞರ ಸಲಹೆ',
        chatPlaceholder: 'ಸಹಾಯಧನ, ಬೆಳೆ ತಿರುಗುವಿಕೆ, ಬೆಲೆಗಳ ಬಗ್ಗೆ ಕೇಳಿ…',
        welcome: '👋 AgriAdapt+ ಗೆ ಸ್ವಾಗತ! ಬೆಳೆ ಬೆಲೆಗಳು, ಬರ ಅಪಾಯ, ಸಹಾಯಧನ ಅಥವಾ ಕೃಷಿ ತಂತ್ರಗಳ ಬಗ್ಗೆ ಕೇಳಿ.',
        loading: 'ವಿಶ್ಲೇಷಿಸಲಾಗುತ್ತಿದೆ…',
    },
    'Malayalam (മലയാളം)': {
        parameters: '⚙️ പാരാമീറ്ററുകൾ',
        preferredLanguage: 'ഇഷ്ടഭാഷ',
        district: 'ജില്ല',
        cropType: 'വിള തരം',
        rainfall: 'മഴ (മി.മീ)',
        temperature: 'താപനില (°C)',
        humidity: 'ഈർപ്പം (%)',
        generateForecast: 'പ്രവചനം ഉണ്ടാക്കുക',
        priceForecast: 'വില പ്രവചനം',
        perQuintal: 'ക്വിന്റലിന്',
        droughtRisk: 'വരൾച്ചാ അപകടസാധ്യത',
        highAlert: '⚠️ ഉയർന്ന മുന്നറിയിപ്പ്',
        stable: '✅ സ്ഥിരം',
        expertAdvisory: 'വിദഗ്ധ ഉപദേശം',
        chatPlaceholder: 'സബ്‌സിഡി, വിള ഭ്രമണം, വിലകൾ എന്നിവ ചോദിക്കൂ…',
        welcome: '👋 AgriAdapt+ ലേക്ക് സ്വാഗതം! വിള വിലകൾ, വരൾച്ചാ അപകടസാധ്യത, സബ്‌സിഡികൾ അല്ലെങ്കിൽ കൃഷി സാങ്കേതിക വിദ്യകളെക്കുറിച്ച് ചോദിക്കൂ.',
        loading: 'വിശകലനം ചെയ്യുന്നു…',
    },
};

export default function Dashboard() {
    // --- State for Controls ---
    const [language, setLanguage] = useState('English');
    const [district, setDistrict] = useState('Pune');
    const [crop, setCrop] = useState('Wheat');
    const [weather, setWeather] = useState({ rainfall: 2.5, temperature: 28.0, humidity: 65 });
    const [loadingWeather, setLoadingWeather] = useState(false);

    // Shorthand: current language strings
    const t = UI[language] || UI['English'];

    // --- Auto-fetch weather when district changes ---
    useEffect(() => {
        const fetchWeather = async () => {
            setLoadingWeather(true);
            try {
                const resp = await fetch(`http://127.0.0.1:8000/weather/${district}`);
                if (resp.ok) setWeather(await resp.json());
            } catch (err) {
                console.error('Failed to fetch live weather:', err);
            } finally {
                setLoadingWeather(false);
            }
        };
        fetchWeather();
    }, [district]);

    // --- State for Prediction Results ---
    const [prediction, setPrediction] = useState(null);
    const [loadingPredict, setLoadingPredict] = useState(false);

    // --- Chat state ---
    const [messages, setMessages] = useState([{ id: 1, sender: 'bot', text: UI['English'].welcome, suggested_followups: ["Latest crop prices?", "Drought risk here?", "Government subsidies?"] }]);
    const [chatInput, setChatInput] = useState('');
    const [loadingChat, setLoadingChat] = useState(false);
    const messagesEndRef = useRef(null);

    // Update welcome message + clear prediction card when language changes
    useEffect(() => {
        setMessages(prev => {
            const updated = [...prev];
            updated[0] = {
                ...updated[0],
                text: (UI[language] || UI['English']).welcome,
                // We don't translate the hardcoded initial chips perfectly here yet, but the user can still click them.
                // Ideally they would be in the UI dict, let's just clear them to encourage natural flow, or let backend fetch new ones.
                suggested_followups: []
            };
            return updated;
        });
    }, [language]);

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    // --- Handlers ---
    const sendChatMessage = async (userText) => {
        if (!userText.trim()) return;
        setMessages(prev => [...prev, { id: Date.now(), sender: 'user', text: userText }]);
        setChatInput('');
        setLoadingChat(true);
        try {
            const resp = await fetch(ASK_API, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    query: userText,
                    language,
                    context: { district, crop_type: crop, rainfall: weather.rainfall, temperature: weather.temperature, humidity: weather.humidity },
                }),
            });
            if (!resp.ok) throw new Error('Ask API Error');
            const data = await resp.json();
            setMessages(prev => [...prev, {
                id: Date.now() + 1,
                sender: 'bot',
                text: data.advisory,
                suggested_followups: data.suggested_followups || []
            }]);

            if (data.predicted_price != null || data.risk_score != null) {
                setPrediction({
                    predicted_price: data.predicted_price ?? (prediction?.predicted_price ?? 0),
                    risk_probability: data.risk_score ?? (prediction?.risk_probability ?? 0),
                    risk_classification: (data.risk_score >= 0.7) ? 1 : 0,
                    advisory: data.advisory,
                });
            }
        } catch {
            setMessages(prev => [...prev, { id: Date.now() + 1, sender: 'bot', text: '⚠️ System offline. Please ensure the backend is running.' }]);
        } finally {
            setLoadingChat(false);
        }
    };

    const handlePredict = async () => {
        setLoadingPredict(true);
        try {
            const payload = {
                rainfall: weather.rainfall,
                temperature: weather.temperature,
                humidity: weather.humidity,
                district,
                crop_type: crop,
                language,
            };
            const resp = await fetch(PREDICT_API, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
            });
            if (!resp.ok) throw new Error('Prediction API Error');
            const data = await resp.json();
            setPrediction(data);
            // Advisory is already in the selected language from the backend
            setMessages(prev => [...prev, { id: Date.now(), sender: 'bot', text: data.advisory }]);
        } catch (err) {
            console.error(err);
            setMessages(prev => [...prev, { id: Date.now(), sender: 'bot', text: '⚠️ Failed to fetch prediction. Is the backend running?' }]);
        } finally {
            setLoadingPredict(false);
        }
    };

    const handleChatSend = (e) => {
        e.preventDefault();
        sendChatMessage(chatInput);
    };

    const handleChipClick = (chipText) => {
        sendChatMessage(chipText);
    };

    const renderText = (text) =>
        text.split('\n').map((line, i) => {
            const parts = line.split(/(\*\*.*?\*\*)/g).map((part, idx) =>
                part.startsWith('**') && part.endsWith('**')
                    ? <strong key={idx} style={{ color: 'var(--accent-color)' }}>{part.slice(2, -2)}</strong>
                    : part
            );
            return <React.Fragment key={i}>{parts}<br /></React.Fragment>;
        });

    return (
        <div className="dashboard-grid">
            {/* ── LEFT PANEL ── */}
            <div className="glass-panel">
                <h2 style={{ marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    {t.parameters}
                </h2>

                <div className="input-group">
                    <label>{t.preferredLanguage}</label>
                    <select value={language} onChange={(e) => setLanguage(e.target.value)}>
                        <option value="English">English</option>
                        <option value="Hindi">Hindi (हिंदी)</option>
                        <option value="Telugu (తెలుగు)">Telugu (తెలుగు)</option>
                        <option value="Tamil (தமிழ்)">Tamil (தமிழ்)</option>
                        <option value="Kannada (ಕನ್ನಡ)">Kannada (ಕನ್ನಡ)</option>
                        <option value="Malayalam (മലയാളം)">Malayalam (മലയാളം)</option>
                    </select>
                </div>

                <div className="input-group">
                    <label>{t.district}</label>
                    <select value={district} onChange={(e) => setDistrict(e.target.value)}>
                        {DISTRICT_KEYS.map((key, i) => (
                            <option key={key} value={key}>
                                {(DISTRICTS[language] || DISTRICTS['English'])[i]}
                            </option>
                        ))}
                    </select>
                </div>

                <div className="input-group">
                    <label>{t.cropType}</label>
                    <select value={crop} onChange={(e) => setCrop(e.target.value)}>
                        {CROP_KEYS.map((key, i) => (
                            <option key={key} value={key}>
                                {(CROPS[language] || CROPS['English'])[i]}
                            </option>
                        ))}
                    </select>
                </div>

                <div className="input-group">
                    <label>{t.rainfall}: {weather.rainfall.toFixed(1)}</label>
                    <input type="range" min="0" max="50" step="0.1"
                        value={weather.rainfall}
                        onChange={(e) => setWeather({ ...weather, rainfall: parseFloat(e.target.value) })}
                    />
                </div>

                <div className="input-group">
                    <label>{t.temperature}: {weather.temperature.toFixed(1)}</label>
                    <input type="range" min="10" max="50" step="0.5"
                        value={weather.temperature}
                        onChange={(e) => setWeather({ ...weather, temperature: parseFloat(e.target.value) })}
                    />
                </div>

                <div className="input-group">
                    <label>{t.humidity}: {weather.humidity}</label>
                    <input type="range" min="10" max="100"
                        value={weather.humidity}
                        onChange={(e) => setWeather({ ...weather, humidity: parseInt(e.target.value) })}
                    />
                </div>

                <button className="btn-primary" onClick={handlePredict} disabled={loadingPredict}>
                    {loadingPredict ? <span className="loading-spinner" /> : t.generateForecast}
                </button>
            </div>

            {/* ── RIGHT PANEL ── */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>

                {/* Prediction Cards */}
                {prediction && (
                    <div className="glass-panel" style={{ padding: '1.5rem' }}>
                        <div className="results-container">
                            <div className="result-card">
                                <h3>{t.priceForecast}</h3>
                                <div className="value">₹{prediction.predicted_price.toFixed(2)}</div>
                                <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>{t.perQuintal}</div>
                            </div>
                            <div className={`result-card ${prediction.risk_classification === 1 ? 'danger' : ''}`}>
                                <h3>{t.droughtRisk}</h3>
                                <div className="value">{(prediction.risk_probability * 100).toFixed(1)}%</div>
                                <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                                    {prediction.risk_classification === 1 ? t.highAlert : t.stable}
                                </div>
                            </div>
                        </div>
                        <div className="advisory-box">
                            <strong>{t.expertAdvisory}:</strong><br />
                            {prediction.advisory}
                        </div>
                    </div>
                )}

                {/* Chat Terminal */}
                <div className="glass-panel" style={{ padding: 0, overflow: 'hidden', height: '500px', display: 'flex', flexDirection: 'column' }}>
                    <div className="chat-history">
                        {messages.map((msg, index) => (
                            <React.Fragment key={msg.id}>
                                <div className={`message ${msg.sender}`}>
                                    {msg.sender === 'bot' && <div className="bot-avatar">AI</div>}
                                    <div className="msg-content">{renderText(msg.text)}</div>
                                </div>
                                {/* Render suggestion chips if they exist for this message */}
                                {msg.suggested_followups && msg.suggested_followups.length > 0 && index === messages.length - 1 && (
                                    <div className="suggestion-chips" style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', marginLeft: '3rem', marginBottom: '1rem' }}>
                                        {msg.suggested_followups.map((chip, idx) => (
                                            <button
                                                key={idx}
                                                onClick={() => handleChipClick(chip)}
                                                style={{
                                                    background: 'rgba(56, 189, 248, 0.15)',
                                                    border: '1px solid rgba(56, 189, 248, 0.4)',
                                                    color: 'var(--accent-color)',
                                                    padding: '6px 14px',
                                                    borderRadius: '20px',
                                                    fontSize: '0.85rem',
                                                    cursor: 'pointer',
                                                    transition: 'all 0.2s ease',
                                                    whiteSpace: 'nowrap'
                                                }}
                                                onMouseOver={(e) => { e.target.style.background = 'rgba(56, 189, 248, 0.3)'; }}
                                                onMouseOut={(e) => { e.target.style.background = 'rgba(56, 189, 248, 0.15)'; }}
                                            >
                                                {chip}
                                            </button>
                                        ))}
                                    </div>
                                )}
                            </React.Fragment>
                        ))}
                        {loadingChat && (
                            <div className="message bot typing">
                                <div className="bot-avatar">AI</div>
                                <div className="msg-content">
                                    <span className="dot" /><span className="dot" /><span className="dot" />
                                </div>
                            </div>
                        )}
                        <div ref={messagesEndRef} />
                    </div>

                    <div className="chat-input-wrapper" style={{ padding: '1rem' }}>
                        <form onSubmit={handleChatSend} className="chat-input-area">
                            <input
                                type="text"
                                className="chat-input"
                                value={chatInput}
                                onChange={(e) => setChatInput(e.target.value)}
                                placeholder={t.chatPlaceholder}
                            />
                            <button type="submit" className="send-btn" style={{ width: '45px', height: '45px' }}
                                disabled={loadingChat || !chatInput.trim()}>
                                <svg viewBox="0 0 24 24" fill="none" width="20" height="20" stroke="currentColor" strokeWidth="2">
                                    <path strokeLinecap="round" strokeLinejoin="round" d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z" />
                                </svg>
                            </button>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    );
}
