# Notas de Desarrollo

## 📝 Concepto Inicial

Bot de trading para MGC (Micro Gold) que identifica y opera en niveles psicológicos de precio en incrementos de 0.5:
- 1.0, 1.5, 2.0, 2.5, 3.0, 3.5... hasta 10.5

El precio tiende a reaccionar (retroceder) en estos niveles psicológicos.

## 🎯 Estrategia Implementada

### 1. Detección de Niveles (`level_detector.py`)
- Genera niveles en incrementos de 0.5
- Identifica nivel más cercano al precio actual
- Analiza comportamiento histórico en cada nivel (bounce rate)
- Identifica soportes y resistencias basados en reacciones previas

### 2. Detección de Tendencias (`trend_detector.py`)
- Identifica swing highs y swing lows
- Detecta tendencias alcistas (Higher Highs, Higher Lows)
- Detecta tendencias bajistas (Lower Highs, Lower Lows)
- Calcula fuerza de tendencia usando regresión lineal
- Identifica el punto de inicio de una nueva tendencia

### 3. Señales de Trading (`trading_strategy.py`)
**Señal de COMPRA (LONG):**
- Tendencia alcista confirmada
- Precio cerca de nivel de soporte (±tolerance)
- Nivel tiene historial de rebotes (bounce rate > 40%)
- Confirmación: vela con mecha inferior rechazando nivel

**Señal de VENTA (SHORT):**
- Tendencia bajista confirmada
- Precio cerca de nivel de resistencia (±tolerance)
- Nivel tiene historial de rebotes (bounce rate > 40%)
- Confirmación: vela con mecha superior rechazando nivel

**Stop Loss y Take Profit:**
- SL: Debajo/arriba del nivel + margen
- TP: Ajustado al siguiente nivel significativo
- Risk/Reward ratio: 1.5 por defecto

### 4. Gestión de Riesgo
- Riesgo por operación: 2% del capital
- Tamaño de posición calculado automáticamente
- Máximo de posiciones simultáneas: 3

## 🔧 Parámetros Ajustables

En `config.py` puedes ajustar:

```python
# Niveles
LEVEL_INCREMENT = 0.5
LEVEL_TOLERANCE = 0.2  # ±0.2 del nivel

# Tendencia
TREND_LOOKBACK_BARS = 20
MIN_TREND_STRENGTH = 0.6

# Riesgo
RISK_PER_TRADE = 0.02  # 2%
DEFAULT_STOP_LOSS_POINTS = 2.0
DEFAULT_TAKE_PROFIT_POINTS = 3.0
```

## 🚀 Próximas Mejoras

### Corto Plazo
1. **Datos Reales:**
   - Integrar MT5 para obtener datos históricos reales de MGC
   - Implementar `get_market_data()` en `bot.py`

2. **Backtesting con Datos Reales:**
   - Descargar datos históricos de MGC
   - Ejecutar backtests exhaustivos
   - Optimizar parámetros basados en resultados

3. **Filtros Adicionales:**
   - Volumen: Confirmar con volumen superior al promedio
   - Momentum: Agregar indicador de momentum (RSI, MACD)
   - Time filters: Evitar operar en horas de bajo volumen

### Mediano Plazo
4. **Trailing Stop Loss:**
   - Mover SL a breakeven cuando el precio se mueva favorable
   - Trailing stop dinámico basado en ATR

5. **Multi-Timeframe:**
   - Confirmar tendencia en timeframe superior
   - Ejecutar en timeframe inferior

6. **Refinamiento de Niveles:**
   - Ajustar automáticamente niveles basados en datos históricos
   - Identificar "niveles calientes" con más reacciones

### Largo Plazo
7. **Machine Learning:**
   - Predecir probabilidad de rebote en cada nivel
   - Clasificar niveles por fuerza histórica
   - Optimización automática de parámetros

8. **Dashboard y Alertas:**
   - Interfaz web para monitoreo
   - Alertas por Telegram/email
   - Visualización de equity curve en tiempo real

## 🐛 Issues Conocidos y TODOs

### TODO Crítico
- [ ] Implementar conexión real a MT5
- [ ] Obtener y probar con datos reales de MGC
- [ ] Agregar logging más detallado
- [ ] Manejo de errores de conexión
- [ ] Reconexión automática si se pierde conexión

### TODO Mejoras
- [ ] Agregar más tests unitarios
- [ ] Optimizar detección de swing points (puede ser lento)
- [ ] Cachear análisis de niveles para evitar recalcular
- [ ] Agregar visualización de niveles con matplotlib
- [ ] Exportar trades a formato compatible con TradingView

### Bugs Potenciales
- Swing detection puede no funcionar bien con gaps
- Backtesting no considera slippage realista durante noticias
- Position sizing no considera margen requerido por broker

## 📊 Resultados Esperados

Con datos sintéticos, el backtesting muestra:
- Win rate esperado: 50-60% (debido a R:R 1.5)
- Profit factor objetivo: > 1.5
- Max drawdown objetivo: < 15%

**IMPORTANTE:** Estos son resultados con datos sintéticos.
Los resultados reales pueden variar significativamente.

## 💡 Ideas Adicionales

1. **Niveles Dinámicos:**
   - En lugar de niveles fijos, usar niveles round numbers del precio actual
   - Ejemplo: Si MGC cotiza a 2584, usar 2580, 2585, 2590, etc.

2. **Breakout Strategy:**
   - Además de rebotes, detectar roturas de niveles con volumen
   - Entrar en dirección de la rotura

3. **Session Filtering:**
   - Operar solo en sesión de NY (mayor volumen para oro)
   - Evitar rollover y apertura de mercado

4. **News Filter:**
   - Integrar calendario económico
   - No operar durante noticias de alto impacto (NFP, FOMC, etc.)

5. **Correlación Multi-Asset:**
   - Considerar correlación con DXY (dólar)
   - Usar como filtro adicional

## 🔍 Cómo Testear Mejoras

1. Modificar parámetros en `config.py`
2. Ejecutar `python backtesting.py`
3. Revisar métricas en `backtest_results.json`
4. Comparar con baseline anterior
5. Si mejora métricas, probar en demo
6. Solo después de éxito en demo, considerar live

## 📚 Recursos Útiles

- **MetaTrader 5 Python API:** https://www.mql5.com/en/docs/integration/python_metatrader5
- **Backtesting.py docs:** https://kernc.github.io/backtesting.py/
- **VectorBT:** https://vectorbt.dev/
- **Pandas-TA:** https://github.com/twopirllc/pandas-ta

## 🤝 Contribuciones

Para contribuir:
1. Crear branch: `git checkout -b feature/nombre-feature`
2. Hacer cambios y tests
3. Commit: `git commit -m "feat: descripción"`
4. Push y crear PR

## ⚠️ Disclaimer

Este bot es para propósitos educativos y de investigación.
Trading con instrumentos financieros conlleva riesgo de pérdida.
Nunca operes con dinero que no puedas permitirte perder.
Siempre prueba exhaustivamente en demo antes de usar dinero real.
