import pandas as pd
import numpy as np
from typing import List, Dict, Tuple
from datetime import datetime, timedelta

class Backtest:
    def __init__(self, initial_capital: float = 10000.0):
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.positions = []
        self.trades = []
        
    def run(self, data: pd.DataFrame, signals: pd.DataFrame) -> Dict:
        """
        Esegue il backtest sui dati storici utilizzando i segnali forniti
        
        Args:
            data: DataFrame con i dati storici (OHLCV)
            signals: DataFrame con i segnali di trading
            
        Returns:
            Dict con i risultati del backtest
        """
        results = []
        position = 0
        
        for i in range(len(data)):
            if i < len(signals):
                signal = signals.iloc[i]['signal']
                
                if signal == 1 and position <= 0:  # Segnale di acquisto
                    position = 1
                    entry_price = data.iloc[i]['close']
                    self.trades.append({
                        'type': 'buy',
                        'price': entry_price,
                        'timestamp': data.index[i]
                    })
                    
                elif signal == -1 and position >= 0:  # Segnale di vendita
                    position = -1
                    entry_price = data.iloc[i]['close']
                    self.trades.append({
                        'type': 'sell',
                        'price': entry_price,
                        'timestamp': data.index[i]
                    })
            
            # Calcola il P&L giornaliero
            daily_return = (data.iloc[i]['close'] - data.iloc[i-1]['close']) / data.iloc[i-1]['close']
            position_return = position * daily_return
            
            results.append({
                'timestamp': data.index[i],
                'position': position,
                'return': position_return,
                'cumulative_return': (1 + position_return).cumprod()
            })
        
        results_df = pd.DataFrame(results)
        
        # Calcola le metriche di performance
        total_return = (results_df['cumulative_return'].iloc[-1] - 1) * 100
        sharpe_ratio = np.sqrt(252) * results_df['return'].mean() / results_df['return'].std()
        max_drawdown = self._calculate_max_drawdown(results_df['cumulative_return'])
        
        return {
            'total_return': total_return,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'trades': self.trades,
            'equity_curve': results_df['cumulative_return'].tolist()
        }
    
    def _calculate_max_drawdown(self, cumulative_returns: pd.Series) -> float:
        """Calcola il massimo drawdown"""
        rolling_max = cumulative_returns.expanding().max()
        drawdowns = cumulative_returns / rolling_max - 1
        return drawdowns.min() * 100 