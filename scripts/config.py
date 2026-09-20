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
    "TX": "Materiales",       # Ternium, grupo Techint (argentino) -- el ticker real de NYSE es "TX", no "TXR" (ese es el código interno de BYMA)
    "TEN": "Energía",         # Tenaris, grupo Techint (argentino), caños para petróleo/gas
    "T": "Telecomunicaciones",
    "AAL": "Transporte",
    "BIOX": "Agro",           # Bioceres, agrobiotecnología argentina
    "ARKK": "ETF",
    "BRK-B": "Diversificado", # Berkshire Hathaway -- BYMA lo llama "BRKB", en Yahoo es "BRK-B"
    "DOW": "Materiales",      # Dow Inc., química
    # "NTCO": "Consumo",       # Natura -- sacado del universo: falló 4 corridas
    # seguidas en yfinance a pesar de estar realmente listada en NYSE (parece
    # un problema específico y persistente de Yahoo con este símbolo puntual,
    # no un error nuestro). Si en algún momento se quiere reintentar, solo
    # hay que sacarle el comentario a esta línea.
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
    # --- 19 tickers nuevos sumados en sept. 2026 (7 confirmados + 12 de la tanda BYMA/Comafi) ---
    "ARM": "Tecnología",       # ARM Holdings, diseño de chips
    "AVGO": "Tecnología",      # Broadcom
    "IREN": "Tecnología",      # IREN Ltd -- data centers Bitcoin/IA
    "TXN": "Tecnología",       # Texas Instruments
    "AMAT": "Tecnología",      # Applied Materials
    "SNDK": "Tecnología",      # SanDisk, spin-off de Western Digital
    "EDN": "Energía",          # Edenor -- distribución eléctrica AMBA (ADR, sin CEDEAR propio)
    "KLAC": "Tecnología",      # KLA Corp -- equipos de inspección de semiconductores
    "SKHY": "Tecnología",      # SK Hynix -- memorias DRAM/NAND para IA
    "DELL": "Tecnología",      # Dell -- servidores y storage corporativo
    "WDC": "Tecnología",       # Western Digital -- discos rígidos
    "GEV": "Energía",          # GE Vernova -- equipos de generación eléctrica
    "TLN": "Energía",          # Talen Energy -- generadora con exposición a data centers
    "MS": "Bancos",            # Morgan Stanley
    "IBKR": "Fintech",         # Interactive Brokers
    "SPCX": "Aeroespacial",    # SpaceX
    "WELL": "Real Estate",     # Welltower -- REIT de infraestructura de salud
    "PLD": "Real Estate",      # Prologis -- REIT de depósitos y logística
    "LIN": "Materiales",       # Linde -- gases industriales
    "SHW": "Materiales",       # Sherwin-Williams -- pinturas
    # --- Tanda 1 del listado completo de CEDEARs de tu bróker (sept. 2026) ---
    # Sin ratio todavía (las capturas no lo mostraban) -- entran al universo
    # técnico (RS Score, alertas) pero no al panel de CEDEAR caro/barato.
    "BP": "Energía", "CAT": "Materiales", "CL": "Consumo", "COST": "Consumo",
    "CRM": "Tecnología", "CRWD": "Tecnología", "DE": "Materiales", "DHR": "Materiales",
    "DIS": "Tecnología",       # Walt Disney -- ticker real de NYSE, no "DISN" (código interno de BYMA)
    "EBAY": "Consumo", "ETSY": "Consumo", "GS": "Bancos",
    "IBM": "Tecnología", "INTC": "Tecnología", "ISRG": "Salud", "MA": "Fintech",
    "MCD": "Consumo", "MDLZ": "Consumo", "META": "Tecnología", "MMM": "Materiales",
    "MRNA": "Salud", "MRVL": "Tecnología", "MU": "Tecnología", "NKE": "Consumo",
    "NOW": "Tecnología", "ORCL": "Tecnología", "OXY": "Energía", "PANW": "Tecnología",
    "PATH": "Tecnología", "PG": "Consumo", "PINS": "Tecnología", "PSX": "Energía",
    "RBLX": "Tecnología", "ROKU": "Tecnología", "ROST": "Consumo", "SBUX": "Consumo",
    "SHEL": "Energía", "SLB": "Energía", "SNAP": "Tecnología", "SNOW": "Tecnología",
    "TEAM": "Tecnología", "TJX": "Consumo", "TTE": "Energía", "UAL": "Transporte",
    "UNP": "Transporte", "UPST": "Fintech", "USB": "Bancos", "VRTX": "Salud",
    "CVS": "Salud",  # CVS Health Corp -- confirmado por Victoria
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

