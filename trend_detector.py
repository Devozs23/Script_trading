"""
Detector de Tendencias
Identifica el inicio y dirección de movimientos alcistas y bajistas
"""

import numpy as np
import pandas as pd
from typing import Tuple, Dict, Optional
from enum import Enum
import config


class TrendDirection(Enum):
    """Dirección de la tendencia"""
    BULLISH = "bullish"
    BEARISH = "bearish"
    NEUTRAL = "neutral"


class TrendDetector:
    """Detecta y analiza tendencias de precio"""

    def __init__(self, lookback: int = config.TREND_LOOKBACK_BARS):
        self.lookback = lookback

    def detect_swing_points(self, df: pd.DataFrame, period: int = config.SWING_DETECTION_PERIOD) -> pd.DataFrame:
        """
        Detecta swing highs y swing lows

        Args:
            df: DataFrame con datos OHLCV
            period: Período para detección de swings

        Returns:
            DataFrame con columnas 'swing_high' y 'swing_low'
        """
        df = df.copy()

        df['swing_high'] = False
        df['swing_low'] = False

        for i in range(period, len(df) - period):
            # Swing High: high es mayor que 'period' barras antes y después
            is_swing_high = all(
                df['high'].iloc[i] > df['high'].iloc[i - j] and
                df['high'].iloc[i] > df['high'].iloc[i + j]
                for j in range(1, period + 1)
            )

            # Swing Low: low es menor que 'period' barras antes y después
            is_swing_low = all(
                df['low'].iloc[i] < df['low'].iloc[i - j] and
                df['low'].iloc[i] < df['low'].iloc[i + j]
                for j in range(1, period + 1)
            )

            df.loc[df.index[i], 'swing_high'] = is_swing_high
            df.loc[df.index[i], 'swing_low'] = is_swing_low

        return df

    def get_trend_direction(self, df: pd.DataFrame) -> TrendDirection:
        """
        Determina la dirección de la tendencia actual

        Args:
            df: DataFrame con datos OHLCV

        Returns:
            TrendDirection (BULLISH, BEARISH, NEUTRAL)
        """
        if len(df) < self.lookback:
            return TrendDirection.NEUTRAL

        recent_data = df.tail(self.lookback)

        # Detectar swing points
        df_with_swings = self.detect_swing_points(recent_data)

        # Obtener últimos swing highs y lows
        swing_highs = df_with_swings[df_with_swings['swing_high']]['high']
        swing_lows = df_with_swings[df_with_swings['swing_low']]['low']

        # Necesitamos al menos 2 swings para determinar tendencia
        if len(swing_highs) < 2 or len(swing_lows) < 2:
            return TrendDirection.NEUTRAL

        # Tendencia alcista: Higher Highs y Higher Lows
        higher_highs = swing_highs.iloc[-1] > swing_highs.iloc[-2]
        higher_lows = swing_lows.iloc[-1] > swing_lows.iloc[-2]

        # Tendencia bajista: Lower Highs y Lower Lows
        lower_highs = swing_highs.iloc[-1] < swing_highs.iloc[-2]
        lower_lows = swing_lows.iloc[-1] < swing_lows.iloc[-2]

        if higher_highs and higher_lows:
            return TrendDirection.BULLISH
        elif lower_highs and lower_lows:
            return TrendDirection.BEARISH
        else:
            return TrendDirection.NEUTRAL

    def detect_trend_start(self, df: pd.DataFrame) -> Optional[Dict]:
        """
        Detecta el inicio de una nueva tendencia

        Args:
            df: DataFrame con datos OHLCV

        Returns:
            Diccionario con información del inicio de tendencia o None
        """
        if len(df) < self.lookback + 10:
            return None

        # Analizar tendencia actual
        current_trend = self.get_trend_direction(df)

        # Analizar tendencia previa (excluyendo últimas barras)
        previous_df = df.iloc[:-10]
        previous_trend = self.get_trend_direction(previous_df)

        # Detectar cambio de tendencia
        if current_trend != previous_trend and current_trend != TrendDirection.NEUTRAL:
            # Encontrar el punto aproximado de inicio
            df_with_swings = self.detect_swing_points(df.tail(self.lookback))

            if current_trend == TrendDirection.BULLISH:
                # Inicio alcista: último swing low significativo
                swing_lows = df_with_swings[df_with_swings['swing_low']]
                if len(swing_lows) > 0:
                    start_idx = swing_lows.index[-1]
                    start_price = swing_lows.loc[start_idx, 'low']

                    return {
                        'direction': TrendDirection.BULLISH,
                        'start_index': start_idx,
                        'start_price': start_price,
                        'current_price': df['close'].iloc[-1],
                        'bars_since_start': len(df) - df.index.get_loc(start_idx)
                    }

            elif current_trend == TrendDirection.BEARISH:
                # Inicio bajista: último swing high significativo
                swing_highs = df_with_swings[df_with_swings['swing_high']]
                if len(swing_highs) > 0:
                    start_idx = swing_highs.index[-1]
                    start_price = swing_highs.loc[start_idx, 'high']

                    return {
                        'direction': TrendDirection.BEARISH,
                        'start_index': start_idx,
                        'start_price': start_price,
                        'current_price': df['close'].iloc[-1],
                        'bars_since_start': len(df) - df.index.get_loc(start_idx)
                    }

        return None

    def get_trend_strength(self, df: pd.DataFrame) -> float:
        """
        Calcula la fuerza de la tendencia actual (0 a 1)

        Args:
            df: DataFrame con datos OHLCV

        Returns:
            Fuerza de tendencia (0 = débil, 1 = fuerte)
        """
        if len(df) < self.lookback:
            return 0.0

        recent_data = df.tail(self.lookback)

        # Calcular pendiente de regresión lineal
        x = np.arange(len(recent_data))
        y = recent_data['close'].values

        # Regresión lineal simple
        slope = np.polyfit(x, y, 1)[0]

        # Normalizar slope relativo al precio
        avg_price = recent_data['close'].mean()
        normalized_slope = abs(slope) / avg_price if avg_price > 0 else 0

        # Calcular R² para medir consistencia de la tendencia
        y_pred = np.poly1d(np.polyfit(x, y, 1))(x)
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - y.mean()) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0

        # Combinar slope normalizado y R² para obtener fuerza
        # Slope indica dirección, R² indica consistencia
        strength = min(normalized_slope * 100 * r_squared, 1.0)

        return max(0.0, min(strength, 1.0))

    def is_trend_confirmed(self, df: pd.DataFrame, min_strength: float = config.MIN_TREND_STRENGTH) -> bool:
        """
        Verifica si la tendencia está confirmada

        Args:
            df: DataFrame con datos OHLCV
            min_strength: Fuerza mínima requerida

        Returns:
            True si la tendencia está confirmada
        """
        direction = self.get_trend_direction(df)
        strength = self.get_trend_strength(df)

        return direction != TrendDirection.NEUTRAL and strength >= min_strength

    def get_trend_info(self, df: pd.DataFrame) -> Dict:
        """
        Obtiene información completa sobre la tendencia actual

        Args:
            df: DataFrame con datos OHLCV

        Returns:
            Diccionario con información de tendencia
        """
        direction = self.get_trend_direction(df)
        strength = self.get_trend_strength(df)
        confirmed = self.is_trend_confirmed(df)
        trend_start = self.detect_trend_start(df)

        return {
            'direction': direction.value,
            'strength': strength,
            'confirmed': confirmed,
            'trend_start': trend_start,
            'current_price': df['close'].iloc[-1] if len(df) > 0 else None
        }


