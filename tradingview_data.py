"""
TradingView Data Fetcher
Obtiene datos de futuros desde TradingView
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Optional
import time

try:
    from tvDatafeed import TvDatafeed, Interval
    TV_AVAILABLE = True
except ImportError:
    TV_AVAILABLE = False
    print("⚠️  tvDatafeed no instalado. Instalar con: pip install tvDatafeed")

try:
    from tradingview_ta import TA_Handler, Interval as TA_Interval, Exchange
    TA_AVAILABLE = True
except ImportError:
    TA_AVAILABLE = False
    print("⚠️  tradingview-ta no instalado. Instalar con: pip install tradingview-ta")

import config


class TradingViewDataFetcher:
    """Obtiene datos de TradingView para MGC y otros futuros"""

    # Mapeo de timeframes
    TIMEFRAME_MAP = {
        '1min': Interval.in_1_minute if TV_AVAILABLE else None,
        '5min': Interval.in_5_minute if TV_AVAILABLE else None,
        '15min': Interval.in_15_minute if TV_AVAILABLE else None,
        '30min': Interval.in_30_minute if TV_AVAILABLE else None,
        '1h': Interval.in_1_hour if TV_AVAILABLE else None,
        '4h': Interval.in_4_hour if TV_AVAILABLE else None,
        '1d': Interval.in_daily if TV_AVAILABLE else None,
    }

    def __init__(self, username: str = "", password: str = ""):
        """
        Inicializa el fetcher de TradingView

        Args:
            username: Usuario de TradingView (opcional, para más requests)
            password: Contraseña de TradingView (opcional)
        """
        self.tv = None

        if TV_AVAILABLE:
            try:
                if username and password:
                    self.tv = TvDatafeed(username, password)
                else:
                    # Sin login (limitado pero funcional)
                    self.tv = TvDatafeed()
                print("✅ TradingView data fetcher inicializado")
            except Exception as e:
                print(f"⚠️  Error al conectar con TradingView: {e}")
                self.tv = None
        else:
            print("⚠️  tvDatafeed no disponible. Instalar: pip install tvDatafeed")

    def get_futures_data(self, symbol: str = "MGC1!", exchange: str = "COMEX",
                         timeframe: str = '5min', bars: int = 500) -> Optional[pd.DataFrame]:
        """
        Obtiene datos de futuros desde TradingView

        Args:
            symbol: Símbolo del futuro (ej: MGC1!, GC1!, ES1!)
            exchange: Exchange (COMEX para oro, CME para índices)
            timeframe: Timeframe (1min, 5min, 15min, 1h, etc.)
            bars: Número de barras a obtener

        Returns:
            DataFrame con datos OHLCV o None si falla
        """
        if not self.tv:
            print("❌ TradingView no está disponible")
            return None

        try:
            # Obtener intervalo correcto
            interval = self.TIMEFRAME_MAP.get(timeframe)
            if not interval:
                print(f"❌ Timeframe no válido: {timeframe}")
                return None

            print(f"📊 Obteniendo datos de {symbol} ({exchange}) - {timeframe} - {bars} barras...")

            # Obtener datos
            df = self.tv.get_hist(
                symbol=symbol,
                exchange=exchange,
                interval=interval,
                n_bars=bars
            )

            if df is None or df.empty:
                print("❌ No se obtuvieron datos")
                return None

            # Renombrar columnas al formato esperado
            df = df.rename(columns={
                'open': 'open',
                'high': 'high',
                'low': 'low',
                'close': 'close',
                'volume': 'volume'
            })

            # Asegurar que el índice sea datetime
            if not isinstance(df.index, pd.DatetimeIndex):
                df.index = pd.to_datetime(df.index)

            # Ordenar por fecha (más antiguo primero)
            df = df.sort_index()

            print(f"✅ Datos obtenidos: {len(df)} barras")
            print(f"   Rango: {df.index[0]} a {df.index[-1]}")
            print(f"   Último precio: {df['close'].iloc[-1]:.2f}")

            return df[['open', 'high', 'low', 'close', 'volume']]

        except Exception as e:
            print(f"❌ Error al obtener datos: {e}")
            return None

    def get_mgc_data(self, timeframe: str = None, bars: int = 500) -> Optional[pd.DataFrame]:
        """
        Obtiene datos específicamente para Micro Gold (MGC)

        Args:
            timeframe: Timeframe (usa config.TIMEFRAME si no se especifica)
            bars: Número de barras

        Returns:
            DataFrame con datos OHLCV
        """
        if timeframe is None:
            timeframe = config.TIMEFRAME

        # MGC cotiza en COMEX
        return self.get_futures_data(
            symbol="MGC1!",  # Micro Gold continuous contract
            exchange="COMEX",
            timeframe=timeframe,
            bars=bars
        )

    def get_technical_analysis(self, symbol: str = "MGC1!", exchange: str = "COMEX",
                               timeframe: str = "5m") -> Optional[dict]:
        """
        Obtiene análisis técnico de TradingView

        Args:
            symbol: Símbolo
            exchange: Exchange
            timeframe: Timeframe (1m, 5m, 15m, 1h, 4h, 1d)

        Returns:
            Diccionario con análisis técnico
        """
        if not TA_AVAILABLE:
            return None

        try:
            # Mapeo de timeframes para TA_Handler
            ta_timeframe_map = {
                '1min': TA_Interval.INTERVAL_1_MINUTE,
                '5min': TA_Interval.INTERVAL_5_MINUTES,
                '15min': TA_Interval.INTERVAL_15_MINUTES,
                '30min': TA_Interval.INTERVAL_30_MINUTES,
                '1h': TA_Interval.INTERVAL_1_HOUR,
                '4h': TA_Interval.INTERVAL_4_HOURS,
                '1d': TA_Interval.INTERVAL_1_DAY,
            }

            ta_interval = ta_timeframe_map.get(timeframe, TA_Interval.INTERVAL_5_MINUTES)

            handler = TA_Handler(
                symbol=symbol,
                exchange=exchange,
                screener="america",
                interval=ta_interval,
                timeout=10
            )

            analysis = handler.get_analysis()

            return {
                'summary': analysis.summary,
                'oscillators': analysis.oscillators,
                'moving_averages': analysis.moving_averages,
                'indicators': analysis.indicators
            }

        except Exception as e:
            print(f"⚠️  Error al obtener análisis técnico: {e}")
            return None


def test_tradingview_data():
    """Test de obtención de datos"""
    print("="*60)
    print("🧪 TEST: TRADINGVIEW DATA FETCHER")
    print("="*60)

    fetcher = TradingViewDataFetcher()

    if not fetcher.tv:
        print("\n❌ No se pudo inicializar TradingView")
        print("📝 Instrucciones:")
        print("   1. Instalar: pip install tvDatafeed")
        print("   2. Ejecutar de nuevo este script")
        return

    # Test 1: Obtener datos de MGC
    print("\n📊 Test 1: Obtener datos de MGC")
    df_mgc = fetcher.get_mgc_data(timeframe='5min', bars=100)

    if df_mgc is not None:
        print(f"\n✅ Datos de MGC obtenidos exitosamente")
        print(f"\nÚltimas 5 barras:")
        print(df_mgc.tail())

        print(f"\nEstadísticas:")
        print(f"  Precio actual: ${df_mgc['close'].iloc[-1]:.2f}")
        print(f"  Máximo (100 barras): ${df_mgc['high'].max():.2f}")
        print(f"  Mínimo (100 barras): ${df_mgc['low'].min():.2f}")
        print(f"  Volumen promedio: {df_mgc['volume'].mean():.0f}")

    # Test 2: Otros futuros
    print("\n" + "="*60)
    print("📊 Test 2: Obtener datos de Gold (GC)")
    df_gc = fetcher.get_futures_data("GC1!", "COMEX", "5min", 50)

    if df_gc is not None:
        print(f"✅ Gold: ${df_gc['close'].iloc[-1]:.2f}")

    # Test 3: Análisis técnico
    if TA_AVAILABLE:
        print("\n" + "="*60)
        print("📊 Test 3: Análisis técnico de MGC")
        ta = fetcher.get_technical_analysis("MGC1!", "COMEX", "5min")

        if ta:
            print(f"\n📈 Resumen TradingView:")
            print(f"  Recomendación: {ta['summary']['RECOMMENDATION']}")
            print(f"  Buy signals: {ta['summary']['BUY']}")
            print(f"  Sell signals: {ta['summary']['SELL']}")
            print(f"  Neutral: {ta['summary']['NEUTRAL']}")

    print("\n" + "="*60)
    print("✅ TESTS COMPLETADOS")
    print("="*60)


if __name__ == "__main__":
    test_tradingview_data()
