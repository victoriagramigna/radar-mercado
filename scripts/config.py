"""
Configuración central del Radar de Mercado.
Cambiar acá el universo de tickers, sectores, y parámetros del sistema
NO requiere tocar el resto del código.
"""

# --- Universo de tickers por sector (ampliable a demanda) ---
TICKERS = {
    "XOM": "Energía", "CVX": "Energía", "VIST": "Energía", "YPF": "Energía",
    "AAPL": "Tecnología", "MSFT": "Tecnología", "NVDA": "Tecnología", "GOOGL": "Tecnología",
    "JPM": "Bancos", "BMA": "Bancos", "GGAL": "Bancos", "WFC": "Bancos",
    "JNJ": "Salud", "PFE": "Salud", "MRK": "Salud",
    "WMT": "Consumo", "KO": "Consumo", "MELI": "Consumo",
    "EWZ": "ETF", "XLE": "ETF", "XLK": "ETF",
}

BENCHMARK = "SPY"

# --- Palabras clave por sector, para detectar eventos geopolíticos/macro en noticias ---
PALABRAS_CLAVE_SECTOR = {
    "Energía": ["ormuz", "opep", "opep+", "sanciones petroleras", "recorte de producción",
                "precio del crudo", "barril", "gasoducto", "refinería"],
    "Tecnología": ["aranceles semiconductores", "controles de exportación china", "chips",
                   "ban tecnológico", "taiwan semiconductor"],
    "Bancos": ["suba de tasas", "fed", "reserva federal", "crisis bancaria", "quiebra banco",
               "tasa de interés"],
    "Salud": ["fda", "retiro de mercado", "juicio farmacéutica", "patente vencida"],
    "Consumo": ["aranceles importación", "guerra comercial", "boicot"],
}

# --- Parámetros del Score de Confirmación (ajustables tras el backtest con datos reales) ---
SCORE_MINIMO_ALERTA = 3       # score a partir del cual se considera señal relevante
VOLUMEN_RELATIVO_MINIMO = 1.5 # volumen de hoy vs promedio 20d, para confirmar
RSI_ZONA_SANA = (40, 65)      # rango de RSI que suma punto al score
VENTANA_BASE_DIAS = 30        # días recientes para medir si hubo consolidación previa

# --- Confirmación con demora (evita que el score suba/baje de golpe por un solo día) ---
DIAS_CONFIRMACION = 2          # días verdes seguidos (o nuevo máximo) para pasar a "confirmado"
SCORE_TECHO_SIN_CONFIRMAR = 3  # score máximo que puede mostrar una señal recién detectada, sin confirmar aún

# --- Estados narrativos (van junto al score numérico, no lo reemplazan) ---
ESTADOS = {
    "recien_cruzo":  "🔨 Recién cruzó, sin confirmar",
    "confirmado":    "✅ Confirmado",
    "ruptura_vol":   "💣 Ruptura de máximo con volumen",
    "sacudon":       "⚠️ Sacudón, sin definición clara",
    "deterioro":     "🔻 Rompió piso (SMA200)",
    "stop_loss":     "🛑 Perdió EMA200 tras rebote — stop sugerido",
}

# --- Medias móviles a calcular ---
SMA_CORTAS = (10, 21, 50)   # diario: SMA10, SMA21, SMA50 (setup Minervini)
EMA_LARGA = 200              # diario: EMA200
EMA_SEMANAL = (10, 200)      # semanal: EMA10, EMA200

# --- VCP (Volatility Contraction Pattern) ---
VCP_MIN_CONTRACCIONES = 2     # cantidad mínima de contracciones decrecientes para considerarlo válido
VCP_VENTANA_DIAS = 10         # tamaño de cada "ola" analizada, en días

# --- Régimen de mercado vía VIX (análogo al contexto macro-local, pero para EEUU) ---
VIX_TICKER = "^VIX"
VIX_UMBRAL_ALTO = 25          # VIX > 25 se considera mercado nervioso/volátil

# --- Umbrales de contexto macro-local (Argentina) ---
RIESGO_PAIS_VARIACION_ALERTA = 0.08   # 8% de salto diario dispara "inestable"
BRECHA_CAMBIARIA_ALERTA_PCT = 30      # brecha oficial/blue > 30% dispara "inestable"

# --- Historial persistente (necesario para confirmación con demora y stop-loss) ---
ARCHIVO_HISTORIAL = "data/historial_alertas.json"

# --- Modo de ejecución: en "test" no se envían notificaciones reales de Telegram ---
import os
MODO = os.environ.get("RADAR_MODO", "test")  # "test" | "produccion"