if __name__ == "__main__":
    # Test básico con datos sintéticos
    print("=== TREND DETECTOR TEST ===\n")

    # Crear datos de prueba con tendencia alcista
    dates = pd.date_range(start='2024-01-01', periods=100, freq='5min')
    np.random.seed(42)

    # Tendencia alcista con ruido
    trend = np.linspace(2570, 2580, 100)
    noise = np.random.randn(100) * 0.5
    prices = trend + noise

    df = pd.DataFrame({
        'open': prices,
        'high': prices + np.random.rand(100) * 0.3,
        'low': prices - np.random.rand(100) * 0.3,
        'close': prices + np.random.randn(100) * 0.2,
        'volume': np.random.randint(100, 1000, 100)
    }, index=dates)

    detector = TrendDetector()

    info = detector.get_trend_info(df)
    print(f"Dirección: {info['direction']}")
    print(f"Fuerza: {info['strength']:.2f}")
    print(f"Confirmada: {info['confirmed']}")
    print(f"Precio actual: {info['current_price']:.2f}")

    if info['trend_start']:
        print(f"\nInicio de tendencia detectado:")
        print(f"  Dirección: {info['trend_start']['direction'].value}")
        print(f"  Precio de inicio: {info['trend_start']['start_price']:.2f}")
        print(f"  Barras desde inicio: {info['trend_start']['bars_since_start']}")
