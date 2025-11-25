"""
Estrategia de Trading Basada en Niveles
Combina detección de niveles y tendencias para generar señales
"""

import pandas as pd
import numpy as np
from typing import Optional, Dict, List
from enum import Enum

from level_detector import LevelDetector
from trend_detector import TrendDetector, TrendDirection
import config


class SignalType(Enum):
    """Tipo de señal de trading"""
    BUY = "buy"
    SELL = "sell"
    CLOSE_LONG = "close_long"
    CLOSE_SHORT = "close_short"
    HOLD = "hold"


class TradingSignal:
    """Clase para representar una señal de trading"""

    def __init__(self, signal_type: SignalType, price: float, level: float,
                 stop_loss: float, take_profit: float, reason: str = ""):
        self.signal_type = signal_type
        self.price = price
        self.level = level
        self.stop_loss = stop_loss
        self.take_profit = take_profit
        self.reason = reason
        self.timestamp = None

    def __repr__(self):
        return (f"TradingSignal({self.signal_type.value}, "
                f"price={self.price:.2f}, level={self.level:.2f}, "
                f"SL={self.stop_loss:.2f}, TP={self.take_profit:.2f})")


class LevelTradingStrategy:
    """Estrategia de trading basada en niveles psicológicos"""

    def __init__(self):
        self.level_detector = LevelDetector()
        self.trend_detector = TrendDetector()
        self.active_position = None

    def analyze_entry_opportunity(self, df: pd.DataFrame) -> Optional[TradingSignal]:
        """
        Analiza si existe una oportunidad de entrada

        Args:
            df: DataFrame con datos OHLCV

        Returns:
            TradingSignal o None
        """
        if len(df) < config.TREND_LOOKBACK_BARS:
            return None

        current_price = df['close'].iloc[-1]
        current_bar = df.iloc[-1]

        # 1. Verificar si estamos cerca de un nivel
        is_near, nearest_level = self.level_detector.is_near_level(
            current_price,
            config.LEVEL_TOLERANCE
        )

        if not is_near:
            return None

        # 2. Obtener información de tendencia
        trend_info = self.trend_detector.get_trend_info(df)

        # 3. Verificar confirmación de tendencia si está configurado
        if config.REQUIRE_TREND_CONFIRMATION and not trend_info['confirmed']:
            return None

        # 4. Analizar el comportamiento histórico del nivel
        level_analysis = self.level_detector.analyze_price_action_at_level(df, nearest_level)

        # El nivel debe tener historial de reacciones
        if level_analysis['bounce_rate'] < 0.4:  # Menos del 40% de rebotes
            return None

        # 5. Determinar tipo de señal basado en tendencia y nivel
        signal = self._generate_signal(
            current_price,
            current_bar,
            nearest_level,
            trend_info,
            level_analysis
        )

        return signal

    def _generate_signal(self, current_price: float, current_bar: pd.Series,
                         level: float, trend_info: Dict,
                         level_analysis: Dict) -> Optional[TradingSignal]:
        """
        Genera señal de trading basada en análisis

        Args:
            current_price: Precio actual
            current_bar: Barra actual
            level: Nivel identificado
            trend_info: Información de tendencia
            level_analysis: Análisis del nivel

        Returns:
            TradingSignal o None
        """
        trend_direction = trend_info['direction']

        # SEÑAL DE COMPRA (LONG)
        # Condiciones: Tendencia alcista + Precio cerca de nivel de soporte
        if trend_direction == TrendDirection.BULLISH.value:
            if current_price <= level + config.LEVEL_TOLERANCE:
                # Buscar confirmación de rebote
                # El precio debe estar cerca del nivel pero mostrando señales de rechazo
                wick_below = current_bar['low'] < level < current_bar['close']

                if wick_below or level_analysis['bounce_rate'] > 0.6:
                    # Calcular Stop Loss y Take Profit
                    stop_loss = level - config.DEFAULT_STOP_LOSS_POINTS
                    take_profit = current_price + (config.DEFAULT_TAKE_PROFIT_POINTS)

                    # Ajustar TP al siguiente nivel de resistencia si existe
                    next_resistance_levels = self.level_detector.get_next_levels(
                        current_price, "up", 3
                    )
                    if next_resistance_levels:
                        take_profit = min(take_profit, next_resistance_levels[0] - 0.1)

                    reason = f"Bullish trend + Support bounce at {level}"

                    return TradingSignal(
                        SignalType.BUY,
                        current_price,
                        level,
                        stop_loss,
                        take_profit,
                        reason
                    )

        # SEÑAL DE VENTA (SHORT)
        # Condiciones: Tendencia bajista + Precio cerca de nivel de resistencia
        elif trend_direction == TrendDirection.BEARISH.value:
            if current_price >= level - config.LEVEL_TOLERANCE:
                # Buscar confirmación de rechazo
                wick_above = current_bar['high'] > level > current_bar['close']

                if wick_above or level_analysis['bounce_rate'] > 0.6:
                    # Calcular Stop Loss y Take Profit
                    stop_loss = level + config.DEFAULT_STOP_LOSS_POINTS
                    take_profit = current_price - config.DEFAULT_TAKE_PROFIT_POINTS

                    # Ajustar TP al siguiente nivel de soporte si existe
                    next_support_levels = self.level_detector.get_next_levels(
                        current_price, "down", 3
                    )
                    if next_support_levels:
                        take_profit = max(take_profit, next_support_levels[0] + 0.1)

                    reason = f"Bearish trend + Resistance rejection at {level}"

                    return TradingSignal(
                        SignalType.SELL,
                        current_price,
                        level,
                        stop_loss,
                        take_profit,
                        reason
                    )

        return None

    def check_exit_conditions(self, df: pd.DataFrame, position: Dict) -> Optional[SignalType]:
        """
        Verifica condiciones de salida para posición activa

        Args:
            df: DataFrame con datos OHLCV
            position: Diccionario con información de posición

        Returns:
            SignalType de cierre o None
        """
        current_price = df['close'].iloc[-1]

        # Verificar Stop Loss
        if position['type'] == 'long':
            if current_price <= position['stop_loss']:
                return SignalType.CLOSE_LONG
            elif current_price >= position['take_profit']:
                return SignalType.CLOSE_LONG

        elif position['type'] == 'short':
            if current_price >= position['stop_loss']:
                return SignalType.CLOSE_SHORT
            elif current_price <= position['take_profit']:
                return SignalType.CLOSE_SHORT

        # Verificar reversión de tendencia
        trend_info = self.trend_detector.get_trend_info(df)

        if position['type'] == 'long' and trend_info['direction'] == TrendDirection.BEARISH.value:
            if trend_info['confirmed']:
                return SignalType.CLOSE_LONG

        elif position['type'] == 'short' and trend_info['direction'] == TrendDirection.BULLISH.value:
            if trend_info['confirmed']:
                return SignalType.CLOSE_SHORT

        return None

    def get_position_size(self, account_balance: float, entry_price: float,
                         stop_loss: float) -> int:
        """
        Calcula tamaño de posición basado en riesgo

        Args:
            account_balance: Balance de cuenta
            entry_price: Precio de entrada
            stop_loss: Stop loss

        Returns:
            Número de contratos
        """
        risk_amount = account_balance * config.RISK_PER_TRADE
        risk_per_contract = abs(entry_price - stop_loss) * config.TICK_VALUE

        if risk_per_contract == 0:
            return 0

        position_size = int(risk_amount / risk_per_contract)

        # Mínimo 1 contrato
        return max(1, position_size)

    def analyze_market(self, df: pd.DataFrame) -> Dict:
        """
        Análisis completo del mercado actual

        Args:
            df: DataFrame con datos OHLCV

        Returns:
            Diccionario con análisis de mercado
        """
        current_price = df['close'].iloc[-1]

        # Niveles cercanos
        nearby_levels = self.level_detector.get_levels_in_range(current_price, 3)

        # Información de tendencia
        trend_info = self.trend_detector.get_trend_info(df)

        # Soporte y resistencia
        sr_levels = self.level_detector.get_support_resistance_levels(df)

        # Verificar si hay señal
        signal = self.analyze_entry_opportunity(df)

        return {
            'current_price': current_price,
            'nearby_levels': nearby_levels,
            'trend': trend_info,
            'support_levels': sr_levels['support'][:3],  # Top 3
            'resistance_levels': sr_levels['resistance'][:3],  # Top 3
            'signal': signal
        }


