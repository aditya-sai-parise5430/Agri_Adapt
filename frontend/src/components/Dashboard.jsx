import React, { useState, useRef, useEffect } from 'react';

const API_URL = 'http://127.0.0.1:8000/predict';

export default function Dashboard() {
    const [messages, setMessages] = useState([
        {
            id: 1,
            sender: 'bot',
            text: '👋 Hello! I am the AgriAdapt+ AI Assistant. \n\nI can answer questions about **Crop Price Forecasts** and **Climate Risk**. \n\nTry asking: "What is the forecast for Wheat in Pune?" or "Any drought risks for Soybean in Nagpur?"'
        }
    ]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    // NLP-lite entity extraction using heuristics
    const parseInput = (text) => {
        const textLower = text.toLowerCase();

        const cropsAvailable = ['wheat', 'rice', 'cotton', 'soybean', 'maize'];
        const districtsAvailable = ['pune', 'nagpur', 'nashik', 'aurangabad', 'kolhapur', 'andhra']; // Added 'andhra'

        let selectedCrop = 'Wheat'; // default fallback
        let selectedDistrict = 'Pune'; // default fallback

        cropsAvailable.forEach(c => {
            if (textLower.includes(c)) selectedCrop = c.charAt(0).toUpperCase() + c.slice(1);
        });

        districtsAvailable.forEach(d => {
            if (textLower.includes(d)) {
                selectedDistrict = d.charAt(0).toUpperCase() + d.slice(1);
                // Specifically map "andhra" to "Andhra Pradesh" for rendering
                if (d === 'andhra') selectedDistrict = 'Andhra Pradesh';
            }
        });

        // Determine slight variability in weather based on district for realism
        let baseTemp = 25.0;
        let baseRain = 1.0;

        if (selectedDistrict === 'Nagpur') { baseTemp = 32.5; baseRain = 0.2; }
        if (selectedDistrict === 'Nashik') { baseTemp = 22.0; baseRain = 2.5; }

        return {
            rainfall: baseRain,
            temperature: baseTemp,
            humidity: 60,
            district: selectedDistrict,
            crop_type: selectedCrop
        };
    };

    const handleSend = async (e) => {
        e.preventDefault();
        if (!input.trim()) return;

        const userMsg = input.trim();
        // Add User message
        setMessages(prev => [...prev, { id: Date.now(), sender: 'user', text: userMsg }]);
        setInput('');
        setLoading(true);

        try {
            const parsedData = parseInput(userMsg);

            // Simulate real-time bot typing delay
            await new Promise(r => setTimeout(r, 600));

            const resp = await fetch(API_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(parsedData)
            });

            if (!resp.ok) {
                throw new Error('API Error');
            }

            const data = await resp.json();

            const riskBadge = data.risk_classification === 1 ? '🚨 HIGH CLIMATE RISK ALERT' : '✅ FAVORABLE CONDITIONS';

            const botMsg = `Based on our intelligence engine for **${parsedData.crop_type}** in **${parsedData.district}**:\n\n` +
                `💰 **Price Forecast:** ₹${data.predicted_price.toFixed(2)} per quintal\n` +
                `🌡️ **Risk Evaluation:** ${riskBadge} (${(data.risk_probability * 100).toFixed(1)}% drought probability)\n\n` +
                `📝 **Expert Advisory:**\n${data.advisory}`;

            setMessages(prev => [...prev, { id: Date.now() + 1, sender: 'bot', text: botMsg }]);
        } catch (err) {
            setMessages(prev => [...prev, { id: Date.now() + 1, sender: 'bot', text: "⚠️ System offline. Please ensure the backend Python API engine is running on port 8000." }]);
        } finally {
            setLoading(false);
        }
    };

    // Convert markdown-style text to HTML for bolding things nicely
    const renderText = (text) => {
        return text.split('\n').map((line, i) => {
            // Very basic markdown parser for bold mapping
            const parts = line.split(/(\*\*.*?\*\*)/g).map((part, index) => {
                if (part.startsWith('**') && part.endsWith('**')) {
                    return <strong key={index} style={{ color: 'var(--accent-color)' }}>{part.slice(2, -2)}</strong>;
                }
                return part;
            });
            return <React.Fragment key={i}>{parts}<br /></React.Fragment>;
        });
    };

    return (
        <div className="glass-panel QA-panel" style={{ padding: 0, overflow: 'hidden', height: '80vh', display: 'flex', flexDirection: 'column' }}>

            {/* Header bar of QA Chat */}
            <div style={{ padding: '1.5rem', borderBottom: '1px solid var(--glass-border)', background: 'rgba(15, 23, 42, 0.7)' }}>
                <h2 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', margin: 0 }}>
                    <span style={{ fontSize: '1.5rem' }}>🤖</span> QA Advisory Terminal
                </h2>
                <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', margin: '0.2rem 0 0 2rem' }}>
                    Ask natural language questions about the agricultural market
                </p>
            </div>

            {/* Chat History */}
            <div className="chat-history">
                {messages.map(msg => (
                    <div key={msg.id} className={`message ${msg.sender}`}>
                        {msg.sender === 'bot' && <div className="bot-avatar">AI</div>}
                        <div className="msg-content">
                            {renderText(msg.text)}
                        </div>
                    </div>
                ))}
                {loading && (
                    <div className="message bot typing">
                        <div className="bot-avatar">AI</div>
                        <div className="msg-content">
                            <span className="dot"></span>
                            <span className="dot"></span>
                            <span className="dot"></span>
                        </div>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="chat-input-wrapper">
                <form onSubmit={handleSend} className="chat-input-area">
                    <input
                        type="text"
                        className="chat-input"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        placeholder="E.g., What is the price of Cotton in Aurangabad?"
                        autoFocus
                    />
                    <button type="submit" className="send-btn" disabled={loading || !input.trim()}>
                        <svg viewBox="0 0 24 24" fill="none" width="24" height="24" stroke="currentColor" strokeWidth="2">
                            <path strokeLinecap="round" strokeLinejoin="round" d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z" />
                        </svg>
                    </button>
                </form>
            </div>
        </div>
    );
}
