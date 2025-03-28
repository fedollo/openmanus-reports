import React, { useState, useEffect } from 'react';
import SignalDisplay from './components/SignalDisplay';
import BacktestResults from './components/BacktestResults';

const App: React.FC = () => {
  const [signals, setSignals] = useState<any[]>([]);
  const [historicalData, setHistoricalData] = useState<any[]>([]);

  useEffect(() => {
    // Qui implementeremo la logica per ottenere i dati in tempo reale
    // Per ora usiamo dati di esempio
    const mockSignals = [
      {
        timestamp: '2024-03-27T10:00:00Z',
        price: 50000,
        signal: 1,
        indicator_value: 0.8
      },
      {
        timestamp: '2024-03-27T11:00:00Z',
        price: 51000,
        signal: -1,
        indicator_value: 0.2
      }
    ];

    const mockHistoricalData = [
      {
        timestamp: '2024-03-27T10:00:00Z',
        open: 50000,
        high: 51000,
        low: 49000,
        close: 51000,
        volume: 100
      },
      {
        timestamp: '2024-03-27T11:00:00Z',
        open: 51000,
        high: 52000,
        low: 50000,
        close: 50000,
        volume: 150
      }
    ];

    setSignals(mockSignals);
    setHistoricalData(mockHistoricalData);
  }, []);

  return (
    <div>
      <header className="header">
        <div className="container">
          <h1>Bitcoin Trading App</h1>
        </div>
      </header>
      <main className="container">
        <SignalDisplay signals={signals} />
        <BacktestResults historicalData={historicalData} signals={signals} />
      </main>
    </div>
  );
};

export default App; 