# --- Umbral de "corrida degradada": si falla más de este % del universo,
# el RS Score de los que sí llegaron se calcula sobre un percentil chico y
# no representativo -- se sigue guardando el resultado (los datos que sí
# vinieron son reales), pero se marca la corrida y se salta el envío de
# Telegram esa vez puntual, para no mandar una alerta de compra basada en
# un ranking inflado por matemática de percentil rota, no por el mercado.
UMBRAL_CORRIDA_DEGRADADA_PCT = 25
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
    "gap_alcista":   "🚀 Gap alcista con macrotendencia",
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
    # --- 19 tickers nuevos sumados en sept. 2026 (EDN queda afuera: es ADR sin CEDEAR propio) ---
    "ARM": 27, "AVGO": 39, "IREN": 12, "TXN": 5, "AMAT": 5, "SNDK": 170,
    "KLAC": 34, "SKHY": 25, "DELL": 74, "WDC": 92, "GEV": 180, "TLN": 63,
    "MS": 41, "IBKR": 17, "SPCX": 50, "WELL": 48, "PLD": 29, "LIN": 102, "SHW": 69,
    # --- Tanda 1 del listado completo (ratios oficiales BYMA, PDF actualizado 3/2/2026,
    # salvo CRWD que se sumó a BYMA después de esa fecha -- ratio de fuentes cruzadas) ---
    "BP": 5, "CAT": 20, "CL": 3, "COST": 48, "CRM": 18, "CRWD": 79, "DE": 40,
    "DHR": 54, "DIS": 12, "EBAY": 2, "ETSY": 16, "GS": 13, "IBM": 15, "INTC": 5,
    "ISRG": 90, "MA": 33, "MCD": 24, "MDLZ": 15, "META": 24, "MMM": 10, "MRNA": 19,
    "MRVL": 14, "MU": 5, "NKE": 12, "NOW": 172, "ORCL": 3, "OXY": 5, "PANW": 50,
    "PATH": 2, "PG": 15, "PINS": 7, "PSX": 6, "RBLX": 2, "ROKU": 13, "ROST": 4,
    "SBUX": 12, "SHEL": 2, "SLB": 3, "SNAP": 1, "SNOW": 30, "TEAM": 47, "TJX": 22,
    "TTE": 3, "UAL": 5, "UNP": 20, "UPST": 5, "USB": 5, "VRTX": 101, "CVS": 15,
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

# --- Señal "Gap alcista + macrotendencia" (adaptada de un dossier de bot de trading con IA) ---
# Original: precio de HOY > máximo intradiario de AYER + gap de apertura >=3%.
# Adaptada porque el pipeline solo trae precio de cierre (no apertura/máximo/mínimo):
# variación de CIERRE a CIERRE >= umbral, + precio de ayer ya por encima de su SMA200
# (misma idea de "solo operar a favor de la macrotendencia"), + que hoy sea el cierre
# más alto de los últimos 10 días (proxy de "ruptura", ya que no tenemos el máximo real).
UMBRAL_GAP_ALCISTA_PCT = 3       # % mínimo de suba de cierre a cierre para considerarlo "gap"
VENTANA_GAP_MAXIMO_DIAS = 10     # días hacia atrás para chequear que hoy sea el cierre más alto

# --- Modo de ejecución: en "test" no se envían notificaciones reales de Telegram ---
import os
MODO = os.environ.get("RADAR_MODO", "test")  # "test" | "produccion"
