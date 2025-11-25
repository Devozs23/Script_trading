"""
Sistema de Backtesting
Prueba la estrategia con datos históricos
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import List, Dict, Optional
import json

from trading_strategy import LevelTradingStrategy, SignalType
import config


class Trade:
    """Representa una operación de trading"""

    def __init__(self, trade_id: int, signal_type: str, entry_time: datetime,
                 entry_price: float, size: int, stop_loss: float, take_profit: float):
        self.trade_id = trade_id
        self.signal_type = signal_type
        self.entry_time = entry_time
        self.entry_price = entry_price
        self.size = size
        self.stop_loss = stop_loss
        self.take_profit = take_profit

        self.exit_time = None
        self.exit_price = None
        self.exit_reason = None
        self.profit_loss = 0.0
        self.profit_loss_percent = 0.0

    def close(self, exit_time: datetime, exit_price: float, reason: str):
        """Cierra la operación"""
        self.exit_time = exit_time
        self.exit_price = exit_price
        self.exit_reason = reason

        # Calcular P&L
        if self.signal_type == 'buy':
            self.profit_loss = (exit_price - self.entry_price) * self.size * config.TICK_VALUE
        else:  # sell
            self.profit_loss = (self.entry_price - exit_price) * self.size * config.TICK_VALUE

        # Aplicar comisión
        commission = abs(self.entry_price * self.size * config.BACKTEST_COMMISSION * 2)  # entrada + salida
        self.profit_loss -= commission

        # Calcular porcentaje
        if self.entry_price > 0:
            self.profit_loss_percent = (self.profit_loss / (self.entry_price * self.size)) * 100

    def to_dict(self) -> Dict:
        """Convierte a diccionario"""
        return {
            'trade_id': self.trade_id,
            'type': self.signal_type,
            'entry_time': str(self.entry_time),
            'entry_price': self.entry_price,
            'exit_time': str(self.exit_time) if self.exit_time else None,
            'exit_price': self.exit_price,
            'size': self.size,
            'stop_loss': self.stop_loss,
            'take_profit': self.take_profit,
            'exit_reason': self.exit_reason,
            'profit_loss': round(self.profit_loss, 2),
            'profit_loss_percent': round(self.profit_loss_percent, 2)
        }


class BacktestEngine:
    """Motor de backtesting"""

    def __init__(self, initial_capital: float = config.INITIAL_CAPITAL):
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.strategy = LevelTradingStrategy()
        self.trades: List[Trade] = []
        self.active_trades: List[Trade] = []
        self.trade_counter = 0

    def run(self, df: pd.DataFrame, verbose: bool = True) -> Dict:
        """
        Ejecuta el backtesting

        Args:
            df: DataFrame con datos OHLCV
            verbose: Mostrar progreso

        Returns:
            Diccionario con resultados
        """
        if verbose:
            print(f"🔄 Iniciando backtesting...")
            print(f"   Período: {df.index[0]} a {df.index[-1]}")
            print(f"   Barras: {len(df)}")
            print(f"   Capital inicial: ${self.initial_capital:,.2f}\n")

        # Iterar sobre cada barra
        for i in range(config.TREND_LOOKBACK_BARS, len(df)):
            current_df = df.iloc[:i+1]
            current_bar = current_df.iloc[-1]
            current_time = current_df.index[-1]

            # 1. Verificar condiciones de salida para trades activos
            self._check_exit_conditions(current_df, current_bar)

            # 2. Buscar nuevas oportunidades de entrada
            if len(self.active_trades) < config.MAX_POSITIONS:
                signal = self.strategy.analyze_entry_opportunity(current_df)

                if signal and signal.signal_type in [SignalType.BUY, SignalType.SELL]:
                    self._open_trade(signal, current_time, current_bar['close'])

            # Mostrar progreso
            if verbose and i % 100 == 0:
                print(f"   Procesando barra {i}/{len(df)} - Trades activos: {len(self.active_trades)}")

        # Cerrar trades restantes al final
        if self.active_trades:
            final_bar = df.iloc[-1]
            final_time = df.index[-1]
            for trade in self.active_trades[:]:
                trade.close(final_time, final_bar['close'], "End of backtest")
                self.current_capital += trade.profit_loss
                self.active_trades.remove(trade)

        # Calcular resultados
        results = self._calculate_results()

        if verbose:
            self._print_results(results)

        return results

    def _open_trade(self, signal, current_time: datetime, current_price: float):
        """Abre una nueva operación"""
        # Calcular tamaño de posición
        position_size = self.strategy.get_position_size(
            self.current_capital,
            current_price,
            signal.stop_loss
        )

        if position_size == 0:
            return

        self.trade_counter += 1

        trade = Trade(
            trade_id=self.trade_counter,
            signal_type=signal.signal_type.value,
            entry_time=current_time,
            entry_price=current_price,
            size=position_size,
            stop_loss=signal.stop_loss,
            take_profit=signal.take_profit
        )

        self.active_trades.append(trade)
        self.trades.append(trade)

    def _check_exit_conditions(self, df: pd.DataFrame, current_bar: pd.Series):
        """Verifica condiciones de salida para trades activos"""
        for trade in self.active_trades[:]:  # Copiar lista para modificar durante iteración
            current_price = current_bar['close']
            current_time = df.index[-1]

            # Verificar Stop Loss
            if trade.signal_type == 'buy':
                if current_bar['low'] <= trade.stop_loss:
                    trade.close(current_time, trade.stop_loss, "Stop Loss")
                    self.current_capital += trade.profit_loss
                    self.active_trades.remove(trade)
                    continue

                # Verificar Take Profit
                if current_bar['high'] >= trade.take_profit:
                    trade.close(current_time, trade.take_profit, "Take Profit")
                    self.current_capital += trade.profit_loss
                    self.active_trades.remove(trade)
                    continue

            else:  # sell
                if current_bar['high'] >= trade.stop_loss:
                    trade.close(current_time, trade.stop_loss, "Stop Loss")
                    self.current_capital += trade.profit_loss
                    self.active_trades.remove(trade)
                    continue

                # Verificar Take Profit
                if current_bar['low'] <= trade.take_profit:
                    trade.close(current_time, trade.take_profit, "Take Profit")
                    self.current_capital += trade.profit_loss
                    self.active_trades.remove(trade)
                    continue

            # Verificar señal de salida por cambio de tendencia
            position_dict = {
                'type': 'long' if trade.signal_type == 'buy' else 'short',
                'stop_loss': trade.stop_loss,
                'take_profit': trade.take_profit
            }

            exit_signal = self.strategy.check_exit_conditions(df, position_dict)

            if exit_signal:
                trade.close(current_time, current_price, "Trend reversal")
                self.current_capital += trade.profit_loss
                self.active_trades.remove(trade)

    def _calculate_results(self) -> Dict:
        """Calcula resultados del backtesting"""
        if not self.trades:
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0.0,
                'total_profit_loss': 0.0,
                'final_capital': self.initial_capital,
                'return_percent': 0.0
            }

        closed_trades = [t for t in self.trades if t.exit_time is not None]

        winning_trades = [t for t in closed_trades if t.profit_loss > 0]
        losing_trades = [t for t in closed_trades if t.profit_loss < 0]

        total_profit = sum(t.profit_loss for t in winning_trades)
        total_loss = sum(abs(t.profit_loss) for t in losing_trades)

        win_rate = len(winning_trades) / len(closed_trades) * 100 if closed_trades else 0

        total_pl = sum(t.profit_loss for t in closed_trades)
        return_percent = (self.current_capital - self.initial_capital) / self.initial_capital * 100

        # Calcular máximo drawdown
        equity_curve = [self.initial_capital]
        running_capital = self.initial_capital

        for trade in closed_trades:
            running_capital += trade.profit_loss
            equity_curve.append(running_capital)

        max_drawdown = self._calculate_max_drawdown(equity_curve)

        # Calcular promedio de ganancia/pérdida
        avg_win = total_profit / len(winning_trades) if winning_trades else 0
        avg_loss = total_loss / len(losing_trades) if losing_trades else 0

        profit_factor = total_profit / total_loss if total_loss > 0 else float('inf')

        return {
            'total_trades': len(closed_trades),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': round(win_rate, 2),
            'total_profit': round(total_profit, 2),
            'total_loss': round(total_loss, 2),
            'total_profit_loss': round(total_pl, 2),
            'avg_win': round(avg_win, 2),
            'avg_loss': round(avg_loss, 2),
            'profit_factor': round(profit_factor, 2),
            'max_drawdown': round(max_drawdown, 2),
            'initial_capital': self.initial_capital,
            'final_capital': round(self.current_capital, 2),
            'return_percent': round(return_percent, 2),
            'equity_curve': equity_curve
        }

    def _calculate_max_drawdown(self, equity_curve: List[float]) -> float:
        """Calcula máximo drawdown"""
        max_dd = 0
        peak = equity_curve[0]

        for value in equity_curve:
            if value > peak:
                peak = value
            dd = (peak - value) / peak * 100 if peak > 0 else 0
            max_dd = max(max_dd, dd)

        return max_dd

    def _print_results(self, results: Dict):
        """Imprime resultados del backtesting"""
        print("\n" + "="*60)
        print("📊 RESULTADOS DEL BACKTESTING")
        print("="*60)

        print(f"\n💼 Capital:")
        print(f"   Inicial:  ${results['initial_capital']:,.2f}")
        print(f"   Final:    ${results['final_capital']:,.2f}")
        print(f"   Retorno:  {results['return_percent']:+.2f}%")

        print(f"\n📈 Operaciones:")
        print(f"   Total:    {results['total_trades']}")
        print(f"   Ganadoras: {results['winning_trades']} ({results['win_rate']:.1f}%)")
        print(f"   Perdedoras: {results['losing_trades']}")

        print(f"\n💰 Profit & Loss:")
        print(f"   Total P&L:      ${results['total_profit_loss']:+,.2f}")
        print(f"   Ganancia total: ${results['total_profit']:,.2f}")
        print(f"   Pérdida total:  ${results['total_loss']:,.2f}")
        print(f"   Ganancia promedio: ${results['avg_win']:,.2f}")
        print(f"   Pérdida promedio:  ${results['avg_loss']:,.2f}")

        print(f"\n📉 Métricas de Riesgo:")
        print(f"   Profit Factor:   {results['profit_factor']:.2f}")
        print(f"   Max Drawdown:    {results['max_drawdown']:.2f}%")

        print("\n" + "="*60)

    def save_results(self, filename: str = "backtest_results.json"):
        """Guarda resultados en archivo JSON"""
        results = self._calculate_results()

        # Agregar trades
        results['trades'] = [t.to_dict() for t in self.trades if t.exit_time]

        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)

        print(f"\n💾 Resultados guardados en: {filename}")

    def save_trades_csv(self, filename: str = config.TRADES_CSV_FILE):
        """Guarda trades en CSV"""
        if not self.trades:
            return

        trades_data = [t.to_dict() for t in self.trades if t.exit_time]
        df = pd.DataFrame(trades_data)
        df.to_csv(filename, index=False)

        print(f"💾 Trades guardados en: {filename}")


if __name__ == "__main__":
    print("=== BACKTEST ENGINE TEST ===\n")

    # Crear datos de prueba más realistas
    dates = pd.date_range(start='2024-01-01', periods=500, freq='5min')
    np.random.seed(42)

    # Simular precio con tendencias
    base_price = 2575.0
    trend1 = np.linspace(0, 3, 200)  # Tendencia alcista
    trend2 = np.linspace(3, 1, 200)  # Tendencia bajista
    trend3 = np.linspace(1, 4, 100)  # Tendencia alcista fuerte

    trend = np.concatenate([trend1, trend2, trend3])
    noise = np.random.randn(500) * 0.3

    prices = base_price + trend + noise

    df = pd.DataFrame({
        'open': prices,
        'high': prices + np.random.rand(500) * 0.3,
        'low': prices - np.random.rand(500) * 0.3,
        'close': prices + np.random.randn(500) * 0.2,
        'volume': np.random.randint(100, 1000, 500)
    }, index=dates)

    # Ejecutar backtest
    engine = BacktestEngine(initial_capital=10000)
    results = engine.run(df, verbose=True)

    # Guardar resultados
    engine.save_results("test_backtest_results.json")
    engine.save_trades_csv("test_trades.csv")
