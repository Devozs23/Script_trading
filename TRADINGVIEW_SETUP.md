# 📊 Configuración TradingView para MGC Trading Bot

Este documento explica cómo usar el bot con TradingView para obtener datos reales de Micro Gold (MGC) futuros.

## 🎯 Dos Formas de Usar TradingView

### Opción 1: Python Bot con Datos de TradingView
Usa el bot Python que obtiene datos en tiempo real de TradingView.

### Opción 2: Pine Script Directamente en TradingView
Ejecuta la estrategia completa dentro de TradingView usando Pine Script.

---

## 📡 Opción 1: Python Bot + TradingView Data

### Paso 1: Instalar Dependencias

```bash
pip install tradingview-ta tvDatafeed
```

### Paso 2: Ejecutar el Bot

```bash
# Modo demo con datos reales de TradingView
python bot.py --mode demo --interval 60

# Sin TradingView (datos sintéticos)
python bot.py --mode demo --no-tradingview
```

### Paso 3: Test de Conexión

```bash
# Probar si TradingView está funcionando
python tradingview_data.py
```

Esto debería mostrar:
```
✅ TradingView data fetcher inicializado
📊 Obteniendo datos de MGC1! (COMEX) - 5min - 100 barras...
✅ Datos obtenidos: 100 barras
   Rango: 2024-11-25 00:00:00 a 2024-11-25 08:20:00
   Último precio: 2575.50
```

### Configuración Avanzada

En `config.py`, ajusta el símbolo si es necesario:

```python
# Para MGC (Micro Gold)
SYMBOL = "MGC1!"  # Contrato continuo
EXCHANGE = "COMEX"

# Otros futuros populares:
# SYMBOL = "GC1!"   # Gold Full Size
# SYMBOL = "ES1!"   # E-mini S&P 500
# SYMBOL = "NQ1!"   # E-mini Nasdaq
```

### Limitaciones

- **Sin login:** ~5-10 requests por minuto
- **Con login:** Más requests disponibles
- Los datos son delayed (15-20 min), no real-time

Para login (opcional):
```python
fetcher = TradingViewDataFetcher(
    username="tu_usuario_tv",
    password="tu_password_tv"
)
```

---

## 🌲 Opción 2: Pine Script en TradingView

### Paso 1: Copiar el Script

1. Abre TradingView: https://www.tradingview.com
2. Abre el gráfico de MGC:
   - Busca: `MGC1!` o `COMEX:MGC1!`
   - Timeframe: 5 minutos
3. Clic en "Pine Editor" (abajo de la pantalla)
4. Pega el contenido de `strategy_pinescript.pine`
5. Clic en "Add to Chart"

### Paso 2: Configurar Parámetros

En el panel de configuración de la estrategia:

```
🎯 Niveles:
  - Incremento de Nivel: 0.5
  - Tolerancia de Nivel: 0.2

📈 Tendencia:
  - Barras para Tendencia: 20
  - Período de Swing: 10
  - Fuerza Mínima: 0.6

💰 Riesgo:
  - Riesgo por Trade: 2%
  - Stop Loss: 2.0 puntos
  - Take Profit: 3.0 puntos

✅ Filtros:
  - ☑ Requiere Confirmación de Tendencia
  - Tasa Mínima de Rebote: 0.4
```

### Paso 3: Backtest

1. Clic en "Strategy Tester" (abajo)
2. Selecciona el rango de fechas
3. Revisa las métricas:
   - Net Profit
   - Win Rate
   - Profit Factor
   - Max Drawdown

### Paso 4: Alertas (Opcional)

Para recibir notificaciones cuando hay señales:

1. Clic derecho en el gráfico → "Add Alert"
2. Condición: Selecciona "Señal LONG" o "Señal SHORT"
3. Opciones:
   - Once Per Bar Close (recomendado)
   - Notificación: Email, SMS, o Webhook
4. Guardar

### Visualización en Pine Script

El script Pine muestra:

- **Niveles grises punteados**: Niveles psicológicos cada 0.5
- **Nivel amarillo**: Nivel más cercano al precio actual
- **Triángulos rojos**: Swing highs
- **Triángulos verdes**: Swing lows
- **Fondo verde claro**: Tendencia alcista
- **Fondo rojo claro**: Tendencia bajista
- **Tabla (esquina superior derecha)**: Info de tendencia, fuerza, nivel cercano

---

## 🔗 Opción 3: Webhooks (Avanzado)

Conecta TradingView → Bot Python usando webhooks.

### Configuración

1. **En TradingView:**
   - Crear alerta con Webhook URL
   - URL: `http://tu-servidor.com/webhook`

2. **En el Bot Python:**
   ```bash
   python webhook_server.py
   ```

3. **El servidor recibe señales y ejecuta trades**

> ⚠️ Requiere servidor público o ngrok para testing

---

## 📊 Comparación de Opciones

| Feature | Python + TV Data | Pine Script | Webhooks |
|---------|-----------------|-------------|----------|
| Datos reales | ✅ | ✅ | ✅ |
| Backtesting | ✅ | ✅ | ❌ |
| Trading automatizado | ✅ | ❌ | ✅ |
| Fácil de configurar | ⭐⭐ | ⭐⭐⭐ | ⭐ |
| Personalizablecustom logic | ✅ | Limitado | ✅ |
| Requiere servidor | ❌ | ❌ | ✅ |

---

## 🎯 Recomendación

**Para empezar:**
1. Usa **Pine Script** para backtesting y ver cómo funciona
2. Optimiza parámetros en TradingView
3. Cuando estés satisfecho, usa **Python Bot + TV Data** para automatización

**Para trading en vivo:**
- Si solo quieres señales → Usa **Pine Script + Alertas**
- Si quieres automatización completa → Usa **Python Bot + Webhooks**

---

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'tvDatafeed'"
```bash
pip install tvDatafeed
```

### "❌ TradingView no está disponible"
Verifica la instalación:
```bash
python -c "import tvDatafeed; print('OK')"
```

### "No se pudieron obtener datos"
- Verifica que el símbolo sea correcto: `MGC1!`
- Verifica el exchange: `COMEX`
- Prueba con otro timeframe: `1h` en vez de `5min`

### Los datos están delayed
Esto es normal. TradingView gratuito tiene delay de 15-20 min.
Para datos real-time necesitas suscripción premium de TradingView.

### Pine Script no compila
- Verifica que la versión sea `//@version=5`
- Copia el script completo sin modificaciones
- Si persiste, contacta soporte

---

## 📚 Recursos

- **TradingView:** https://www.tradingview.com
- **Pine Script Docs:** https://www.tradingview.com/pine-script-docs/
- **tvDatafeed GitHub:** https://github.com/StreamAlpha/tvdatafeed
- **tradingview-ta:** https://github.com/brian-the-dev/python-tradingview-ta

---

## ⚠️ Disclaimer

- Los datos de TradingView pueden tener delay
- Backtesting en TradingView usa datos históricos que pueden diferir de la realidad
- Siempre prueba en cuenta demo antes de usar dinero real
- Las comisiones y slippage reales pueden afectar los resultados

---

## 🎓 Próximos Pasos

1. ✅ Instalar dependencias de TradingView
2. ✅ Probar `python tradingview_data.py`
3. ✅ Cargar Pine Script en TradingView
4. ✅ Hacer backtesting con datos históricos
5. ✅ Optimizar parámetros
6. ✅ Configurar alertas
7. ⏳ Probar en cuenta demo
8. ⏳ Trading en vivo (solo después de éxito en demo)

¡Buena suerte! 🚀
