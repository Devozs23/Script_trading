"""
Configuración del Trading Bot
"""

# ==================== CONFIGURACIÓN DE NIVELES ====================
LEVEL_INCREMENT = 0.5  # Incremento de niveles (1.0, 1.5, 2.0, 2.5, etc.)
LEVEL_RANGE_MIN = 1.0  # Nivel mínimo a considerar
LEVEL_RANGE_MAX = 10.5  # Nivel máximo a considerar

# ==================== CONFIGURACIÓN MGC ====================
SYMBOL = "MGC"  # Micro Gold
TIMEFRAME = "5min"  # Temporalidad principal
TICK_SIZE = 0.1  # Tamaño mínimo de tick para MGC
TICK_VALUE = 1.0  # Valor de cada tick
CONTRACT_SIZE = 10  # Tamaño del contrato MGC

# ==================== DETECCIÓN DE TENDENCIA ====================
TREND_LOOKBACK_BARS = 20  # Barras para detectar inicio de tendencia
SWING_DETECTION_PERIOD = 10  # Período para detectar swing high/low
MIN_TREND_STRENGTH = 0.6  # Fuerza mínima de tendencia (0-1)

# ==================== PARÁMETROS DE TRADING ====================
# Zona de reacción alrededor del nivel
LEVEL_TOLERANCE = 0.2  # ±0.2 puntos del nivel exacto

# Gestión de riesgo
RISK_PER_TRADE = 0.02  # 2% de riesgo por operación
INITIAL_CAPITAL = 10000  # Capital inicial para backtesting
MAX_POSITIONS = 3  # Máximo de posiciones simultáneas

# Stop Loss y Take Profit
DEFAULT_STOP_LOSS_POINTS = 2.0  # Stop loss en puntos
DEFAULT_TAKE_PROFIT_POINTS = 3.0  # Take profit en puntos
RISK_REWARD_RATIO = 1.5  # Ratio riesgo/beneficio

# ==================== FILTROS DE ENTRADA ====================
MIN_DISTANCE_TO_LEVEL = 0.1  # Distancia mínima al nivel para considerar entrada
MAX_DISTANCE_TO_LEVEL = 0.3  # Distancia máxima al nivel para considerar entrada
REQUIRE_TREND_CONFIRMATION = True  # Requiere confirmación de tendencia
MIN_VOLUME_MULTIPLIER = 1.2  # Volumen mínimo vs promedio

# ==================== BACKTESTING ====================
BACKTEST_START_DATE = "2024-01-01"
BACKTEST_END_DATE = "2024-11-25"
BACKTEST_COMMISSION = 0.0002  # 0.02% comisión por operación
BACKTEST_SLIPPAGE = 0.1  # Slippage estimado en puntos

# ==================== BROKER / CONEXIÓN ====================
# MetaTrader 5
MT5_LOGIN = ""  # Llenar con tu login
MT5_PASSWORD = ""  # Llenar con tu password
MT5_SERVER = ""  # Llenar con tu servidor

# Trading mode
TRADING_MODE = "demo"  # "demo" o "live" (NUNCA empezar con live)

# ==================== LOGGING ====================
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
LOG_FILE = "trading_bot.log"
SAVE_TRADES_TO_CSV = True
TRADES_CSV_FILE = "trades.csv"
