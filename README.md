# MGC Trading Bot - Price Level Strategy

Bot de trading algorítmico para Micro Gold (MGC) que identifica y opera en niveles psicológicos de precio.

## Estrategia

El bot identifica niveles de precio en incrementos de 0.5 (1.0, 1.5, 2.0, 2.5, etc.) donde el precio tiende a reaccionar. Detecta el inicio de movimientos alcistas o bajistas y opera basándose en las reacciones del precio en estos niveles.

## Características

- ✅ Detección de niveles psicológicos cada 0.5 puntos
- ✅ Identificación de inicio de tendencias alcistas/bajistas
- ✅ Detección de reacciones en niveles clave
- ✅ Sistema de backtesting integrado
- ✅ Configuración específica para MGC
- 🔄 En desarrollo: Reglas adicionales y optimización

## Instalación

### 1. Clonar el repositorio
```bash
git clone <url-del-repo>
cd Script_trading
```

### 2. Crear entorno virtual (recomendado)
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno (opcional)
```bash
cp .env.example .env
# Editar .env con tus credenciales de broker
```

## Uso

### Prueba rápida (sin broker)
```bash
python quick_test.py
```

### Backtesting con datos sintéticos
```bash
python backtesting.py
```

### Trading en vivo (Demo primero)
```bash
# SIEMPRE probar en demo primero
python bot.py --mode demo --interval 60
```

### Trading en vivo (Real)
⚠️ **SOLO después de pruebas exhaustivas en demo**
```bash
python bot.py --mode live
```

## ⚠️ Advertencias

- **SIEMPRE** prueba en cuenta demo primero
- El rendimiento pasado no garantiza resultados futuros
- Usa gestión de riesgo apropiada
- Monitorea el bot activamente
- Ten en cuenta comisiones y slippage

## Configuración

Edita `config.py` para ajustar:
- Niveles de precio
- Parámetros de detección de tendencia
- Gestión de riesgo
- Configuración del broker

## Estructura del Proyecto

```
Script_trading/
├── README.md                 # Este archivo
├── requirements.txt          # Dependencias
├── config.py                 # Configuración centralizada
├── level_detector.py         # Detecta niveles psicológicos (0.5 increments)
├── trend_detector.py         # Detecta inicio de tendencias
├── trading_strategy.py       # Lógica de trading y señales
├── backtesting.py            # Motor de backtesting
├── bot.py                    # Bot principal para trading en vivo
├── quick_test.py             # Script de prueba rápida
└── .env.example              # Plantilla de configuración

```

## Próximos Pasos (Roadmap)

### ✅ Completado
- [x] Estructura básica del proyecto
- [x] Lógica de detección de niveles (incrementos de 0.5)
- [x] Detección de tendencias (swing highs/lows, HH/HL, LH/LL)
- [x] Sistema de señales basado en niveles + tendencia
- [x] Framework de backtesting básico
- [x] Gestión de riesgo (% de cuenta)
- [x] Configuración específica para MGC

### 🔄 En Desarrollo
- [ ] Integración con broker real (MetaTrader 5)
- [ ] Obtención de datos históricos reales para MGC
- [ ] Backtesting con datos reales
- [ ] Optimización de parámetros
- [ ] Filtros adicionales (volumen, momentum)
- [ ] Trailing stop loss
- [ ] Gestión de múltiples timeframes

### 📋 Futuro
- [ ] Dashboard web de monitoreo
- [ ] Alertas por email/telegram
- [ ] Machine Learning para mejorar detección de niveles
- [ ] Auto-ajuste de parámetros
- [ ] Reporting avanzado