if __name__ == "__main__":
    # Test básico
    print("=== TRADING STRATEGY TEST ===\n")

    # Crear datos de prueba
    dates = pd.date_range(start='2024-01-01', periods=100, freq='5min')
    np.random.seed(42)

    # Tendencia alcista hacia nivel 2575
    trend = np.linspace(2572, 2575, 100)
    noise = np.random.randn(100) * 0.2

    df = pd.DataFrame({
        'open': trend + noise,
        'high': trend + noise + np.random.rand(100) * 0.2,
        'low': trend + noise - np.random.rand(100) * 0.2,
        'close': trend + noise,
        'volume': np.random.randint(100, 1000, 100)
    }, index=dates)

    strategy = LevelTradingStrategy()
    analysis = strategy.analyze_market(df)

    print(f"Precio actual: {analysis['current_price']:.2f}")
    print(f"Tendencia: {analysis['trend']['direction']} (fuerza: {analysis['trend']['strength']:.2f})")
    print(f"Niveles cercanos: {analysis['nearby_levels']}")
    print(f"Soportes clave: {analysis['support_levels']}")
    print(f"Resistencias clave: {analysis['resistance_levels']}")

    if analysis['signal']:
        print(f"\n🎯 SEÑAL DETECTADA:")
        print(analysis['signal'])
        print(f"Razón: {analysis['signal'].reason}")
