import React, { useState, useEffect, useCallback } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';

interface BacktestResult {
  total_return: number;
  sharpe_ratio: number;
  max_drawdown: number;
  trades: Array<{
    type: 'buy' | 'sell';
    price: number;
    timestamp: string;
  }>;
  equity_curve: number[];
}

interface Props {
  historicalData: any[];
  signals: any[];
}

const BacktestResults: React.FC<Props> = ({ historicalData, signals }) => {
  const [results, setResults] = useState<BacktestResult | null>(null);
  const [loading, setLoading] = useState(false);

  const runBacktest = useCallback(async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/backtest', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          historical_data: historicalData,
          signals: signals,
        }),
      });
      const data = await response.json();
      setResults(data);
    } catch (error) {
      console.error('Errore durante il backtest:', error);
    } finally {
      setLoading(false);
    }
  }, [historicalData, signals]);

  useEffect(() => {
    if (historicalData.length > 0 && signals.length > 0) {
      runBacktest();
    }
  }, [historicalData, signals, runBacktest]);

  if (loading) {
    return <div className="card">Caricamento risultati del backtest...</div>;
  }

  if (!results) {
    return <div className="card">Nessun risultato disponibile</div>;
  }

  return (
    <div>
      <h2 className="card">Risultati del Backtest</h2>
      
      <div className="grid">
        <div className="card">
          <h3>Rendimento Totale</h3>
          <p className={results.total_return >= 0 ? 'text-green' : 'text-red'}>
            {results.total_return.toFixed(2)}%
          </p>
        </div>
        <div className="card">
          <h3>Sharpe Ratio</h3>
          <p>{results.sharpe_ratio.toFixed(2)}</p>
        </div>
        <div className="card">
          <h3>Max Drawdown</h3>
          <p className="text-red">{results.max_drawdown.toFixed(2)}%</p>
        </div>
      </div>

      <div className="card">
        <h3>Curva di Equity</h3>
        <div style={{ height: '400px' }}>
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={results.equity_curve.map((value, index) => ({
              time: index,
              value: value
            }))}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="time" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="value" stroke="#8884d8" name="Equity" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="card">
        <h3>Ultimi Trade</h3>
        <div className="table-container">
          <table className="table">
            <thead>
              <tr>
                <th>Data</th>
                <th>Tipo</th>
                <th>Prezzo</th>
              </tr>
            </thead>
            <tbody>
              {results.trades.slice(-5).map((trade, index) => (
                <tr key={index}>
                  <td>{new Date(trade.timestamp).toLocaleDateString()}</td>
                  <td className={trade.type === 'buy' ? 'text-green' : 'text-red'}>
                    {trade.type === 'buy' ? 'Acquisto' : 'Vendita'}
                  </td>
                  <td>{trade.price.toFixed(2)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default BacktestResults; 