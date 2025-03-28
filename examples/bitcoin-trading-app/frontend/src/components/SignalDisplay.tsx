import React from 'react';
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

interface Signal {
  timestamp: string;
  price: number;
  signal: number;
  indicator_value: number;
}

interface Props {
  signals: Signal[];
}

const SignalDisplay: React.FC<Props> = ({ signals }) => {
  return (
    <div>
      <h2 className="card">Segnali di Trading</h2>
      
      <div className="card">
        <h3>Grafico dei Segnali</h3>
        <div style={{ height: '400px' }}>
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={signals}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="timestamp" />
              <YAxis yAxisId="left" />
              <YAxis yAxisId="right" orientation="right" />
              <Tooltip />
              <Legend />
              <Line
                yAxisId="left"
                type="monotone"
                dataKey="price"
                stroke="#8884d8"
                name="Prezzo"
              />
              <Line
                yAxisId="right"
                type="monotone"
                dataKey="indicator_value"
                stroke="#82ca9d"
                name="Indicatore"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="card">
        <h3>Ultimi Segnali</h3>
        <div className="table-container">
          <table className="table">
            <thead>
              <tr>
                <th>Data</th>
                <th>Prezzo</th>
                <th>Segnale</th>
                <th>Valore Indicatore</th>
              </tr>
            </thead>
            <tbody>
              {signals.slice(-5).map((signal, index) => (
                <tr key={index}>
                  <td>{new Date(signal.timestamp).toLocaleDateString()}</td>
                  <td>{signal.price.toFixed(2)}</td>
                  <td className={
                    signal.signal === 1 ? 'text-green' : 
                    signal.signal === -1 ? 'text-red' : 
                    'text-gray'
                  }>
                    {signal.signal === 1 ? 'Acquista' : 
                     signal.signal === -1 ? 'Vendi' : 
                     'Neutrale'}
                  </td>
                  <td>{signal.indicator_value.toFixed(2)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default SignalDisplay; 