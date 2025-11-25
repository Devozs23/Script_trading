"""
Bot Principal de Trading
Ejecuta la estrategia en tiempo real o modo demo
"""

import pandas as pd
import time
from datetime import datetime, timedelta
import argparse
import sys

from trading_strategy import LevelTradingStrategy, SignalType
from level_detector import LevelDetector
from trend_detector import TrendDetector
from tradingview_data import TradingViewDataFetcher
import config


class TradingBot:
    """Bot de trading principal"""

    def __init__(self, mode: str = "demo", use_tradingview: bool = True):
        self.mode = mode
        self.use_tradingview = use_tradingview
        self.strategy = LevelTradingStrategy()
        self.level_detector = LevelDetector()
        self.trend_detector = TrendDetector()
        self.active_positions = []
        self.trade_log = []

        # Inicializar TradingView data fetcher si está habilitado
        self.tv_fetcher = None
        if use_tradingview:
            try:
                self.tv_fetcher = TradingViewDataFetcher()
                if self.tv_fetcher.tv:
                    print("✅ TradingView data fetcher habilitado")
            except Exception as e:
                print(f"⚠️  Error al inicializar TradingView: {e}")
                print("   Usando datos sintéticos")
                self.use_tradingview = False

        print(f"🤖 Trading Bot iniciado en modo: {mode.upper()}")
        print(f"📊 Símbolo: {config.SYMBOL}")
        print(f"⏱️  Timeframe: {config.TIMEFRAME}")
        print(f"💰 Riesgo por trade: {config.RISK_PER_TRADE * 100}%")
        print(f"📡 Fuente de datos: {'TradingView' if self.use_tradingview and self.tv_fetcher else 'Sintéticos'}\n")

    def get_market_data(self) -> pd.DataFrame:
        """
        Obtiene datos del mercado

        Usa TradingView si está disponible, sino datos sintéticos.

        Returns:
            DataFrame con datos OHLCV
        """
        # Intentar obtener datos de TradingView
        if self.use_tradingview and self.tv_fetcher and self.tv_fetcher.tv:
            try:
                df = self.tv_fetcher.get_mgc_data(
                    timeframe=config.TIMEFRAME,
                    bars=100
                )

                if df is not None and not df.empty:
                    return df

                print("⚠️  No se pudieron obtener datos de TradingView, usando sintéticos")

            except Exception as e:
                print(f"⚠️  Error al obtener datos de TradingView: {e}")
                print("   Usando datos sintéticos")

        # Fallback: Datos sintéticos para testing
        print("⚠️  USANDO DATOS SINTÉTICOS")

        import numpy as np

        dates = pd.date_range(end=datetime.now(), periods=100, freq='5min')
        base_price = 2575.0
        trend = np.linspace(0, 2, 100)
        noise = np.random.randn(100) * 0.3

        prices = base_price + trend + noise

        df = pd.DataFrame({
            'time': dates,
            'open': prices,
            'high': prices + np.random.rand(100) * 0.3,
            'low': prices - np.random.rand(100) * 0.3,
            'close': prices + np.random.randn(100) * 0.2,
            'volume': np.random.randint(100, 1000, 100)
        })

        df.set_index('time', inplace=True)

        return df

    def analyze_market(self, df: pd.DataFrame):
        """Analiza el mercado y muestra información"""
        analysis = self.strategy.analyze_market(df)

        print(f"\n{'='*60}")
        print(f"📊 ANÁLISIS DE MERCADO - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")

        print(f"\n💵 Precio actual: {analysis['current_price']:.2f}")

        print(f"\n📈 Tendencia:")
        print(f"   Dirección: {analysis['trend']['direction'].upper()}")
        print(f"   Fuerza: {analysis['trend']['strength']:.2f}")
        print(f"   Confirmada: {'✅' if analysis['trend']['confirmed'] else '❌'}")

        print(f"\n🎯 Niveles cercanos: {analysis['nearby_levels']}")

        if analysis['support_levels']:
            print(f"\n🟢 Soportes clave: {analysis['support_levels']}")

        if analysis['resistance_levels']:
            print(f"\n🔴 Resistencias clave: {analysis['resistance_levels']}")

        if analysis['signal']:
            signal = analysis['signal']
            print(f"\n{'🔔'*20}")
            print(f"🎯 SEÑAL DETECTADA:")
            print(f"   Tipo: {signal.signal_type.value.upper()}")
            print(f"   Precio: {signal.price:.2f}")
            print(f"   Nivel: {signal.level:.2f}")
            print(f"   Stop Loss: {signal.stop_loss:.2f}")
            print(f"   Take Profit: {signal.take_profit:.2f}")
            print(f"   Razón: {signal.reason}")
            print(f"{'🔔'*20}")

        print(f"\n{'='*60}\n")

        return analysis

    def execute_signal(self, signal):
        """
        Ejecuta una señal de trading

        Args:
            signal: TradingSignal a ejecutar
        """
        if self.mode == "demo":
            print(f"📝 [DEMO] Ejecutando señal: {signal.signal_type.value}")
            print(f"   (En modo LIVE esto abriría una posición real)")

            # Simular apertura de posición
            position = {
                'type': signal.signal_type.value,
                'entry_price': signal.price,
                'entry_time': datetime.now(),
                'level': signal.level,
                'stop_loss': signal.stop_loss,
                'take_profit': signal.take_profit,
                'size': 1  # En producción, calcular con get_position_size()
            }

            self.active_positions.append(position)
            self.trade_log.append(position)

            print(f"✅ Posición abierta (simulada)")

        else:
            # TODO: Implementar ejecución real con MT5
            print("⚠️  Modo LIVE - Implementar conexión a broker")
            pass

    def check_positions(self, df: pd.DataFrame):
        """Verifica posiciones activas"""
        if not self.active_positions:
            return

        print(f"\n📌 Verificando {len(self.active_positions)} posición(es) activa(s)...")

        for position in self.active_positions[:]:
            current_price = df['close'].iloc[-1]

            # Verificar condiciones de salida
            should_close = False
            reason = ""

            if position['type'] == 'buy':
                if current_price <= position['stop_loss']:
                    should_close = True
                    reason = "Stop Loss"
                elif current_price >= position['take_profit']:
                    should_close = True
                    reason = "Take Profit"

            else:  # sell
                if current_price >= position['stop_loss']:
                    should_close = True
                    reason = "Stop Loss"
                elif current_price <= position['take_profit']:
                    should_close = True
                    reason = "Take Profit"

            if should_close:
                print(f"🔴 Cerrando posición - Razón: {reason}")
                print(f"   Entrada: {position['entry_price']:.2f}")
                print(f"   Salida: {current_price:.2f}")

                # Calcular P&L
                if position['type'] == 'buy':
                    pl = (current_price - position['entry_price']) * position['size']
                else:
                    pl = (position['entry_price'] - current_price) * position['size']

                print(f"   P&L: ${pl:.2f} {'📈' if pl > 0 else '📉'}")

                self.active_positions.remove(position)

    def run(self, interval_seconds: int = 60):
        """
        Ejecuta el bot en loop continuo

        Args:
            interval_seconds: Segundos entre iteraciones
        """
        print(f"\n🚀 Bot en ejecución - Presiona Ctrl+C para detener\n")

        try:
            iteration = 0
            while True:
                iteration += 1
                print(f"\n🔄 Iteración {iteration} - {datetime.now().strftime('%H:%M:%S')}")

                # 1. Obtener datos del mercado
                df = self.get_market_data()

                # 2. Verificar posiciones activas
                self.check_positions(df)

                # 3. Analizar mercado y buscar señales
                analysis = self.analyze_market(df)

                # 4. Ejecutar señales si hay espacio
                if analysis['signal'] and len(self.active_positions) < config.MAX_POSITIONS:
                    self.execute_signal(analysis['signal'])

                # 5. Esperar siguiente iteración
                print(f"⏳ Esperando {interval_seconds}s hasta próxima iteración...")
                time.sleep(interval_seconds)

        except KeyboardInterrupt:
            print("\n\n⏹️  Bot detenido por el usuario")
            self.shutdown()

    def shutdown(self):
        """Cierra el bot de forma segura"""
        print("\n📊 Resumen de sesión:")
        print(f"   Total de señales: {len(self.trade_log)}")
        print(f"   Posiciones activas: {len(self.active_positions)}")

        if self.active_positions:
            print("\n⚠️  Hay posiciones activas que deben cerrarse manualmente")

        print("\n👋 ¡Hasta pronto!")


def main():
    parser = argparse.ArgumentParser(description='MGC Trading Bot')
    parser.add_argument('--mode', type=str, default='demo',
                       choices=['demo', 'live'],
                       help='Modo de ejecución (demo o live)')
    parser.add_argument('--interval', type=int, default=60,
                       help='Intervalo en segundos entre análisis')
    parser.add_argument('--no-tradingview', action='store_true',
                       help='No usar TradingView (usar datos sintéticos)')

    args = parser.parse_args()

    if args.mode == 'live':
        print("⚠️  ADVERTENCIA: Modo LIVE ⚠️")
        print("Estás a punto de ejecutar el bot con dinero real.")
        confirm = input("¿Estás seguro? (escribe 'SI' para continuar): ")

        if confirm != 'SI':
            print("Cancelado.")
            sys.exit(0)

    use_tv = not args.no_tradingview

    bot = TradingBot(mode=args.mode, use_tradingview=use_tv)
    bot.run(interval_seconds=args.interval)


if __name__ == "__main__":
    main()
