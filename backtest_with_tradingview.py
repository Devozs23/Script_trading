#!/usr/bin/env python3
"""
Backtesting con Datos Reales de TradingView
"""

import argparse
from datetime import datetime

from backtesting import BacktestEngine
from tradingview_data import TradingViewDataFetcher
import config


def main():
    parser = argparse.ArgumentParser(description='Backtest MGC con datos de TradingView')
    parser.add_argument('--symbol', type=str, default='MGC1!',
                       help='Símbolo de futuro (ej: MGC1!, GC1!, ES1!)')
    parser.add_argument('--exchange', type=str, default='COMEX',
                       help='Exchange (COMEX, CME, etc.)')
    parser.add_argument('--timeframe', type=str, default='5min',
                       help='Timeframe (1min, 5min, 15min, 1h, 4h, 1d)')
    parser.add_argument('--bars', type=int, default=1000,
                       help='Número de barras históricas')
    parser.add_argument('--capital', type=float, default=10000,
                       help='Capital inicial')

    args = parser.parse_args()

    print("="*60)
    print("📊 BACKTESTING CON DATOS DE TRADINGVIEW")
    print("="*60)
    print(f"\nSímbolo: {args.symbol}")
    print(f"Exchange: {args.exchange}")
    print(f"Timeframe: {args.timeframe}")
    print(f"Barras: {args.bars}")
    print(f"Capital inicial: ${args.capital:,.2f}\n")

    # Inicializar fetcher de TradingView
    print("📡 Conectando con TradingView...")
    fetcher = TradingViewDataFetcher()

    if not fetcher.tv:
        print("❌ No se pudo conectar con TradingView")
        print("\n💡 Solución:")
        print("   pip install tvDatafeed")
        return

    # Obtener datos históricos
    print(f"\n📊 Descargando {args.bars} barras de {args.symbol}...")

    df = fetcher.get_futures_data(
        symbol=args.symbol,
        exchange=args.exchange,
        timeframe=args.timeframe,
        bars=args.bars
    )

    if df is None or df.empty:
        print("❌ No se pudieron obtener datos")
        print("\n💡 Verifica:")
        print("   - Símbolo correcto (ej: MGC1! para Micro Gold)")
        print("   - Exchange correcto (COMEX para metales)")
        print("   - Conexión a internet")
        return

    print(f"\n✅ Datos obtenidos:")
    print(f"   Período: {df.index[0]} a {df.index[-1]}")
    print(f"   Total barras: {len(df)}")
    print(f"   Precio inicial: ${df['close'].iloc[0]:.2f}")
    print(f"   Precio final: ${df['close'].iloc[-1]:.2f}")
    print(f"   Máximo: ${df['high'].max():.2f}")
    print(f"   Mínimo: ${df['low'].min():.2f}")

    # Ejecutar backtest
    print("\n" + "="*60)
    engine = BacktestEngine(initial_capital=args.capital)
    results = engine.run(df, verbose=True)

    # Guardar resultados
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"backtest_{args.symbol.replace('!', '')}_{args.timeframe}_{timestamp}.json"
    trades_file = f"trades_{args.symbol.replace('!', '')}_{args.timeframe}_{timestamp}.csv"

    engine.save_results(results_file)
    engine.save_trades_csv(trades_file)

    print(f"\n💾 Archivos guardados:")
    print(f"   - {results_file}")
    print(f"   - {trades_file}")

    # Recomendaciones basadas en resultados
    print("\n" + "="*60)
    print("📝 RECOMENDACIONES")
    print("="*60)

    if results['win_rate'] >= 50 and results['profit_factor'] >= 1.5:
        print("✅ Resultados prometedores!")
        print("   - Win rate ≥ 50%")
        print("   - Profit factor ≥ 1.5")
        print("\n📌 Próximo paso: Probar en cuenta DEMO")
    elif results['win_rate'] >= 40:
        print("⚠️  Resultados mixtos")
        print("   - Considerar optimizar parámetros")
        print("   - Revisar filtros adicionales")
        print("\n📌 Próximo paso: Ajustar config.py y volver a probar")
    else:
        print("❌ Resultados pobres")
        print("   - La estrategia necesita ajustes significativos")
        print("   - Revisar lógica de entrada/salida")
        print("\n📌 Próximo paso: Revisar strategy y parámetros")

    if results['max_drawdown'] > 20:
        print(f"\n⚠️  ADVERTENCIA: Max Drawdown alto ({results['max_drawdown']:.1f}%)")
        print("   - Considerar reducir riesgo por trade")
        print("   - Ajustar stops más ajustados")

    print("\n" + "="*60)


if __name__ == "__main__":
    main()
