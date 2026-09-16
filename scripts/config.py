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
    # --- Sumados desde la cartera de CEDEARs de Victoria (versión en USD del activo real) ---
    "TSLA": "Automotriz",
    "QQQ": "ETF",
    "BABA": "Consumo",       # e-commerce, mismo grupo que MELI
    "OKLO": "Energía",       # reactores nucleares modulares
    "JMIA": "Consumo",       # e-commerce africano
    "SATL": "Tecnología",    # imágenes satelitales
    "CRWV": "Tecnología",    # cómputo en la nube para IA
    "TEM": "Salud",          # IA aplicada a diagnóstico/datos de salud
    "LAC": "Materiales",     # litio, insumo para baterías
    # --- Lista ampliada pedida por Victoria (ver notas de ajuste de tickers en el chat) ---
    "AMD": "Tecnología",      # asumido por "AM" -- confirmar si no era esto
    "TSM": "Tecnología",
    "QCOM": "Tecnología",
    "GLOB": "Tecnología",     # Globant, de origen argentino
    "ADBE": "Tecnología",
    "SHOP": "Tecnología",
    "ZM": "Tecnología",
    "AMZN": "Consumo",
    "UBER": "Consumo",
    "NFLX": "Consumo",
    "TGT": "Consumo",
    "ABNB": "Consumo",
    "HOOD": "Fintech",
    "PYPL": "Fintech",
    "V": "Fintech",
    "XYZ": "Fintech",         # antes "Square"
    "SPGI": "Fintech",        # calificadora/datos financieros
    "C": "Bancos",
    "GM": "Automotriz",
    "F": "Automotriz",
    "VALE": "Materiales",
    "B": "Materiales",        # Barrick Gold -- ticker corto, confirmar que no colisione
    "TXR": "Materiales",      # Ternium, grupo Techint (argentino)
    "TEN": "Energía",         # Tenaris, grupo Techint (argentino), caños para petróleo/gas
    "T": "Telecomunicaciones",
    "AAL": "Transporte",
    "BIOX": "Agro",           # Bioceres, agrobiotecnología argentina
    "ARKK": "ETF",
    "BRK-B": "Diversificado", # Berkshire Hathaway -- BYMA lo llama "BRKB", en Yahoo es "BRK-B"
    "DOW": "Materiales",      # Dow Inc., química
    "NTCO": "Consumo",        # Natura (antes NATU3) -- cosmética, mismo grupo que WMT/TGT
    "LAR": "Materiales",      # Lithium Americas (Argentina) -- distinto de LAC
    "BBD": "Bancos",          # Banco Bradesco (Brasil)
    "FSLR": "Energía",        # First Solar
    "GPRK": "Energía",        # GeoPark
    "LLY": "Salud",           # Eli Lilly
    "NIO": "Automotriz",      # NIO, autos eléctricos chinos
    "NU": "Fintech",          # Nu Holdings (Nubank)
    "PAGS": "Fintech",        # PagSeguro
    "PEP": "Consumo",         # PepsiCo
    "PLTR": "Tecnología",     # Palantir
    "RIO": "Materiales",      # Rio Tinto
    "SPCE": "Aeroespacial",   # Virgin Galactic
    "SPOT": "Tecnología",     # Spotify
    "SPXL": "ETF",            # Direxion S&P500 Bull 3x -- APALANCADO, más volátil que un ETF normal
    "UNH": "Salud",           # UnitedHealth
    "URA": "Energía",         # Global X Uranium ETF, insumo para nuclear (par de OKLO)
    "TGS": "Energía",         # Transportadora de Gas del Sur -- ADR en NYSE, misma empresa que TGSU2
    "PAM": "Energía",         # Pampa Energía -- generación eléctrica + oil & gas
    "SUPV": "Bancos",         # Grupo Supervielle
    "BBAR": "Bancos",         # Banco BBVA Argentina -- asumí que no era el BBVA español, confirmame
    "BBVA": "Bancos",         # Banco Bilbao Vizcaya Argentaria (España) -- la matriz, distinta de BBAR
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
    "lider_soporte": "📈 Líder apoyando en soporte",
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
# Desde la salida del cepo cambiario (abril 2025), la brecha oficial/blue
# ronda 1-3% en condiciones normales -- un umbral de 30% (pensado para la
# época de controles cambiarios) casi nunca se dispararía. Se baja a 10%
# para que siga siendo una alerta útil si la brecha empieza a ensancharse
# de nuevo (ej. ante una eventual reimposición de controles).
BRECHA_CAMBIARIA_ALERTA_PCT = 10

# --- Historial persistente (necesario para confirmación con demora y stop-loss) ---
ARCHIVO_HISTORIAL = "data/historial_alertas.json"

# --- Ratios de conversión CEDEAR (BYMA, actualizado 3/2/2026 -- fuente oficial).
# Formato "N:1" en BYMA significa N CEDEARs = 1 acción real -> valor teórico ARS
# = (precio_usd * CCL) / ratio. Ninguno de los tuyos usa el formato inverso "1:N".
# IMPORTANTE: los ratios cambian ocasionalmente por decisiones corporativas
# (splits) -- conviene re-chequear contra BYMA cada tanto, no son eternos.
RATIOS_CEDEAR = {
    "SPY": 20, "TSLA": 15, "QQQ": 20, "NVDA": 24, "BABA": 9, "OKLO": 28,
    "AAPL": 20, "JMIA": 1, "SATL": 1, "CRWV": 27, "TEM": 12, "LAC": 1,
}

# --- Umbral para marcar un CEDEAR como "caro" o "barato" respecto a su valor teórico ---
BRECHA_CEDEAR_ALERTA_PCT = 3   # +/- 3% de diferencia se considera una distorsión a mirar

# --- Panel de "Movimientos del día" -- tickers que se movieron fuerte HOY (no en meses) ---
UMBRAL_MOVIMIENTO_DIARIO_PCT = 5   # +/- 5% en un solo día entra al panel

# --- Ventana de vigencia de una alerta en el dashboard (ver bug de acumulación infinita) ---
VENTANA_ALERTA_HORAS = 48   # una alerta deja de mostrarse en "Alertas Activas" pasadas estas horas
                             # desde que ese ESTADO empezó (no desde que se detectó por primera vez
                             # el ticker) -- el historial completo se sigue guardando igual

# --- Señal "Líder apoyando en soporte" (RS alto + descansando cerca de su SMA50 sin romperla) ---
UMBRAL_LIDER_RS = 80              # RS Score mínimo para considerarse "líder"
UMBRAL_LIDER_DIST_SMA50_PCT = 2   # como máximo a este % POR ENCIMA de la SMA50 (no por debajo)

# --- Modo de ejecución: en "test" no se envían notificaciones reales de Telegram ---
import os
MODO = os.environ.get("RADAR_MODO", "test")  # "test" | "produccion"
