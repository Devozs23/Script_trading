#!/usr/bin/env python3
"""
Script de prueba rápida
Ejecuta un análisis simple del mercado
"""

import pandas as pd
import numpy as np
from datetime import datetime

from level_detector import LevelDetector
from trend_detector import TrendDetector
from trading_strategy import LevelTradingStrategy


def generate_test_data(trend_type: str = "bullish", periods: int = 100):
    """
    Genera datos de prueba con tendencia específica

    Args:
        trend_type: "bullish", "bearish", o "neutral"
        periods: Número de barras

    Returns:
        DataFrame con datos OHLCV
    """
    dates = pd.date_range(end=datetime.now(), periods=periods, freq='5min')
    base_price = 2575.0

    if trend_type == "bullish":
        trend = np.linspace(0, 3, periods)
    elif trend_type == "bearish":
        trend = np.linspace(3, 0, periods)
    else:  # neutral
        trend = np.random.randn(periods) * 0.5

    noise = np.random.randn(periods) * 0.3
    prices = base_price + trend + noise

    df = pd.DataFrame({
        'open': prices,
        'high': prices + np.random.rand(periods) * 0.3,
        'low': prices - np.random.rand(periods) * 0.3,
        'close': prices + np.random.randn(periods) * 0.2,
        'volume': np.random.randint(100, 1000, periods)
    }, index=dates)

    return df


def main():
    print("="*60)
    print("🚀 PRUEBA RÁPIDA - MGC LEVEL TRADING BOT")
    print("="*60)

    # Generar datos de prueba
    print("\n📊 Generando datos de prueba con tendencia alcista...")
    df = generate_test_data(trend_type="bullish", periods=100)

    print(f"   Período: {df.index[0]} a {df.index[-1]}")
    print(f"   Barras: {len(df)}")
    print(f"   Precio inicial: {df['close'].iloc[0]:.2f}")
    print(f"   Precio final: {df['close'].iloc[-1]:.2f}")

    # Test Level Detector
    print("\n" + "="*60)
    print("🎯 TEST: LEVEL DETECTOR")
    print("="*60)

    detector = LevelDetector()
    current_price = df['close'].iloc[-1]

    print(f"\nPrecio actual: {current_price:.2f}")
    print(f"Nivel más cercano: {detector.get_nearest_level(current_price):.1f}")

    is_near, level = detector.is_near_level(current_price)
    print(f"¿Cerca de nivel? {is_near} - Nivel: {level}")

    nearby = detector.get_levels_in_range(current_price, 3)
    print(f"Niveles cercanos (±3): {nearby}")

    sr_levels = detector.get_support_resistance_levels(df)
    print(f"Soportes identificados: {sr_levels['support'][:3]}")
    print(f"Resistencias identificadas: {sr_levels['resistance'][:3]}")

    # Test Trend Detector
    print("\n" + "="*60)
    print("📈 TEST: TREND DETECTOR")
    print("="*60)

    trend_detector = TrendDetector()
    trend_info = trend_detector.get_trend_info(df)

    print(f"\nDirección: {trend_info['direction'].upper()}")
    print(f"Fuerza: {trend_info['strength']:.2f}")
    print(f"Confirmada: {'✅' if trend_info['confirmed'] else '❌'}")

    if trend_info['trend_start']:
        ts = trend_info['trend_start']
        print(f"\nInicio de tendencia detectado:")
        print(f"   Dirección: {ts['direction'].value}")
        print(f"   Precio de inicio: {ts['start_price']:.2f}")
        print(f"   Precio actual: {ts['current_price']:.2f}")
        print(f"   Barras desde inicio: {ts['bars_since_start']}")

    # Test Trading Strategy
    print("\n" + "="*60)
    print("🎲 TEST: TRADING STRATEGY")
    print("="*60)

    strategy = LevelTradingStrategy()
    analysis = strategy.analyze_market(df)

    print(f"\nPrecio actual: {analysis['current_price']:.2f}")
    print(f"Tendencia: {analysis['trend']['direction']} (fuerza: {analysis['trend']['strength']:.2f})")
    print(f"Niveles cercanos: {analysis['nearby_levels']}")
    print(f"Soportes clave: {analysis['support_levels']}")
    print(f"Resistencias clave: {analysis['resistance_levels']}")

    if analysis['signal']:
        signal = analysis['signal']
        print(f"\n{'🎯'*20}")
        print(f"SEÑAL DETECTADA:")
        print(f"   Tipo: {signal.signal_type.value.upper()}")
        print(f"   Precio: {signal.price:.2f}")
        print(f"   Nivel: {signal.level:.2f}")
        print(f"   Stop Loss: {signal.stop_loss:.2f}")
        print(f"   Take Profit: {signal.take_profit:.2f}")
        print(f"   Razón: {signal.reason}")
        print(f"{'🎯'*20}")
    else:
        print("\n⚪ No hay señales en este momento")

    print("\n" + "="*60)
    print("✅ PRUEBA COMPLETADA")
    print("="*60)


if __name__ == "__main__":
    np.random.seed(42)  # Para resultados reproducibles
    main()
