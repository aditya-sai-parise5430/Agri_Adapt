import React from 'react';
import Dashboard from './components/Dashboard';

function App() {
    return (
        <div className="app-container">
            <header>
                <h1>AgriAdapt+</h1>
                <div style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
                    Intelligence Advisory System
                </div>
            </header>

            <main>
                <Dashboard />
            </main>
        </div>
    );
}

export default App;
